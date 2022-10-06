#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility functions for `data_analysis` module

Todo:

"""

import logging


class DefaultLogger:
    """Default logger class."""

    def __init__(self, name: str = "", log_level=logging.DEBUG):
        # module_name = __file__.rsplit('/', maxsplit=1)[-1].split('.')[-2]
        # my_logger = logging.getLogger(module_name)
        if name:
            self.my_logger = logging.getLogger(name)
        else:
            self.my_logger = logging.getLogger(__name__)
        self.my_logger.setLevel(log_level)
        logging.basicConfig()

    def info(self, log_txt):
        """Info"""
        self.my_logger.info(log_txt)

    def debug(self, log_txt):
        """Debug"""
        self.my_logger.info(log_txt)

    def error(self, log_txt):
        """Error"""
        self.my_logger.info("Error: %s", log_txt)

