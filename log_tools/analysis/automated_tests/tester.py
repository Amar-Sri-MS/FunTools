#!/usr/bin/env python3

#
# Tester script to handle generic operations like
# setup & teardown.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

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
        self.es = Elasticsearch(ELASTICSEARCH_HOSTS)

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

        self.run()
        self.validate()
        self.teardown()
        self.notify()

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

        status = Mail(self.email_watchers, subject, body)
        if not status:
            logging.error(f'Failed to send email to {self.email_watchers}')