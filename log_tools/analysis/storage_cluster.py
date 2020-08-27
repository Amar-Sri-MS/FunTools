#!/usr/bin/env python3

#
# Analysis of logs from a storage cluster.
#

import argparse

import pipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="Log directory")
    parser.add_argument('machines', nargs='+', help='FS1600 machines')

    args = parser.parse_args()

    env = {}
    env['logdir'] = args.dir
    cfg = build_pipeline(args.machines)

    block_factory = pipeline.BlockFactory()

    p = pipeline.Pipeline(block_factory, cfg, env)
    p.process()


def build_pipeline(machines):

    cfg = {}
    pipeline_cfg = []

    for machine in machines:
        pipeline_cfg.extend(funos_input_pipeline(machine))

    pipeline_cfg.extend(
        controller_input_pipeline('kafka',
                                  '${logdir}/fc/sclogs/start_kafka_consumer/info*'))
    pipeline_cfg.extend(
        controller_input_pipeline('apigw',
                                  '${logdir}/fc/apigateway/info*'))

    pipeline_cfg.extend(common_pipeline())

    cfg['pipeline'] = pipeline_cfg
    return cfg


def controller_input_pipeline(id, file_pattern):
    parse_id = id + '_parse'

    input = {
        'id': id,
        'block': 'TextFileInput',
        'cfg': {
            'file_pattern': file_pattern
        },
        'out': parse_id
    }

    parse = {
        'id': parse_id,
        'block': 'MsecInput',
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
            'file_pattern': '${{logdir}}/{}/system_current/F1_0_funos.txt'.format(machine)
        },
        'out': parse_id
    }

    parse = {
        'id': parse_id,
        'block': 'FunOSInput',
        'out': 'merge'
    }

    return [input, parse]


def common_pipeline():
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
            'dir': 'testoutput',
            'lines_per_page': 10000
        }
    }

    return [merge, dt, html]


if __name__ == '__main__':
    main()
