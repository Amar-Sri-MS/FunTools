#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility code to process funos module init time data

This is a test script for `funos_module_init_time.py`.
To run `PYTHONPATH` needs to be set to point where `dpcsh_interactive_client` modules are

`export PYTHONPATH=$WORKSPACE/FunTools/dpcsh_interactive_client/src/dpcsh_interactive_client:.`


Example:
    The following example runs the module init time analysis on the log file and plots the data:

        $ python3 funos_module_init_time_test.py

Todo:

"""

import os
from pathlib import Path

from funos_module_init_time import process_module_notif_init_data
from convert_nb import generate_report

from utils import DefaultLogger


def generate_html(in_dir, working_dir, out_dir, logger) -> str:
    """Generate html by running jupyter notebook"""

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


def gen_module_init_data(logger) -> None:

    # load config file, for testing
    current_path = os.getcwd()
    print("current directory is: " + current_path)

    # raw log file is passed through env
    input_file_url = os.environ["INPUT_FILE_URL"]

    logger.info(f"INPUT_FILE_URL: {input_file_url}")
    _, result = process_module_notif_init_data(
        input_file_url, logger=logger, working_dir=current_path
    )

    # result contains the metric for the chart
    # > `Perf stat result: {'longest_duration_ns': 2823587999.999998, 'longest_duration_id': 'rcnvme-init', 'total_duration_ns': 12637173858.0}`

    logger.info(f"Perf stat result: {result}")

    # Generate html report
    in_dir = f"{Path.home()}/Projects/Fng/FunTools/data_analysis/"
    working_dir = f"{Path.home()}/Projects/Fng/FunTools/dpcsh_interactive_client/src"
    out_dir = f"{Path.home()}/tmp/test_gen"

    html_filename = generate_html(in_dir, working_dir, out_dir, logger)

    logger.info(f"html_filename: {html_filename}")


if __name__ == "__main__":

    logger = DefaultLogger("module_init")
    logger.info("Starting module init time analysis")

    # prepare url from the FoD tag and set it to env variable
    DEFAULT_TEST_URL = "http://palladium-jobs.fungible.local:8080/job/4297914/raw_file/odp/uartout0.0.txt"

    # set os env INPUT_FILE_URL if not set
    if "INPUT_FILE_URL" not in os.environ:
        os.environ["INPUT_FILE_URL"] = DEFAULT_TEST_URL

    gen_module_init_data(logger)
