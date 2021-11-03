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
import glob
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
from flask import current_app, g

from common import login_required
from utils import archive_extractor, manifest_parser
from utils import mail
from utils import timeline
import ingest as ingest_handler
import logger
import config_loader

config = config_loader.get_config()
ingester_page = Blueprint('ingester_page', __name__)

DOWNLOAD_DIRECTORY = 'downloads'
QA_REGRESSION_BASE_ENDPOINT = 'http://integration.fungible.local/api/v1/regression'
QA_JOB_INFO_ENDPOINT = f'{QA_REGRESSION_BASE_ENDPOINT}/suite_executions'
QA_LOGS_ENDPOINT = f'{QA_REGRESSION_BASE_ENDPOINT}/test_case_time_series'
QA_SUITE_ENDPOINT = f'{QA_REGRESSION_BASE_ENDPOINT}/suites'
QA_STATIC_ENDPOINT = 'http://integration.fungible.local/static/logs'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ingest_type', help='Ingestion type', choices=['qa', 'techsupport'])
    parser.add_argument('job_id', help='Job ID')
    parser.add_argument('--log_path', help='Log archive path', default=None)
    parser.add_argument('--test_index', type=int, help='Test index of the QA job', default=0)
    parser.add_argument('--tags', nargs='*', help='Tags for the ingestion', default=[])
    parser.add_argument('--start_time', type=int, help='Epoch start time to filter logs', default=None)
    parser.add_argument('--end_time', type=int, help='Epoch end time to filter logs', default=None)
    parser.add_argument('--sources', nargs='*', help='Sources to filter the logs during ingestion', default=None)
    parser.add_argument('--file_name', help='File name of the uploaded log archive', default=None)
    parser.add_argument('--submitted_by', help='Email address of the submitter', default=None)
    parser.add_argument('--techsupport_ingest_type', help='Techsupport ingestion type', choices=['mount_path', 'upload'])

    try:
        args = parser.parse_args()
        ingest_type = args.ingest_type
        job_id = args.job_id
        test_index = args.test_index
        log_path = args.log_path
        file_name = args.file_name
        tags = args.tags
        submitted_by = args.submitted_by
        start_time = args.start_time
        end_time = args.end_time
        sources = args.sources
        techsupport_ingest_type = args.techsupport_ingest_type

        LOG_ID = _get_log_id(job_id, ingest_type, test_index=test_index)
        es_metadata = ElasticsearchMetadata()

        custom_logging = logger.get_logger(filename=f'{LOG_ID}.log')
        custom_logging.propagate = False

        # Initializing the timeline tracker
        timeline.init(LOG_ID)

        metadata = {
            'tags': tags,
            'submitted_by': submitted_by,
            'ingest_type': ingest_type
        }

        filters = {
            'include': {
                'time': (start_time, end_time),
                'sources': sources
            }
        }

        # Start ingestion
        if ingest_type == 'qa':
            ingestion_status = ingest_qa_logs(job_id, test_index, metadata, filters)
        elif ingest_type == 'techsupport':
            metadata['techsupport_ingest_type'] = techsupport_ingest_type
            LOG_ID = _get_log_id(job_id, ingest_type)
            log_dir = os.path.join(DOWNLOAD_DIRECTORY, LOG_ID)
            os.makedirs(log_dir, exist_ok=True)

            if techsupport_ingest_type == 'upload':
                log_path = os.path.join(log_dir, file_name)
                ingestion_status = ingest_techsupport_logs(job_id, log_path, metadata, filters)
            elif techsupport_ingest_type == 'mount_path':
                # Check if the mount path exists
                if not os.path.exists(log_path):
                    raise Exception('Could not find the mount path')
                metadata['mount_path'] = log_path

                archive_name = os.path.basename(log_path)
                path = os.path.join(log_dir, archive_name)

                # Copying the log archive to download directory to avoid write
                # permission issue when unarchiving the archive.
                shutil.copy(log_path, log_dir)

                ingestion_status = ingest_techsupport_logs(job_id, path, metadata, filters)
            else:
                raise Exception('Wrong techsupport ingest type')
        else:
            raise Exception('Wrong ingest type')

        if ingestion_status and not ingestion_status['success']:
            _update_metadata(es_metadata, LOG_ID, 'FAILED', {
                **metadata,
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
        clean_up(LOG_ID)

        # Notify via email
        email_notify(LOG_ID)

        # Backing up the logs generated during ingestion
        logger.backup_ingestion_logs(LOG_ID)


@ingester_page.route('/upload', methods=['POST'])
@login_required
def upload():
    """
    Upload API for uploading techsupport log archive. Using the
    dropzone.js in UI to upload the files and hence the dropzone
    specific form data for chunking.

    Form data:
    job_id: unique job_id
    file: binary file of log archive uploaded in chunks
    """
    job_id = request.form.get('job_id')
    file = request.files['file']
    LOG_ID = _get_log_id(job_id, ingest_type='techsupport')

    save_dir = os.path.join(DOWNLOAD_DIRECTORY, LOG_ID)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, file.filename)

    current_chunk = int(request.form['dzchunkindex'])

    # If the file already exists it's ok if we are appending to it,
    # but not if it's new file that would overwrite the existing one
    if os.path.exists(save_path) and current_chunk == 0:
        # 400 and 500s will tell dropzone that an error occurred and show an error
        return jsonify('File already exists for this job id.'
                    'Please enter a new job id if this was not uploaded by you.'), 400

    try:
        with open(save_path, 'ab') as f:
            f.seek(int(request.form['dzchunkbyteoffset']))
            f.write(file.stream.read())
    except OSError:
        logging.exception('Could not write to file')
        return jsonify("Not sure why,"
                    " but we couldn't write the file to disk"), 500

    total_chunks = int(request.form['dztotalchunkcount'])

    if current_chunk + 1 == total_chunks:
        # This was the last chunk, the file should be complete and the size we expect
        if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
            logging.error(f"File {file.filename} was completed, "
                      f"but has a size mismatch."
                      f"Was {os.path.getsize(save_path)} but we"
                      f" expected {request.form['dztotalfilesize']}")
            return jsonify('Size mismatch after final upload'), 500
        else:
            logging.info(f'File {file.filename} has been uploaded successfully')
    else:
        logging.debug(f'Chunk {current_chunk + 1} of {total_chunks} '
                  f'for file {file.filename} complete')

    return jsonify('Chunk upload successful'), 200


@ingester_page.route('/remove_file', methods=['DELETE'])
def remove_uploaded_file():
    """
    Removes the uploaded file saved under the given "job_id".

    Request Args:
    job_id
    filename: name of the file to delete
    """
    job_id = request.args.get('job_id')
    filename = request.args.get('filename')
    LOG_ID = _get_log_id(job_id, ingest_type='techsupport')

    log_dir = os.path.join(DOWNLOAD_DIRECTORY, LOG_ID)
    log_path = os.path.join(log_dir, filename)

    if not os.path.exists(log_path):
        return jsonify('Could not find the uploaded file'), 500

    try:
        os.remove(log_path)
    except Exception as e:
        logging.exception(f'Error while deleting the uploaded file: {filename} from {LOG_ID}')
        return jsonify('Error while deleting the uploaded file'), 500

    return jsonify('success')

@ingester_page.route('/ingest', methods=['GET'])
@login_required
def render_ingest_page():
    """ UI for ingesting logs """
    ingest_type = request.args.get('ingest_type', 'qa')
    techsupport_ingest_type = request.args.get('techsupport_ingest_type', 'mount_path')
    return render_template(
        'ingester.html',
        feedback={},
        ingest_type=ingest_type,
        techsupport_ingest_type=techsupport_ingest_type)


@ingester_page.route('/ingest', methods=['POST'])
@login_required
def ingest():
    """
    Handling ingestion of logs from QA jobs.
    Required QA "job_id"
    """
    try:
        accept_type = request.headers.get('Accept', 'text/html')

        ingest_type = request.form.get('ingest_type', 'qa')
        techsupport_ingest_type = request.form.get('techsupport_ingest_type')
        job_id = request.form.get('job_id')
        test_index = request.form.get('test_index', 0)
        tags = request.form.get('tags')
        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip() != '']
        file_name = request.form.get('filename')
        mount_path = request.form.get('mount_path')
        submitted_by = g.user

        start_time = request.form.get('start_time', None)
        end_time = request.form.get('end_time', None)
        sources = request.form.getlist('sources', None)

        job_id = job_id.strip()

        LOG_ID = _get_log_id(job_id, ingest_type, test_index=test_index)

        def render_error_template(msg=None):
            feedback = {
                'success': False,
                'started': False,
                'log_id': LOG_ID,
                'job_id': job_id,
                'test_index': test_index,
                'tags': tags,
                'submitted_by': submitted_by,
                'start_time': start_time,
                'end_time': end_time,
                'sources': sources,
                'mount_path': mount_path,
                'msg': msg if msg else 'Some error occurred'
            }
            if accept_type == 'application/json':
                return jsonify(feedback)
            return render_template(
                'ingester.html',
                feedback=feedback,
                ingest_type=ingest_type,
                techsupport_ingest_type=techsupport_ingest_type
            )

        if not job_id:
            return render_error_template('Missing JOB ID')

        if techsupport_ingest_type == 'mount_path' and not mount_path:
            return render_error_template('Missing mount path')
        elif techsupport_ingest_type == 'upload' and not file_name:
            return render_error_template('Missing filename')

        es_metadata = ElasticsearchMetadata()
        metadata = es_metadata.get(LOG_ID)

        # If metadata exists then either ingestion for this job
        # is already done or in progress
        if not metadata or metadata['ingestion_status'] == 'FAILED':
            cmd = ['./ingester.py', job_id, '--ingest_type', ingest_type]
            if len(tags_list) > 0:
                cmd.append('--tags')
                cmd.extend(tags_list)

            if start_time:
                cmd.append('--start_time')
                cmd.append(start_time)

            if end_time:
                cmd.append('--end_time')
                cmd.append(end_time)

            if len(sources) > 0:
                cmd.append('--sources')
                cmd.extend(sources)

            if ingest_type == 'qa':
                cmd.append('--test_index')
                cmd.append(str(test_index))
            elif ingest_type == 'techsupport':
                cmd.append('--techsupport_ingest_type')
                cmd.append(techsupport_ingest_type)
                if techsupport_ingest_type == 'mount_path':
                    cmd.append('--log_path')
                    cmd.append(mount_path)
                elif techsupport_ingest_type == 'upload':
                    cmd.append('--file_name')
                    cmd.append(file_name)

            if submitted_by:
                cmd.append('--submitted_by')
                cmd.append(submitted_by)

            ingestion = subprocess.Popen(cmd)

        feedback = {
            'started': True,
            'log_id': LOG_ID,
            'success': metadata.get('ingestion_status') == 'COMPLETED',
            'is_partial_ingestion': metadata.get('is_partial_ingestion', False),
            'job_id': job_id,
            'test_index': test_index,
            'tags': tags,
            'submitted_by': submitted_by,
            'start_time': start_time,
            'end_time': end_time,
            'sources': sources,
            'mount_path': mount_path,
            'metadata': metadata
        }

        if accept_type == 'application/json':
            return jsonify(feedback)
        return render_template(
            'ingester.html',
            feedback=feedback,
            ingest_type=ingest_type,
            techsupport_ingest_type=techsupport_ingest_type
        )
    except Exception as e:
        current_app.logger.exception(f'Error when starting ingestion for job: {job_id}')
        return render_error_template(str(e)), 500


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


def _get_log_id(job_id, ingest_type, **additional_data):
    """
    Returns log identifier based on the job_id, ingest_type and
    any additional_data.
    """
    # job_id should be lowercase due to Elasticsearch index
    # naming constraints
    job_id = job_id.lower()
    if ingest_type == 'qa':
        test_index = additional_data.get('test_index', 0)
        return f'log_qa-{job_id}-{test_index}'
    elif ingest_type == 'techsupport':
        return f'log_techsupport-{job_id}'


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

    # These are the log archives from QA platform to ingest.
    # fc_log.tgz & fcs_log.tgz are from single & HA node setup.
    # cs_all_logs_techsupport.tar.gz is collected from devices attached to a controller.
    log_filenames_to_ingest = ('fc_log.tgz', 'fcs_log.tgz', 'cs_all_logs_techsupport.tar.gz')
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


def ingest_qa_logs(job_id, test_index, metadata, filters):
    """
    Ingesting logs using QA "job_id" and "test_index".

    This function downloads the log archives from QA platform
    and ingest them to the Log Analyzer.
    """
    es_metadata = ElasticsearchMetadata()
    LOG_ID = _get_log_id(job_id, ingest_type='qa', test_index=test_index)

    path = f'{DOWNLOAD_DIRECTORY}/{LOG_ID}'
    file_path = os.path.abspath(os.path.dirname(__file__))
    QA_LOGS_DIRECTORY = '/regression/Integration/fun_test/web/static/logs'
    found_logs = False

    manifest_contents = list()

    start = time.time()
    try:
        job_info = fetch_qa_job_info(job_id)
        suite_info = fetch_qa_suite_info(job_info['data']['suite_id'])
        log_files = fetch_qa_logs(job_id, suite_info, test_index)

        release_train = job_info['data']['primary_release_train']

        tags = set(metadata.get('tags') if metadata.get('tags') else [])
        # Adding the release train to the tags
        tags.add(release_train)
        # Adding the tags from suite_info to the tags
        suite_info_tags = suite_info.get('tags')
        if suite_info_tags:
            tags.update(suite_info_tags)

        metadata = {
            **metadata,
            'tags': list(tags)
        }

        _update_metadata(es_metadata, LOG_ID, 'DOWNLOAD_STARTED')

        for log_file in log_files:
            log_dir = log_file.split(QA_LOGS_DIRECTORY)[1]
            url = f'{QA_STATIC_ENDPOINT}{log_dir}'
            if check_and_download_logs(url, path):
                found_logs = True
                # techsupport log archive
                if log_file.endswith('cs_all_logs_techsupport.tar.gz'):
                    filename = log_file.split('/')[-1].replace(' ', '_')
                    manifest_contents.append(f'frn::::::archive::"{filename}"')
                    # TODO(Sourabh): This is a temp workaround to get QA ingestion working.
                    # This will be removed after the fixes to manifest creation by David G.
                    archive_name = os.path.splitext(filename)[0]
                    # HA logs
                    if 'FC-HA-cluster' in suite_info.get('custom_test_bed_spec', {}).get('asset_request', {}):
                        archive_path = f'{path}/{filename}'
                        # Extracting the archive
                        archive_extractor.extract(archive_path)

                        # Get the folders of each node in the cluster
                        folders = glob.glob(f'{path}/{archive_name}/techsupport/*[!devices][!other]')
                        for folder in folders:
                            folder_name = folder.split('/')[-1].replace(' ', '_')
                            manifest_contents.extend([
                                f'frn:composer:cluster:{folder_name}:host:apigateway:folder:"{archive_name}/techsupport/{folder_name}":apigateway',
                                f'frn:composer:cluster:{folder_name}:host:cassandra:folder:"{archive_name}/techsupport/{folder_name}":cassandra',
                                f'frn:composer:cluster:{folder_name}:host:kafka:folder:"{archive_name}/techsupport/{folder_name}":kafka',
                                f'frn:composer:cluster:{folder_name}:host:kapacitor:folder:"{archive_name}/techsupport/{folder_name}":kapacitor',
                                f'frn:composer:cluster:{folder_name}:host:node-service:folder:"{archive_name}/techsupport/{folder_name}":nms',
                                f'frn:composer:cluster:{folder_name}:host:pfm:folder:"{archive_name}/techsupport/{folder_name}":pcie',
                                f'frn:composer:cluster:{folder_name}:host:telemetry-service:folder:"{archive_name}/techsupport/{folder_name}":tms',
                                f'frn:composer:cluster:{folder_name}:host:dataplacement:folder:"{archive_name}/techsupport/{folder_name}/sc":dataplacement',
                                f'frn:composer:cluster:{folder_name}:host:discovery:folder:"{archive_name}/techsupport/{folder_name}/sc":discovery',
                                f'frn:composer:cluster:{folder_name}:host:lrm_consumer:folder:"{archive_name}/techsupport/{folder_name}/sc":lrm_consumer',
                                f'frn:composer:cluster:{folder_name}:host:expansion_rebalance:folder:"{archive_name}/techsupport/{folder_name}/sc":expansion_rebalance',
                                f'frn:composer:cluster:{folder_name}:host:metrics_manager:folder:"{archive_name}/techsupport/{folder_name}/sc":metrics_manager',
                                f'frn:composer:cluster:{folder_name}:host:metrics_server:folder:"{archive_name}/techsupport/{folder_name}/sc":metrics_server',
                                f'frn:composer:cluster:{folder_name}:host:scmscv:folder:"{archive_name}/techsupport/{folder_name}/sc":scmscv',
                                f'frn:composer:cluster:{folder_name}:host:setup_db:folder:"{archive_name}/techsupport/{folder_name}/sc":setup_db',
                                f'frn:composer:cluster:{folder_name}:host:sns:folder:"{archive_name}/techsupport/{folder_name}":sns'
                            ])
                    else:
                        manifest_contents.extend([
                            f'frn:composer:controller::host:apigateway:folder:"{archive_name}/techsupport/cs":apigateway',
                            f'frn:composer:controller::host:cassandra:folder:"{archive_name}/techsupport/cs":cassandra',
                            f'frn:composer:controller::host:kafka:textfile:"{archive_name}/techsupport/cs/container":kafka.log',
                            f'frn:composer:controller::host:kapacitor:folder:"{archive_name}/techsupport/cs":container',
                            f'frn:composer:controller::host:node-service:folder:"{archive_name}/techsupport/cs":nms',
                            f'frn:composer:controller::host:pfm:folder:"{archive_name}/techsupport/cs":pfm',
                            f'frn:composer:controller::host:telemetry-service:folder:"{archive_name}/techsupport/cs":tms',
                            f'frn:composer:controller::host:dataplacement:folder:"{archive_name}/techsupport/cs/sclogs":dataplacement',
                            f'frn:composer:controller::host:discovery:folder:"{archive_name}/techsupport/cs/sclogs":discovery',
                            f'frn:composer:controller::host:lrm_consumer:folder:"{archive_name}/techsupport/cs/sclogs":lrm_consumer',
                            f'frn:composer:controller::host:expansion_rebalance:folder:"{archive_name}/techsupport/cs/sclogs":expansion_rebalance',
                            f'frn:composer:controller::host:metrics_manager:folder:"{archive_name}/techsupport/cs/sclogs":metrics_manager',
                            f'frn:composer:controller::host:metrics_server:folder:"{archive_name}/techsupport/cs/sclogs":metrics_server',
                            f'frn:composer:controller::host:scmscv:folder:"{archive_name}/techsupport/cs/sclogs":scmscv',
                            f'frn:composer:controller::host:setup_db:folder:"{archive_name}/techsupport/cs/sclogs":setup_db',
                            f'frn:composer:controller::host:sns:folder:"{archive_name}/techsupport/cs":sns'
                        ])

                # single node FC
                elif log_file.endswith('_fc_log.tgz'):
                    filename = log_file.split('/')[-1].replace(' ', '_')
                    archive_path = f'{path}/{filename}'
                    archive_extractor.extract(archive_path)

                    archive_name = os.path.splitext(filename)[0]
                    # Path to the extracted log files
                    LOG_DIR = f'{path}/{archive_name}'

                    if release_train in ('master', '2.0', '2.0.1', '2.0.2', '2.1', '2.2', '2.2.1', '2.3', '3.0', '3.1'):
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
                    if release_train in ('master', '2.1', '2.2', '2.2.1', '2.3', '3.0', '3.1'):
                        files = _get_valid_files(LOG_DIR)
                        # TODO(Sourabh): This is an assumption that there will not be
                        # other files in this directory
                        if len(files) == 0:
                            raise Exception('Could not find the CS log archive')
                        if len(files) > 1:
                            raise Exception('There are more than 1 CS log archive')

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

                    if release_train in ('master', '2.0', '2.0.1', '2.1', '2.2', '2.2.1', '2.3'):
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
            **metadata,
            'ingestion_error': str(e)
        })


def ingest_techsupport_logs(job_id, log_path, metadata, filters):
    """
    Ingesting logs using an uploaded techsupport log archive.

    This function ingest logs to the Log Analyzer from the log
    archive in the given "log_path".
    """
    es_metadata = ElasticsearchMetadata()
    LOG_ID = _get_log_id(job_id, ingest_type='techsupport')
    path = f'{DOWNLOAD_DIRECTORY}/{LOG_ID}'
    ingest_path = log_path

    try:
        # Extract if the file is an archive
        if archive_extractor.is_archive(log_path):
            archive_extractor.extract(log_path)
            log_path = os.path.splitext(log_path)[0]

        # TODO(Sourabh): Techsupport archive does not have the manifest
        # at the root but one level down.
        if not manifest_parser.has_manifest(log_path):
            folders = next(os.walk(os.path.join(log_path,'.')))[1]

            # TODO(Sourabh): This is an assumption that there will only
            # be techsupport folder.
            log_folder_name = folders[0]
            log_path = os.path.join(log_path, log_folder_name)

            # TODO(Sourabh): Temp workaround until David G's fix to ingest
            # storage agent logs collected by node-service since it is the
            # only source for storage agent debug logs.
            manifest = manifest_parser.parse(log_path)

            contents = list()
            # TODO(Sourabh) Temp workaround for techsupport dumps generated
            # from S1 chips.
            for content in manifest['contents']:
                content = content.replace('platform-agent:archive', 'cclinux:archive')
                contents.append(content)

            contents.extend([
                'frn:plaform:DPU::system:storage_agent:textfile:other:*storageagent.log*'
            ])

            _create_manifest(log_path, manifest['metadata'], contents)

        else:
            manifest_contents = list()
            filename = log_path.split('/')[-1].replace(' ', '_')
            manifest_contents.append(f'frn::::::bundle::"{filename}"')

            # TODO(Sourabh): This is a temp workaround to get techsupport ingestion working.
            # This will be removed after the fixes to manifest creation by David G.
            archive_name = os.path.basename(filename)

            # Get the folders of each node in the cluster
            folders = glob.glob(f'{log_path}/techsupport/*[!devices][!other]')
            # HA logs
            if len(folders) == 3:
                for folder in folders:
                    folder_name = folder.split('/')[-1].replace(' ', '_')
                    manifest_contents.extend([
                        f'frn:composer:cluster:{folder_name}:host:apigateway:folder:"{archive_name}/techsupport/{folder_name}":apigateway',
                        f'frn:composer:cluster:{folder_name}:host:cassandra:folder:"{archive_name}/techsupport/{folder_name}":cassandra',
                        f'frn:composer:cluster:{folder_name}:host:kafka:folder:"{archive_name}/techsupport/{folder_name}":kafka',
                        f'frn:composer:cluster:{folder_name}:host:kapacitor:folder:"{archive_name}/techsupport/{folder_name}":kapacitor',
                        f'frn:composer:cluster:{folder_name}:host:node-service:folder:"{archive_name}/techsupport/{folder_name}":nms',
                        f'frn:composer:cluster:{folder_name}:host:pfm:folder:"{archive_name}/techsupport/{folder_name}":pcie',
                        f'frn:composer:cluster:{folder_name}:host:telemetry-service:folder:"{archive_name}/techsupport/{folder_name}":tms',
                        f'frn:composer:cluster:{folder_name}:host:dataplacement:folder:"{archive_name}/techsupport/{folder_name}/sc":dataplacement',
                        f'frn:composer:cluster:{folder_name}:host:discovery:folder:"{archive_name}/techsupport/{folder_name}/sc":discovery',
                        f'frn:composer:cluster:{folder_name}:host:lrm_consumer:folder:"{archive_name}/techsupport/{folder_name}/sc":lrm_consumer',
                        f'frn:composer:cluster:{folder_name}:host:expansion_rebalance:folder:"{archive_name}/techsupport/{folder_name}/sc":expansion_rebalance',
                        f'frn:composer:cluster:{folder_name}:host:metrics_manager:folder:"{archive_name}/techsupport/{folder_name}/sc":metrics_manager',
                        f'frn:composer:cluster:{folder_name}:host:metrics_server:folder:"{archive_name}/techsupport/{folder_name}/sc":metrics_server',
                        f'frn:composer:cluster:{folder_name}:host:scmscv:folder:"{archive_name}/techsupport/{folder_name}/sc":scmscv',
                        f'frn:composer:cluster:{folder_name}:host:setup_db:folder:"{archive_name}/techsupport/{folder_name}/sc":setup_db',
                        f'frn:composer:cluster:{folder_name}:host:sns:folder:"{archive_name}/techsupport/{folder_name}":sns'
                    ])
            else:
                manifest_contents.extend([
                    f'frn:composer:controller::host:apigateway:folder:"{archive_name}/techsupport/cs":apigateway',
                    f'frn:composer:controller::host:cassandra:folder:"{archive_name}/techsupport/cs":cassandra',
                    f'frn:composer:controller::host:kafka:textfile:"{archive_name}/techsupport/cs/container":kafka.log',
                    f'frn:composer:controller::host:kapacitor:folder:"{archive_name}/techsupport/cs":container',
                    f'frn:composer:controller::host:node-service:folder:"{archive_name}/techsupport/cs":nms',
                    f'frn:composer:controller::host:pfm:folder:"{archive_name}/techsupport/cs":pfm',
                    f'frn:composer:controller::host:telemetry-service:folder:"{archive_name}/techsupport/cs":tms',
                    f'frn:composer:controller::host:dataplacement:folder:"{archive_name}/techsupport/cs/sclogs":dataplacement',
                    f'frn:composer:controller::host:discovery:folder:"{archive_name}/techsupport/cs/sclogs":discovery',
                    f'frn:composer:controller::host:lrm_consumer:folder:"{archive_name}/techsupport/cs/sclogs":lrm_consumer',
                    f'frn:composer:controller::host:expansion_rebalance:folder:"{archive_name}/techsupport/cs/sclogs":expansion_rebalance',
                    f'frn:composer:controller::host:metrics_manager:folder:"{archive_name}/techsupport/cs/sclogs":metrics_manager',
                    f'frn:composer:controller::host:metrics_server:folder:"{archive_name}/techsupport/cs/sclogs":metrics_server',
                    f'frn:composer:controller::host:scmscv:folder:"{archive_name}/techsupport/cs/sclogs":scmscv',
                    f'frn:composer:controller::host:setup_db:folder:"{archive_name}/techsupport/cs/sclogs":setup_db',
                    f'frn:composer:controller::host:sns:folder:"{archive_name}/techsupport/cs":sns'
                ])

        _create_manifest(path, contents=manifest_contents)
        ingest_path = path

        # Start the ingestion
        return ingest_handler.start_pipeline(ingest_path,
                                         f'techsupport-{job_id}',
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


@timeline.timeline_logger('downloading_logs')
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
    if not log_id or not metadata_handler:
        logging.error('log_id or metadata_handler is None')
        return
    metadata = {
        **additional_data,
        'ingestion_status': status
    }
    return metadata_handler.update(log_id, metadata)


def email_notify(logID):
    """ Notifying via email at the end of the ingestion """
    es_metadata = ElasticsearchMetadata()
    metadata = es_metadata.get(logID)

    if not metadata:
        logging.warning('Sending email aborted: metadata not found.')
        return
    submitted_by = metadata.get('submitted_by')
    if not submitted_by:
        logging.warning('Sending email aborted: submitted_by email not found.')
        return

    is_failed = metadata.get('ingestion_status') == 'FAILED'
    logID = metadata.get('logID')

    if not logID:
        logging.warning('Sending email aborted: logID not found.')
        return

    if is_failed:
        subject = f'Ingestion of {logID} failed.'
        body = f"""
            Ingestion of {logID} failed. Please email tools-pals@fungible.com for help!
            Reason: {metadata.get('ingestion_error')}
        """
    else:
        subject = f'Ingestion of {logID} is successful.'
        body = f"""
            Ingestion of {logID} is successful.
            Log Analyzer Dashboard: {config['LOG_VIEW_BASE_URL'].replace('LOG_ID', logID)}/dashboard

            Time to ingest logs: {metadata.get('ingestion_time')} seconds
        """

    status = mail.Mail(submitted_by, subject, body)
    if not status:
        logging.error(f'Failed to send email to {submitted_by}')


def clean_up(log_id):
    """ Deleting the downloaded directory for the log_id """
    path = os.path.join(DOWNLOAD_DIRECTORY, log_id)
    if os.path.exists(path):
        logging.info(f'Cleaning up downloaded files from: {path}')
        # Deletes the entire directory with its children
        shutil.rmtree(path)


if __name__ == '__main__':
    main()