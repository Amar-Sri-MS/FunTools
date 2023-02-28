#!/usr/bin/env python3

"""Check SDK APIs documentation generations

   Copyright (c) 2023 Fungible. All rights reserved.

    Preconditions
    -------------
    This script uses inputs of an api summary (--sdk_api) and a function coverage summary (--cov) generated by gcovr.

    Examples
    --------

    >>> python ./check_sdk_api_doc_gen.py

    Test
    -----
    >>> pytest tests/test_check_sdk_api_doc_gen.py -o log_cli=true

    Checks
    ------
    static check:
    >>> mypy ./check_sdk_api_doc_gen.py

    format:
    >>> black ./check_sdk_api_doc_gen.py

"""

"""
TODO
----

- 

"""

import os
import argparse
import sys
from pathlib import Path
import json
from typing import Iterable, Any, List, Optional, Union, Callable, TextIO, Dict, Tuple
import yaml
import glob

try:
    import pandas as pd
except ImportError:
    print("{}: Import failed!".format(__file__))
    print("Install missing modules")
    print(">>> pip install pandas")
    sys.exit()


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--output_dir", type=str, default=".", help="Output directory")

    parser.add_argument(
        "--output_json",
        type=str,
        default="sdk_api_doc_gen_report.json",
        help="Output json file",
    )

    parser.add_argument(
        "--api_doc_gen_dir",
        type=str,
        default="../../FunSDK/FunDoc/html/FunOS/headers",
        help="Generated doc (html) directory",
    )

    args = parser.parse_args()
    return args


def load_sdk_file_summary(in_per_file_list: str = "per_file_all.csv") -> pd.DataFrame:
    """load sdk file summary

    Returns
    -------
    df: pd.DataFrame
        A dataframe of SDK API per file summary
    """

    df = pd.read_csv(in_per_file_list)

    # select unique values from a column with filename
    sdk_file_df = pd.DataFrame(df["filename"].unique())

    # set the column name to be "filename"
    sdk_file_df.columns = ["filename"]

    return sdk_file_df


def load_sdk_api_doc_gen_summary(
    html_search_path: str = "../../FunSDK/FunDoc/html/FunOS/headers",
) -> pd.DataFrame:
    """load sdk API doc generation summary

    Parameters
    ----------
    html_search_path: str
        A path to search for html files from the point of the current directory

    Returns
    -------
    df: pd.DataFrame
        A dataframe of SDK API doc generation summary
    """

    html_path = f"{html_search_path}/**/*.html"
    n_path = len(html_search_path.split("/"))

    html_files = glob.glob(html_path, recursive=True)

    file_names = []
    for file in html_files:
        # remove index.html
        if "index.html" in file:
            continue
        # rearrange file path to be relative to FunOS so that it can be eaily compared with the SDK file list
        file_name = "FunOS/" + "/".join(file.split("/")[n_path:])
        file_names.append(file_name[:-5])  # -5 to remove '.html'
    return pd.DataFrame(file_names, columns=["filename"])


def diff_sdk_api_doc_gen(
    sdk_file_df: pd.DataFrame, sdk_gen_doc_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Compare SDK API doc generation summary with SDK API per file summary

    Parameters
    ----------
    sdk_file_df: pd.DataFrame
        A dataframe of SDK API per file summary

    sdk_gen_doc_df: pd.DataFrame
        A dataframe of SDK API doc generation summary

    Returns
    -------
    common_df: pd.DataFrame
        A dataframe of common SDK API

    df: pd.DataFrame
        A dataframe of undocumented SDK API
    """

    # find filename of sdk_gen_doc_df that is in sdk_file_df
    common_df = sdk_gen_doc_df[sdk_gen_doc_df["filename"].isin(sdk_file_df["filename"])]

    # find filename that is different than common_df filename
    undocumented_df = sdk_file_df[~sdk_file_df["filename"].isin(common_df["filename"])]

    return common_df, undocumented_df


def main() -> None:
    """Main function"""

    args = _get_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    output_json = os.path.join(args.output_dir, args.output_json)

    print("Inputs")
    print("-------")
    print("API HTML search path: {}".format(args.api_doc_gen_dir))
    print("Output json file: {}".format(output_json))
    print()

    # load SDK file list
    sdk_file_df = load_sdk_file_summary()

    # load SDK API doc generation list
    html_search_path = args.api_doc_gen_dir
    sdk_gen_doc_df = load_sdk_api_doc_gen_summary(html_search_path)

    _, undocumented_df = diff_sdk_api_doc_gen(sdk_file_df, sdk_gen_doc_df)

    # output the result
    report = {}
    report["total_sdk_files"] = len(sdk_file_df)
    report["total_sdk_files_api_doc_gen"] = len(sdk_gen_doc_df)
    report["total_sdk_files_undocumented"] = len(undocumented_df)

    # fill zero data as placeholder
    report["total_sdk_apis"] = 0
    report["total_sdk_apis_api_doc_gen"] = 0
    report["total_sdk_apis_undocumented"] = 0

    report["undocumented_files"] = undocumented_df["filename"].tolist()
    report["sdk_file_doc_gen_percent"] = "{:.2f}".format(
        (len(sdk_gen_doc_df) / len(sdk_file_df)) * 100
    )
    # TODO: populate the following fields
    # fill zero data
    report["sdk_apis_doc_gen_percent"] = "{:.2f}".format(0.0)

    # save report to json file
    with open(output_json, "w") as f:
        json.dump(report, f, indent=4)

    print("Summary")
    print("-------")
    print("Output json file: {}".format(output_json))

    print("Total number of SDK header files: {}".format(report["total_sdk_files"]))
    print(
        "Total number of SDK API doc generated: {}".format(
            report["total_sdk_files_api_doc_gen"]
        )
    )
    print(
        "Total number of undocumented SDK API: {}".format(
            report["total_sdk_files_undocumented"]
        )
    )
    print(
        "Percentage of files SDK API doc generated: {}".format(
            report["sdk_file_doc_gen_percent"]
        )
    )
    print(
        "Percentage of SDK API doc generated: {}".format(
            report["sdk_file_doc_gen_percent"]
        )
    )


if __name__ == "__main__":
    main()