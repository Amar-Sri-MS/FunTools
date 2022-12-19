#!/usr/bin/env python3

"""Generate function coverage by reading a function coverage report html file

   Copyright (c) 2022 Fungible. All rights reserved.


    Preconditions
    -------------
    This script uses an input of either a generate function coverage html file (--local_file) or a build number (--build_no) to generate a function coverage csv file (--output_csv).

    Examples
    --------
    >>> python3 ./gen_func_cov.py --build_no 107 --output_csv func_cov.csv --output_dir .
    >>> python3 ./gen_func_cov.py --local_file ../../coverage/all/index.functions.html --output_csv func_cov.csv --output_dir .

    Test
    -----
    >>> pytest tests/test_gen_func_cov.py -o log_cli=true

    Checks
    ------
    static check:
    >>> mypy ./gen_func_cov.py
    >>> pylint ./gen_func_cov.py

    format:
    >>> black ./gen_func_cov.py

"""

"""
TODO
----
- try/except
- handle multiple coverage modules

"""

import argparse
import os
import sys
from typing import Iterable, Any, List, Optional, Union, Callable, TextIO, Dict, Tuple

try:
    import pandas as pd
    from requests.auth import HTTPBasicAuth
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("{}: Import failed!".format(__file__))
    print("Install missing modules")
    print(">>> pip install pandas requests beautifulsoup4")
    sys.exit()

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


def extract_html(html_file: str) -> str:
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


def extract_table(html_doc: str) -> pd.DataFrame:
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


def get_html_file(build_no, modules, local_file, remote_url: str = BUILD_URL) -> str:
    """Get html file from either remote url or local file

    Parameters
    ----------
    build_no : int
        build number
    modules : str
        modules
    local_file : str
        local file
    remote_url : str, optional
        remote url, by default BUILD_URL

    Returns
    -------
    str : html file

    """
    html_file = (
        remote_url.format(build_no, modules) if build_no is not None else local_file
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

    html_file = get_html_file(args.build_no, args.modules, args.local_file)
    html_doc = extract_html(html_file)
    df = extract_table(html_doc)
    df.to_csv(args.output_csv, index=False)

    print(f"Saving table to csv file: {output_csv}")


if __name__ == "__main__":
    main()
