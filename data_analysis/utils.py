#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility functions for `data_analysis` module

Todo:

"""

import logging
import yaml
import requests
import os
import re


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


def save_yml_log_with_input_file_url(
    file_name: str, input_file_url: str, out_dir: str
) -> None:
    """Save yml config file with input_file_url entry in.
    This config file is used for passing config to the notebook.
    Note that this function overwrites the current config file if exists.

    Parameters
    ----------
    file_name: str
        file name for config yml file
    input_file_url: str
        config entry
    out_dir: str
        output directory

    Returns
    -------

    """

    config = {}
    config["file_names"] = {"input_file_url": input_file_url}
    config["out_dir"] = out_dir

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


def read_from_file_or_url(
    working_dir: str, file_name_url: str, logger=DefaultLogger()
) -> str:
    """Read from file or url
    if it is file, `working_dir` is expected to be the directory where the file is located

    """
    if file_name_url.startswith("http"):
        logger.info(f"Use file from URL: {file_name_url}")
        try:
            response = requests.get(file_name_url, timeout=10)
            lines = response.text
        except requests.exceptions.HTTPError as ex:
            logger.error(f"Http error: {ex}")
            raise ex
        except requests.exceptions.ConnectionError as ex:
            logger.error(f"Error Connecting: {ex}")
            raise ex
        except requests.exceptions.Timeout as ex:
            logger.error(f"Timeout Error: {ex}")
            raise ex
        except requests.exceptions.RequestException as ex:
            logger.error(f"Exception {ex}")
            raise ex
    else:
        file_name = os.path.join(working_dir, file_name_url)
        logger.info(f"Use file this path {file_name}")
        try:
            with open(file_name, encoding="utf-8") as f:
                lines = f.read()
        except FileNotFoundError as ex:
            logger.error(f"File not found: {file_name}")
            raise ex
    return lines

def remove_timestamps_from_log(lines: str) -> str:
    """Remove timestamps from log

    remove time stamp from each line
    > [1664319485.206378 0.0.0] pci_early: performing i2c/MUD initialization

    Parameters
    ----------
    lines: str
        lines to parse

    Returns
    -------
    filtered_lines: str
        lines with timestamp removed
    """

    lines = re.sub(r"\[.*\] ", "", lines)

    return lines

def filter_line_with_pattern(
    lines: str, pattern: str, logger=DefaultLogger()
) -> str:
    """Filter based on the marker and create an output with json format by adding the ending "}"

    Parameters
    ----------

    lines: str
        lines to parse
    marker_type: str
        marker type string, "module_init", "notif"

    Returns
    -------
    filtered_lines: str
        filtered lines in json format

    Raises
    ------
    AssertionError
        if regex does not match
    """

    try:
        filtered_lines = re.search(pattern, lines, re.DOTALL).group(1)
        # filtered_lines += "}"  # add back the end marker

    except AttributeError as ex:
        logger.error(f"Read result : {lines}")
        logger.error(f"Error parsing log file: {ex}")
        raise ex

    return filtered_lines
    # return json.loads(filtered_lines)
