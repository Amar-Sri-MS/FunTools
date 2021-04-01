#!/usr/bin/env python3

#
# Ingest logs using manifest file
#

import argparse
import datetime
import glob
import os
import sys
import time

sys.path.append('.')

from pathlib import Path

import pipeline

from elastic_metadata import ElasticsearchMetadata
from utils import archive_extractor
from utils import manifest_parser


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('build_id', help='Unique build ID')
    parser.add_argument('path', help='Path to the logs directory or the log archive')
    parser.add_argument('--output', help='Output block type', default='ElasticOutput')

    args = parser.parse_args()

    # TODO(Sourabh): Check if the build_id is valid
    # based on the Elasticsearch rules.
    # Limitation with ES that it only supports lowercase
    # index names.
    build_id = args.build_id.lower()

    start_pipeline(args.path, build_id, args.output)


def start_pipeline(base_path, build_id, metadata={}, output_block='ElasticOutput'):
    """
    Start ingestion pipeline.
    base_path - path to the log directory/archive
    build_id - Unique identfier for the ingestion
    output_block (defaults to ES)
    """
    start = time.time()
    try:
        # If the base_path is an archive then extract it
        if archive_extractor.is_archive(base_path):
            archive_extractor.extract(base_path)
            # Remove the extension from the base path
            base_path = os.path.splitext(base_path)[0]

        if not os.path.exists(os.path.join(base_path, 'FUNLOG_MANIFEST')):
            raise Exception('Could not find manifest file')

        env = dict()
        env['logdir'] = base_path
        env['build_id'] = build_id

        cfg = build_pipeline_cfg(base_path, output_block)

        block_factory = pipeline.BlockFactory()

        p = pipeline.Pipeline(block_factory, cfg, env)
        p.process()

    except Exception as e:
        print(f'ERROR: Ingestion for {build_id} - {str(e)}')
        return {
            'success': False,
            'msg': str(e)
        }

    es_metadata = ElasticsearchMetadata()
    print(f'INFO: Storing metadata for log_{build_id}')
    metadata_store_resp = es_metadata.store(f'log_{build_id}', metadata)
    print(f'Response: {metadata_store_resp}')

    end = time.time()
    time_taken = end - start
    print(f'COMPLETED: Time spent processing: {time_taken}s')

    return {
        'success': True,
        'time_taken': time_taken
    }


def build_pipeline_cfg(path, output_block):
    """ Constructs pipeline and metadata based on the manifest file """
    cfg = dict()
    pipeline_cfg, metadata = parse_manifest(path)

    if not pipeline_cfg:
        raise Exception('Could not parse the manifest file')

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

            # The content path does not exist
            if not glob.glob(content_path):
                print('WARNING: Path does not exist:', content_path)
                continue

            # Extract archive and check for manifest file
            if frn_info['resource_type'] in ['archive', 'compressed', 'bundle']:
                resource_path = content_path
                # Extract if the file is an archive
                if archive_extractor.is_archive(content_path):
                    resource_path = os.path.splitext(content_path)[0]
                    archive_extractor.extract(content_path)

                # Build input pipeline by parsing the manifest file in the archive
                content_pipeline_cfg, content_metadata = parse_manifest(resource_path, frn_info)

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
                print('INFO: Checking for logs in', content_path)
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

    elif source in ['storage-agent', 'storage_agent']:
        # nms contains SA<MAC_ID>-storageagent.log whereas system log archive contains storage-agent.log
        file_pattern = f'{path}/*storage?agent.log*' if resource_type == 'folder' else path
        blocks.extend(
            fun_agent_input_pipeline(frn_info, source, file_pattern)
        )

    elif source in ['platform-agent', 'platform_agent']:
        # nms contains PA<MAC_ID>-platformagent.log whereas system log archive contains platform-agent.log
        file_pattern = f'{path}/*platform?agent.log*' if resource_type == 'folder' else path
        blocks.extend(
            fun_agent_input_pipeline(frn_info, source, file_pattern)
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

    elif source in ['discovery', 'metrics_manager']:
        file_pattern = f'{path}/info*' if resource_type == 'folder' else path
        blocks.extend(
            controller_input_pipeline(frn_info, source, file_pattern)
        )

    elif source == 'scmscv':
        file_pattern = f'{path}/info*' if resource_type == 'folder' else path
        blocks.extend(
            controller_input_pipeline(frn_info, source, file_pattern,
                multiline_settings={
                    'pattern': r'(\[.*\])\s+([(-0-9|/0-9)]+)+(?:T|\s)([:0-9]+).([0-9]+)\s?((?:\-|\+)[0-9]{4})'
                })
        )

    elif source in ['kafka', 'storage_consumer', 'lrm_consumer', 'setup_db', 'metrics_server']:
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

    elif source == 'node-service':
        # nms folder contains funos and agent logs
        if resource_type == 'folder':
            frn_info['system_type'] = 'DPU'
            frn_info['system_id'] = None
            # platform agent logs
            file_pattern = f'{path}/archives/other/*platformagent.log*'
            blocks.extend(
                fun_agent_input_pipeline(frn_info, 'platform_agent', file_pattern)
            )

            # storage agent logs
            file_pattern = f'{path}/archives/other/*storageagent.log*'
            blocks.extend(
                fun_agent_input_pipeline(frn_info, 'storage_agent', file_pattern)
            )

            # funos logs
            file_pattern = f'{path}/archives/other/*funos.log*'
            blocks.extend(
                funos_input(frn_info, 'funos', file_pattern)
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

    # For the funos logs within nms directory
    blocks.extend(funos_input(frn_info, source, f'{path}/FOS*-funos.log*'))

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


def fun_agent_input_pipeline(frn_info, source, file_pattern):
    """ Input pipeline for Fun agent source """
    cfg = _get_cfg_from_frn(frn_info)
    id = _generate_unique_id(source, cfg['system_id'])

    fun_agent_parse_id = f'{id}_parse'

    fun_agent = {
        'id': id,
        'block': 'TextFileInput',
        'cfg': {
            **cfg,
            'file_pattern': file_pattern,
            'src': source,
            'pattern': r'([(-0-9|/0-9)]+)+(?:T|\s)([:0-9]+)(?:.|,)([0-9]{3,9})'
        },
        'out': fun_agent_parse_id
    }

    fun_agent_parse = {
        'id': fun_agent_parse_id,
        'block': 'GenericInput',
        'out': 'merge'
    }

    return [fun_agent, fun_agent_parse]


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
        file_path = os.path.abspath(os.path.dirname(__file__))
        anchors_path = os.path.join(file_path, 'config/anchors.json')
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
                'anchor_files': [
                    # TODO(Sourabh) Need to include anchors from each module
                    anchors_path
                ],
                'anchor_keys': None
            }
        }

        return [output, output_analytics]


if __name__ == '__main__':
    main()