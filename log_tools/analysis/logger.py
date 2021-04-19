#!/usr/bin/env python3

#
# Logging module for the Log Analyzer Server.
#
# This lets us add handlers and filters at one place.
#
# Usage:
# logger.setup(FILE_NAME)
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import logging
import logging.handlers
import os


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
LOGS_DIRECTORY = os.path.abspath(os.path.join(CURRENT_DIR, 'logs'))
DEFAULT_LOG_FORMAT = '%(asctime)s %(module)s %(levelname)s %(message)s'
MEGABYTE = 1000000


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
