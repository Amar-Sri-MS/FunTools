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

from utils import DefaultLogger, save_yml_log_with_input_file_url


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


def gen_module_init_data(
    in_dir, working_dir, out_dir, input_file_url, logger
) -> Tuple[str, dict]:
    """Generate module init data

    Parameters
    ----------
    in_dir: str
        notebook directory
    working_dir: str
        directory to run notebook, so that we can pick up the data files
    out_dir: str
        directory for generate file
    input_file_url: str
        url of the input file
    logger: logger
        logger

    Returns
    -------
    html_filename: str
        generate html filename
    result: dict
        result dict
    """

    # prepare config file for note book
    # save config file to the out_dir, which is a temp directory
    config_file = os.path.join(out_dir, "funos_module_init_analysis_config.yml")
    save_yml_log_with_input_file_url(config_file, input_file_url, out_dir)

    os.environ["FUNOS_MODULE_INIT_ANALYSIS_CONFIG_FILE"] = config_file
    logger.info("config_file: " + config_file)

    # load config file, for testing
    current_path = os.getcwd()
    logger.info("current directory is: " + current_path)

    logger.info(f"INPUT_FILE_URL: {input_file_url}")
    # setting working_dir for `process_module_notif_init_data` as `out_dir
    # so that the data files are generated in the `out_dir`
    df, result = process_module_notif_init_data(
        input_file_url, logger=logger, working_dir=out_dir
    )

    # result contains the metric for the chart
    # > `Perf stat result: {'longest_duration_ns': 2823587999.999998, 'longest_duration_id': 'rcnvme-init', 'total_duration_ns': 12637173858.0}`

    logger.info(f"Perf stat result: {result}")

    html_filename = _generate_html(in_dir, working_dir, out_dir, logger)

    logger.info(f"html_filename: {html_filename}")

    dump_df_to_files(df, out_dir)

    return html_filename, result


def main(logger) -> None:
    """Main entry point"""

    # note book directory
    in_dir = f"{Path.home()}/Projects/Fng/FunTools/data_analysis/"

    # directory for generate file
    out_dir = f"{Path.home()}/tmp/test_gen"

    # directory to run notebook, so that we can pick up the data files
    working_dir = out_dir

    input_file_url = "http://palladium-jobs.fungible.local:8080/job/5862646/raw_file/odp/uartout0.0.txt"

    html_name, result = gen_module_init_data(
        in_dir, working_dir, out_dir, input_file_url, logger
    )
    logger.info("html_name: " + html_name)
    logger.info("result: " + str(result))


if __name__ == "__main__":

    logger = DefaultLogger("module_init")
    logger.info("Starting module init time analysis")

    main(logger)
