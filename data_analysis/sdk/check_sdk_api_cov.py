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

import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from utils.utils import *

NOTE_STR_1 = "NOTE: gcovr does not generate function coverage summary for some functions that are defined in heaaders (i.e. static functions), around 13 percent of the of the total functions are not reported because of this)."


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk_api", type=str, help="SDK APIs csv file")

    parser.add_argument("--cov", type=str, help="Coverage data in csv file")
    parser.add_argument("--input_dir", type=str, default=".", help="Input directory")

    parser.add_argument("--output_dir", type=str, help="Output directory")

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
        "--output_per_module_all_html",
        type=str,
        default="sdk_per_module_coverage_report_all.html",
        help="Per module coverage html file",
    )
    parser.add_argument(
        "--output_per_module_filtered_html",
        type=str,
        default="sdk_per_module_coverage_report_filtered.html",
        help="Per module coverage html file",
    )

    parser.add_argument(
        "--exclude_list",
        type=str,
        default="configs/f1_sdk_coverage_config.yml",
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
    cov_func_name = df_cov["Function (File:Line)"].tolist()

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
                df_cov.loc[
                    df_cov["Function (File:Line)"] == func_name, "Call count"
                ].values[0]
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

    # use the filter_key, which is thek key of the list in the config file, to filter out
    # APIs and files, wich are in target_column_name columns of the df_api
    # list of [filter_key, target_column_name]
    exclude_configs = [
        ["exclude_filenames", "filename"],
        ["exclude_api_patterns", "proto_name"],
    ]

    def _get_config(exclude_file, exclude_keys):
        """load config and merge with common_config if exists"""
        with open(exclude_file, "r") as f:
            config = yaml.safe_load(f)
        if "common_config" in config:
            # use the same path as the exclude_file
            base_dir = os.path.dirname(exclude_file)
            common_file = os.path.join(base_dir, config["common_config"])
            with open(common_file, "r") as f:
                common_config = yaml.safe_load(f)

            for key, _ in exclude_keys:
                if key in common_config:
                    config[key] = common_config[key] + config[key]

        return config

    config = _get_config(exclude_file, exclude_configs)

    def _is_excluded(row, exclude_configs):
        """util function to check if a row should be excluded"""
        for key, target in exclude_configs:
            for exclude in config[key]:
                if exclude in row[target]:
                    return True
        return False

    df_api["exclude"] = df_api.apply(
        lambda row: _is_excluded(row, exclude_configs), axis=1
    )

    return config


def main() -> None:
    """Main function"""

    args = _get_args()

    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    sdk_api = args.sdk_api if args.sdk_api else get_default_sdk_api(sdk_dir)
    cov = args.cov

    output_html = os.path.join(output_dir, args.output_html)
    output_untested_html = os.path.join(output_dir, args.output_untested_html)
    output_untested_filtered_html = os.path.join(
        output_dir, args.output_untested_filtered_html
    )

    output_per_file_all_html = os.path.join(output_dir, args.output_per_file_all_html)
    output_per_file_filtered_html = os.path.join(
        output_dir, args.output_per_file_filtered_html
    )

    output_per_module_all_html = os.path.join(
        output_dir, args.output_per_module_all_html
    )
    output_per_module_filtered_html = os.path.join(
        output_dir, args.output_per_module_filtered_html
    )

    output_json = os.path.join(output_dir, args.output_json)
    output_csv = (
        os.path.join(output_dir, args.output_csv)
        if args.output_csv is not None
        else None
    )

    exclude_list_file = os.path.join(currentdir, args.exclude_list)

    output_exclude_list_file = "{}.json".format(
        get_file_base_name_without_ext(args.exclude_list)
    )
    output_exclude_list_file = os.path.join(output_dir, output_exclude_list_file)

    # read csv
    df_api = pd.read_csv(sdk_api)
    df_cov = pd.read_csv(cov)

    df_api, cov_percent = update_coverage_for_sdk_api(df_api, df_cov)

    # only keep the last dir names from FunOS
    df_api["filename"] = df_api["filename"].apply(lambda x: "/".join(x.split("/")[6:]))

    # apply exlude filter
    exclude_config = apply_exclude_filter(df_api, exclude_list_file)

    # save exclude config to json
    with open(output_exclude_list_file, "w") as f:
        json.dump(exclude_config, f, indent=4)

    # save df_api to csv
    if output_csv:
        df_api.to_csv(output_csv)

    # save df_api to html
    gen_summary_html(df_api, output_html)
    gen_summary_html(df_api, output_untested_html, failed_in_report_type_api_only=True)
    gen_summary_html(
        df_api,
        output_untested_filtered_html,
        failed_in_report_type_api_only=True,
        use_exclude_col=True,
    )

    # per file summary
    df1 = gen_per_group_summary_html(
        df_api,
        output_per_file_all_html,
        group_type="file",
        report_type="coverage",
        use_exclude_col=False,
        return_df=True,
    )
    df2 = gen_per_group_summary_html(
        df_api,
        output_per_file_filtered_html,
        group_type="file",
        report_type="coverage",
        use_exclude_col=True,
        return_df=True,
    )

    # save df1 to csv
    df1.to_csv("per_file_all.csv")

    # per module summary
    gen_per_group_summary_html(
        df_api,
        output_per_module_all_html,
        group_type="module",
        report_type="coverage",
        use_exclude_col=False,
    )
    gen_per_group_summary_html(
        df_api,
        output_per_module_filtered_html,
        group_type="module",
        report_type="coverage",
        use_exclude_col=True,
    )

    gen_gcovr_json(df_api, cov_percent, output_json)

    print(f"SDK APIs coverage:              {cov_percent:.2f}%")
    print(f"SDK exclusion list:    {output_exclude_list_file}")
    print()
    print(f"Saving summary to html file:    {output_html}")
    print(f"Saving per file (all) summary to html file:    {output_per_file_all_html}")
    print(
        f"Saving per file (filtered) summary to html file:    {output_per_file_filtered_html}"
    )
    print(f"Saving summary to csv file:     {output_csv}")


if __name__ == "__main__":
    main()
