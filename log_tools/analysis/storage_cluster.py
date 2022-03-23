#!/usr/bin/env python3

#
# Analysis of logs from a storage cluster.
#

import argparse

from . import pipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('build_id', help="Unique build ID")
    parser.add_argument("dir", help="Log directory")
    parser.add_argument('machines', nargs='*', help='FS1600 machines')
    parser.add_argument('--output', help='Output block type', default='ElasticOutput')

    args = parser.parse_args()

    env = {}
    env['logdir'] = args.dir
    env['build_id'] = args.build_id

    cfg = build_pipeline(args.machines, args.output)

    block_factory = pipeline.BlockFactory()

    p = pipeline.Pipeline(block_factory, cfg, env)
    p.process()


def build_pipeline(machines, output_block):
    """ Constructs a pipeline for all the specified machines """

    cfg = {}
    pipeline_cfg = []

    for machine in machines:
        pipeline_cfg.extend(funos_input_pipeline(machine))

    pipeline_cfg.extend(
        controller_input_pipeline('kafka',
                                  '${logdir}/cs/sclogs/storage_consumer/info*'))
    pipeline_cfg.extend(
        controller_input_pipeline('apigw',
                                  '${logdir}/cs/apigateway/info*'))

    pipeline_cfg.extend(
        controller_input_pipeline('sns',
                                  '${logdir}/cs/sns/sns*',
                                  parse_block='KeyValueInput'))

    pipeline_cfg.extend(
        controller_input_pipeline('dataplacement',
                                  '${logdir}/cs/sclogs/dataplacement/info*',
                                  # [logger.go:158] 2022-01-10T04:04:31.707689851Z info log level:debug and backupcount:8 in /var/log/dataplacement/info.log 
                                  multiline_settings={
                                      'pattern': r'(\[.*\])\s+(\d{4}(?:-|/)\d{2}(?:-|/)\d{2})+(?:T|\s)([:0-9]+).([0-9]+)(?:Z|)'
                                  }))

    pipeline_cfg.extend(output_pipeline(output_block))

    cfg['pipeline'] = pipeline_cfg
    return cfg


def controller_input_pipeline(id, file_pattern, multiline_settings={}, parse_block='GenericInput'):
    parse_id = id + '_parse'

    input = {
        'id': id,
        'block': 'TextFileInput',
        'cfg': {
            'file_pattern': file_pattern,
            **multiline_settings
        },
        'out': parse_id
    }

    parse = {
        'id': parse_id,
        'block': parse_block,
        'out': 'merge'
    }

    return [input, parse]


def funos_input_pipeline(machine):
    blocks = []
    # 2 DPUs in FS1600 machine
    # TODO: (Sourabh) Unnecessary blocks for FS800
    for i in range(0, 2):

        # Support for v1.x directory structure
        input_id_v1 = f'{machine}_f1_{i}_v1'
        parse_id_v1 = f'{input_id_v1}_parse'

        input_v1 = {
            'id': input_id_v1,
            'block': 'TextFileInput',
            'cfg': {
                'file_pattern': '${{logdir}}/devices/{}/F1_{}_funos.txt*'.format(machine, i)
            },
            'out': parse_id_v1
        }

        parse_v1 = {
            'id': parse_id_v1,
            'block': 'FunOSInput',
            'out': 'merge'
        }

        # Support for v2.0 directory structure
        input_id = f'{machine}_f1_{i}'
        parse_id = f'{input_id}_parse'

        input = {
            'id': input_id,
            'block': 'TextFileInput',
            'cfg': {
                'file_pattern': '${{logdir}}/devices/{}/dpu_logs_lines_c_s{}_0/*funos.txt*'.format(machine, i)
            },
            'out': parse_id
        }

        parse = {
            'id': parse_id,
            'block': 'FunOSInput',
            'out': 'merge'
        }

        storage_agent_id = f'{input_id}_storage_agent'
        storage_agent_parse_id = f'{storage_agent_id}_parse'

        storage_agent = {
            'id': storage_agent_id,
            'block': 'TextFileInput',
            'cfg': {
                'file_pattern': '${{logdir}}/devices/{}/come_optfungible_log/fungible/logs/storage_agent_{}/storage_agent/info*'.format(machine, i),
                'pattern': r'([(-0-9|/0-9)]+)+(?:T|\s)([:0-9]+)(?:.|,)([0-9]{3,9})'
            },
            'out': storage_agent_parse_id
        }

        storage_agent_parse = {
            'id': storage_agent_parse_id,
            'block': 'GenericInput',
            'out': 'merge'
        }

        blocks.extend([input_v1, parse_v1, input, parse, storage_agent, storage_agent_parse])

    return blocks


def output_pipeline(output_block):
    if output_block == 'HTMLOutput':
        merge = {
            'id': 'merge',
            'block': 'Merge',
            'out': 'dt'
        }

        dt = {
            'id': 'dt',
            'block': 'HumanDateTime',
            'out': 'html'
        }

        html = {
            'id': 'html',
            'block': 'HTMLOutput',
            'cfg': {
                'dir': 'log_${build_id}',
                'lines_per_page': 10000
            }
        }

        return [merge, dt, html]
    elif output_block == 'ElasticOutput':
        output = {
            "id": "merge",
            "block": "ElasticOutput",
            "cfg": {
                "index": "log_${build_id}"
            },
            "out": "analytics"
        }
        output_analytics = {
            "id": "analytics",
            "block": "AnalyticsOutput",
            "cfg": {
                "dir": "view/analytics/log_${build_id}/duplicates.html"
            }
        }

        return [output, output_analytics]

if __name__ == '__main__':
    main()
