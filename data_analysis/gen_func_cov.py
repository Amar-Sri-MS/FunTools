#!/usr/bin/env python3

"""Generate function coverage by reading html file function coverage report

   Copyright (c) 2022 Fungible. All rights reserved.


    Preconditions
    -------------
    This script uses generate function coverage html file (--local_file) or build number (--build_no) to generate function coverage csv file (--output_csv).

    Examples
    --------
    >>> python ./gen_func_cov.py --build_no 107 --output_csv func_cov.csv --out_dir .

    Checks
    ------
    static check:
    >>> mypy ./gen_func_cov.py

    format:
    >>> black ./gen_func_cov.py

"""

"""
TODO:
- handling extracting html file as jenkins, likely use file access
  - this is likely running during the build, so it can reach out based on the path
- handle multiple modules
- BUILD_URL update

"""

import argparse
import os
import sys
from typing import Iterable, Any, List, Optional, Union, Callable, TextIO, Dict, Tuple

try:
    # for table
    from tabulate import tabulate
    import pandas as pd
    from requests.auth import HTTPBasicAuth
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("{}: Import failed!".format(__file__))
    print("Install missing modules")
    print(">>> pip install tabulate pandas requests beautifulsoup4")
    sys.exit()

# NOTE _20 will be updated to '-'
BUILD_URL = "http://jenkins-sw-master.fungible.local/ci/job/scheduled/job/coverage/{}/Coverage-Reports/{}/index.functions.html"


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_no", type=int, help="Build number for remote build url"
    )
    parser.add_argument(
        "--modules", type=str, default="all", help="Build number for remote build url"
    )
    parser.add_argument("--local_file", type=str, help="Local html file")
    parser.add_argument("--output_dir", type=str, default=".", help="Output directory")
    parser.add_argument("--output_csv", type=str, required=True, help="Output csv file")

    args = parser.parse_args()

    return args


def _extract_html(html_file: str) -> str:
    """Extract html file either from url or local and return as string

    Parameters
    ----------
    html_file : str
        html file

    Returns
    -------
    str
        html file as string
    """

    if html_file.startswith("http"):
        try:
            ID = os.environ["JENKINS_ID"]
            PASSWD = os.environ["JENKINS_PASSWD"]
        except KeyError:
            print("Please define the environment variable JENKINS_ID, JENKINS_PASSWD")
            sys.exit(1)
        basic = HTTPBasicAuth(ID, PASSWD)
        response = requests.get(html_file, auth=basic)
        html_doc = response.text
    else:
        # local file
        with open(html_file, "r", encoding="utf-8") as f:
            html_doc = f.read()

    return html_doc


def _extract_table(html_doc: str) -> pd.DataFrame:
    """Extract table from html and return as pandas dataframe

    Parameters
    ----------
    html_doc : str
        html document

    Returns
    -------
    pd.DataFrame
        pandas dataframe
    """

    soup = BeautifulSoup(html_doc, "html.parser")
    # table = soup.find("table", {"class": "coverage
    table = soup.find("table", {"class": "listOfFunctions"})
    dfs = pd.read_html(str(table))
    # display(type(dfs))

    return dfs[0]


def _get_html_file(args: argparse.Namespace, remote_url: str = BUILD_URL) -> str:
    html_file = (
        remote_url.format(args.build_no, args.modules)
        if args.build_no is not None
        else args.local_file
    )

    return html_file


def main() -> None:
    """Main function"""

    args = _get_args()
    output_csv = os.path.join(args.output_dir, args.output_csv)

    # check arguments
    if args.build_no is None and args.local_file is None:
        print("Please provide either build_no or local_file")
        sys.exit()

    html_file = _get_html_file(args)
    html_doc = _extract_html(html_file)
    df = _extract_table(html_doc)
    df.to_csv(args.output_csv, index=False)

    print(f"Saving table to csv file: {output_csv}")


if __name__ == "__main__":
    main()
