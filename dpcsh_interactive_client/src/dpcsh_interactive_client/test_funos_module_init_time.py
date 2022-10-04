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


def test_generate_html(logger):
    in_dir = f"{Path.home()}/Projects/Fng/FunTools/dpcsh_interactive_client/src/dpcsh_interactive_client"
    working_dir = f"{Path.home()}/Projects/Fng/FunTools/dpcsh_interactive_client/src"
    out_dir = f"{Path.home()}/tmp/test_gen"
    # temp_dir = f"{Path.home()}/tmp/test_gen"

    html_filename = generate_report(
        "funos_module_init_analysis.ipynb",
        in_dir=in_dir,
        out_dir=out_dir,
        execute=True,
        working_dir=in_dir,
        logger=logger,
        report_filename="funos_module_init_analysis.html"
    )

def main(logger):

    # INPUT_FILE_URL = "uartout0.0.txt"
    INPUT_FILE_URL = "http://palladium-jobs.fungible.local:8080/job/4297914/raw_file/odp/uartout0.0.txt"

    process_module_notif_init_data(
        INPUT_FILE_URL, logger=logger, working_dir=current_path
    )

    test_generate_html(logger)
    # load config file
    current_path = os.getcwd()
    print("current directory is: " + current_path)

if __name__ == "__main__":
    # logger.setLevel(logging.DEBUG)
    logger = _default_logger()
    main(logger)
