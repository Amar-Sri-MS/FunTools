#!/usr/bin/env python3

"""Compare sdk summary information

   Copyright (c) 2023 Fungible. All rights reserved.


   This script compares the previous sdk summary file with the new sdk summary file.

   Preconditions
   -------------
   This script uses an input of two sdk summary files (--prev_summary, --new_summary) to generate a function coverage csv file (--output_csv).

   Examples
   --------
   >>> python3 ./compare_sdk_summary.py --prev_summary sdk_api_summary.csv --new_summary sdk_api_summary_new.csv

   Test
   -----
   >>> pytest tests/test_compare_sdk_summary.py -o log_cli=true

   Checks
   ------
   static check:
   >>> mypy ./compare_sdk_summary.py
   >>> pylint ./compare_sdk_summary.py

   format:
   >>> black ./compare_sdk_summary.py

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
    from tabulate import tabulate
except ImportError:
    print("{}: Import failed!".format(__file__))
    print("Install missing modules")
    print(">>> pip install pandas tabulate")
    sys.exit()

import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from utils.utils import *


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output_filename",
        type=str,
        default="sdk_api_doc_diff_report",
        help="Output filename without extension",
    )

    parser.add_argument("--output_dir", type=str, default=".", help="Output directory")

    parser.add_argument(
        "--prev_summary",
        type=str,
        help="Previous sdk summary file",
    )

    parser.add_argument(
        "--new_summary",
        type=str,
        help="New sdk summary file",
    )

    parser.add_argument(
        "--prev_sdk",
        type=int,
        help="Previous sdk number",
    )

    parser.add_argument(
        "--new_sdk",
        type=int,
        help="New sdk number",
    )

    parser.add_argument(
        "--compare_type",
        type=str,
        default="documentation",
        help="Compare type, documentation, coverage, or all etc",
    )

    parser.add_argument("--debug", type=bool, default=False, help="Debug flag")

    args = parser.parse_args()

    return args


def comp_sdk_doc(
    prev_summary: str, new_summary: str, debug: bool = False
) -> Tuple[int, int, pd.DataFrame]:
    """Compare two sdk summary files for documentation"""
    df_prev_summary = pd.read_csv(prev_summary)
    df_new_summary = pd.read_csv(new_summary)

    # find if there is new entry in combined_api column
    df_new_combined_api = df_new_summary["combined_api"].tolist()
    df_prev_combined_api = df_prev_summary["combined_api"].tolist()
    # check if there is new entry in df_new_combined_api compared to df_prev_combined_api
    new_apis = [x for x in df_new_combined_api if x not in df_prev_combined_api]

    # print the row of df_new with the column "combined_api" in new_combined_api
    new_df = df_new_summary[df_new_summary["combined_api"].isin(new_apis)]

    if debug and len(new_df) > 0:
        print("New new_apis: {}".format(new_apis))
        print("There are {} new APIs".format(len(new_df)))
        print("There are {} documented APIs".format(sum(new_df.documented)))
        print(new_df)
    return len(new_df), sum(new_df.documented), new_df


def comp_sdk_coverage(prev_summary: str, new_summary: str) -> None:
    """Compare two sdk summary files for coverage"""
    # TODO
    pass


def _generate_error_outputs(df: pd.DataFrame, output_filename: str) -> None:
    """Generate error output and files

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to save
    output_filename : str
        Output filename, full path, without extension

    Returns
    -------
    None

    """

    columns = ["proto_name", "filename", "documented"]
    undoc_df = df[df.documented == False][columns]
    undoc_len = len(undoc_df)

    verb = "are" if undoc_len > 1 else "is"
    error_msg = "ERROR: There {} {} undocumented API(s)".format(verb, undoc_len)
    error_desc = "The following table shows the undocumented API(s):"
    headers = ["API Name", "Filename", "Documented"]
    table_str = tabulate(undoc_df, headers=headers, tablefmt="psql", showindex=False)
    # stdout log
    print()
    print(error_msg)
    print()
    print(error_desc)
    print(table_str)
    print()

    # save to json
    undoc_df.to_json(output_filename + ".json", orient="records")

    # save to html file
    output_html = output_filename + ".html"
    undoc_df.rename(
        columns={
            "proto_name": "API Name",
            "filename": "Filename",
            "documented": "Documented",
        },
        inplace=True,
    )
    table_str = undoc_df.to_html(
        index=False,
        justify="center",
        float_format="{:.2f}".format,
    )

    html_header_str = f"<br>  <br> <h1> {error_msg} </h1> <br>"
    html_header_str += f"<h4> {error_desc} </h4>"
    html_header_str += f"<br>"
    html_footer_str = """<br> <br>"""
    html_str = html_header_str + table_str + html_footer_str

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_str)

    del undoc_df


def main() -> None:
    """Main function"""

    ret = 0
    # get args
    args = _get_args()

    prev_summary = args.prev_summary
    new_summary = args.new_summary
    prev_sdk = args.prev_sdk
    new_sdk = args.new_sdk
    compare_type = args.compare_type
    debug = args.debug

    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = os.path.join(output_dir, args.output_filename)

    if compare_type == "documentation":
        num_diff, num_doc, comp_df = comp_sdk_doc(prev_summary, new_summary, debug)
        if num_diff > 0 and num_diff > num_doc:
            _generate_error_outputs(comp_df, output_filename)
            ret = -1
    else:
        assert False, "Unsupported compare type: {}".format(compare_type)

    def _debug_log():
        print()
        print("Compare sdk summary:")
        print("=" * 80)
        print(f"prev_summary: {prev_summary}")
        print(f"new_summary: {new_summary}")
        print(f"prev_sdk: {prev_sdk}")
        print(f"new_sdk: {new_sdk}")
        print(f"output path and file w/o extention: {output_filename}")
        print("=" * 80)
        print()

    if debug:
        _debug_log()

    sys.exit(ret)


if __name__ == "__main__":
    main()
