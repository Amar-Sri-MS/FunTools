#!/usr/bin/env python3

#
# Ingest logs using manifest file
#

import argparse
import datetime
import os
import time

from pathlib import Path

import pipeline
from utils import archive_extractor
from utils import manifest_parser


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('build_id', help='Unique build ID')
    parser.add_argument('path', help='Path to the logs directory')
    parser.add_argument('--output', help='Output block type', default='ElasticOutput')

    args = parser.parse_args()

    start = time.time()

    base_path = args.path

    # If the base_path is an archive then extract it
    if archive_extractor.is_archive(base_path):
        archive_extractor.extract(base_path)
        # Remove the extension from the base path
        base_path = os.path.splitext(base_path)[0]

    env = dict()
    env['logdir'] = base_path
    env['build_id'] = args.build_id.lower()

    cfg = build_pipeline(base_path, args.output)

    block_factory = pipeline.BlockFactory()

    p = pipeline.Pipeline(block_factory, cfg, env)
    p.process()

    end = time.time()
    print('COMPLETED: Time spent processing: {}s'.format(end - start))


def build_pipeline(path, output_block):
    """ Constructs pipeline and metadata based on the manifest file """
    cfg = dict()
    pipeline_cfg, metadata = parse_manifest(path)

    # Adding output pipeline
    pipeline_cfg.extend(output_pipeline(output_block))

    cfg['pipeline'] = pipeline_cfg
    # TODO(Sourabh): Need to store metadata
    cfg['metadata'] = metadata

    return cfg


def parse_manifest(path, parent_frn={}):
    """ Parses manifest file """
    pipeline_cfg = list()

    manifest = manifest_parser.parse(path)
    metadata = manifest.get('metadata', {})
    contents = manifest.get('contents', [])

    for content in contents:
        # Validating if the content is FRN string
        if type(content) == str and content.startswith('frn'):
            frn_info = manifest_parser.parse_FRN(content)
            frn_info = manifest_parser.merge_frn(parent_frn, frn_info)

            # Ignore if the resource_type is not present in the FRN
            if frn_info['resource_type'] == '':
                continue

            # Path to the content in the FRN
            content_path = os.path.join(path, frn_info['prefix_path'], frn_info['sub_path'])

            # Extract archive and check for manifest file
            if frn_info['resource_type'] == 'archive' or frn_info['resource_type'] == 'compressed':
                archive_path = os.path.splitext(content_path)[0]
                archive_extractor.extract(content_path)

                # Build input pipeline by parsing the manifest file in the archive
                content_pipeline_cfg, content_metadata = parse_manifest(archive_path, frn_info)

                pipeline_cfg.extend(content_pipeline_cfg)
                # TODO(Sourabh): Need to store metadata properly based on each archive.
                # Attempting to create a unique key so that the metadata from
                # different manifest files do not get overridden.
                metadata_key = '{}_{}_{}_{}_{}'.format(frn_info['namespace'],
                                                    frn_info['system_type'],
                                                    frn_info['system_id'],
                                                    frn_info['component'],
                                                    frn_info['source'])
                metadata = {
                    **metadata,
                    metadata_key: content_metadata
                }

            # Check for logs in the folder or textfile based on the source
            if frn_info['resource_type'] == 'folder' or frn_info['resource_type'] == 'textfile':
                print('Checking for logs in', content_path)
                pipeline_cfg.extend(build_input_pipeline(content_path, frn_info))

        else:
            print('WARNING: Unknown FRN', content)

    return pipeline_cfg, metadata


def build_input_pipeline(path, frn_info):
    """ Building input pipeline based on reading the manifest file """
    blocks = list()
    resource_type = frn_info['resource_type']
    source = frn_info['source']

    # If the folder does not exist
    if resource_type == 'folder' and not os.path.exists(path):
        return blocks

    # TODO(Sourabh): Have multiple source keywords to check for a source
    # Ex: apigateway could also be apigw
    if 'funos' in source or 'dpu' in source:
        # TODO(Sourabh): Fix for creating blocks based on system type(fs1600, fs800)
        if resource_type == 'folder':
            blocks.extend(
                funos_input_pipeline(frn_info, path)
            )
        else:
            blocks.extend(
                funos_input(frn_info, source, path)
            )

    elif 'storage_agent' in source:
        file_pattern = f'{path}/info*' if resource_type == 'folder' else path
        blocks.extend(
            storage_agent_input_pipeline(frn_info, source, file_pattern)
        )

    elif source == 'apigateway':
        file_pattern = f'{path}/info*' if resource_type == 'folder' else path
        blocks.extend(
            controller_input_pipeline(frn_info, source, file_pattern)
        )

    elif source == 'dataplacement':
        file_pattern = f'{path}/info*' if resource_type == 'folder' else path
        blocks.extend(
            controller_input_pipeline(frn_info, source, file_pattern,
                multiline_settings={
                    'pattern': r'(\[.*\])\s+([(-0-9|/0-9)]+)+(?:T|\s)([:0-9]+).([0-9]+)\s?((?:\-|\+)[0-9]{4})'
                })
        )

    elif source == 'kafka' or source == 'storage_consumer':
        file_pattern = f'{path}/info*' if resource_type == 'folder' else path
        blocks.extend(
            controller_input_pipeline(frn_info, source, file_pattern)
        )

    elif source == 'sns':
        file_pattern = f'{path}/sns*' if resource_type == 'folder' else path
        blocks.extend(
            controller_input_pipeline(frn_info, source, file_pattern,
                parse_block='KeyValueInput')
        )

    else:
        print(f'WARNING: Unknown source: {source}!')

    return blocks


def _get_cfg_from_frn(frn_info):
    """ Returns cfg of type dict from frn_info """
    return {
        'system_type': frn_info.get('system_type'),
        'system_id': frn_info.get('system_id'),
    }


def _generate_unique_id(source, system_id):
    """ Generating unique ID using source, system_id and current time """
    time = datetime.datetime.now().timestamp()
    unique_id = f'{source}_{system_id}_{time}'
    return unique_id


def funos_input_pipeline(frn_info, path):
    """ Input pipeline for FunOS source """
    blocks = list()
    system_type = frn_info.get('system_type', 'fs1600')
    source = frn_info['source']
    dpu_count = 2 if system_type == 'fs1600' else 1
    for dpu in range(0, dpu_count):
        # Support for v1.x directory structure
        input_id_v1 = f'funos_f1_{dpu}'

        blocks.extend(
            funos_input(
                frn_info, input_id_v1, f'{path}/F1_{dpu}_funos.txt*'
            )
        )

    # TODO(Sourabh): Add blocks based on system_type
    # Support for v2.0 directory structures
    blocks.extend(funos_input(frn_info, source, f'{path}/dpu_funos.txt*'))

    return blocks


def funos_input(frn_info, source, file_pattern):
    cfg = _get_cfg_from_frn(frn_info)
    id = _generate_unique_id(source, cfg['system_id'])

    parse_id = f'{id}_parse'

    input = {
        'id': id,
        'block': 'TextFileInput',
        'cfg': {
            **cfg,
            'file_pattern': file_pattern,
            'src': source
        },
        'out': parse_id
    }

    parse = {
        'id': parse_id,
        'block': 'FunOSInput',
        'out': 'merge'
    }

    return [input, parse]


def controller_input_pipeline(frn_info, source, file_pattern, multiline_settings={}, parse_block='GenericInput'):
    """ Input pipeline for Controller services source """
    cfg = _get_cfg_from_frn(frn_info)
    id = _generate_unique_id(source, cfg['system_id'])

    parse_id = f'{id}_parse'

    input = {
        'id': id,
        'block': 'TextFileInput',
        'cfg': {
            **cfg,
            'file_pattern': file_pattern,
            'src': source,
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


def storage_agent_input_pipeline(frn_info, source, file_pattern):
    """ Input pipeline for Storage agent source """
    cfg = _get_cfg_from_frn(frn_info)
    id = _generate_unique_id(source, cfg['system_id'])

    storage_agent_parse_id = f'{id}_parse'

    storage_agent = {
        'id': id,
        'block': 'TextFileInput',
        'cfg': {
            **cfg,
            'file_pattern': file_pattern,
            'src': source,
            'pattern': r'([(-0-9|/0-9)]+)+(?:T|\s)([:0-9]+)(?:.|,)([0-9]{3,9})'
        },
        'out': storage_agent_parse_id
    }

    storage_agent_parse = {
        'id': storage_agent_parse_id,
        'block': 'GenericInput',
        'out': 'merge'
    }

    return [storage_agent, storage_agent_parse]


def output_pipeline(output_block = 'ElasticOutput'):
    """ Output pipeline """
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
            'id': 'merge',
            'block': 'ElasticOutput',
            'cfg': {
                'index': 'log_${build_id}'
            },
            'out': 'analytics'
        }
        output_analytics = {
            'id': 'analytics',
            'block': 'AnalyticsOutput',
            'cfg': {
                'dir': 'view/analytics/log_${build_id}',
                'anchor_files': [
                    # TODO(Sourabh) Need to include anchors from each module
                    'config/anchors.json'
                ],
                'anchor_keys': None
            }
        }

        return [output, output_analytics]


if __name__ == '__main__':
    main()