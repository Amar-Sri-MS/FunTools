#!/usr/bin/env python3

#
# Analysis of logs from a storage cluster.
#

import argparse
import time

import pipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('build_id', help="Unique build ID")
    parser.add_argument("dir", help="Log directory")
    parser.add_argument('machines', nargs='+', help='FS1600 machines')
    parser.add_argument('output', help='Output block type', default='ElasticOutput')

    args = parser.parse_args()

    env = {}
    env['logdir'] = args.dir
    env['build_id'] = args.build_id

    cfg = build_pipeline(args.machines, args.output)

    block_factory = pipeline.BlockFactory()

    start = time.time()
    p = pipeline.Pipeline(block_factory, cfg, env)
    p.process()
    end = time.time()

    print('Time spent processing: {}s'.format(end - start))


def build_pipeline(machines, output_block):
    """ Constructs a pipeline for all the specified machines """

    cfg = {}
    pipeline_cfg = []

    for machine in machines:
        pipeline_cfg.extend(funos_input_pipeline(machine))

    pipeline_cfg.extend(
        controller_input_pipeline('kafka',
                                  '${logdir}/cs/sclogs/start_kafka_consumer/info*'))
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
                                  multiline_settings={
                                      'pattern': r'(\[.*\])\s+([(-0-9|/0-9)]+)+(?:T|\s)([:0-9]+).([0-9]+)\s?((?:\-|\+)[0-9]{4})'
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
    input_id = machine + '_f1_0'
    parse_id = input_id + '_parse'

    input = {
        'id': input_id,
        'block': 'TextFileInput',
        'cfg': {
            'file_pattern': '${{logdir}}/devices/{}/system_current/F1_0_funos.txt'.format(machine)
        },
        'out': parse_id
    }

    parse = {
        'id': parse_id,
        'block': 'FunOSInput',
        'out': 'merge'
    }

    return [input, parse]


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
            }
        }

        return [output]

if __name__ == '__main__':
    main()
