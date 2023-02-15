#!/usr/local/bin/python3 -u

"""Utilities for git operations
"""

from typing import List, Set, Dict, Tuple, Optional, Any

import re
from collections import Counter
import subprocess


def _get_commit_id_from_git_blame_str(blame_str: str) -> Tuple[List[str], List[str]]:
    """Return commit id from git blame string

    Parameters
    ----------
    blame_str : str
        git blame string

    Returns
    -------
    Tuple[List[str], List[str]]
        email and id_of_email
    """
    outputs = blame_str.split("\n")

    emails = [
        re.findall(r"<(.*?)>", o)[0]
        for o in outputs
        if "fungible" in o or "github" in o
    ]
    only_ids = [o.split("@")[0] for o in emails]
    return (emails, only_ids)


def _get_top_k_commit_ids(ids: List[str], k: int = 10) -> List[Tuple[str, int]]:
    """Helper function to get top k commit ids

    Parameters
    ----------
    ids : List[str]
        list of ids
    k : int, optional
        top k, by default 10

    Returns
    -------
    List[Tuple[str, int]]
        top k commit ids
    """

    ids = Counter(ids)
    return ids.most_common(k)


def git_top_k_committers(
    filename: str, dir_path: str = "../../", k=10, remove_prefix_from_filename: str = ""
) -> List[Tuple[str, int]]:
    """Return top k commit ids

    Parameters
    ----------
    filename : str
        filename
    dir_path : str, optional
        directory path, by default "../../"
    k : int, optional
        top k, by default 10
    remove_prefix_from_filename : str, optional
        remove prefix from filename, by default ""

    Returns
    -------
    List[Tuple[str, int]]
        top k commit ids
    """
    if remove_prefix_from_filename != "":
        if remove_prefix_from_filename[-1] != "/":
            remove_prefix_from_filename += "/"
        filename = filename.replace(remove_prefix_from_filename, "")

    cmd = f"git blame -e {filename}".split()
    p = subprocess.run(cmd, cwd=dir_path, capture_output=True, text=True)

    emails, ids = _get_commit_id_from_git_blame_str(p.stdout)
    tk = _get_top_k_commit_ids(ids, k=k)
    return tk
