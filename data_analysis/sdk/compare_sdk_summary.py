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

    # parser.add_argument("--output_dir", type=str, help="Output directory")

    # parser.add_argument(
    #     "--output_json",
    #     type=str,
    #     default="sdk_api_doc_gen_report.json",
    #     help="Output json file",
    # )

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
        "--compare_type",
        type=str,
        default="documentation",
        help="Compare type, documentation, coverage, etc",
    )

    args = parser.parse_args()

    return args


def comp_sdk_doc(prev_summary: str, new_summary: str) -> None:
    """Compare two sdk summary files for documentation"""
    df_prev_summary = pd.read_csv(prev_summary)
    df_new_summary = pd.read_csv(new_summary)

    # find if there is new entry in combined_api column
    df_new_combined_api = df_new_summary["combined_api"].tolist()
    df_prev_combined_api = df_prev_summary["combined_api"].tolist()
    # check if there is new entry in df_new_combined_api compared to df_prev_combined_api
    new_apis = [x for x in df_new_combined_api if x not in df_prev_combined_api]
    print("New new_apis: {}".format(new_apis))

    # print the row of df_new with the column "combined_api" in new_combined_api
    new_df = df_new_summary[df_new_summary["combined_api"].isin(new_apis)]

    # select row with documented == False
    new_df = new_df[new_df["documented"] == False]

    print(new_df)
    return new_df


def comp_sdk_coverage(prev_summary: str, new_summary: str) -> None:
    """Compare two sdk summary files for coverage"""
    pass


def main() -> None:
    """Main function"""

    # get args
    args = _get_args()

    # prev_summary = "sdk_doc/sdk_api_summary.csv"
    # new_summary = "sdk_doc/sdk_api_summary_new.csv"
    prev_summary = args.prev_summary
    new_summary = args.new_summary
    compare_type = args.compare_type

    if compare_type == "documentation":
        comp_df = comp_sdk_doc(prev_summary, new_summary)
    else:
        assert False, "Unknown compare type: {}".format(compare_type)


if __name__ == "__main__":
    main()
