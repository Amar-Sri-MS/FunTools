#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility functions for `data_analysis` module

Todo:

"""

import logging
import yaml


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


def save_yml_log_with_input_file_url(file_name: str, input_file_url: str) -> None:
    """Save yml config file with input_file_url entry in.
    This config file is used for passing config to the notebook.
    Note that this function overwrites the current config file if exists.

    Parameters
    ----------
    file_name: str
        file name for config yml file
    input_file_url: str
        config entry

    Returns
    -------

    """

    config = {}
    config["file_names"] = {"input_file_url": input_file_url}

    # save to yml file
    with open(file_name, "w", encoding="utf-8") as outfile:
        yaml.dump(config, outfile, default_flow_style=False)


def get_input_file_url(file_name: str = "funos_module_init_analysis_config.yml") -> str:
    """Get input file url

    Parameters
    ----------
    file_name: str
        input file name

    Returns
    -------
    str
        input file url

    """
    # load yml file

    with open(file_name, "r", encoding="utf-8") as infile:
        config = yaml.load(infile, Loader=yaml.FullLoader)

    return config["file_names"]["input_file_url"]
