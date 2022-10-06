#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility code to process funos module init time data

This is a test script for `funos_module_init_time.py`.
To run `PYTHONPATH` needs to be set to point where `dpcsh_interactive_client` modules are

```
export PYTHONPATH=$WORKSPACE/FunTools/data_analysis:$PYTHONPATH
```


Example:
    The following example runs the module init time analysis on the log file and plots the data:

        $ python3 funos_module_init_time_test.py

Todo:

"""

import os
from pathlib import Path
from typing import Any, Tuple, Union

from funos_module_init_time import process_module_notif_init_data, dump_df_to_files
from convert_nb import generate_report

from utils import DefaultLogger


def _generate_html(in_dir, working_dir, out_dir, logger) -> str:
    """Generate html by running jupyter notebook"""

    html_filename = generate_report(
        "funos_module_init_analysis.ipynb",
        in_dir=in_dir,
        out_dir=out_dir,
        execute=True,
        working_dir=working_dir,
        logger=logger,
        report_filename="funos_module_init_analysis.html",
    )

    return html_filename


def gen_module_init_data(in_dir, working_dir, out_dir, logger) -> Tuple[str, dict]:
    """Generate module init data

    Parameters
    ----------
    logger: logger
        logger
    in_dir: str
        notebook directory
    out_dir: str
        directory for generate file
    execute: bool
        to run notebook or not
    working_dir: str
        directory to run notebook, so that we can pick up the data files

    Returns
    -------
    html_filename: str
        generate html filename
    result: dict
        result dict
    """

    # load config file, for testing
    current_path = os.getcwd()
    logger.info("current directory is: " + current_path)

    # raw log file is passed through env
    input_file_url = os.environ["INPUT_FILE_URL"]

    logger.info(f"INPUT_FILE_URL: {input_file_url}")
    df, result = process_module_notif_init_data(
        input_file_url, logger=logger, working_dir=current_path
    )

    # result contains the metric for the chart
    # > `Perf stat result: {'longest_duration_ns': 2823587999.999998, 'longest_duration_id': 'rcnvme-init', 'total_duration_ns': 12637173858.0}`

    logger.info(f"Perf stat result: {result}")

    html_filename = _generate_html(in_dir, working_dir, out_dir, logger)

    logger.info(f"html_filename: {html_filename}")

    dump_df_to_files(df)

    return html_filename, result


def main(logger) -> None:
    """Main entry point"""

    # note book directory
    in_dir = f"{Path.home()}/Projects/Fng/FunTools/data_analysis/"

    # directory to run notebook, so that we can pick up the data files
    working_dir = in_dir

    # directory for generate file
    out_dir = f"{Path.home()}/tmp/test_gen"

    html_name, result = gen_module_init_data(in_dir, working_dir, out_dir, logger)
    logger.info("html_name: " + html_name)
    logger.info("result: " + str(result))


if __name__ == "__main__":

    logger = DefaultLogger("module_init")
    logger.info("Starting module init time analysis")

    # prepare url from the FoD tag and set it to env variable
    DEFAULT_TEST_URL = "http://palladium-jobs.fungible.local:8080/job/4297914/raw_file/odp/uartout0.0.txt"

    # set os env INPUT_FILE_URL if not set
    if "INPUT_FILE_URL" not in os.environ:
        os.environ["INPUT_FILE_URL"] = DEFAULT_TEST_URL

    main(logger)
