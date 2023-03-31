#! /usr/bin/env python3

##############################################################################
#  enrollment_boot_step.cgi
#
#
#  Copyright (c) 2018-2020. Fungible, inc. All Rights Reserved.
#
##############################################################################

import os
import re
import cgi
import traceback
import requests

URL_FMT = 'https://raw.githubusercontent.com/fungible-inc/SBPFirmware/%s/software/esec/libs/common/eSecure_secureboot.h'

PUF_INIT_BOOT_STEP_RE = re.compile('#\s*define\s+BOOT_STEP_PUF_INIT\s+(.*)$')

from common import (
    log,
    send_response_body,
)

def parse_version(version):
    VER_RE = '(bld_(\d+))*-*([0-9a-fA-F]+)*'
    m = re.match(VER_RE, version)
    if not m:
       raise ValueError("Invalid version format")
    return m[2], m[3]


def process_query():
    form = cgi.FieldStorage()
    version = form.getvalue("version", None)

    if not version:
        raise ValueError("Missing version argument")

    bld_val, commit_val = parse_version(version)
    if not commit_val:
        raise ValueError("Invalid version")

    with open('/etc/github_auth') as f:
        lines = f.readlines()

    github_user = lines[0].strip()
    github_token = lines[1].strip()

    r = requests.get(URL_FMT % commit_val, auth=(github_user, github_token))
    if r.status_code != 200:
        raise ValueError("Git hub response for commit %s: %d" %
                         (commit_val, r.status_code))

    m = None
    for l in r.text.splitlines():
        m = PUF_INIT_BOOT_STEP_RE.match(l)
        if m:
            send_response_body(hex(eval(m[1])))
            return

    raise ValueError("Could not find boot step in file")


def main_program():
    # our content is always text/plain
    print("Content-type: text/plain")
    try:
        # get the request
        method = os.environ["REQUEST_METHOD"]
        if method != "GET":
            raise ValueError("Invalid request method %s" % method)

        process_query()

    # key errors (missing form entries) as well as
    # value errors are translated as 400 Bad Request
    except (ValueError, KeyError) as err:
        # Log
        log("Exception: %s" % err)
        # Response
        print("Status: 400 Bad Request\n")

        # all other errors are reported as 500 Internal Server Error
    except Exception as err:
        # Log
        log("Exception: %s" % err)
        traceback.print_exc()
        # Response
        print("Status: 500 Internal Server Error\n")


main_program()
