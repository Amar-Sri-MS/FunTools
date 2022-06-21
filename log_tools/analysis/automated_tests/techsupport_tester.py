#!/usr/bin/env python3

#
# Tester script to handle testing Techsupport ingestion.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import logging
import os
import requests
import subprocess
import time

from os.path import basename, dirname, isfile, join

import config_loader
import logger

from automated_tests.tester import Tester
from utils.archive_extractor import is_archive
from utils.cleanup import clean
from view.ingester import _get_log_id


FILE_PATH = os.path.abspath(os.path.dirname(__file__))
SCRIPT_BASE_PATH = os.path.dirname(FILE_PATH)

config = config_loader.get_config()


def main():
    # Setting up the logger.
    custom_logger = logger.get_logger(filename='techsupport_tester.log')

    LOGS_DIRECTORY = '/project/users/bugbits'
    TEST_COUNT = 3

    # List all the directories sorted by latest creation date.
    # folders = glob.glob(f'{LOGS_DIRECTORY}/*')
    folders = [f.path for f in os.scandir(LOGS_DIRECTORY) if f.is_dir()]
    folders.sort(key=os.path.getmtime, reverse=True)

    # Loop over them and search if they contain a techsupport archive
    techsupport_archives = list()
    for folder in folders:
        logging.info(f'Looking for techsupport in {folder}')
        try:
            for file in os.listdir(folder):
                file_path = join(folder, file)
                if (isfile(file_path) and
                    is_techsupport(file) and
                    is_archive(file_path)):
                    logging.info(f'Found techsupport {file}')
                    techsupport_archives.append(file_path)
                    break
            # Stop searching if we found TEST_COUNT number of archives
            if len(techsupport_archives) == TEST_COUNT:
                break
        except Exception as e:
            logging.exception('Error while finding techsupport archive')

    if len(techsupport_archives) == 0:
        logging.error(f'Could not find any techsupport archive in: {LOGS_DIRECTORY}')

    # Start ingestion
    for test_index in range(len(techsupport_archives)):
        techsupport_archive = techsupport_archives[test_index]
        ingest_type = 'techsupport'
        # Test the upload API for the last techsupport archive
        # if it is less than the MAX size.
        is_archive_size_within_limit = os.stat(techsupport_archive).st_size <= config["MAX_CONTENT_LENGTH"]
        is_last_index = test_index == len(techsupport_archives)-1
        if is_last_index and is_archive_size_within_limit:
            ingest_type = 'upload'

        logging.info('-*-'*50)
        folder_name = basename(dirname(techsupport_archive))
        logging.info(f'{ingest_type}, {folder_name}, {techsupport_archive}')
        tester = TechsupportTester(folder_name, ingest_type, techsupport_archive)
        tester.start()
        logging.info('-*-'*50)

    logging.info('END OF TEST')
    logging.info('-'*150)


def is_techsupport(file):
    """ Techsupport archive can be named differently if collected manually. """
    TECHSUPPORT_ARCHIVE_NAMES = ['techsupport', 'tech-support', 'tech_support', 'cs-logs']
    if any(archive_name in file for archive_name in TECHSUPPORT_ARCHIVE_NAMES):
        return True
    return False


class TechsupportTester(Tester):
    """
    Class for testing Techsupport ingestion into Log Analyzer.
    """
    def __init__(self, job_id, ingest_type, file_path):
        super().__init__()
        self.job_id = str(job_id).lower()
        self.file_path = file_path
        self.ingest_type = 'techsupport'
        self.techsupport_ingest_type = ingest_type

    def setup(self):
        """ Setting up the test ingestion """
        self.log_id = _get_log_id(self.job_id, self.ingest_type)

    def run(self):
        """
        Running & monitoring the status of test ingestion.
        """
        logging.info('*'*100)
        logging.info(f'Ingesting: {self.job_id}')
        logging.info('*'*100)

        if self.techsupport_ingest_type == 'upload':
            try:
                URL = f'{config["LOG_ANALYZER_BASE_URL"]}/upload_file'
                headers = {
                    'Accept': 'application/json'
                }
                data = {
                    'job_id': self.job_id,
                    'tags': 'automated_testing',
                    'submitted_by': 'sourabh.jain@fungible.com'
                }
                file_name = os.path.basename(self.file_path)
                files = {
                    'file': (file_name, open(self.file_path, 'rb'))
                }
                response = requests.post(URL,
                                         headers=headers,
                                         data=data,
                                         files=files)
                response.raise_for_status()
                response_data = response.json()
                if response_data.get('ingestion_status') == 'FAILED':
                    self.ingestion_status = False
                    self.ingestion_status_msg = response_data.get('ingestion_error')
                    return

                LOG_ID = response_data.get('log_id')
                STATUS_URL = f'{config["LOG_ANALYZER_BASE_URL"]}/ingest/{LOG_ID}/status'
                while True:
                    # Wait for 5 minutes and check the status
                    time.sleep(300)
                    response = requests.get(STATUS_URL)
                    response_data = response.json()
                    if response_data.get('ingestion_status') == 'FAILED':
                        self.ingestion_status = False
                        self.ingestion_status_msg = response_data.get('ingestion_error')
                        break
                    elif response_data.get('ingestion_status') in ['COMPLETED', 'PARTIAL']:
                        self.ingestion_status = True
                        break
            except Exception as e:
                self.ingestion_status = False
                self.ingestion_status_msg = str(e)
                logging.exception('Could not start ingestion via upload')
        else:
            cmd = [f'{SCRIPT_BASE_PATH}/view/ingester.py', self.job_id,
                '--ingest_type', 'techsupport',
                '--techsupport_ingest_type', 'mount_path',
                '--log_path', str(self.file_path),
                '--tags', 'automated_testing',
                '--ignore_size_restrictions']
            logging.info(cmd)

            try:
                out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                self.ingestion_status = True
            except subprocess.CalledProcessError as e:
                self.ingestion_status = False
                self.ingestion_status_msg = str(e.output)
                logging.exception('Could not start ingestion')

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