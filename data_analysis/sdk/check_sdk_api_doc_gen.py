#!/usr/bin/env python3

"""Check SDK APIs documentation generations

   Copyright (c) 2023 Fungible. All rights reserved.

    Examples
    --------

    >>> python ./check_sdk_api_doc_gen.py

    Checks
    ------
    static check:
    >>> mypy ./check_sdk_api_doc_gen.py

    format:
    >>> black ./check_sdk_api_doc_gen.py

"""

import os
import argparse
import sys
import json
from typing import Iterable, Any, List, Optional, Union, Callable, TextIO, Dict, Tuple
import glob
from bs4 import BeautifulSoup

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


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--output_dir", type=str, help="Output directory")

    parser.add_argument(
        "--output_json",
        type=str,
        default="sdk_api_doc_gen_report.json",
        help="Output json file",
    )

    parser.add_argument(
        "--api_doc_gen_dir",
        type=str,
        help="Generated doc (html) directory",
    )

    parser.add_argument(
        "--sdk_dir",
        type=str,
        default="../../FunSDK",
        help="SDK directory",
    )

    parser.add_argument("--sdk_api", type=str, help="SDK APIs csv file")

    parser.add_argument(
        "--save_summary",
        type=bool,
        default=False,
        help="Save summary to csv file",
    )

    parser.add_argument(
        "--output_html",
        type=str,
        default="sdk_doc.html",
        help="Output documentation summary html file",
    )

    parser.add_argument(
        "--output_undocumented_html",
        type=str,
        default="sdk_doc_undocumented.html",
        help="Output html file for undocumented APIs",
    )

    parser.add_argument(
        "--output_per_file_all_html",
        type=str,
        default="sdk_per_file_doc_report_all.html",
        help="Per file documentation html file",
    )

    parser.add_argument(
        "--output_per_module_all_html",
        type=str,
        default="sdk_per_module_doc_report_all.html",
        help="Per module documentation html file",
    )

    args = parser.parse_args()
    return args


def _extract_func_name(proto_str: str) -> str:
    """extract function name from proto string

    Parameters
    ----------
    proto_str : str
        function prototype string

    Returns
    -------
    str: function name
    """
    # find a function name
    # split with "(", then find a function name only
    # NOTE: strip() is added for a case like "fun_name (xxx)", which include space between func_name "("
    name = proto_str.split("(")[0].strip().split(" ")[-1]

    # remove leading '*' if exists
    name = name[1:] if name.startswith("*") else name
    return name


def _extract_api_from_html(soup, debug=False):
    """extract api from html file

    Parameters
    ----------
    soup : BeautifulSoup
        bs4

    Returns
    -------
    List[str]: api list

    """
    keys = []
    for dl in soup.findAll("dl", {"class": "c function"}):
        if debug:
            print("DL ", dl)
        for dt in dl.findAll("dt"):
            if debug:
                print("DT ", dt.text)
            proto_name = _extract_func_name(dt.text.strip())
            if proto_name == "":
                continue
            if debug:
                print(proto_name)
            keys.append(proto_name)
        # for debugging, collection dscription
        if False:
            for dd in dl.findAll("dd"):
                values.append(dd.text.strip())
    return keys

def _trim_leading_path(_df: pd.DataFrame, leading_str: str="../../FunSDK/FunSDK/funosrt/include/") -> None:
    """trim leading path from filename"""
    leading_str = leading_str[:-1] if leading_str.endswith("/") else leading_str
    n_path = len(leading_str.split("/"))
    _df["filename"] = _df["filename"].apply(lambda x: "/".join(x.split("/")[n_path:]))


def _trim_filename(filename: str, n_path: int) -> str:
    """trim filename

    Parameters
    ----------
    filename : str
        filename

    n_path: str
        number of path to trim

    Returns
    -------
    str: trimmed filename
    """
    filename = "FunOS/" + "/".join(filename.split("/")[n_path:])[:-5]
    return filename


def _update_filename_prepend_str(_df: pd.DataFrame, prepend_str: str="FunOS/sdk_include/") -> None:
    """Update filename with  prepend_str"""
    _df["filename"] = prepend_str + _df["filename"]

def extract_generated_api_info_from_html(header_search_path: str):
    """Extract generated API information by loading html files from the given path

    Parameters
    ----------
    header_search_path : str
        path to search for html files

    Returns
    -------
    List[Dict]: list of API information

    """

    api_table_list = []

    html_files = glob.glob(f"{header_search_path}/**/*.html", recursive=True)
    n_path = len(header_search_path.split("/"))

    for html_file in html_files:
        if "index.html" in html_file:
            continue
        # read html file
        with open(html_file, "r") as f:
            html = f.read()
            soup = BeautifulSoup(html, features="html.parser")
            proto_names = _extract_api_from_html(soup)
            filename = _trim_filename(html_file, n_path)
            for proto_name in proto_names:
                d = {
                    "proto_name": proto_name,
                    "filename": filename,
                    "combined_api": f"{proto_name}:{filename}",
                }
                api_table_list.append(d)

    return api_table_list


def load_sdk_file_summary_using_csv(
    in_per_file_list: str = "per_file_all.csv",
) -> pd.DataFrame:
    """load sdk file summary by using the pre-generated csv file

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


def load_sdk_file_summary_counting_sdk_headers(
    sdk_dir: str, sdk_header_dir: str
) -> pd.DataFrame:
    """load sdk file summary by counting the number of headder files in SDK directory

    Returns
    -------
    df: pd.DataFrame
        A dataframe of SDK API per file summary
    """

    header_search_path = f"{sdk_dir}/{sdk_header_dir}"
    # check if the path is connect
    if not os.path.exists(header_search_path):
        print(f"{header_search_path} does not exist")
        sys.exit()

    n_path = len(header_search_path.split("/"))

    header_path = f"{header_search_path}/**/*.h"

    header_files = glob.glob(header_path, recursive=True)

    file_names = []
    for file in header_files:
        # remove index.html
        if "index.html" in file:
            continue
        # rearrange file path to be relative to FunOS so that it can be eaily compared with the SDK file list
        file_name = "FunOS/" + "/".join(file.split("/")[n_path:])
        file_names.append(file_name)
    return pd.DataFrame(file_names, columns=["filename"])


def load_sdk_file_summary(
    sdk_dir: str, sdk_header_dir: str = "FunSDK/funosrt/include/FunOS"
) -> pd.DataFrame:

    # by counting the number of headder files in SDK directory
    return load_sdk_file_summary_counting_sdk_headers(sdk_dir, sdk_header_dir)


def load_sdk_api_doc_gen_summary(
    html_search_path: str,
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

    if not os.path.exists(html_search_path):
        print(f"{html_search_path} does not exist")
        sys.exit()

    html_path = f"{html_search_path}/**/*.html"

    n_path = len(html_search_path.split("/"))

    html_files = glob.glob(html_path, recursive=True)

    file_names = []
    for file in html_files:
        # remove index.html
        if "index.html" in file:
            continue
        # rearrange file path to be relative to FunOS so that it can be easily compared with the SDK file list
        file_name = "FunOS/" + "/".join(file.split("/")[n_path:])
        file_names.append(file_name[:-5])  # -5 to remove '.html'

    return pd.DataFrame(file_names, columns=["filename"])


def generate_api_documentation_summary(
    sdk_dir: str, html_search_path: str, sdk_api: str
):
    """Generate API documentation summary

    Parameters
    ----------
    sdk_dir: str
        A path to search for SDK header files
    html_search_path: str
        A path to search for generate html files
    sdk_api: str
        A path to search for "total" API information

    Returns
    -------
    report: Dict
        A dictionary of API documentation summary
    summary_df: pd.DataFrame
        A dataframe of API documentation summary
    undocumented_header_df: pd.DataFrame
        A dataframe of undocumented header files
    """

    def check_api_is_documented(df_doc_gen: pd.DataFrame, combined_api: str) -> bool:
        """Check if api is documented"""
        return not df_doc_gen[(df_doc_gen["combined_api"] == combined_api)].empty

    report = {}

    # load SDK file list
    sdk_file_df = load_sdk_file_summary(sdk_dir)

    # append 'FunOS/sdk_include/' to filename of sdk_file_df
    _update_filename_prepend_str(sdk_file_df)

    # load generated documentation list
    sdk_gen_doc_df = load_sdk_api_doc_gen_summary(html_search_path)

    # find filenames of sdk_gen_doc_df that is in sdk_file_df
    common_df = sdk_gen_doc_df[sdk_gen_doc_df["filename"].isin(sdk_file_df["filename"])]

    # find filename that is different than common_df filename
    undocumented_headers_df = sdk_file_df[
        ~sdk_file_df["filename"].isin(common_df["filename"])
    ]

    df_api = pd.read_csv(sdk_api)

    # only keep the last dir names from FunOS
    _trim_leading_path(df_api)
    _update_filename_prepend_str(df_api)

    # add 'combined_api' column to create a unique key for each api
    df_api["combined_api"] = df_api["proto_name"] + ":" + df_api["filename"]

    api_table_list = extract_generated_api_info_from_html(html_search_path)
    df_api_doc_gen = pd.DataFrame(api_table_list)

    df_api["documented"] = df_api["combined_api"].apply(
        lambda x: check_api_is_documented(df_api_doc_gen, x)
    )

    doc_api_percentage = df_api["documented"].sum() / len(df_api) * 100

    # select df_api_extracted's documented == False
    undocumented_apis_df = df_api[df_api["documented"] == False]

    report["total_sdk_files"] = len(sdk_file_df)
    report["total_sdk_files_api_doc_gen"] = len(sdk_gen_doc_df)
    report["total_sdk_files_undocumented"] = len(undocumented_headers_df)

    # fill zero data as placeholder
    report["total_sdk_apis"] = len(df_api)
    report["total_sdk_apis_api_doc_gen"] = int(df_api["documented"].sum())
    report["total_sdk_apis_undocumented"] = (
        report["total_sdk_apis"] - report["total_sdk_apis_api_doc_gen"]
    )

    report["undocumented_files"] = undocumented_headers_df["filename"].tolist()
    report["undocumented_apis"] = undocumented_apis_df["combined_api"].tolist()

    report["sdk_file_doc_gen_percent"] = "{:.2f}".format(
        (len(sdk_gen_doc_df) / len(sdk_file_df)) * 100
    )

    report["sdk_apis_doc_gen_percent"] = "{:.2f}".format(doc_api_percentage)

    report_str = json.dumps(report, indent=4)
    print(report_str)

    return report, df_api, undocumented_headers_df


def main() -> None:
    """Main function"""

    # get args
    args = _get_args()

    # prepare dirs and filenames
    sdk_dir = args.sdk_dir if args.sdk_dir else get_defatult_sdk_dir()
    api_doc_gen_dir = (
        args.api_doc_gen_dir
        if args.api_doc_gen_dir
        else get_default_api_doc_gen_dir(sdk_dir)
    )
    sdk_api = args.sdk_api if args.sdk_api else get_default_sdk_api(sdk_dir)

    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_json = os.path.join(output_dir, args.output_json)

    output_html = os.path.join(output_dir, args.output_html)
    output_undocumented_html = os.path.join(output_dir, args.output_undocumented_html)
    output_per_file_all_html = os.path.join(output_dir, args.output_per_file_all_html)
    output_per_module_all_html = os.path.join(
        output_dir, args.output_per_module_all_html
    )

    print("Inputs")
    print("-------")
    print("API HTML search path: {}".format(api_doc_gen_dir))
    print("Output json file: {}".format(output_json))
    print()


    (
        report,
        df_api_extracted,
        undocumented_headers_df,
    ) = generate_api_documentation_summary(sdk_dir, api_doc_gen_dir, sdk_api)

    # save report to json file
    with open(output_json, "w") as f:
        json.dump(report, f, indent=4)

    df_api_extracted.to_csv(
        os.path.join(output_dir, "sdk_api_summary.csv"), index=False
    )

    gen_summary_html(df_api_extracted, output_html, report_type="document")

    gen_summary_html(
        df_api_extracted,
        output_undocumented_html,
        report_type="document",
        failed_in_report_type_api_only=True,
    )

    # per file summary
    gen_per_group_summary_html(
        df_api_extracted,
        output_per_file_all_html,
        group_type="file",
        report_type="document",
        use_exclude_col=False,
        return_df=False,
    )

    # per module summary
    gen_per_group_summary_html(
        df_api_extracted,
        output_per_module_all_html,
        group_type="module",
        report_type="document",
        use_exclude_col=False,
    )

    if args.save_summary:
        df_api_extracted.to_pickle(os.path.join(output_dir, "sdk_api_summary.pkl"))

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
