#!/usr/bin/env python3
"""Utility code to process funos module init time data"""


import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Tuple
import yaml
import json
import os
import requests
import errno
import re
from pathlib import Path

import logging

try:
    from dpcsh_interactive_client.funos_module_init_time import *
    from dpcsh_interactive_client.convert_nb import generate_report, get_module_info

except ImportError:
    from convert_nb import generate_report, get_module_info
    from funos_module_init_time import *


class _default_logger:
    def __init__(self):
        pass

    def info(self, str):
        print(str)

    def debug(self, str):
        print(str)

    def error(self, str):
        print("Error: {}".format(str))


def generate_html(in_dir, working_dir, out_dir, logger):

    html_filename = generate_report(
        "funos_module_init_analysis.ipynb",
        in_dir=in_dir,
        out_dir=out_dir,
        execute=True,
        working_dir=in_dir,
        logger=logger,
        report_filename="funos_module_init_analysis.html",
    )

    return html_filename


def gen_module_init_data(logger):

    # load config file, for testing
    current_path = os.getcwd()
    print("current directory is: " + current_path)

    # raw log file is passed through env
    INPUT_FILE_URL = os.environ["INPUT_FILE_URL"]

    print("INPUT_FILE_URL: {}".format(INPUT_FILE_URL))
    df, result = process_module_notif_init_data(
        INPUT_FILE_URL, logger=logger, working_dir=current_path
    )

    """
    result contains the metric for the chart

    > `Perf stat result: {'longest_duration_ns': 2823587999.999998, 'longest_duration_id': 'rcnvme-init', 'total_duration_ns': 12637173858.0}`
    """

    logger.info("Perf stat result: {}".format(result))

    """Generate html report"""
    in_dir = f"{Path.home()}/Projects/Fng/FunTools/dpcsh_interactive_client/src/dpcsh_interactive_client"
    working_dir = f"{Path.home()}/Projects/Fng/FunTools/dpcsh_interactive_client/src"
    out_dir = f"{Path.home()}/tmp/test_gen"

    html_filename = generate_html(in_dir, working_dir, out_dir, logger)

    logger.info("html_filename: {}".format(html_filename))


if __name__ == "__main__":
    # logger.setLevel(logging.DEBUG)
    logger = _default_logger()

    # prepare url from the FoD tag and set it to env variable
    os.environ[
        "INPUT_FILE_URL"
    ] = "http://palladium-jobs.fungible.local:8080/job/4297914/raw_file/odp/uartout0.0.txt"

    gen_module_init_data(logger)
