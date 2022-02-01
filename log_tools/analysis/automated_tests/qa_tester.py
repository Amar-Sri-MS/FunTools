#!/usr/bin/env python3

#
# Tester script to handle testing QA ingestion.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import logging
import os
import requests
import subprocess

import logger

from automated_tests.tester import Tester
from utils.cleanup import clean
from view.ingester import _get_log_id


FILE_PATH = os.path.abspath(os.path.dirname(__file__))

def main():
    # Setting up the logger.
    custom_logger = logger.get_logger(filename='qa_tester.log')

    # These are the initial focus points for testing log ingestion.
    NEEDED_TESTS = ['FS1600 Bundle Sanity', 'FS1600 HA sanity', 'FS800 Bundle Sanity', 'FS800 HA Sanity', 'VFabric Bundle Sanity']
    QA_BASE_URL = 'http://integration.fungible.local/api/v1/regression'

    # Get all the unarchived releases
    releases_response = requests.get(f'{QA_BASE_URL}/release_properties')
    releases_json = releases_response.json()
    releases = releases_json['data']
    unarchived_releases = [release for release in releases if release['archived'] == False]

    # Get all the types of tests for a release
    for release in unarchived_releases:
        release_id = release['id']
        release_name = release['release_train']
        tests_response = requests.get(f'{QA_BASE_URL}/catalog_execution_specification?primary_release_train={release_name}')
        tests_json = tests_response.json()
        tests = tests_json['data']

        # Filter out the needed tests (FS1600/FS800 Bundle Sanity, FS1600/FS800 HA Sanity)
        needed_tests = [test for test in tests if test['name'] in NEEDED_TESTS and test['paused'] != True]

        # Get the recent 5 runs of a test in a particular release
        for test in needed_tests:
            test_id = test['id']
            test_name = test['name']
            test_response = requests.get(f'{QA_BASE_URL}/release_catalog_executions?specification_id={test_id}&count=5')
            test_json = test_response.json()
            test_data = test_json['data']

            # Filter out the runs with result as PASSED or state as -30(ERROR)
            test_runs = [test_run for test_run in test_data if test_run['result'] == 'PASSED' or test_run['state'] == -30]
            if len(test_runs) > 0:
                logging.info('-*-'*50)
                logging.info(f'{release_name}, {test_id}: {test_name}')
                job_id = test_runs[0]['suite_executions'][0]['job_id']
                test_index = 0
                # HA Tests collects logs in the next test index.
                if test_name in ('FS1600 HA sanity', 'FS800 HA Sanity'):
                    test_index = 1
                tester = QATester(job_id, test_index)
                tester.start()
                logging.info('-*-'*50)
            else:
                logging.warning(f'Could not find any PASSED or ERROR run for test: {release_name}, {test_id}, {test_name}')

    logging.info('END OF TEST')
    logging.info('-'*150)

class QATester(Tester):
    """
    Class for testing QA ingestion into Log Analyzer.
    """

    def __init__(self, job_id, test_index=0):
        super().__init__()
        self.job_id = str(job_id)
        self.test_index = test_index
        self.ingest_type = 'qa'

    def setup(self):
        """ Setting up the test ingestion """
        self.log_id = _get_log_id(self.job_id,
                                  self.ingest_type,
                                  test_index=self.test_index)

    def run(self):
        """
        Running & monitoring the status of test ingestion.
        """
        logging.info('*'*100)
        logging.info(f'Ingesting: {self.job_id}')
        logging.info('*'*100)

        cmd = [f'{FILE_PATH}/../view/ingester.py', self.job_id,
               '--ingest_type', 'qa',
               '--test_index', str(self.test_index),
               '--tags', 'automated_testing']
        logging.info(cmd)

        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            self.ingestion_status = True
        except subprocess.CalledProcessError as e:
            self.ingestion_status = False
            self.ingestion_status_msg = str(e.output)

    def validate(self):
        """
        Validating the test ingestion after it is done.
        """
        logging.info(f'Validating..')
        logging.info(f'Ingestion Status: {self.ingestion_status}')
        self.status = self.ingestion_status

    def teardown(self):
        """
        Cleaning up the internal logs and the test ingestion.
        """
        if self.status:
            logging.info('Tearing down')
            clean(self.log_id, ['all'])


if __name__ == '__main__':
    main()