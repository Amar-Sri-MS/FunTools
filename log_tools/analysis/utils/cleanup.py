#!/usr/bin/env python3

#
# Cleaning all the data collected for the ingestion
#
# This script can be used to clean all or selected components
#
# Usage:
# python cleanup.py <JOB_ID> -components <COMPONENT_NAME>
#
# JOB_ID is the Log Analyzer Job ID
# COMPONENT_NAME (defaults to "all") could be a list of values
# from [files, logs, metadata]
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import argparse
import requests

from elasticsearch7 import Elasticsearch
from elasticsearch7.exceptions import NotFoundError

from elastic_metadata import ElasticsearchMetadata

import config_loader
import logger


config = config_loader.get_config()
logging = logger.get_logger(name='cleanup', filename='cleanup.log')
logging.propagate = False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('job_id', help='Job ID of Log Analyzer')
    parser.add_argument('-components',
        nargs='*',
        help='Components to delete. ["all", "files", "logs"]',
        default=['all']
    )
    try:
        args = parser.parse_args()
        job_id = args.job_id
        components = args.components

        status = clean(job_id, components)
    except Exception as e:
        logging.exception(f'Error while cleaning up {components} of job: {job_id}')

    if status:
        logging.info('Cleanup successful')
    else:
        logging.error('Cleanup failed')


def clean(job_id, components):
    status = True

    for component in components:
        logging.info(f'Starting to cleanup component: {component} of job: {job_id}')
        if component == 'all' or component == 'logs':
            status = status and clean_logs(job_id)

        if component == 'all' or component == 'files':
            status = status and clean_files(job_id)

        if component == 'all' or component == 'metadata':
            status = status and clean_metadata(job_id)

    return status


def clean_logs(job_id):
    """ Cleaning logs of the given job_id """
    global config

    try:
        ELASTICSEARCH_HOSTS = config['ELASTICSEARCH']['hosts']
        ELASTICSEARCH_TIMEOUT = config['ELASTICSEARCH']['timeout']
        ELASTICSEARCH_MAX_RETRIES = config['ELASTICSEARCH']['max_retries']
        es = Elasticsearch(ELASTICSEARCH_HOSTS,
                                timeout=ELASTICSEARCH_TIMEOUT,
                                max_retries=ELASTICSEARCH_MAX_RETRIES,
                                retry_on_timeout=True)

        es.indices.delete(job_id)

        return True
    except NotFoundError as e:
        logging.warning(f'Could not find logs for job: {job_id}')
        return True
    except Exception as e:
        logging.exception(f'Could not delete logs for job: {job_id}')

    return False


def clean_files(job_id):
    """ Cleaning files collected by file server for the "job_id" """
    global config

    FILE_SERVER_URL = config['FILE_SERVER_URL']
    url = f'{FILE_SERVER_URL}/{job_id}'
    try:
        response = requests.delete(url)
         # If the response was successful, no Exception will be raised
        response.raise_for_status()

        return True
    except requests.exceptions.HTTPError as http_err:
        status_code = http_err.response.status_code
        # Ignore NotFoundError
        if status_code == 404:
            logging.warning(f'Could not find files for job: {job_id}')
            return True

        logging.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logging.exception(f'Could not delete files for job: {job_id}')

    return False


def clean_metadata(job_id):
    """ Cleaning metadata for the given job_id """
    try:
        es_metadata = ElasticsearchMetadata()
        es_metadata.remove(job_id)

        return True
    except NotFoundError as e:
        logging.warning(f'Could not find metadata for job: {job_id}')
        return True
    except Exception as e:
        logging.exception(f'Could not delete metadata for job: {job_id}')

    return False


if __name__ == '__main__':
    main()