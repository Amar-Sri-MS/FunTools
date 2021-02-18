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

sys.path.insert(0, '..')

from flask import Blueprint, jsonify, request, render_template
from analysis.utils import archive_extractor
from analysis import ingest as ingest_handler

ingester_page = Blueprint('ingester_page', __name__)

DOWNLOAD_DIRECTORY = 'downloads'
QA_JOB_INFO_ENDPOINT = 'http://integration.fungible.local/api/v1/regression/suite_executions'
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
        if not job_id:
            return render_template('ingester.html', feedback={
                'success': False,
                'msg': 'Missing JOB ID'
            })
        job_info = fetch_qa_job_info(job_id)

        # We want the "Script cleanup" test case
        # test_case_exec_ids is a stringified list of IDs
        # Assumption that the last id is always the one we want
        test_case_exec_ids = job_info['data']['test_case_execution_ids'][1:-1].split(', ')

        # Start ingestion
        ingestion_status = ingest_logs(job_id, test_case_exec_ids[-1], job_info)
        # Clean up the downloaded files
        clean_up(job_id)

        if not ingestion_status['success']:
            return render_template('ingester.html', feedback={
                'success': False,
                'msg': 'Ingestion failed.'
            })

        return render_template('ingester.html', feedback={
            'success': True,
            'dashboard_link': f'{request.host_url}log/log_qa-{job_id}/dashboard',
            'time_taken': ingestion_status['time_taken']
        })
    except Exception as e:
        print('ERROR:', e)
        return render_template('ingester.html', feedback={
            'success': False,
            'msg': str(e)
        })


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


def _get_valid_files(path):
    """ Listing valid files in a given "path" """
    return [file for file in os.listdir(path)
                if os.path.isfile(os.path.join(path, file)) and
                file not in ('.DS_Store')
            ]


def ingest_logs(job_id, test_case_exec_id, job_info):
    """
    Ingesting logs using "job_id" and "test_case_exec_id"

    Required job_info to get the release train info and
    ingest logs accordingly.

    This function first checks for logs in single node FC
    and then if not found checks in HA.
    """
    path = f'{DOWNLOAD_DIRECTORY}/{job_id}'
    release_train = job_info['data']['primary_release_train']

    # Format of FC log archive which is stored in QA
    FC_LOG_ENDPOINT = f'{QA_STATIC_ENDPOINT}/s_{job_id}/_0fc_bundle_sanity.py_{job_id}_{test_case_exec_id}_fc_log.tgz'
    # Format of FCS log archive which is stored in QA
    FCS_LOG_ENDPOINT = f'{QA_STATIC_ENDPOINT}/s_{job_id}/_0fc_bundle_sanity.py_{job_id}_{test_case_exec_id}_fcs_log.tgz'

    # TODO(Sourabh): A way to differentiate between single FC and HA jobs
    # using the job_info.

    # single node FC
    if check_and_download_logs(FC_LOG_ENDPOINT, path):
        filename = FC_LOG_ENDPOINT.split('/')[-1].replace(' ', '_')
        archive_path = f'{path}/{filename}'
        archive_extractor.extract(archive_path)

        archive_name = os.path.splitext(filename)[0]
        # Path to the extracted log files
        LOG_DIR = f'{path}/{archive_name}'

        if release_train in ('master', '2.0', '2.0.1'):
            # Copying FUNLOG_MANIFEST file
            shutil.copy('config/templates/fc/FUNLOG_MANIFEST', LOG_DIR)

            # Start the ingestion
            return ingest_handler.start_pipeline(LOG_DIR, f'qa-{job_id}')
        else:
            raise Exception('Unsupported release train')

    # HA FC
    elif check_and_download_logs(FCS_LOG_ENDPOINT, path):
        filename = FCS_LOG_ENDPOINT.split('/')[-1].replace(' ', '_')
        archive_path = f'{path}/{filename}'
        # Extracting the archive
        archive_extractor.extract(archive_path)

        archive_name = os.path.splitext(filename)[0]
        # Path to the extracted log files
        LOG_DIR = f'{path}/{archive_name}/tmp/debug_logs'

        # master release
        if release_train == 'master':
            files = _get_valid_files(LOG_DIR)
            # TODO(Sourabh): This is an assumption that there will not be
            # other files in this directory

            # The path contains only a tar file, with a FUNLOG_MANIFEST
            # file, which needs to be ingested
            ingest_path = f'{LOG_DIR}/{files[0]}'

            # Start the ingestion
            return ingest_handler.start_pipeline(ingest_path, f'qa-{job_id}')
        elif release_train == '2.0' or release_train == '2.0.1':
            folders = next(os.walk(os.path.join(LOG_DIR,'.')))[1]

            # TODO(Sourabh): This is an assumption that there will not be
            # other folders in this directory
            log_folder_name = folders[0]
            # Path to the extracted log files
            LOG_DIR = os.path.join(LOG_DIR, log_folder_name)

            # Creating FUNLOG_MANIFEST file by replacing timestamp folder name
            with open('config/templates/ha/FUNLOG_MANIFEST', 'rt') as fin:
                with open(f'{LOG_DIR}/FUNLOG_MANIFEST', 'wt') as fout:
                    for line in fin:
                        fout.write(line.replace('<TIMESTAMP>', log_folder_name))

            # Start the ingestion
            return ingest_handler.start_pipeline(LOG_DIR, f'qa-{job_id}')
        else:
            raise Exception('Unsupported release train')
    else:
        raise Exception('Logs not found')


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