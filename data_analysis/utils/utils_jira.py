#!/usr/local/bin/python3 -u

"""Utilities for working with JIRA.
"""

from typing import List, Set, Dict, Tuple, Optional, Any
import jira  # type: ignore
import sys
import datetime
import getpass
import os
import json

# dict for converting ids from git to jira id format (firstname.lastname)
jira_convert_id_from_git_dict = {
    "cgray": "charles.gray",
    "nponugoti": "nag.ponugoti",
    "59043152+satishkumarch": "satishkumar.ch",
}

JIRA_SERVER = "http://jira.fungible.local:80"
JIRA_INIT = "~/.jira.ini"


def jira_convert_id_from_git(
    ids: List[str], convert_dict: Dict[str, str] = jira_convert_id_from_git_dict
) -> List[str]:
    """Convert id (extracted from git) that is not in jira id convention

    Parameters
    ----------
    ids : List(str)
        list of ids
    convert_dict : Dict[str, str]
        convert dictionary

    Returns
    -------
    List[str]
        list of converted ids
    """
    return [convert_dict.get(j, j) for j in ids]


def jira_connect(uname: str = None, p: str = None, jira_server=JIRA_SERVER) -> Any:
    """Connect to JIRA and return a connection object.

    Parameters
    ----------
    uname : str
        JIRA username
    p : str
        JIRA password

    Returns
    -------
    jconn : Any
        JIRA connection object
    """

    # TODO: use .env
    # check if file exists
    if not os.path.exists(os.path.expanduser(JIRA_INIT)):
        print("JIRA init file does not exist")
        sys.exit(1)

    with open(os.path.expanduser(JIRA_INIT)) as f:
        js = json.load(f)
        assert "username" in js and "password" in js, "Invalid JIRA init file"
        uname = js["username"]
        p = js["password"]

    jconn = jira.JIRA(jira_server, auth=(uname, p))
    return jconn


def jira_get_active_user(jconn: Any, username: str) -> bool:
    """Return True if the user is active in JIRA.

    Parameters
    ----------
    jconn : Any
        JIRA connection object
    username : str
        JIRA username

    Returns
    -------
    active : bool
        True if the user is active in JIRA
    """
    user = jconn.user(username)
    return user.active


def main() -> None:
    """Main entry point for the script."""
    uname = input("JIRA username: ")
    p = getpass.getpass("JIRA password: ")
    jconn = jira_connect(uname, p)
    print(jconn)


if __name__ == "__main__":
    sys.exit(main())
