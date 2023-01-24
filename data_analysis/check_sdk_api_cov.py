#!/usr/bin/env python3

"""Check SDK APIs test code coverage

   Copyright (c) 2022 Fungible. All rights reserved.

    Preconditions
    -------------
    This script uses inputs of an api summary (--sdk_api) and a function coverage summary (--cov) generated by gcovr.

    Examples
    --------

    >>> python ./check_sdk_api_cov.py --sdk_api ../ApiSummarizer/sdk_api.csv --cov ./func_cov.csv --output_html ./sdk_api.html --output_csv ./sdk_api_updated.csv --output_dir .

    Test
    -----
    >>> pytest tests/test_check_sdk_api_cov.py -o log_cli=true

    Checks
    ------
    static check:
    >>> mypy ./check_sdk_api_cov.py

    format:
    >>> black ./check_sdk_api_cov.py

"""

"""
TODO
----

- update the generate table
- update the generated html with meta information

"""

import os
import argparse
import sys
from pathlib import Path
import json
from typing import Iterable, Any, List, Optional, Union, Callable, TextIO, Dict, Tuple
import yaml

try:
    import pandas as pd
except ImportError:
    print("{}: Import failed!".format(__file__))
    print("Install missing modules")
    print(">>> pip install pandas")
    sys.exit()

NOTE_STR_1 = "NOTE: gcovr does not generate function coverage summary for some functions that are defined in heaaders (i.e. static functions), around 13 percent of the of the total functions are not reported because of this)."


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk_api", type=str, help="SDK APIs csv file")

    parser.add_argument("--cov", type=str, help="Coverage data in csv file")
    parser.add_argument("--input_dir", type=str, default=".", help="Input directory")

    parser.add_argument("--output_dir", type=str, default=".", help="Output directory")

    parser.add_argument("--output_html", type=str, help="Output html file")
    parser.add_argument(
        "--output_untested_html",
        type=str,
        default="sdk_api_untested.html",
        help="Output html file for untested APIs",
    )
    parser.add_argument(
        "--output_untested_filtered_html",
        type=str,
        default="sdk_api_untested_filtered.html",
        help="Output html file for untested APIs with filtered files",
    )

    parser.add_argument("--output_csv", type=str, help="Output csv file")
    parser.add_argument(
        "--output_per_file_all_html",
        type=str,
        default="sdk_per_file_coverage_report_all.html",
        help="Per file coverage html file",
    )
    parser.add_argument(
        "--output_per_file_filtered_html",
        type=str,
        default="sdk_per_file_coverage_report_filtered.html",
        help="Per file coverage html file",
    )

    parser.add_argument(
        "--exclude_list",
        type=str,
        default="coverage/f1_sdk_coverage_config.yml",
        help="Exclude file list for coverage",
    )

    parser.add_argument(
        "--output_json", type=str, default="coverage.json", help="Output json file"
    )

    args = parser.parse_args()

    return args


def update_coverage_for_sdk_api(
    df_api: pd.DataFrame, df_cov: pd.DataFrame
) -> Tuple[pd.DataFrame, float]:
    """update coverage for SDK APIs
        Use df_cov to update df_api

    Parameters
    ----------
    df_api : pd.DataFrame
        SDK APIs
    df_cov : pd.DataFrame
        Coverage data

    Returns
    -------
    pd.DataFrame : updated df_api
    float : coverage percent

    """

    api_func_name = df_api["proto_name"].tolist()
    cov_func_name = df_cov["Function"].tolist()

    # add column to df_api
    df_api["coverage"] = False

    # NOTE: gcovr does not generate function coverage summary for some functions that are defined
    # in heaaders (i.e. static functions), around 13 % of the static inline functions are not
    # reported in the summary (regardless of their calling status)

    # update df_api coverage column
    for func_name in api_func_name:
        if func_name in cov_func_name:
            # check if df_cov "Call count" is "not called", then update coverage column
            if (
                df_cov.loc[df_cov["Function"] == func_name, "Call count"].values[0]
                != "not called"
            ):

                df_api.loc[df_api["proto_name"] == func_name, "coverage"] = True

    # coverage percentage
    cov_percent = df_api["coverage"].sum() / len(df_api) * 100

    return df_api, cov_percent


def gen_gcovr_json(
    df_api: pd.DataFrame,
    cov_percent: float,
    output_json: str,
) -> None:
    """Generate gcovr compatible json file

    Parameters
    ----------
    df_api : pd.DataFrame
        SDK APIs
    cov_percent : float
        Coverage percent
    output_html : str
        Output html file
    additional_note : List[str], optional
        Additional note, by default None

    Returns
    -------
    None

    """

    gcovr_dict = {
        "function_covered": int(df_api["coverage"].sum()),
        "function_total": len(df_api),
        "function_percent": cov_percent,
    }

    # save gcovr_dict to json file
    with open(output_json, "w") as f:
        json.dump(gcovr_dict, f, indent=4)


def gen_per_file_summary_html(
    df_api: pd.DataFrame,
    output_html: str,
    additional_note: List[str] = None,
    use_exclude_col: bool = False,
) -> None:
    """Prepare per file summary html and save to file

    Parameters
    ----------
    df_api : pd.DataFrame
        SDK APIs
    output_html : str
        Output html file
    additional_note : List[str], optional
        Additional note, by default None
    exclude_files : List[str], optional
        Exclude files, by default None

    Returns
    -------
    None
    """

    # copy df_api to df_api_summary
    _df_api = df_api.copy()

    df_api_group = _df_api.groupby("filename", as_index=False).sum()
    df_group_proto_count = _df_api.groupby("filename", as_index=False)[
        "proto_name"
    ].count()
    # merge proto_name from df_group_proto_count to df_api_group
    df_api_group = pd.merge(df_api_group, df_group_proto_count, on="filename")

    df_api_group["cov_percent_per_file"] = (
        df_api_group["coverage"] / df_api_group["proto_name"] * 100
    )

    # sort based on cov_percent_per_file column
    df_api_group = df_api_group.sort_values(by="cov_percent_per_file", ascending=True)

    # only include files where 'exclude' columns is False
    description = "all files"
    if use_exclude_col:
        df_api_group = df_api_group[df_api_group["exclude"] == False]
        description = "filtered files"

    summary = f"SDK APIs coverage per file report ({description})"

    total_df_api = len(df_api)  # use the original df_api
    total_files = len(df_api_group)

    df_api_group["untested"] = df_api_group["proto_name"] - df_api_group["coverage"]
    # use more readable column names
    df_api_group.rename(
        columns={
            "proto_name": "No. of all APIs",
            # "coverage": "No. of tested APIs",
            "untested": "No. of untested APIs",
            "filename": "Files",
            "cov_percent_per_file": "Per file API test coverage %",
            "exclude": "Exclude for Coverage",
        },
        inplace=True,
    )

    table_str = df_api_group[
        [
            "Files",
            "No. of all APIs",
            "No. of untested APIs",
            # "No. of tested APIs",
            "Per file API test coverage %",
        ]
    ].to_html(
        index=False,
        justify="center",
        float_format="{:.2f}".format,
    )

    html_header_str = f"<br>  <br> <h1> {summary} </h1> <br>"

    html_header_str += f"<h4> Total number of APIs: {total_df_api} </h4>"
    html_header_str += f"<h4> Total number files: {total_files} </h4>"

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

    del _df_api


def gen_summary_html(
    df_api: pd.DataFrame,
    output_html: str,
    additional_note: List[str] = None,
    untested_api_only: bool = False,
    use_exclude_col: bool = False,
) -> None:
    """Prepare summary html and save to file

    Parameters
    ----------
    df_api : pd.DataFrame
        SDK APIs
    output_html : str
        Output html file
    additional_note : List[str], optional
        Additional note, by default None
    untested_api_only : bool, optional
        Only include untested APIs, by default False
    exclude_files : List[str], optional
        Exclude files, by default None

    Returns
    -------
    None

    """

    # copy df_api to df_api_summary
    df_api_summary = df_api.copy()

    # coverage percentage
    cov_percent = df_api_summary["coverage"].sum() / len(df_api_summary) * 100

    description = "all files"
    # only include files where 'exclude' columns is False
    if use_exclude_col:
        df_api_summary = df_api_summary[df_api_summary["exclude"] == False]
        # update coverage percentage when exclude_files is used
        cov_percent = df_api_summary["coverage"].sum() / len(df_api_summary) * 100
        description = "filtered files"

    total_df_api = len(df_api_summary)
    total_files = len(df_api_summary["filename"].unique())

    if untested_api_only:
        df_api_summary = df_api_summary[df_api_summary["coverage"] == False]
        description += ", untested APIs only "

    summary = f"SDK APIs coverage ({description}): {cov_percent:.2f}%"
    num_untested_api = len(df_api_summary[df_api_summary["coverage"] == False])

    # use more readable column names
    df_api_summary.rename(
        columns={
            "proto_name": "Function",
            "coverage": "Coverage Status",
            "filename": "File",
            # "exclude": "Exclude for Coverage",
        },
        inplace=True,
    )

    table_str = df_api_summary[
        ["Function", "Coverage Status", "File"]
        # ["Function", "Coverage Status", "File", "Exclude for Coverage"]
    ].to_html(
        index=False,
        justify="center",
        float_format="{:.2f}".format,
    )

    html_header_str = f"<br>  <br> <h1> {summary} </h1> <br>"

    html_header_str += f"<h4> Total number of APIs: {total_df_api} </h4>"

    html_header_str += f"<h4> Total number files: {total_files} </h4>"

    html_header_str += f"<h4> Number of untested APIs: {num_untested_api} </h4> <br>"

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


def apply_exclude_filter(df_api: pd.DataFrame, exclude_file: str) -> pd.DataFrame:
    """Apply exclude filter to df_api

    Parameters
    ----------
    df_api : pd.DataFrame
        SDK APIs
    exclude_file : str
        Exclude file

    Returns
    -------
    pd.DataFrame
        SDK APIs with exclude filter applied

    """

    with open(exclude_file, "r") as f:
        config = yaml.safe_load(f)

    def _is_excluded(row, exclude_list):
        for exclude in exclude_list:
            if exclude in row["filename"]:
                return True
        return False

    df_api["exclude"] = df_api.apply(
        lambda row: _is_excluded(row, config["exclude_filenames"]), axis=1
    )

    return config


def get_file_base_name_without_ext(file_name):
    return os.path.splitext(os.path.basename(file_name))[0]


def main() -> None:
    """Main function"""

    args = _get_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    output_html = os.path.join(args.output_dir, args.output_html)
    output_untested_html = os.path.join(args.output_dir, args.output_untested_html)
    output_untested_filtered_html = os.path.join(
        args.output_dir, args.output_untested_filtered_html
    )

    output_per_file_all_html = os.path.join(
        args.output_dir, args.output_per_file_all_html
    )
    output_per_file_filtered_html = os.path.join(
        args.output_dir, args.output_per_file_filtered_html
    )
    output_json = os.path.join(args.output_dir, args.output_json)
    output_csv = (
        os.path.join(args.output_dir, args.output_csv)
        if args.output_csv is not None
        else None
    )
    exclude_list = os.path.join(args.input_dir, args.exclude_list)

    output_exclude_list = "{}.json".format(
        get_file_base_name_without_ext(args.exclude_list)
    )
    output_exclude_list = os.path.join(args.output_dir, output_exclude_list)

    # read csv
    df_api = pd.read_csv(args.sdk_api)
    df_cov = pd.read_csv(args.cov)

    df_api, cov_percent = update_coverage_for_sdk_api(df_api, df_cov)

    # apply exlude filter
    exclude_config = apply_exclude_filter(df_api, exclude_list)

    # save exclude config to json
    with open(output_exclude_list, "w") as f:
        json.dump(exclude_config, f, indent=4)

    # save df_api to csv
    if output_csv:
        df_api.to_csv(output_csv)

    # save df_api to html
    gen_summary_html(df_api, output_html)
    gen_summary_html(df_api, output_untested_html, untested_api_only=True)
    gen_summary_html(
        df_api,
        output_untested_filtered_html,
        untested_api_only=True,
        use_exclude_col=True,
    )

    # per file summary
    gen_per_file_summary_html(df_api, output_per_file_all_html, use_exclude_col=False)
    gen_per_file_summary_html(
        df_api, output_per_file_filtered_html, use_exclude_col=True
    )

    gen_gcovr_json(df_api, cov_percent, output_json)

    print(f"SDK APIs coverage:              {cov_percent:.2f}%")
    print(f"SDK exclusion list:    {output_exclude_list}")
    print()
    print(f"Saving summary to html file:    {output_html}")
    print(f"Saving per file (all) summary to html file:    {output_per_file_all_html}")
    print(
        f"Saving per file (filtered) summary to html file:    {output_per_file_filtered_html}"
    )
    print(f"Saving summary to csv file:     {output_csv}")


if __name__ == "__main__":
    main()
