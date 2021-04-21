#!/usr/bin/env python3

#
# Logging module for the Log Analyzer Server.
#
# This lets us add handlers and filters at one place.
#
# Usage:
# logger.get_logger(NAME, FILE_NAME)
# Where, NAME is to unique identify the logger
# FILE_NAME is the name of file to store the logs
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import glob
import logging
import logging.handlers
import os
import requests

import config_loader


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
LOGS_DIRECTORY = os.path.abspath(os.path.join(CURRENT_DIR, 'logs'))
DEFAULT_LOG_FORMAT = '%(asctime)s %(module)s %(levelname)s %(message)s'
MEGABYTE = 1000000

config = config_loader.get_config()


def get_logger(name=None, filename=None):
    """
    Get custom logger with StreamHandler and FileHandler
    if "filename" is given and with the default log format.
    """
    # Get the default logger
    custom_logger = logging.getLogger(name)

    # Always register a stderr handler.
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt=DEFAULT_LOG_FORMAT)

    handler.setFormatter(formatter)
    custom_logger.addHandler(handler)
    custom_logger.setLevel(logging.INFO)

    if filename:
        os.makedirs(LOGS_DIRECTORY, exist_ok=True)
        path = os.path.join(LOGS_DIRECTORY, filename)

        # Also route to rotating file if requested.
        # Automatically write and rotate logs.
        handler = logging.handlers.RotatingFileHandler(path,
                                                       maxBytes=100 * MEGABYTE,
                                                       backupCount=10)
        handler.setFormatter(formatter)
        custom_logger.addHandler(handler)

    return custom_logger


def backup_ingestion_logs(log_id):
    """
    Backing up the logs collected during ingestion
    of the given "log_id".

    Sending the logs to FILE_SERVER at the end of ingestion.
    """
    try:
        FILE_SERVER_URL = config['FILE_SERVER_URL']
        url = f'{FILE_SERVER_URL}/{log_id}/file'

        pattern = os.path.join(LOGS_DIRECTORY, f'{log_id}.log*')
        log_files = glob.glob(pattern)

        files = list()

        for file in log_files:
            filename = os.path.basename(file)
            files.append(
                (filename, (filename, open(file, 'rb')))
            )

        if len(files) > 0:
            response = requests.post(url, files=files)
            response.raise_for_status()
            logging.info(f'Log files for {log_id} uploaded!')

            # Removing the collected log files
            for file in log_files:
                os.remove(file)

    except Exception as e:
        logging.exception(f'Uploading log files for {log_id} failed.')
