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
from bs4 import BeautifulSoup
import pandas as pd
import json


from typing import Iterable, Any, List, Optional, Union, Callable, TextIO, Dict, Tuple


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


def get_defatult_sdk_dir() -> str:
    if "WORKSPACE" not in os.environ:
        assert False, "Set WORKSPACE environment variable or provide sdk_dir arg"
    return os.path.join(os.environ.get("WORKSPACE"), "FunSDK")


def get_default_api_doc_gen_dir(sdk_dir: str) -> str:
    assert sdk_dir, "Missing sdk_dir"
    return os.path.join(sdk_dir, "FunDoc/html/FunOS/headers")


def get_default_sdk_api(sdk_dir: str) -> str:
    assert sdk_dir, "Missing sdk_dir"
    return os.path.join(sdk_dir, "FunTools/ApiSummarizer/sdk_api.csv")


def get_file_base_name_without_ext(file_name):
    return os.path.splitext(os.path.basename(file_name))[0]


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

    Parameters
    ----------
    working_dir: str
        working directory
    file_name_url: str
        file name or url
    logger: DefaultLogger
        logger

    Returns
    -------
    str

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


def filter_line_with_pattern(lines: str, pattern: str, logger=DefaultLogger()) -> str:
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


def read_config(filename: str) -> dict:
    """Read config file in yaml format

    Parameters
    ----------
    file_name: str
        config file name

    Returns
    -------
    config: dict
        config dict

    """
    try:
        with open(filename, "r") as f:
            config = yaml.safe_load(f)
    except Exception as ex:
        print("Exception {}".format(ex))
        config = None

    assert config

    return config


def _check_report_type(report_type: str) -> Tuple[str, str, str]:
    """A helper function to process 'report_type'

    Parameters
    ----------
    report_type : str
        reporting type, either "coverage" or "document"

    Returns
    -------
    report_key, display_column_name, display_not_done_name: Tuple[str, str, str]
    """

    if report_type == "coverage":
        report_key = "coverage"
        display_column_name = "Coverage Status"
        display_not_done_name = "untested"
    elif report_type == "document":
        report_key = "documented"
        display_column_name = "Documentation Status"
        display_not_done_name = "undocumented"
    else:
        raise ValueError(f"Invalid report_type: {report_type}")

    return report_key, display_column_name, display_not_done_name


def _check_group_type(group_type: str, report_type: str, display_not_done_name: str):
    """A helper function to process 'group_tpye"""

    if group_type == "module":
        group = "dirname"
        col_list = [
            "Modules",
            "No. of all APIs",
            f"No. of {display_not_done_name} APIs",
            f"Per file API test {report_type} %",
        ]
    elif group_type == "file":
        group = "filename"
        col_list = [
            "Files",
            "No. of all APIs",
            f"No. of {display_not_done_name} APIs",
            f"Per file API test {report_type} %",
        ]
    else:
        raise ValueError(f"Invalid group_type: {group_type}")

    return group, col_list


def gen_per_group_summary_html(
    df_api: pd.DataFrame,
    output_html: str,
    group_type: str,
    report_type: str = "coverage",
    additional_note: List[str] = None,
    use_exclude_col: bool = False,
    return_df: bool = False,
) -> Union[None, pd.DataFrame]:
    """Generate per "group_type" summary html and save to file

    Parameters
    ----------
    df_api : pd.DataFrame
        SDK APIs
    output_html : str
        Output html file
    group_type : str
        Group type, "module" or "file"
    additional_note : List[str], optional
        Additional note, by default None
    exclude_files : List[str], optional
        Exclude files, by default None
    return_df : bool, optional
        Return df_api_summary, by default False

    Returns
    -------
    return_df : bool, optional
        Return df_api_summary, by default False
    """

    report_key, display_column_name, display_not_done_name = _check_report_type(
        report_type
    )

    group, col_list = _check_group_type(group_type, report_key, display_not_done_name)

    # copy df_api to df_api_summary
    _df_api = df_api.copy()

    _df_api["dirname"] = _df_api["filename"].apply(lambda x: os.path.dirname(x))

    # only include files where 'exclude' columns is False
    if use_exclude_col:
        _df_api = _df_api[_df_api["exclude"] == False]
        description = "filtered files"
    else:
        description = "all files"

    # group by behavior changed in pandas 2.0.0
    # https://pandas.pydata.org/docs/dev/whatsnew/v2.0.0.html#
    # DataFrame and DataFrameGroupBy aggregations (e.g. “sum”) with object-dtype columns no longer infer non-object dtypes for their results, explicitly call
    df_api_group = _df_api.groupby(group, as_index=False)['documented'].sum()
    df_group_proto_count = _df_api.groupby(group, as_index=False)["proto_name"].count()
    # merge proto_name from df_group_proto_count to df_api_group
    df_api_group = pd.merge(df_api_group, df_group_proto_count, on=group)

    df_api_group["percent_per_file"] = (
        df_api_group[report_key] / df_api_group["proto_name"] * 100
    )

    # sort based on percent_per_file column
    df_api_group = df_api_group.sort_values(by="percent_per_file", ascending=True)

    summary = f"SDK APIs {report_key} per {group_type} report ({description})"

    total_df_api = len(df_api)  # use the original df_api
    total_group_elements = len(df_api_group)
    total_df_api_group = sum(df_api_group["proto_name"])

    df_api_group[display_not_done_name] = (
        df_api_group["proto_name"] - df_api_group[report_key]
    )

    # use more readable column names
    df_api_group.rename(
        columns={
            "proto_name": "No. of all APIs",
            display_not_done_name: f"No. of {display_not_done_name} APIs",
            "dirname": "Modules",
            "filename": "Files",
            "percent_per_file": f"Per file API test {report_key} %",
            "exclude": f"Exclude for {report_key}",
        },
        inplace=True,
    )

    table_str = df_api_group[col_list].to_html(
        index=False,
        justify="center",
        float_format="{:.2f}".format,
    )

    html_header_str = f"<br>  <br> <h1> {summary} </h1> <br>"

    html_header_str += f"<h4> Total number of APIs: {total_df_api} </h4>"
    html_header_str += (
        f"<h4>       Number of APIs in this page: {total_df_api_group} </h4>"
    )
    html_header_str += (
        f"<h4> Total number of {group_type} in this page: {total_group_elements} </h4>"
    )

    if additional_note is not None:
        html_header_str += f"<br>"

        for note in additional_note:
            html_header_str += f"<h4> {note} </h4> <br>"

    html_footer_str = """<br> <br>"""

    # prepend html_header_stsr to html_str
    html_str = html_header_str + table_str + html_footer_str

    # save html_str to file
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_str)

    if return_df:
        return _df_api

    del _df_api
    return None


def gen_summary_html(
    df_api: pd.DataFrame,
    output_html: str,
    report_type: str = "coverage",
    additional_note: List[str] = None,
    failed_in_report_type_api_only: bool = False,
    use_exclude_col: bool = False,
) -> None:
    """Generate a summary html and save to file for test coverage or API documentation

    Parameters
    ----------
    df_api : pd.DataFrame
        SDK APIs
    output_html : str
        Output html file
    report_type : str, optional
        Report type either coverage or documentation, by default "coverage"
    additional_note : List[str], optional
        Additional note, by default None
    failed_in_report_type_api_only : bool, optional
        Only include failed in report type (coverage or documentation) APIs, by default False
    exclude_files : List[str], optional
        Exclude files, by default None

    Returns
    -------
    None

    """

    report_key, display_column_name, display_not_done_name = _check_report_type(
        report_type
    )

    # copy df_api to df_api_summary
    df_api_summary = df_api.copy()

    # coverage percentage
    cov_percent = df_api_summary[report_key].sum() / len(df_api_summary) * 100

    description = "all files"
    # only include files where 'exclude' columns is False
    if use_exclude_col:
        df_api_summary = df_api_summary[df_api_summary["exclude"] == False]
        # update coverage percentage when exclude_files is used
        cov_percent = df_api_summary[report_key].sum() / len(df_api_summary) * 100
        description = "filtered files"

    total_df_api = len(df_api_summary)
    total_files = len(df_api_summary["filename"].unique())

    if failed_in_report_type_api_only:
        df_api_summary = df_api_summary[df_api_summary[report_key] == False]
        description += f", {display_not_done_name} APIs only "

    summary = f"SDK APIs {report_type} ({description}): {cov_percent:.2f}%"
    num_not_done_api = len(df_api_summary[df_api_summary[report_key] == False])

    df_api_summary.rename(
        {
            "proto_name": "Function",
            report_key: display_column_name,
            "filename": "File",
        },
        axis=1,
        inplace=True,
    )

    table_str = df_api_summary[["Function", display_column_name, "File"]].to_html(
        index=False,
        justify="center",
        float_format="{:.2f}".format,
    )

    html_header_str = f"<br>  <br> <h1> {summary} </h1> <br>"

    html_header_str += f"<h4> Total number of APIs: {total_df_api} </h4>"

    html_header_str += f"<h4> Total number files: {total_files} </h4>"

    html_header_str += (
        f"<h4> Number of {display_not_done_name} APIs: {num_not_done_api} </h4> <br>"
    )

    # if NOTE_STR_1:
    #     html_header_str += f"<h4> {NOTE_STR_1} </h4> <br>"

    if additional_note is not None:
        html_header_str += f"<br>"

        for note in additional_note:
            html_header_str += f"<h4> {note} </h4> <br>"

    html_footer_str = """<br> <br>"""

    # prepend html_header_stsr to html_str
    html_str = html_header_str + table_str + html_footer_str

    # save html_str to file
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_str)

    del df_api_summary
