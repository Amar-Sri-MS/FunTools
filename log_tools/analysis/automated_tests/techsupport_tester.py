#!/usr/bin/env python3

#
# Tester script to handle testing Techsupport ingestion.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import logging
import os
import subprocess

from os.path import basename, dirname, isfile, join

import logger

from automated_tests.tester import Tester
from utils.cleanup import clean
from view.ingester import _get_log_id


FILE_PATH = os.path.abspath(os.path.dirname(__file__))

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
                if isfile(join(folder, file)) and is_techsupport(file):
                    logging.info(f'Found techsupport {file}')
                    techsupport_archives.append(f'{folder}/{file}')
                    break
            # Stop searching if we found TEST_COUNT number of archives
            if len(techsupport_archives) == TEST_COUNT:
                break
        except Exception as e:
            logging.exception('Error while finding techsupport archive')

    # Start ingestion
    for techsupport_archive in techsupport_archives:
        logging.info('-*-'*50)
        folder_name = basename(dirname(techsupport_archive))
        logging.info(f'{folder_name}, {techsupport_archive}')
        tester = TechsupportTester(folder_name, techsupport_archive)
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
    def __init__(self, job_id, mount_path):
        super().__init__()
        self.job_id = str(job_id).lower()
        self.log_id = None
        self.mount_path = mount_path

    def setup(self):
        """ Setting up the test ingestion """
        self.log_id = _get_log_id(self.job_id, 'techsupport')

    def run(self):
        """
        Running & monitoring the status of test ingestion.
        """
        logging.info('*'*100)
        logging.info(f'Ingesting: {self.job_id}')
        logging.info('*'*100)

        cmd = [f'{FILE_PATH}/../view/ingester.py', self.job_id,
               '--ingest_type', 'techsupport',
               '--techsupport_ingest_type', 'mount_path',
               '--log_path', str(self.mount_path),
               '--tags', 'automated_testing']
        logging.info(cmd)

        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            self.ingestion_status = True
        except subprocess.CalledProcessError as e:
            self.ingestion_status = False
            self.ingestion_status_msg = e.output

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