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
from werkzeug.utils import secure_filename

from utils import archive_extractor, manifest_parser
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
    parser.add_argument('--ingest_type', help='Ingestion type', choices=['qa', 'upload'])
    parser.add_argument('job_id', help='Job ID')
    parser.add_argument('--test_index', type=int, help='Test index of the QA job', default=0)
    parser.add_argument('--tags', nargs='*', help='Tags for the ingestion', default=[])
    parser.add_argument('--start_time', type=int, help='Epoch start time to filter logs', default=None)
    parser.add_argument('--end_time', type=int, help='Epoch end time to filter logs', default=None)
    parser.add_argument('--sources', nargs='*', help='Sources to filter the logs during ingestion', default=None)
    parser.add_argument('--file_name', help='File name of the uploaded log archive', default=None)

    try:
        args = parser.parse_args()
        ingest_type = args.ingest_type
        job_id = args.job_id
        test_index = args.test_index
        file_name = args.file_name
        tags = args.tags
        start_time = args.start_time
        end_time = args.end_time
        sources = args.sources

        LOG_ID = _get_log_id(job_id, ingest_type, test_index=test_index)
        es_metadata = ElasticsearchMetadata()

        custom_logging = logger.get_logger(filename=f'{LOG_ID}.log')
        custom_logging.propagate = False

        metadata = {
            'tags': tags,
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
        elif ingest_type == 'upload':
            ingestion_status = ingest_techsupport_logs(job_id, file_name, metadata, filters)
        else:
            raise Exception('Wrong ingest type')

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
        clean_up(LOG_ID)

        # Backing up the logs generated during ingestion
        logger.backup_ingestion_logs(LOG_ID)


@ingester_page.route('/upload', methods=['POST'])
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
    LOG_ID = _get_log_id(job_id, ingest_type='upload')

    save_dir = os.path.join(DOWNLOAD_DIRECTORY, LOG_ID)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, secure_filename(file.filename))

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


@ingester_page.route('/ingest', methods=['GET'])
def render_ingest_page():
    """ UI for ingesting logs """
    ingest_type = request.args.get('ingest_type', 'qa')
    return render_template('ingester.html', feedback={}, ingest_type=ingest_type)


@ingester_page.route('/ingest', methods=['POST'])
def ingest():
    """
    Handling ingestion of logs from QA jobs.
    Required QA "job_id"
    """
    try:
        ingest_type = request.form.get('ingest_type', 'qa')
        job_id = request.form.get('job_id')
        test_index = request.form.get('test_index', 0)
        tags = request.form.get('tags')
        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip() != '']
        file_name = request.form.get('filename')

        start_time = request.form.get('start_time', None)
        end_time = request.form.get('end_time', None)
        sources = request.form.getlist('sources', None)

        if not job_id:
            return render_template('ingester.html', feedback={
                'success': False,
                'job_id': job_id,
                'tags': tags,
                'start_time': start_time,
                'end_time': end_time,
                'sources': sources,
                'msg': 'Missing JOB ID'
            }, ingest_type=ingest_type)

        job_id = job_id.strip()

        LOG_ID = _get_log_id(job_id, ingest_type, test_index=test_index)

        es_metadata = ElasticsearchMetadata()
        metadata = es_metadata.get(LOG_ID)

        # If metadata exists then either ingestion for this job
        # is already done or in progress
        if not metadata or metadata['ingestion_status'] == 'FAILED':
            cmd = ['./ingester.py', job_id, '--ingest_type', ingest_type]
            if len(tags_list) > 0:
                cmd.append('--tags')
                cmd.append(' '.join(tags_list))

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
            elif ingest_type == 'upload':
                cmd.append('--file_name')
                cmd.append(file_name)

            ingestion = subprocess.Popen(cmd)

        return render_template('ingester.html', feedback={
            'started': True,
            'log_id': LOG_ID,
            'success': metadata.get('ingestion_status') == 'COMPLETED',
            'is_partial_ingestion': metadata.get('is_partial_ingestion', False),
            'job_id': job_id,
            'test_index': test_index,
            'tags': tags,
            'start_time': start_time,
            'end_time': end_time,
            'sources': sources,
            'metadata': metadata
        }, ingest_type=ingest_type)
    except Exception as e:
        current_app.logger.exception(f'Error when starting ingestion for job: {job_id}')
        return render_template('ingester.html', feedback={
            'started': False,
            'success': False,
            'log_id': LOG_ID,
            'job_id': job_id,
            'test_index': test_index,
            'tags': tags,
            'start_time': start_time,
            'end_time': end_time,
            'sources': sources,
            'msg': str(e)
        }, ingest_type=ingest_type), 500


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
    if ingest_type == 'qa':
        test_index = additional_data.get('test_index', 0)
        return f'log_qa-{job_id}-{test_index}'
    elif ingest_type == 'upload':
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

        tags = metadata.get('tags') if metadata.get('tags') else []
        # Adding the release train to the tags
        metadata = {
            **metadata,
            'tags': tags + [release_train]
        }

        _update_metadata(es_metadata, LOG_ID, 'DOWNLOAD_STARTED')

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


def ingest_techsupport_logs(job_id, file_name, metadata, filters):
    """
    Ingesting logs using an uploaded techsupport log archive.

    This function ingest logs to the Log Analyzer from the log
    archive uploaded with the name provided as "file_name".
    """
    es_metadata = ElasticsearchMetadata()
    LOG_ID = _get_log_id(job_id, ingest_type='upload')
    LOG_DIR = os.path.join(DOWNLOAD_DIRECTORY, LOG_ID, file_name)

    try:
        # Extract if the file is an archive
        if archive_extractor.is_archive(LOG_DIR):
            archive_extractor.extract(LOG_DIR)
            LOG_DIR = os.path.splitext(LOG_DIR)[0]

        # TODO(Sourabh): Techsupport archive does not have the manifest
        # at the root but one level down.
        if not manifest_parser.has_manifest(LOG_DIR):
            folders = next(os.walk(os.path.join(LOG_DIR,'.')))[1]

            # TODO(Sourabh): This is an assumption that there will only
            # be techsupport folder.
            log_folder_name = folders[0]
            LOG_DIR = os.path.join(LOG_DIR, log_folder_name)

            # TODO(Sourabh): Temp workaround until David G's fix to ingest
            # storage agent logs collected by node-service since it is the
            # only source for storage agent debug logs.
            manifest = manifest_parser.parse(LOG_DIR)

            contents = list()
            # TODO(Sourabh) Temp workaround for techsupport dumps generated
            # from S1 chips.
            for content in manifest['contents']:
                content = content.replace('platform-agent:archive', 'cclinux:archive')
                contents.append(content)

            contents.extend([
                'frn:plaform:DPU::system:storage_agent:textfile:other:*storageagent.log*'
            ])

            _create_manifest(LOG_DIR, manifest['metadata'], contents)

        # Start the ingestion
        return ingest_handler.start_pipeline(LOG_DIR,
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


def clean_up(log_id):
    """ Deleting the downloaded directory for the log_id """
    path = os.path.join(DOWNLOAD_DIRECTORY, log_id)
    if os.path.exists(path):
        logging.info(f'Cleaning up downloaded files from: {path}')
        # Deletes the entire directory with its children
        shutil.rmtree(path)


if __name__ == '__main__':
    main()