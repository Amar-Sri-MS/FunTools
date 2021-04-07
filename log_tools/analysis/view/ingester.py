#!/usr/bin/env python3

#
# Ingester View to handle automated ingestion of
# logs from QA dashboard given a JOB_ID
# 
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import os
import requests
import shutil
import sys
import yaml

sys.path.insert(0, '.')

from flask import Blueprint, jsonify, request, render_template
from utils import archive_extractor
import ingest as ingest_handler

ingester_page = Blueprint('ingester_page', __name__)

DOWNLOAD_DIRECTORY = 'downloads'
QA_REGRESSION_BASE_ENDPOINT = 'http://integration.fungible.local/api/v1/regression'
QA_JOB_INFO_ENDPOINT = f'{QA_REGRESSION_BASE_ENDPOINT}/suite_executions'
QA_LOGS_ENDPOINT = f'{QA_REGRESSION_BASE_ENDPOINT}/test_case_time_series'
QA_SUITE_ENDPOINT = f'{QA_REGRESSION_BASE_ENDPOINT}/suites'
QA_STATIC_ENDPOINT = 'http://integration.fungible.local/static/logs'


@ingester_page.route('/ingest', methods=['GET'])
def render_ingest_page():
    """ UI for ingesting logs """
    return render_template('ingester.html')


@ingester_page.route('/ingest', methods=['POST'])
def ingest():
    """
    Handling ingestion of logs from QA jobs.
    Required QA "job_id"
    """
    try:
        job_id = request.form.get('job_id')
        test_index = int(request.form.get('test_index', 0))
        tags = request.form.get('tags')
        tags_list = [tag.strip() for tag in tags.split(',')]

        if not job_id:
            return render_template('ingester.html', feedback={
                'success': False,
                'job_id': job_id,
                'msg': 'Missing JOB ID'
            })

        job_id = job_id.strip()

        job_info = fetch_qa_job_info(job_id)
        suite_info = fetch_qa_suite_info(job_info['data']['suite_id'])
        log_files = fetch_qa_logs(job_id, suite_info, test_index)

        metadata = {
            'tags': tags_list
        }

        # Start ingestion
        ingestion_status = ingest_logs(job_id, test_index, job_info, log_files, metadata)

        if not ingestion_status['success']:
            return render_template('ingester.html', feedback={
                'success': False,
                'job_id': job_id,
                'test_index': test_index,
                'tags': tags,
                'msg': ingestion_status['msg'] if 'msg' in ingestion_status else 'Ingestion failed.'
            })

        return render_template('ingester.html', feedback={
            'success': True,
            'job_id': job_id,
            'test_index': test_index,
            'tags': tags,
            'dashboard_link': f'{request.host_url}log/log_qa-{job_id}-{test_index}/dashboard',
            'time_taken': ingestion_status['time_taken']
        })
    except Exception as e:
        print('ERROR:', e)
        return render_template('ingester.html', feedback={
            'success': False,
            'job_id': job_id,
            'test_index': test_index,
            'tags': tags,
            'msg': str(e)
        })
    finally:
        # Clean up the downloaded files
        clean_up(job_id)


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
    if test_index and len(suite_info.get('entries', [])) > test_index:
        # Example: _13failures_mgmt_flap_multi.py_180878_1871693_fcs_log.tgz
        test_script_name = suite_info['entries'][test_index]['script_path'].split('/')[-1]
        log_filename_starts = f'_{test_index}{test_script_name}'

    log_filenames_to_ingest = ('fc_log.tgz', 'fcs_log.tgz')
    log_files = list()
    for job_log in job_logs['data']:
        log = job_log['data']

        # We are not interested in other logs
        if log['category'] != 'Diagnostics':
            continue

        filename = log['filename'].split('/')[-1]

        # Only interested for a specific test in the test suite
        if test_index and not filename.startswith(log_filename_starts):
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


def ingest_logs(job_id, test_index, job_info, log_files, metadata):
    """
    Ingesting logs using "job_id" and "log_files"

    Required job_info to get the release train info and
    ingest logs accordingly.

    This function downloads the log file and ingest
    it to the Log Analyzer.
    """
    path = f'{DOWNLOAD_DIRECTORY}/{job_id}'
    file_path = os.path.abspath(os.path.dirname(__file__))
    release_train = job_info['data']['primary_release_train']
    QA_LOGS_DIRECTORY = '/regression/Integration/fun_test/web/static/logs'
    found_logs = False

    manifest_contents = list()

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

                if release_train in ('master', '2.0', '2.0.1', '2.1'):
                    # Copying FUNLOG_MANIFEST file
                    template_path = os.path.join(file_path, '../config/templates/fc/FUNLOG_MANIFEST')
                    shutil.copy(template_path, LOG_DIR)
                else:
                    raise Exception('Unsupported release train')

                manifest_contents.append(f'frn::::::bundle::{archive_name}')

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
                if release_train in ('master', '2.1'):
                    files = _get_valid_files(LOG_DIR)
                    # TODO(Sourabh): This is an assumption that there will not be
                    # other files in this directory

                    # The path contains only a tar file, with a FUNLOG_MANIFEST
                    # file, which needs to be ingested
                    ingest_path = f'{LOG_DIR}/{files[0]}'

                    manifest_contents.append(f'frn::::::archive:{archive_name}/tmp/debug_logs:{files[0]}')
                elif release_train in ('2.0', '2.0.1'):
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

                    manifest_contents.append(f'frn::::::bundle:{archive_name}/tmp/debug_logs:{log_folder_name}')
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

                    manifest_contents.append(f'frn::::::bundle::{archive_name}')
                else:
                    raise Exception('Unsupported release train')

    if not found_logs:
        raise Exception('Logs not found')

    _create_manifest(path, contents=manifest_contents)
    # Start the ingestion
    return ingest_handler.start_pipeline(path,
                                         f'qa-{job_id}-{test_index}',
                                         metadata=metadata)


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
    try:
        filename = url.split('/')[-1].replace(' ', '_') 
        file_path = os.path.join(path, filename)

        response = requests.get(url, allow_redirects=True, stream=True)
        if response.ok:
            os.makedirs(path, exist_ok=True)
            print('INFO: Saving log archive to', os.path.abspath(file_path))
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 8):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        os.fsync(f.fileno())
        else:  # HTTP status code 4XX/5XX
            print(f'ERROR: Download failed: status code {response.status_code}')
            return False
    except Exception as e:
        print('ERROR:', e)
        return False
    return True


def clean_up(job_id):
    """ Deleting the downloaded directory for the job_id """
    path = os.path.join(DOWNLOAD_DIRECTORY, job_id)
    if os.path.exists(path):
        print('INFO: Cleaning up downloaded files from:', path)
        # Deletes the entire directory with its children
        shutil.rmtree(path)