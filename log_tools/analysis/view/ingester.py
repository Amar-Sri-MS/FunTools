#!/usr/bin/env python3

#
# Ingester View to handle automated ingestion of
# logs from QA dashboard given a JOB_ID
#
# This script can also be used to start ingesting QA logs
#
# Usage apart from a Flask template:
#
# python ingester.py <JOB_ID> -test_index <TEST_INDEX> -tags <TAGS>
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import argparse
import logging
import os
import requests
import shutil
import subprocess
import sys
import time
import yaml

sys.path.insert(0, '.')

from elastic_metadata import ElasticsearchMetadata
from flask import Blueprint, jsonify, request, render_template
from flask import current_app
from utils import archive_extractor
import ingest as ingest_handler
import logger


ingester_page = Blueprint('ingester_page', __name__)

DOWNLOAD_DIRECTORY = 'downloads'
QA_REGRESSION_BASE_ENDPOINT = 'http://integration.fungible.local/api/v1/regression'
QA_JOB_INFO_ENDPOINT = f'{QA_REGRESSION_BASE_ENDPOINT}/suite_executions'
QA_LOGS_ENDPOINT = f'{QA_REGRESSION_BASE_ENDPOINT}/test_case_time_series'
QA_SUITE_ENDPOINT = f'{QA_REGRESSION_BASE_ENDPOINT}/suites'
QA_STATIC_ENDPOINT = 'http://integration.fungible.local/static/logs'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('job_id', help='QA Job ID')
    parser.add_argument('-test_index', type=int, help='Test index of the QA job', default=0)
    parser.add_argument('-tags', nargs='*', help='Tags for the ingestion', default=[])
    parser.add_argument('-start_time', type=int, help='Epoch start time to filter logs', default=None)
    parser.add_argument('-end_time', type=int, help='Epoch end time to filter logs', default=None)

    try:
        args = parser.parse_args()
        job_id = args.job_id
        test_index = args.test_index
        tags = args.tags
        start_time = args.start_time
        end_time = args.end_time

        LOG_ID = f'log_qa-{job_id}-{test_index}'
        es_metadata = ElasticsearchMetadata()

        custom_logging = logger.get_logger(filename=f'{LOG_ID}.log')
        custom_logging.propagate = False

        job_info = fetch_qa_job_info(job_id)
        suite_info = fetch_qa_suite_info(job_info['data']['suite_id'])
        log_files = fetch_qa_logs(job_id, suite_info, test_index)

        metadata = {
            'tags': tags
        }

        filters = {
            'include': {
                'time': (start_time, end_time)
            }
        }

        # Start ingestion
        ingestion_status = ingest_logs(job_id, test_index, job_info, log_files, metadata, filters)

        if ingestion_status and not ingestion_status['success']:
            _update_metadata(es_metadata, LOG_ID, 'FAILED', {
                'ingestion_error': ingestion_status.get('msg')
            })

    except Exception as e:
        logging.exception(f'Error when starting ingestion for job: {job_id}')
        _update_metadata(es_metadata, LOG_ID, 'FAILED', {
            'ingestion_error': str(e),
            **metadata
        })
    finally:
        # Clean up the downloaded files
        clean_up(job_id)

        # Backing up the logs generated during ingestion
        logger.backup_ingestion_logs(LOG_ID)


@ingester_page.route('/ingest', methods=['GET'])
def render_ingest_page():
    """ UI for ingesting logs """
    return render_template('ingester.html', feedback={})


@ingester_page.route('/ingest', methods=['POST'])
def ingest():
    """
    Handling ingestion of logs from QA jobs.
    Required QA "job_id"
    """
    try:
        job_id = request.form.get('job_id')
        test_index = request.form.get('test_index', 0)
        tags = request.form.get('tags')
        tags_list = [tag.strip() for tag in tags.split(',')]

        start_time = request.form.get('start_time', None)
        end_time = request.form.get('end_time', None)

        if not job_id:
            return render_template('ingester.html', feedback={
                'success': False,
                'job_id': job_id,
                'msg': 'Missing JOB ID'
            })

        job_id = job_id.strip()

        LOG_ID = f'log_qa-{job_id}-{test_index}'
        es_metadata = ElasticsearchMetadata()
        metadata = es_metadata.get(LOG_ID)

        # If metadata exists then either ingestion for this job
        # is already done or in progress
        if not metadata or metadata['ingestion_status'] == 'FAILED':
            cmd = ['./ingester.py', job_id, '-test_index', str(test_index)]
            if len(tags_list) > 0:
                cmd.append('-tags')
                cmd.append(' '.join(tags_list))

            if start_time:
                cmd.append('-start_time')
                cmd.append(start_time)

            if end_time:
                cmd.append('-end_time')
                cmd.append(end_time)

            ingestion = subprocess.Popen(cmd)

        return render_template('ingester.html', feedback={
            'started': True,
            'success': metadata.get('ingestion_status') == 'COMPLETED',
            'is_partial_ingestion': metadata.get('is_partial_ingestion', False),
            'job_id': job_id,
            'test_index': test_index,
            'tags': tags,
            'start_time': start_time,
            'end_time': end_time,
            'metadata': metadata
        })
    except Exception as e:
        current_app.logger.exception(f'Error when starting ingestion for job: {job_id}')
        return render_template('ingester.html', feedback={
            'started': False,
            'success': False,
            'job_id': job_id,
            'test_index': test_index,
            'tags': tags,
            'start_time': start_time,
            'end_time': end_time,
            'msg': str(e)
        }), 500


@ingester_page.route('/ingest/<log_id>/status', methods=['GET'])
def check_status(log_id):
    """
    Returns the metadata containing the ingestion
    status for the given "log_id"
    """
    es_metadata = ElasticsearchMetadata()
    metadata = es_metadata.get(log_id)

    # TODO(Sourabh): Need an additional check if the status is
    # not COMPLETED to see if the process is running

    return metadata


def fetch_qa_job_info(job_id):
    """
    Fetching QA job info using QA endpoint
    Returns response (dict)
    Raises Exception if Job not found
    """
    url = f'{QA_JOB_INFO_ENDPOINT}/{job_id}'
    response = requests.get(url)
    job_info = response.json()
    if not (job_info and job_info['data']):
        raise Exception('Job info not found')
    return job_info


def fetch_qa_suite_info(suite_id):
    """
    Fetching QA job info using QA endpoint
    Returns response (dict)
    Raises Exception if Job not found
    """
    url = f'{QA_SUITE_ENDPOINT}/{suite_id}'
    response = requests.get(url)
    suite_info = response.json()
    if not (suite_info and suite_info['data']):
        raise Exception(f'QA suite ({suite_id}) not found')
    return suite_info['data']


def fetch_qa_logs(job_id, suite_info, test_index=None):
    """
    Fetches a list of QA log filenames
    QA API returns a list of log info containing data
    in the format:
    {
        description: "CS logs tgz",
        filename: "/regression/Integration/fun_test/web/static/logs/s_170427/_0script_helper.py_170427_1783447_fc_log.tgz",
        asset_type: "Fungible-controller",
        asset_id: "FungibleController: mpoc-server06",
        category: "Diagnostics",
        sub_category: "general"
    }
    """
    url = f'{QA_LOGS_ENDPOINT}/{job_id}?type=200'
    response = requests.get(url)
    job_logs = response.json()
    if not (job_logs and job_logs['data']):
        raise Exception('Logs not found')
    return _filter_qa_log_files(job_logs, suite_info, test_index)


def _filter_qa_log_files(job_logs, suite_info, test_index=None):
    """ Filters out only required QA log files """
    # FC log archives for single node and HA
    log_filename_starts = ''
    if test_index is not None and len(suite_info.get('entries', [])) > test_index:
        # Example: _13failures_mgmt_flap_multi.py_180878_1871693_fcs_log.tgz
        test_script_name = suite_info['entries'][test_index]['script_path'].split('/')[-1]
        # File names either start with _{test_index}{test_script_name} or
        # _{test_index}script_helper.py
        log_filename_starts = (f'_{test_index}{test_script_name}', f'_{test_index}script_helper.py')

    log_filenames_to_ingest = ('fc_log.tgz', 'fcs_log.tgz')
    log_files = list()
    for job_log in job_logs['data']:
        log = job_log['data']

        # We are not interested in other logs
        if log['category'] != 'Diagnostics':
            continue

        filename = log['filename'].split('/')[-1]

        # Only interested for a specific test in the test suite
        if test_index is not None and not filename.startswith(log_filename_starts):
            continue

        if filename.endswith(log_filenames_to_ingest):
            log_files.append(log['filename'])

    return log_files


def _get_valid_files(path):
    """ Listing valid files in a given "path" """
    return [file for file in os.listdir(path)
                if os.path.isfile(os.path.join(path, file)) and
                file not in ('.DS_Store')
            ]


def ingest_logs(job_id, test_index, job_info, log_files, metadata, filters):
    """
    Ingesting logs using "job_id" and "log_files"

    Required job_info to get the release train info and
    ingest logs accordingly.

    This function downloads the log file and ingest
    it to the Log Analyzer.
    """
    es_metadata = ElasticsearchMetadata()
    LOG_ID = f'log_qa-{job_id}-{test_index}'

    path = f'{DOWNLOAD_DIRECTORY}/{job_id}'
    file_path = os.path.abspath(os.path.dirname(__file__))
    release_train = job_info['data']['primary_release_train']
    QA_LOGS_DIRECTORY = '/regression/Integration/fun_test/web/static/logs'
    found_logs = False

    tags = metadata.get('tags') if metadata.get('tags') else []
    # Adding the release train to the tags
    metadata = {
        **metadata,
        'tags': tags + [release_train]
    }

    manifest_contents = list()

    _update_metadata(es_metadata, LOG_ID, 'DOWNLOAD_STARTED')
    start = time.time()
    try:
        for log_file in log_files:
            log_dir = log_file.split(QA_LOGS_DIRECTORY)[1]
            url = f'{QA_STATIC_ENDPOINT}{log_dir}'
            if check_and_download_logs(url, path):
                found_logs = True
                # single node FC
                if log_file.endswith('_fc_log.tgz'):
                    filename = log_file.split('/')[-1].replace(' ', '_')
                    archive_path = f'{path}/{filename}'
                    archive_extractor.extract(archive_path)

                    archive_name = os.path.splitext(filename)[0]
                    # Path to the extracted log files
                    LOG_DIR = f'{path}/{archive_name}'

                    if release_train in ('master', '2.0', '2.0.1', '2.0.2', '2.1', '2.2'):
                        # Copying FUNLOG_MANIFEST file
                        template_path = os.path.join(file_path, '../config/templates/fc/FUNLOG_MANIFEST')
                        shutil.copy(template_path, LOG_DIR)
                    else:
                        raise Exception('Unsupported release train')

                    manifest_contents.append(f'frn::::::bundle::"{archive_name}"')

                # HA FC
                elif log_file.endswith('_fcs_log.tgz'):
                    filename = log_file.split('/')[-1].replace(' ', '_')
                    archive_path = f'{path}/{filename}'
                    # Extracting the archive
                    archive_extractor.extract(archive_path)

                    archive_name = os.path.splitext(filename)[0]
                    # Path to the extracted log files
                    LOG_DIR = f'{path}/{archive_name}/tmp/debug_logs'

                    # master release
                    if release_train in ('master', '2.1', '2.2'):
                        files = _get_valid_files(LOG_DIR)
                        # TODO(Sourabh): This is an assumption that there will not be
                        # other files in this directory

                        # The path contains only a tar file, with a FUNLOG_MANIFEST
                        # file, which needs to be ingested
                        ingest_path = f'{LOG_DIR}/{files[0]}'

                        manifest_contents.append(f'frn::::::archive:"{archive_name}/tmp/debug_logs":"{files[0]}"')
                    elif release_train in ('2.0', '2.0.1', '2.0.2'):
                        folders = next(os.walk(os.path.join(LOG_DIR,'.')))[1]

                        # TODO(Sourabh): This is an assumption that there will not be
                        # other folders in this directory
                        log_folder_name = folders[0]
                        # Path to the extracted log files
                        LOG_DIR = os.path.join(LOG_DIR, log_folder_name)

                        # Creating FUNLOG_MANIFEST file by replacing timestamp folder name
                        template_path = os.path.join(file_path, '../config/templates/ha/FUNLOG_MANIFEST')
                        with open(template_path, 'rt') as fin:
                            with open(f'{LOG_DIR}/FUNLOG_MANIFEST', 'wt') as fout:
                                for line in fin:
                                    fout.write(line.replace('<TIMESTAMP>', log_folder_name))

                        manifest_contents.append(f'frn::::::bundle:"{archive_name}/tmp/debug_logs":"{log_folder_name}"')
                    else:
                        raise Exception('Unsupported release train')

                # system logs
                elif log_file.endswith('system_log.tar'):
                    filename = log_file.split('/')[-1].replace(' ', '_')
                    archive_path = f'{path}/{filename}'
                    archive_extractor.extract(archive_path)

                    archive_name = os.path.splitext(filename)[0]
                    # Path to the extracted log files
                    LOG_DIR = f'{path}/{archive_name}'

                    if release_train in ('master', '2.0', '2.0.1', '2.1'):
                        # Copying FUNLOG_MANIFEST file
                        template_path = os.path.join(file_path, '../config/templates/system/FUNLOG_MANIFEST')
                        shutil.copy(template_path, LOG_DIR)

                        manifest_contents.append(f'frn::::::bundle::"{archive_name}"')
                    else:
                        raise Exception('Unsupported release train')

        if not found_logs:
            raise Exception('Logs not found')

        end = time.time()
        time_taken = end - start

        _update_metadata(es_metadata,
                        LOG_ID,
                        'DOWNLOAD_COMPLETED',
                        {'download_time': time_taken})

        _create_manifest(path, contents=manifest_contents)
        # Start the ingestion
        return ingest_handler.start_pipeline(path,
                                         f'qa-{job_id}-{test_index}',
                                         metadata=metadata,
                                         filters=filters)
    except Exception as e:
        logging.exception('Error while ingesting the logs')
        _update_metadata(es_metadata, LOG_ID, 'FAILED', {
            'ingestion_error': str(e)
        })


def _create_manifest(path, metadata={}, contents=[]):
    """ Creates manifest file at the given path """
    manifest = {
        'metadata': metadata,
        'contents': contents
    }

    with open(f'{path}/FUNLOG_MANIFEST', 'w') as file:
        yaml.dump(manifest, file)


def check_and_download_logs(url, path):
    """ Downloading log archives from QA dashboard """
    filename = url.split('/')[-1].replace(' ', '_')
    file_path = os.path.join(path, filename)

    response = requests.get(url, allow_redirects=True, stream=True)
    if response.ok:
        os.makedirs(path, exist_ok=True)
        logging.info(f'Saving log archive to {os.path.abspath(file_path)}')
        with open(file_path, 'wb') as f:
            # Chunk size of 1GB
            for chunk in response.iter_content(chunk_size=1024 * 100000):
                f.write(chunk)
    else:  # HTTP status code 4XX/5XX
        raise Exception(f'Download failed: status code {response.status_code}')
    return True


def _update_metadata(metadata_handler, log_id, status, additional_data={}):
    """ Updating the ingestion status in the metadata """
    metadata = {
        **additional_data,
        'ingestion_status': status
    }
    return metadata_handler.update(log_id, metadata)


def clean_up(job_id):
    """ Deleting the downloaded directory for the job_id """
    path = os.path.join(DOWNLOAD_DIRECTORY, job_id)
    if os.path.exists(path):
        logging.info(f'Cleaning up downloaded files from: {path}')
        # Deletes the entire directory with its children
        shutil.rmtree(path)


if __name__ == '__main__':
    main()