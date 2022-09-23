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
import json
import logging
import os
import requests
import shutil
import subprocess
import sys
import time
import yaml

sys.path.insert(0, '.')

from custom_exceptions import ArchiveTooBigException
from custom_exceptions import EmptyPipelineException
from custom_exceptions import NotFoundException
from custom_exceptions import NotSupportedException
from dotenv import load_dotenv
from elastic_metadata import ElasticsearchMetadata
from flask import Blueprint, jsonify, request, render_template
from flask import current_app, g

from view.common import login_required
from utils import is_file_readable
from utils import archive_extractor, manifest_parser
from utils import mail
from utils import timeline

import config_loader
import elastic_log_searcher
import logger
import ingest as ingest_handler


load_dotenv(override=True)

config = config_loader.get_config()
ingester_page = Blueprint('ingester_page', __name__)

FILE_PATH = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_DIRECTORY = os.path.join(FILE_PATH, 'downloads')
QA_BASE_ENDPOINT = 'https://integration.fungible.local'
QA_REGRESSION_BASE_ENDPOINT = f'{QA_BASE_ENDPOINT}/api/v1/regression'
QA_JOB_INFO_ENDPOINT = f'{QA_REGRESSION_BASE_ENDPOINT}/suite_executions'
QA_LOGS_ENDPOINT = f'{QA_REGRESSION_BASE_ENDPOINT}/test_case_time_series'
QA_SUITE_ENDPOINT = f'{QA_REGRESSION_BASE_ENDPOINT}/suites'
QA_STATIC_ENDPOINT = f'{QA_BASE_ENDPOINT}/static/logs'

# Users are required to input ingestion filters for log archives greater than 4GB.
RESTRICTED_ARCHIVE_SIZE = 4 * 1024 * 1024 * 1024


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
    parser.add_argument('--techsupport_ingest_type', help='Techsupport ingestion type', choices=['mount_path', 'upload', 'url'])
    parser.add_argument('--ignore_size_restrictions', action='store_true')

    try:
        status = True
        is_partial = False
        status_msg = None
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
        ignore_size_restrictions = args.ignore_size_restrictions

        LOG_ID = _get_log_id(job_id, ingest_type, test_index=test_index)
        es_metadata = ElasticsearchMetadata()

        custom_logging = logger.get_logger(filename=f'{LOG_ID}.log', separate_error_file=True)
        custom_logging.propagate = False

        # Initializing the timeline tracker
        timeline.init(LOG_ID)

        metadata = {
            'tags': tags,
            'submitted_by': submitted_by,
            'ingest_type': ingest_type,
            'ignore_size_restrictions': ignore_size_restrictions
        }

        filters = {
            'include': {
                'time': (start_time, end_time),
                'sources': sources
            }
        }
        filters_available = is_filters_available(filters)
        # Ignore size restrictions if filters are available.
        metadata['ignore_size_restrictions'] = ignore_size_restrictions or filters_available

        _update_metadata(es_metadata, LOG_ID, 'STARTED')

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
                # Check if the archive is beyond the resricted size
                if (not metadata['ignore_size_restrictions'] and
                    os.stat(log_path).st_size > RESTRICTED_ARCHIVE_SIZE):
                    raise ArchiveTooBigException()

                ingestion_status = ingest_techsupport_logs(job_id, log_path, metadata, filters)
            elif techsupport_ingest_type == 'mount_path':
                # Check if the mount path exists
                if not os.path.exists(log_path):
                    raise FileNotFoundError('Could not find the mount path')
                if not is_file_readable(log_path):
                    raise PermissionError('The user (localadmin) does not have read permission for the file.')
                # Check if the archive is beyond the resricted size
                if (not metadata['ignore_size_restrictions'] and
                    os.stat(log_path).st_size > RESTRICTED_ARCHIVE_SIZE):
                    raise ArchiveTooBigException()

                metadata['mount_path'] = log_path

                archive_name = os.path.basename(log_path)
                path = os.path.join(log_dir, archive_name)

                if os.path.isdir(log_path):
                    # Copying the log folder to download directory to avoid write
                    # permission issue when accessing the archive.
                    shutil.copytree(log_path, path)
                else:
                    # Copying the log archive to download directory to avoid write
                    # permission issue when unarchiving the archive.
                    shutil.copy(log_path, log_dir)

                ingestion_status = ingest_techsupport_logs(job_id, path, metadata, filters)
            elif techsupport_ingest_type == 'url':
                start = time.time()
                _update_metadata(es_metadata,
                                 LOG_ID,
                                 'DOWNLOAD_STARTED',
                                 {'log_path': log_path})
                if check_and_download_logs(log_path, log_dir, ignore_size_restrictions=metadata['ignore_size_restrictions']):
                    end = time.time()
                    time_taken = end - start

                    _update_metadata(es_metadata,
                                    LOG_ID,
                                    'DOWNLOAD_COMPLETED',
                                    {'download_time': time_taken})

                    archive_name = os.path.basename(log_path)
                    path = os.path.join(log_dir, archive_name)
                    ingestion_status = ingest_techsupport_logs(job_id, path, metadata, filters)
            else:
                raise TypeError('Wrong techsupport ingest type')
        else:
            raise TypeError('Wrong ingest type')

        if ingestion_status and not ingestion_status['success']:
            status = False
            status_msg = ingestion_status.get('msg')

        is_partial = ingestion_status.get('is_partial', False)
    except ArchiveTooBigException:
        status = False
        status_msg = ('Size of log archive is beyond restricted limit. '
                     'Please provide ingestion filters to reduce the logs '
                     'or check the ignore size restrictions checkbox.')
        logging.exception(status_msg)
        _update_metadata(es_metadata, LOG_ID, 'PROMPT_USER', {
            'ingestion_error': status_msg,
            **metadata
        })
    except (
        EmptyPipelineException,
        NotFoundException,
        FileNotFoundError,
        PermissionError,
        TypeError,
        NotSupportedException
    ) as e:
        logging.exception(f'Error when starting ingestion for job: {job_id}')
        status = False
        status_msg = str(e)
        _update_metadata(es_metadata, LOG_ID, 'FAILED', {
            'ingestion_error': str(e),
            **metadata
        })
    except Exception as e:
        logging.exception(f'Error when ingesting logs for job: {job_id}')
        status = False
        status_msg = str(e)
        _update_metadata(es_metadata, LOG_ID, 'PARTIAL', {
            'ingestion_error': str(e),
            **metadata
        })
    finally:
        # Clean up the downloaded files if successful.
        if status:
            clean_up(LOG_ID)

        # Notify via email
        email_notify(LOG_ID, status, is_partial, status_msg)

        # Backing up the logs generated during ingestion
        logger.backup_ingestion_logs(LOG_ID)

    if not status:
        exit_msg = status_msg if status_msg else 'Some error occurred.'
        sys.exit(exit_msg)

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
    # Reject if file size is greater than the MAX_CONTENT_LENGTH
    UPLOAD_MAX_FILESIZE = current_app.config['MAX_CONTENT_LENGTH']
    if (int(request.form.get('dztotalfilesize', 0)) > UPLOAD_MAX_FILESIZE):
        return jsonify('File is too big.'
                       'Please use other methods to ingest.'), 413

    job_id = request.form.get('job_id')
    job_id = job_id.strip().lower()
    file = request.files['file']
    LOG_ID = _get_log_id(job_id, ingest_type='techsupport')

    save_dir = os.path.join(DOWNLOAD_DIRECTORY, LOG_ID)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, file.filename)

    current_chunk = int(request.form.get('dzchunkindex', 0))

    # If the file already exists it's ok if we are appending to it,
    # but not if it's new file that would overwrite the existing one
    if os.path.exists(save_path) and current_chunk == 0:
        # 400 and 500s will tell dropzone that an error occurred and show an error
        return jsonify('File already exists for this job id.'
                    'Please enter a new job id if this was not uploaded by you.'), 400

    try:
        with open(save_path, 'ab') as f:
            f.seek(int(request.form.get('dzchunkbyteoffset', 0)))
            f.write(file.stream.read())
    except OSError:
        logging.exception('Could not write to file')
        return jsonify("Not sure why,"
                    " but we couldn't write the file to disk"), 500

    total_chunks = int(request.form.get('dztotalchunkcount', 0))

    if current_chunk + 1 == total_chunks:
        # This was the last chunk, the file should be complete and the size we expect
        if os.path.getsize(save_path) != int(request.form.get('dztotalfilesize', 0)):
            logging.error(f"File {file.filename} was completed, "
                      f"but has a size mismatch."
                      f"Was {os.path.getsize(save_path)} but we"
                      f" expected {request.form.get('dztotalfilesize', 0)}")
            return jsonify('Size mismatch after final upload'), 500
        else:
            logging.info(f'File {file.filename} has been uploaded successfully')
    else:
        logging.debug(f'Chunk {current_chunk + 1} of {total_chunks} '
                  f'for file {file.filename} complete')

    return jsonify('Chunk upload successful'), 200


@ingester_page.route('/upload_file', methods=['POST'])
@login_required
def upload_file():
    """
    Example usage with cURL:
        curl -i -XPOST \
        -H 'Accept: application/json' \
        -H 'Content-Type: multipart/form-data' \
        -F 'job_id=test' \
        -F 'submitted_by="sourabh.jain@fungible.com"' \
        -F 'file=@"/bugbits/test/techsupport.tgz"' \
        'http://funlogs/upload_file'
    """
    try:
        # Accept type could be either text/html or application/json if the
        # user wants a JSON response instead of the default html response.
        accept_type = request.headers.get('Accept', 'text/html')

        job_id = request.form.get('job_id')
        job_id = job_id.strip().lower()
        tags = request.form.get('tags', '')
        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip() != ''] if tags else []
        file = request.files['file']
        submitted_by = g.user

        start_time = request.form.get('start_time', None)
        end_time = request.form.get('end_time', None)
        sources = request.form.getlist('sources', None)

        ingest_type = 'techsupport'
        techsupport_ingest_type = 'upload'
        file_name = os.path.basename(file.filename)

        LOG_ID = _get_log_id(job_id, ingest_type=ingest_type)

        save_dir = os.path.join(DOWNLOAD_DIRECTORY, LOG_ID)
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, file_name)
        file.save(save_path)

        metadata = start_ingestion(job_id,
                                   ingest_type,
                                   tags=tags_list,
                                   techsupport_ingest_type=techsupport_ingest_type,
                                   file_name=file_name,
                                   sources=sources,
                                   start_time=start_time,
                                   end_time=end_time)

        feedback = {
            'started': True,
            'log_id': LOG_ID,
            'success': metadata.get('ingestion_status') == 'COMPLETED',
            'is_partial_ingestion': metadata.get('is_partial_ingestion', False),
            'job_id': job_id,
            'tags': tags,
            'submitted_by': submitted_by,
            'start_time': start_time,
            'end_time': end_time,
            'sources': sources,
            'metadata': metadata
        }

    except Exception as e:
        current_app.logger.exception(f'Error when starting ingestion for job: {job_id}')
        feedback = {
            'success': False,
            'started': False,
            'log_id': LOG_ID,
            'job_id': job_id,
            'tags': tags,
            'submitted_by': submitted_by,
            'start_time': start_time,
            'end_time': end_time,
            'sources': sources,
            'msg': str(e)
        }

    if accept_type == 'application/json':
        return jsonify(feedback)
    return render_template(
        'ingester.html',
        feedback=feedback,
        ingest_type=ingest_type,
        techsupport_ingest_type=techsupport_ingest_type,
        file_server_url=config['FILE_SERVER_URL']
    )

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
        techsupport_ingest_type=techsupport_ingest_type,
        file_server_url=config['FILE_SERVER_URL'])


@ingester_page.route('/ingest', methods=['POST'])
@login_required
def ingest():
    """
    Handling ingestion of logs from either QA jobs or
    techsupport archive.

    For ingesting a QA job, requires:
        "job_id" and "test_index"

    For ingesting a techsupport archive, requires:
        unique "job_id" and
        "mount_path" in case the archive is in NFS mounted volume
        "filename" in case the archive is uploaded by the user.
    """
    try:
        # Accept type could be either text/html or application/json if the
        # user wants a JSON response instead of the default html response.
        accept_type = request.headers.get('Accept', 'text/html')

        ingest_type = request.form.get('ingest_type', 'qa')
        techsupport_ingest_type = request.form.get('techsupport_ingest_type')
        job_id = request.form.get('job_id')
        test_index = request.form.get('test_index', 0)
        tags = request.form.get('tags', '')
        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip() != ''] if tags else []
        file_name = request.form.get('filename')
        mount_path = request.form.get('mount_path')
        downloadable_url = request.form.get('downloadable_url')
        ignore_size_restrictions = request.form.get('ignore_size_restrictions', default=False, type=bool)
        submitted_by = g.user

        start_time = request.form.get('start_time', None)
        end_time = request.form.get('end_time', None)
        sources = request.form.getlist('sources', None)

        LOG_ID = None

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
                'downloadable_url': downloadable_url,
                'ignore_size_restrictions': ignore_size_restrictions,
                'msg': msg if msg else 'Some error occurred'
            }
            if accept_type == 'application/json':
                return jsonify(feedback)
            return render_template(
                'ingester.html',
                feedback=feedback,
                ingest_type=ingest_type,
                techsupport_ingest_type=techsupport_ingest_type,
                file_server_url=config['FILE_SERVER_URL']
            )

        if not job_id:
            return render_error_template('Missing JOB ID')

        job_id = job_id.strip().lower()
        LOG_ID = _get_log_id(job_id, ingest_type, test_index=test_index)

        if techsupport_ingest_type == 'mount_path' and not mount_path:
            return render_error_template('Missing mount path')
        elif techsupport_ingest_type == 'upload' and not file_name:
            return render_error_template('Missing filename')
        elif techsupport_ingest_type == 'url' and not downloadable_url:
            return render_error_template('Missing downloadable url')

        metadata = start_ingestion(job_id,
                                   ingest_type,
                                   test_index=test_index,
                                   tags=tags_list,
                                   techsupport_ingest_type=techsupport_ingest_type,
                                   mount_path=mount_path,
                                   downloadable_url=downloadable_url,
                                   file_name=file_name,
                                   ignore_size_restrictions=ignore_size_restrictions,
                                   sources=sources,
                                   start_time=start_time,
                                   end_time=end_time)

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
            'downloadable_url': downloadable_url,
            'ignore_size_restrictions': ignore_size_restrictions,
            'metadata': metadata
        }

        if accept_type == 'application/json':
            return jsonify(feedback)
        return render_template(
            'ingester.html',
            feedback=feedback,
            ingest_type=ingest_type,
            techsupport_ingest_type=techsupport_ingest_type,
            file_server_url=config['FILE_SERVER_URL']
        )
    except Exception as e:
        current_app.logger.exception(f'Error when starting ingestion for job: {job_id}')
        return render_error_template(str(e)), 500


def start_ingestion(job_id, ingest_type, **additional_data):
    """
    Forming the command and starting the ingestion based on the
    additional data.

    Returns the metadata if the job_id already exists.
    """
    test_index = additional_data.get('test_index', 0)
    tags = additional_data.get('tags')
    techsupport_ingest_type = additional_data.get('techsupport_ingest_type')
    mount_path = additional_data.get('mount_path')
    file_name = additional_data.get('file_name')
    downloadable_url = additional_data.get('downloadable_url')
    ignore_size_restrictions = additional_data.get('ignore_size_restrictions')
    submitted_by = g.user

    sources = additional_data.get('sources')
    start_time = additional_data.get('start_time')
    end_time = additional_data.get('end_time')

    LOG_ID = _get_log_id(job_id, ingest_type, test_index=test_index)

    es_metadata = ElasticsearchMetadata()
    metadata = es_metadata.get(LOG_ID)

    # If metadata exists then either ingestion for this job
    # is already done or in progress
    if not metadata or metadata['ingestion_status'] in ['FAILED', 'PROMPT_USER']:
        cmd = ['./ingester.py', job_id, '--ingest_type', ingest_type]
        if len(tags) > 0:
            cmd.append('--tags')
            cmd.extend(tags)

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
            elif techsupport_ingest_type == 'url':
                cmd.append('--log_path')
                cmd.append(downloadable_url)

        if submitted_by:
            cmd.append('--submitted_by')
            cmd.append(submitted_by)

        if ignore_size_restrictions:
            cmd.append('--ignore_size_restrictions')

        logging.info(f'Running ingestion cmd: {cmd}')
        ingestion = subprocess.Popen(cmd)

    return metadata

@ingester_page.route('/ingest/<log_id>/status', methods=['GET'])
def check_status(log_id):
    """
    Returns the metadata containing the ingestion
    status for the given "log_id"
    """
    es_metadata = ElasticsearchMetadata()
    metadata = es_metadata.get(log_id)

    # Fetch index stats which includes log count and store size.
    if metadata:
        index_stats = elastic_log_searcher._get_indices(log_id)
        index_stats = index_stats[0] if len(index_stats) else None
        metadata['index_stats'] = index_stats

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


def is_filters_available(filters):
    """ Returns True if filters are available. """
    included_filters = filters['include']
    if (len(included_filters['time']) > 0 and
        (included_filters['time'][0] or included_filters['time'][1])):
        return True

    if included_filters['sources'] and len(included_filters['sources']) > 0:
        return True

    return False


def fetch_qa_job_info(session, job_id):
    """
    Fetching QA job info using QA endpoint
    Returns response (dict)
    Raises Exception if Job not found
    """
    url = f'{QA_JOB_INFO_ENDPOINT}/{job_id}'
    headers = {"X-CSRFToken": session.cookies['csrftoken']}
    response = requests.get(url, verify=False, headers=headers, cookies=session.cookies)
    job_info = response.json()
    if not (job_info and job_info['data']):
        raise NotFoundException('Job info not found')
    return job_info


def fetch_qa_suite_info(session, suite_id):
    """
    Fetching QA job info using QA endpoint
    Returns response (dict)
    Raises Exception if Job not found
    """
    url = f'{QA_SUITE_ENDPOINT}/{suite_id}'
    headers = {"X-CSRFToken": session.cookies['csrftoken']}
    response = requests.get(url, verify=False, headers=headers, cookies=session.cookies)
    suite_info = response.json()
    if not (suite_info and suite_info['data']):
        raise NotFoundException(f'QA suite ({suite_id}) not found')
    return suite_info['data']


def fetch_qa_logs(session, job_id, suite_info, test_index=None):
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
    headers = {"X-CSRFToken": session.cookies['csrftoken']}
    response = requests.get(url, verify=False, headers=headers, cookies=session.cookies)
    job_logs = response.json()
    if not (job_logs and job_logs['data']):
        raise NotFoundException('Logs not found')
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
    else:
        raise NotFoundException('Logs not found')

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

        # NOTE: Ignoring tm_fc_log.tgz since it does contain fc logs.
        if filename.endswith(log_filenames_to_ingest) and not filename.endswith('_tm_fc_log.tgz'):
            log_files.append(log['filename'])

    return log_files


def _get_valid_files(path):
    """ Listing valid files in a given "path" """
    return [file for file in os.listdir(path)
                if os.path.isfile(os.path.join(path, file)) and
                file not in ('.DS_Store')
            ]


def get_qa_session():
    """
    Authenicates with QA infra using the login REST API and
    creates a session object which contains the cookies with
    csrftoken and sessionid.

    Returns requests.Session object or raises Exception if
    auth fails.
    """
    username = os.getenv('LDAP_USER')
    password = os.getenv('LDAP_PASSWORD')
    uri = "/api/v1/login"
    url = f'{QA_BASE_ENDPOINT}{uri}'
    headers = {'Content-Type': 'application/json'}
    data = {"username": username, "password": password}
    session = requests.Session()
    response = session.post(url, verify=False, headers=headers, data=json.dumps(data))
    if response.status_code == 200 and 'csrftoken' in session.cookies:
        return session
    else:
        logging.error(
            'Could not login to QA infra.'
            'Status: {} Response: {}'.format(response.status_code, response.text))
    raise Exception('Could not login to QA Infra.')


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
    QA_LOGS_DIRECTORY = '/web/static/logs'
    found_logs = False

    manifest_contents = list()

    start = time.time()
    try:
        session = get_qa_session()
        job_info = fetch_qa_job_info(session, job_id)
        suite_info = fetch_qa_suite_info(session, job_info['data']['suite_id'])
        log_files = fetch_qa_logs(session, job_id, suite_info, test_index)

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
            # Ignore files which are not in the logs directory.
            if QA_LOGS_DIRECTORY not in log_file:
                continue
            log_dir = log_file.split(QA_LOGS_DIRECTORY)[1]
            url = f'{QA_STATIC_ENDPOINT}{log_dir}'
            if check_and_download_logs(url, path, session, metadata['ignore_size_restrictions']):
                found_logs = True
                # techsupport log archive
                if log_file.endswith('cs_all_logs_techsupport.tar.gz'):
                    filename = log_file.split('/')[-1].replace(' ', '_')
                    log_path = f'{path}/{filename}'
                    # Extract if the file is an archive
                    if archive_extractor.is_archive(log_path):
                        archive_extractor.extract(log_path)
                        log_path = os.path.splitext(log_path)[0]

                    if not manifest_parser.has_manifest(log_path):
                        raise NotFoundException('Could not find the FUNLOG_MANIFEST file.')
                    manifest_contents.extend(_get_fixed_manifest_contents(f'{log_path}'))

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
                        raise NotSupportedException('Unsupported release train')

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
                            raise NotFoundException('Could not find the CS log archive')
                        if len(files) > 1:
                            raise NotSupportedException('There are more than 1 CS log archive')

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
                        raise NotSupportedException('Unsupported release train')

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
                        raise NotSupportedException('Unsupported release train')

        if not found_logs:
            raise NotFoundException('Logs not found')

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
        return {
            'success': False,
            'msg': str(e)
        }


def _get_fixed_manifest_contents(log_path):
    """ Temporary fixes to the manifest file. """
    manifest_contents = list()
    filename = log_path.split('/')[-1]
    manifest_contents.append(f'frn::::::bundle::"{filename}"')

    # TODO(Sourabh): This is a temp workaround to get techsupport ingestion working.
    # This will be removed after the fixes to manifest creation by David G.
    archive_name = os.path.basename(filename)

    # The techsupport folder name inside the techsupport log archive might contain
    # timestamps.
    techsupport_folder_name = os.path.basename(glob.glob(f'{log_path}/techsupport*')[0])

    # Get the folders of each node in the cluster
    folders = glob.glob(f'{log_path}/{techsupport_folder_name}/*[!devices][!memory][!other]')

    manifest_contents.extend([
        f'frn:plaform:DPU::system:storage_agent:textfile:"{archive_name}/{techsupport_folder_name}/other":*storageagent.log*',
        f'frn:plaform:DPU::system:platform_agent:textfile:"{archive_name}/{techsupport_folder_name}/other":*platformagent.log*',
        f'frn:plaform:DPU::system:funos:textfile:"{archive_name}/{techsupport_folder_name}/other":*funos.log*'
    ])

    # HA logs
    if len(folders) == 3:
        for folder in folders:
            folder_name = folder.split('/')[-1].replace(' ', '_')
            manifest_contents.extend([
                f'frn:composer:cluster:{folder_name}:host:apigateway:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}":apigateway',
                f'frn:composer:cluster:{folder_name}:host:cassandra:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}":cassandra',
                f'frn:composer:cluster:{folder_name}:host:kafka:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}":kafka',
                f'frn:composer:cluster:{folder_name}:host:kapacitor:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}":kapacitor',
                f'frn:composer:cluster:{folder_name}:host:node-service:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}":nms',
                f'frn:composer:cluster:{folder_name}:host:pfm:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}":pcie',
                f'frn:composer:cluster:{folder_name}:host:telemetry-service:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}":tms',
                f'frn:composer:cluster:{folder_name}:host:dataplacement:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}/sc":dataplacement',
                f'frn:composer:cluster:{folder_name}:host:discovery:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}/sc":discovery',
                f'frn:composer:cluster:{folder_name}:host:lrm_consumer:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}/sc":lrm_consumer',
                f'frn:composer:cluster:{folder_name}:host:expansion_rebalance:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}/sc":expansion_rebalance',
                f'frn:composer:cluster:{folder_name}:host:metrics_manager:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}/sc":metrics_manager',
                f'frn:composer:cluster:{folder_name}:host:metrics_server:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}/sc":metrics_server',
                f'frn:composer:cluster:{folder_name}:host:scmscv:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}/sc":scmscv',
                f'frn:composer:cluster:{folder_name}:host:setup_db:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}/sc":setup_db',
                f'frn:composer:cluster:{folder_name}:host:sns:folder:"{archive_name}/{techsupport_folder_name}/{folder_name}":sns',
            ])
    else:
        manifest_contents.extend([
            f'frn:composer:controller::host:apigateway:folder:"{archive_name}/{techsupport_folder_name}/cs":apigateway',
            f'frn:composer:controller::host:cassandra:folder:"{archive_name}/{techsupport_folder_name}/cs":cassandra',
            f'frn:composer:controller::host:kafka:textfile:"{archive_name}/{techsupport_folder_name}/cs/container":kafka.log',
            f'frn:composer:controller::host:kapacitor:folder:"{archive_name}/{techsupport_folder_name}/cs":container',
            f'frn:composer:controller::host:node-service:folder:"{archive_name}/{techsupport_folder_name}/cs":nms',
            f'frn:composer:controller::host:pfm:folder:"{archive_name}/{techsupport_folder_name}/cs":pfm',
            f'frn:composer:controller::host:telemetry-service:folder:"{archive_name}/{techsupport_folder_name}/cs":tms',
            f'frn:composer:controller::host:dataplacement:folder:"{archive_name}/{techsupport_folder_name}/cs/sclogs":dataplacement',
            f'frn:composer:controller::host:discovery:folder:"{archive_name}/{techsupport_folder_name}/cs/sclogs":discovery',
            f'frn:composer:controller::host:lrm_consumer:folder:"{archive_name}/{techsupport_folder_name}/cs/sclogs":lrm_consumer',
            f'frn:composer:controller::host:expansion_rebalance:folder:"{archive_name}/{techsupport_folder_name}/cs/sclogs":expansion_rebalance',
            f'frn:composer:controller::host:metrics_manager:folder:"{archive_name}/{techsupport_folder_name}/cs/sclogs":metrics_manager',
            f'frn:composer:controller::host:metrics_server:folder:"{archive_name}/{techsupport_folder_name}/cs/sclogs":metrics_server',
            f'frn:composer:controller::host:scmscv:folder:"{archive_name}/{techsupport_folder_name}/cs/sclogs":scmscv',
            f'frn:composer:controller::host:setup_db:folder:"{archive_name}/{techsupport_folder_name}/cs/sclogs":setup_db',
            f'frn:composer:controller::host:sns:folder:"{archive_name}/{techsupport_folder_name}/cs":sns',
        ])

    return manifest_contents


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

        if not manifest_parser.has_manifest(log_path):
            raise NotFoundException('Could not find the FUNLOG_MANIFEST file.')

        manifest_contents = _get_fixed_manifest_contents(log_path)

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
            **metadata,
            'ingestion_error': str(e)
        })
        return {
            'success': False,
            'msg': str(e)
        }


def _create_manifest(path, metadata={}, contents=[]):
    """ Creates manifest file at the given path """
    manifest = {
        'metadata': metadata,
        'contents': contents
    }

    with open(f'{path}/FUNLOG_MANIFEST', 'w') as file:
        yaml.dump(manifest, file)


@timeline.timeline_logger('downloading_logs')
def check_and_download_logs(url, path, session=None, ignore_size_restrictions=False):
    """ Downloading log archives from QA dashboard """
    filename = url.split('/')[-1].replace(' ', '_')
    file_path = os.path.join(path, filename)

    headers = {}
    cookies = {}
    if session:
        headers = {"X-CSRFToken": session.cookies['csrftoken']}
        cookies=session.cookies

    response = requests.get(url,
        headers=headers,
        cookies=cookies,
        verify=False,
        allow_redirects=True,
        stream=True)
    if response.ok:
        if not ignore_size_restrictions:
            content_length = int(response.headers['Content-Length'])
            if content_length > RESTRICTED_ARCHIVE_SIZE:
                raise ArchiveTooBigException()

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


def email_notify(logID, is_successful, is_partial, status_msg):
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

    if not logID:
        logging.warning('Sending email aborted: logID not found.')
        return

    if is_successful:
        if is_partial:
            subject = f'Ingestion of {logID} is successful.'
            body = f"""
                Ingestion of {logID} is partially successful.
                Log Analyzer Dashboard: {config['LOG_VIEW_BASE_URL'].replace('LOG_ID', logID)}/dashboard

                Error logs: {config['FILE_SERVER_URL']}/{logID}/file/{logID}_error.log
                Time to ingest logs: {metadata.get('ingestion_time')} seconds
            """
        else:
            subject = f'Ingestion of {logID} is successful.'
            body = f"""
                Ingestion of {logID} is successful.
                Log Analyzer Dashboard: {config['LOG_VIEW_BASE_URL'].replace('LOG_ID', logID)}/dashboard

                Time to ingest logs: {metadata.get('ingestion_time')} seconds
            """
    else:
        subject = f'Ingestion of {logID} failed.'
        body = f"""
            Ingestion of {logID} failed. Please email tools-pals@fungible.com for help!
            Error logs: {config['FILE_SERVER_URL']}/{logID}/file/{logID}_error.log
            Reason: {status_msg}
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