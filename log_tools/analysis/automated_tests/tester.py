#!/usr/bin/env python3

#
# Tester script to handle generic operations like
# setup & teardown.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import datetime
import logging

from elasticsearch7 import Elasticsearch

import config_loader
from utils.mail import Mail

config = config_loader.get_config()


class Tester(object):
    """
    Base class for all testing scripts to test Log Analyzer.
    """

    def __init__(self):
        # Unqiue list of log_id which will be used to reference
        # the test ingestion.
        self.log_id = None
        self.job_id = None

        self.ingest_type = None

        # Test Status. Will be updated after validation.
        self.ingestion_status = False
        self.ingestion_status_msg = None
        self.status = False
        self.status_msg = None

        # Notifier settings
        self.notify_on_success = False
        self.email_watchers = ['sourabh.jain@fungible.com']
        self.email_cc_watchers = ['tools-pals@fungible.com']

        # Elasticsearch client
        ELASTICSEARCH_HOSTS = config['ELASTICSEARCH']['hosts']
        ELASTICSEARCH_TIMEOUT = config['ELASTICSEARCH']['timeout']
        ELASTICSEARCH_MAX_RETRIES = config['ELASTICSEARCH']['max_retries']
        self.es = Elasticsearch(ELASTICSEARCH_HOSTS,
                                timeout=ELASTICSEARCH_TIMEOUT,
                                max_retries=ELASTICSEARCH_MAX_RETRIES,
                                retry_on_timeout=True)

    def setup(self):
        """ Setting up the test ingestion """
        pass

    def start(self):
        """
        Starting the tester.
        """
        self.setup()

        # Skipping tests if the log_id already exists.
        if self.es.indices.exists(self.log_id):
            logging.warning(f'Skipping tests on {self.log_id}. The log_id already exists.')
            return

        try:
            self.run()
            self.validate()
            self.teardown()
        finally:
            self.notify()
            self.collect_status()

    def run(self):
        """
        Running & monitoring the status of test ingestion.
        """
        raise NotImplementedError()

    def validate(self):
        """
        Validating the test ingestion after it is done.
        """
        pass

    def teardown(self):
        """
        Cleaning up the internal logs and the test ingestion.
        """
        pass

    def notify(self):
        """ Notifying about the test result """

        # Check to notify on success.
        if self.status and not self.notify_on_success:
            return
        try:
            logging.info('Notifying users about the test result.')

            test_status = 'SUCCESSFUL' if self.status else 'FAILED'
            subject = f'Automated testing of {self.log_id} on Log Analyzer: {test_status}'
            body = f"""
                Automated testing of {self.log_id} on Log Analyzer: {test_status}
                Log Analyzer Dashboard: {config['LOG_VIEW_BASE_URL'].replace('LOG_ID', self.log_id)}/dashboard

                Ingestion Status: {self.ingestion_status}

                Full log URL: {config['FILE_SERVER_URL']}/{self.log_id}/file/{self.log_id}.log

                Ingestion Output:
                {self.ingestion_status_msg}
            """

            status = Mail(self.email_watchers, subject, body, self.email_cc_watchers)
            if not status:
                logging.error(f'Failed to send email to {self.email_watchers} & {self.email_cc_watchers}')
        except:
            logging.exception(f'Failed to send email to {self.email_watchers} & {self.email_cc_watchers}')

    def collect_status(self):
        """
        Storing the test result status for historical analysis.
        """
        now = datetime.datetime.utcnow()
        INDEX_NAME = f'testdata_{now.year}_{now.month}'

        try:
            data = {
                '@timestamp': now,
                'logID': self.log_id,
                'job_id': self.job_id,
                'ingest_type': self.ingest_type,
                'ingestion_status': self.ingestion_status,
                'ingestion_msg': str(self.ingestion_status_msg),
                'validation_status': self.status,
                'validation_msg': str(self.status_msg)
            }

            result = self.es.index(INDEX_NAME, data)

            return result
        except Exception as e:
            logging.exception('Error occurred during collecting test status.')