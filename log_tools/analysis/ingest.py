#!/usr/bin/env python3

#
# Ingest logs using manifest file
#

import argparse
import datetime
import glob
import json
import logging
import os
import requests
import sys
import time

sys.path.append('.')

import config_loader
import pipeline
import logger

from elastic_metadata import ElasticsearchMetadata
from utils import archive_extractor
from utils import manifest_parser
from utils import timeline


# The manifest file can have different names for a source.
# This is mapping of source name with its aliases.
SOURCE_ALIASES = {
    'funos': ['dpu'],
    'storage_agent': ['storage-agent'],
    'platform_agent': ['platform-agent'],
    'telemetry-service': ['tms'],
    'node-service': ['nms'],
    'sns': ['network-service', 'network_service']
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('build_id', help='Unique build ID')
    parser.add_argument('path', help='Path to the logs directory or the log archive')
    parser.add_argument('--output', help='Output block type', default='ElasticOutput')
    parser.add_argument('--start_time', type=int, help='Epoch start time to filter logs during ingestion', default=None)
    parser.add_argument('--end_time', type=int, help='Epoch end time to filter logs during ingestion', default=None)
    parser.add_argument('--sources', nargs='*', help='Sources to filter the logs during ingestion', default=None)

    args = parser.parse_args()

    # TODO(Sourabh): Check if the build_id is valid
    # based on the Elasticsearch rules.
    # Limitation with ES that it only supports lowercase
    # index names.
    build_id = args.build_id.lower()
    start_time = args.start_time
    end_time = args.end_time
    sources = args.sources

    filters = {
        'include': {
            'time': (start_time, end_time),
            'sources': sources
        }
    }

    LOG_ID = f'log_{build_id}'
    custom_logging = logger.get_logger(filename=f'{LOG_ID}.log')
    custom_logging.propagate = False

    # Initializing the timeline tracker
    timeline.init(LOG_ID)

    status = start_pipeline(args.path, build_id, filters=filters, output_block=args.output)

    # Backing up the logs generated during ingestion
    logger.backup_ingestion_logs(LOG_ID)

    # Sends an exit status if the ingestion fails
    if not status.get('success', False):
        sys.exit(1)


def start_pipeline(base_path, build_id, filters={}, metadata={}, output_block='ElasticOutput'):
    """
    Start ingestion pipeline.
    Args:
        base_path (str) - path to the log directory/archive
        build_id (str) - Unique identfier for the ingestion
        filters (dict) - filters to filter logs to process
        output_block (str) - (defaults to ES)
    Returns:
        dict with success flag, time_taken in seconds and error
        msg if any.
    """
    LOG_ID = f'log_{build_id}'

    # Flag to determine if the ingestion is partial.
    # This would let users to ingest logs from the same job
    # from other time frames.
    is_partial_ingestion = True if _has_ingestion_filters(filters) else False

    es_metadata = ElasticsearchMetadata()
    es_metadata.update(LOG_ID, {
        'ingestion_status': 'INGESTION_IN_PROGRESS',
        'filters': filters.get('include'),
        'is_partial_ingestion': is_partial_ingestion,
        **metadata
    })

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

        cfg = build_pipeline_cfg(base_path, filters, output_block)
        metadata = {
            **metadata,
            **cfg['metadata']
        }

        # Check if tags exists and split it by comma
        if 'tags' in metadata and type(metadata['tags']) == str:
            metadata['tags'] = [tag.strip() for tag in metadata['tags'].split(',')]

        block_factory = pipeline.BlockFactory()

        p = pipeline.Pipeline(block_factory, cfg, env)
        p.process()

    except Exception as e:
        logging.exception(f'Ingestion failed for {build_id}')
        es_metadata.update(LOG_ID, {
            'ingestion_status': 'FAILED',
            'ingestion_error': str(e)
        })
        return {
            'success': False,
            'msg': str(e)
        }

    end = time.time()
    time_taken = end - start
    es_metadata.update(LOG_ID, {
        'ingestion_status': 'COMPLETED',
        'ingestion_error': None,
        'ingestion_time': time_taken,
        **metadata
    })

    timeline.generate_timeline()
    timeline.backup_timeline_files()
    backup_pipeline_cfg(LOG_ID, cfg)

    return {
        'success': True,
        'time_taken': time_taken
    }


def backup_pipeline_cfg(log_id, cfg):
    """
    Backing up the pipeline cfg built during the start of
    ingestion of the given "log_id" for debugging purpose.

    Sending the json cfg to FILE_SERVER.
    """
    try:
        config = config_loader.get_config()
        FILE_SERVER_URL = config['FILE_SERVER_URL']
        url = f'{FILE_SERVER_URL}/{log_id}/file'

        filename = f'{log_id}_cfg.json'
        path = os.path.join(logger.LOGS_DIRECTORY, filename)

        with open(path, 'w') as f:
            json.dump(cfg, f, indent=4, sort_keys=True, default=str)

        files = [
            (filename, (filename, open(path, 'rb')))
        ]

        response = requests.post(url, files=files)
        response.raise_for_status()
        logging.info(f'Pipeline cfg file for {log_id} uploaded!')

        # Removing the temp created cfg json file.
        os.remove(path)
    except Exception as e:
        logging.exception(f'Uploading pipeline cfg for {log_id} failed.')


@timeline.timeline_logger('build_pipeline')
def build_pipeline_cfg(path, filters, output_block):
    """ Constructs pipeline and metadata based on the manifest file """
    cfg = dict()
    pipeline_cfg, metadata = parse_manifest(path, filters=filters)

    if not pipeline_cfg:
        raise Exception('Could not form the ingestion pipeline.')

    # Adding filter pipeline
    pipeline_cfg.extend(filter_pipeline(filters))

    # Adding output pipeline
    pipeline_cfg.extend(output_pipeline(output_block))

    cfg['pipeline'] = pipeline_cfg
    # TODO(Sourabh): Need to store metadata
    cfg['metadata'] = metadata

    return cfg


def parse_manifest(path, parent_frn={}, filters={}):
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
            source = frn_info.get('source')

            # Ignore if the resource_type is not present in the FRN
            if frn_info['resource_type'] == '':
                continue

            # Ignore if the source is not allowed to ingest
            if source and source != '':
                source_filters = filters.get('include', {}).get('sources', [])
                if not _should_ingest_source(frn_info.get('source'), source_filters):
                    logging.info(f'Skipping source: {source}. Allowed sources: {source_filters}')
                    continue

            # Path to the content in the FRN
            content_path = os.path.join(path, frn_info['prefix_path'], frn_info['sub_path'])

            # The content path does not exist
            if not glob.glob(content_path):
                logging.warning(f'Path does not exist: {content_path}')
                continue

            # Extract archive and check for manifest file
            if frn_info['resource_type'] in ['archive', 'compressed', 'bundle']:
                resource_path = content_path
                # Extract if the file is an archive
                if archive_extractor.is_archive(content_path):
                    resource_path = os.path.splitext(content_path)[0]
                    archive_extractor.extract(content_path)

                # Build input pipeline by parsing the manifest file in the archive
                if manifest_parser.has_manifest(resource_path):
                    content_pipeline_cfg, content_metadata = parse_manifest(resource_path, frn_info, filters)
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
                else:
                    frn_info['resource_type'] = 'folder' if os.path.isdir(resource_path) else 'textfile'
                    content_path = resource_path

            # Check for logs in the folder or textfile based on the source
            if frn_info['resource_type'] == 'folder' or frn_info['resource_type'] == 'textfile':
                logging.info(f'Checking for logs in {content_path}')
                # Setting source for all the logs from CCLinux
                if 'system_log.tar' in content_path:
                    frn_info['source'] = f'cclinux_{frn_info["source"]}'
                pipeline_cfg.extend(build_input_pipeline(content_path, frn_info, filters))

        else:
            logging.warning(f'Unknown FRN: {content}')

    return pipeline_cfg, metadata


def build_input_pipeline(path, frn_info, filters={}):
    """ Building input pipeline based on reading the manifest file """
    blocks = list()
    resource_type = frn_info['resource_type']
    source = frn_info['source']

    source_filters = filters.get('include', {}).get('sources', [])

    if not _should_ingest_source(source, source_filters):
        logging.info(f'Skipping to ingest source: {source}. Allowed sources: {source_filters}')
        return blocks

    if not source:
        logging.error(f'Missing source in FRN: {frn_info}')
        return blocks

    # If the folder does not exist
    if resource_type == 'folder' and not os.path.exists(path):
        logging.warning(f'Path does not exist: {path}')
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
                funos_input(frn_info, source, path, file_info_match='FOS(?P<system_id>([0-9a-fA-F]:?){12})-')
            )

    elif source in ['storage-agent', 'storage_agent']:
        # nms contains SA<MAC_ID>-storageagent.log whereas system log archive contains storage-agent.log
        file_pattern = f'{path}/*storage?agent.log*' if resource_type == 'folder' else path
        blocks.extend(
            fun_agent_input_pipeline(
                frn_info,
                source,
                file_pattern,
                file_info_match='SA(?P<system_id>([0-9a-fA-F]:?){12})-'
            )
        )

    elif source in ['platform-agent', 'platform_agent']:
        # nms contains PA<MAC_ID>-platformagent.log whereas system log archive contains platform-agent.log
        file_pattern = f'{path}/*platform?agent.log*' if resource_type == 'folder' else path
        blocks.extend(
            fun_agent_input_pipeline(frn_info, source, file_pattern)
        )

    elif source in ['dataplacement', 'discovery', 'metrics_manager', 'scmscv', 'expansion_rebalance']:
        file_pattern = f'{path}/info*' if resource_type == 'folder' else path
        blocks.extend(
            controller_input_pipeline(frn_info, source, file_pattern,
                # [logger.go:158] 2022-01-10T04:04:31.707689851Z info log level:debug and backupcount:8 in /var/log/dataplacement/info.log
                multiline_settings={
                    'pattern': r'(\[.*\])\s+(\d{4}(?:-|/)\d{2}(?:-|/)\d{2})+(?:T|\s)([:0-9]+).([0-9]+)(?:Z|)'
                })
        )

    elif source in ['apigateway', 'storage_consumer', 'lrm_consumer', 'setup_db', 'metrics_server']:
        file_pattern = f'{path}/info*' if resource_type == 'folder' else path
        blocks.extend(
            controller_input_pipeline(
                frn_info,
                source,
                file_pattern,
                # 2022/01/10 04:02:17.957	INFO	Initialized logger with LoggerFile=/var/log/info.log, Verbosity=info
                multiline_settings={
                    'pattern': r'^(\d{4}(?:-|/)\d{2}(?:-|/)\d{2})+(?:T|\s)([:0-9]+).([0-9]+)'
                })
        )

    elif source in ['kafka']:
        file_pattern = f'{path}/server.log*' if resource_type == 'folder' else path
        blocks.extend(
            controller_input_pipeline(
                frn_info,
                source,
                file_pattern,
                # [2022-01-10 04:01:47,491] INFO [ThrottledChannelReaper-Fetch]: Starting (kafka.server.ClientQuotaManager$ThrottledChannelReaper)
                multiline_settings={
                    'pattern': r'^\[(\d{4}(?:-|/)\d{2}(?:-|/)\d{2})+(?:T|\s)([:0-9]+).([0-9]+)\]'
                }
            )
        )

    elif source in ['sns', 'network-service']:
        file_pattern = f'{path}/sns*' if resource_type == 'folder' else path
        blocks.extend(
            controller_input_pipeline(frn_info, source, file_pattern,
                parse_block='KeyValueInput')
        )

    elif 'kapacitor' in source:
        file_pattern = f'{path}/kapacitord.log*' if resource_type == 'folder' else path
        blocks.extend(
            controller_input_pipeline(frn_info, source, file_pattern,
                parse_block='KeyValueInput',
                parse_settings={
                    'key_name_mappings': {
                        'time': 'ts',
                        'level': 'lvl'
                    }
                })
        )

    elif source in ['pfm']:
        file_pattern = f'{path}/*.log*' if resource_type == 'folder' else path
        blocks.extend(
            controller_input_pipeline(frn_info, source, file_pattern,
                parse_block='KeyValueInput')
        )

    elif source in ['telemetry-service', 'tms']:
        if resource_type == 'folder':
            log_files = glob.glob(f'{path}/*.log*')
            frn_info['resource_type'] = 'textfile'
            for file in log_files:
                filename = os.path.basename(file)
                frn_info['source'] = filename
                # Few log archives contain the kapacitor logs in tms folder.
                if 'kapacitord.log' in filename:
                    frn_info['source'] = 'kapacitor'
                    blocks.extend(build_input_pipeline(file, frn_info, filters))
                else:
                    blocks.extend(
                        controller_input_pipeline(frn_info, filename, file,
                            parse_block='JSONInput')
                    )

    elif source in ['node-service', 'nms']:
        if resource_type == 'folder':
            log_files = glob.glob(f'{path}/*.log*')
            frn_info['resource_type'] = 'textfile'
            for file in log_files:
                filename = os.path.basename(file)
                frn_info['source'] = filename
                if 'audit.log' in filename:
                    blocks.extend(controller_input_pipeline(
                        frn_info,
                        filename,
                        file,
                        parse_block='JSONInput',
                        parse_settings={
                            'key_name_mappings': {
                                'time': 'ts'
                            }
                        }
                    ))
                else:
                    blocks.extend(controller_input_pipeline(frn_info, filename, file))

            # nms folder contains funos and agent logs
            frn_info['system_type'] = 'DPU'
            frn_info['system_id'] = None
            if _should_ingest_source('platform_agent', source_filters):
                # platform agent logs
                file_pattern = f'{path}/archives/other/*platformagent.log*'
                blocks.extend(
                    fun_agent_input_pipeline(frn_info,
                        'platform_agent',
                        file_pattern,
                        file_info_match='PA(?P<system_id>([0-9a-fA-F]:?){12})-')
                )

            if _should_ingest_source('storage_agent', source_filters):
                # storage agent logs
                file_pattern = f'{path}/archives/other/*storageagent.log*'
                blocks.extend(
                    fun_agent_input_pipeline(frn_info,
                        'storage_agent',
                        file_pattern,
                        file_info_match='SA(?P<system_id>([0-9a-fA-F]:?){12})-')
                )

            if _should_ingest_source('funos', source_filters):
                # funos logs
                file_pattern = f'{path}/archives/other/*funos.log*'
                blocks.extend(
                    funos_input(frn_info,
                        'funos',
                        file_pattern,
                        file_info_match='FOS(?P<system_id>([0-9a-fA-F]:?){12})-')
                )

    # This source for CCLinux logs from Fun-on-demand jobs
    elif source.startswith('cclinux_') and resource_type == 'textfile':
        # TODO(Sourabh) Logs under /var/log does have year in the
        # timestamp which makes it harder to parse them.
        if not 'var/log' in path:
            updated_source = source.split('cclinux_')[1]

            # TODO(Sourabh): Reach out to relevant folks to standardize
            # log formats. funapisvr logs are in JSON.
            if 'funapisvr' in source or 'funapisvr' in path:
                blocks.extend(
                    controller_input_pipeline(frn_info,
                        updated_source,
                        path,
                        parse_block='KeyValueInput'
                    )
                )
            else:
                blocks.extend(
                    fun_agent_input_pipeline(frn_info,
                        updated_source,
                        path
                    )
                )

    elif source == 'cclinux' and resource_type == 'folder':
        log_files = glob.glob(f'{path}/**/*.log*', recursive=True)
        frn_info['resource_type'] = 'textfile'
        for file in log_files:
            filename = os.path.basename(file)
            frn_info['source'] = f'cclinux_{filename}'
            blocks.extend(build_input_pipeline(file, frn_info, filters))

    else:
        logging.warning(f'Unknown source: {source} or resource type: {resource_type}!')

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


def _has_ingestion_filters(filters):
    """ Check if any filters are applied for ingestion """
    include = filters.get('include', None)
    if not include:
        return False

    time_filters = include.get('time')
    if not time_filters:
        return False

    start_time, end_time = time_filters
    if not start_time and not end_time:
        return False

    source_filters = include.get('sources')
    if not source_filters or len(source_filters) == 0:
        return False


def _should_ingest_source(source, source_filters=[]):
    """
    Returns True if the source needs to be ingested.
    Allows all sources if no source filters provided.
    """
    # These are parent sources which contain individual sources.
    # node-service contains FunOS, Storage and Platform agent logs.
    allowed_sources = ['cclinux', 'node-service']

    allowed_source_aliases = list()
    if source_filters:
        for source_filter in source_filters:
            allowed_source_aliases.extend(SOURCE_ALIASES.get(source_filter, []))

    # No source filters provided or source in allowed sources.
    if not source_filters or len(source_filters) == 0 or source in allowed_sources:
        return True

    return (source in source_filters or source in allowed_source_aliases)


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
    blocks.extend(funos_input(frn_info, source, f'{path}/FOS*-funos.log*', file_info_match='FOS(?P<system_id>([0-9a-fA-F]:?){12})-'))

    return blocks


def funos_input(frn_info, source, file_pattern, file_info_match=None):
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
            # Regex pattern to pick information from the filename
            'file_info_match': file_info_match
        },
        'out': parse_id
    }

    parse = {
        'id': parse_id,
        'block': 'FunOSInput',
        'out': 'merge'
    }

    return [input, parse]


def controller_input_pipeline(frn_info, source, file_pattern, multiline_settings={}, parse_block='GenericInput', parse_settings={}):
    """
    Input pipeline for Controller services source.
    Args:
        frn_info: (dict) FRN parsed from the manifest
        source: (str)
        file_pattern: (str) Glob pattern for the log filename
        multiline_settings: (dict)
            pattern: (str) Regex pattern for detecting start of a log line
        parse_block: (str) Name of the block type used for parsing the log file

    """
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
        'cfg': parse_settings,
        'out': 'merge'
    }

    return [input, parse]


def fun_agent_input_pipeline(frn_info, source, file_pattern, parse_block='GenericInput', parse_settings={}, file_info_match=None):
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
            'pattern': r'(\d{4}(?:-|/)\d{2}(?:-|/)\d{2})+(?:T|\s)([:0-9]+)[\.|\,]{0,1}([0-9]*)',
            # Regex pattern to pick information from the filename
            'file_info_match': file_info_match
        },
        'out': fun_agent_parse_id
    }

    fun_agent_parse = {
        'id': fun_agent_parse_id,
        'block': parse_block,
        'cfg': parse_settings,
        'out': 'merge'
    }

    return [fun_agent, fun_agent_parse]


def filter_pipeline(filters=None):
    filter_block = {
        'id': 'merge',
        'block': 'Filter',
        'cfg': {
            'filters': filters
        },
        'out': 'filter'
    }

    return [filter_block]


def output_pipeline(output_block = 'ElasticOutput'):
    """ Output pipeline """
    if output_block == 'HTMLOutput':
        merge = {
            'id': 'filter',
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
            'id': 'filter',
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