#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility functions for fod (Fun* On Demand)

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

from utils import read_from_file_or_url

from typing import Iterable, Any, List, Optional, Union, Callable, TextIO, Dict, Tuple


def fod_extract_pages(
    config: dict,
    JOB_URL: str = "http://palladium-jobs.fungible.local:8080/job/{}",
    CONSOL_URL: str = (
        "http://palladium-jobs.fungible.local:8080/job/{}/raw_file/odp/uartout0.0.txt"
    ),
) -> List[dict]:
    """Extract pages info from fod job

    Parameters
    ----------
    config: dict
        config dict
    JOB_URL: str
        job url
    CONSOL_URL: str
        console url

    Returns
    -------
    collected_jobs: List[dict]
        list of dict of job info
    """

    collected_jobs = []

    def get_response(no, job_url_file: str, console_url_file: str):
        dummy_working_dir = "."
        if job_url_file:
            job_response = read_from_file_or_url(dummy_working_dir, job_url_file)
            # job_response = read_from_file_or_url(dummy_working_dir, job_url)
        else:
            job_response = ""
        console_response = read_from_file_or_url(dummy_working_dir, console_url_file)
        row = {
            "job_no": no,
            "job_url": job_url,
            "job_response": job_response,
            "console_url": console_url,
            "console_response": console_response,
        }
        return row

    if "job_no" in config:
        for no in config["job_no"]:
            job_url = JOB_URL.format(no)
            console_url = CONSOL_URL.format(no)

            row = get_response(no, job_url, console_url)
            collected_jobs.append(row)
    elif "console_file" in config:
        for console_file in config["console_file"]:
            job_url = None
            console_url = console_file

            row = get_response(console_file, job_url, console_url)
            collected_jobs.append(row)
    else:
        raise ValueError("job_no or job_file must be specified in config")

    return collected_jobs


def fod_extract_machines_from_job(job_response: str) -> str:
    """Extract machines from job response

    Parameters
    ----------
    job_response : str
        job response

    Returns
    -------
    str
        machines
    str
        completion date
    """
    soup = BeautifulSoup(job_response, "html.parser")
    table = soup.find("table", {"class": "summary"})
    dfs = pd.read_html(str(table))
    df = dfs[0]
    machine = df.loc[
        df["Job Configuration"] == "Machines", "Job Configuration.1"
    ].values[0]
    completion_date = df.loc[
        df["Job Configuration"] == "Completion time", "Job Configuration.1"
    ].values[0]

    return machine, completion_date


def fod_extract_vps_from_console(console_response: str, pattern: str) -> List[str]:
    """Extract VPs from console response

    Parameters
    ----------
    console_response : str
        console response

    Returns
    -------
    List[str]
        list of VPs
    """
    # find all lines include "WDT: Long-running WU warning" and show full line
    filtered_lines = re.findall(".*" + pattern, console_response)
    vps = []
    for line in filtered_lines:
        t = line.split(" ")
        vp = t[1][:-1]
        vps.append(vp)

    return vps


# extract text that includes pattern


def fod_extract_lines_with_pattern_from_console(
    console_response: str, pattern: str
) -> List[str]:
    """Extract lines that matches the given pattern from console response

    Parameters
    ----------
    console_response : str
        console response

    Returns
    -------
    List[str]
        list of filtered lines
    """

    filtered_lines = re.findall(".*" + pattern + ".*", console_response)
    return filtered_lines


def fod_extract_ts_vp_from_line(line: str) -> Tuple[str, str]:
    """Extract timestamp and VP from line

    Parameters
    ----------
    line : str
        line

    Returns
    -------
    Tuple[str, str]
        timestamp, VP
    """
    try:
        m = re.search("\[(.*?)\]", line)
    except AttributeError:
        print(m)
        return None, None

    if m is None:
        return None, None
    ts_vp = m.group(1).split(" ")
    ts = float(ts_vp[0])
    vp = ts_vp[1]
    return ts, vp


def fod_extract_json_from_line(
    lines: List[str], patch: bool = False, add_ts_vp: bool = True
) -> List[Dict[str, Any]]:
    """Extract JSON from line

    create json object from line that includes JSON string.
    output example>
    >> {"ts": 1234567890, "vp": "vp1", "key1": "value1", "key2": "value2"}

    Parameters
    ----------`
    lines : List[str]
        lines
    patch : bool, optional
        OBSOLETE, patch the misformatted json, by default False

    add_ts_vp : bool, optional
        add timestamp and VP to the json, by default True

    Returns
    -------
    Dict[str, Any]
        JSON
    """
    extracted_json = []
    for line in lines:
        if add_ts_vp:
            ts, vp = fod_extract_ts_vp_from_line(line)
        # extract strings enclosed with "{" and "}"
        try:
            m = re.search("{(.+?)}", line)
        except AttributeError:
            print(m)
            continue
        # refomrat to json style string
        if m is None:
            continue
        if add_ts_vp:
            ts_vp_str = '"ts": {}, "vp": "{}", '.format(ts, vp)
        else:
            ts_vp_str = ""
        j_str = "{" + ts_vp_str + m.group(1) + "}"

        # obsolete, patch the misformatted json
        if patch:
            j_str = j_str.replace('"usecs" "count"', '"usecs","count"')

        d = json.loads(j_str)

        extracted_json.append(d)
    return extracted_json
