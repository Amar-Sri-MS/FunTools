#!/usr/bin/env python3

#
# Cleaning all the files collected for all the
# successful and unarchived jobs whose logs are
# deleted by the Elasticsearch's Index Lifecycle
# Management Policy.
#
# This script can be called by any cron job to
# periodically check and remove files and metadata
# after the retetion period.
#
# Usage:
# python cleanup.py
#
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import os

from elasticsearch7 import Elasticsearch

from utils.cleanup import clean
from elastic_metadata import ElasticsearchMetadata
import config_loader
import logger


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
FILES_DIRECTORY = os.path.abspath(os.path.join(CURRENT_DIR, 'files/analytics'))
config = config_loader.get_config()
logging = logger.get_logger(name='cleanup', filename='cleanup.log')
logging.propagate = False

def main():
    ELASTICSEARCH_HOSTS = config['ELASTICSEARCH']['hosts']
    es = Elasticsearch(ELASTICSEARCH_HOSTS)
    es_metadata = ElasticsearchMetadata()

    indices = es.cat.indices(
        index='log_*',
        h='index',
        format='json',
        s='creation.date:desc'
    )
    log_ids = [index['index'] for index in indices]

    # List of the subdirectories inside the files directory
    dirs = next(os.walk(FILES_DIRECTORY))[1]

    for dirname in dirs:
        # Only the logs which are deleted from Elasticsearch after
        # the retension policy
        if dirname not in log_ids:
            metadata = es_metadata.get(dirname)
            # We would want to keep the files for failed ingestion
            # and archived logs
            if (metadata and
                metadata.get('ingestion_status') == 'COMPLETED' and
                not metadata.get('is_archived', True)):

                logging.info(f'Cleaning files and metadata for job: {dirname}')
                status = clean(dirname, ['files', 'metadata'])
                if not status:
                    logging.error(f'Cleaning was not successful')


if __name__ == '__main__':
    main()