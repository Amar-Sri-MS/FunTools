#! /usr/bin/env python3

##############################################################################
#  enrollment_boot_step.cgi
#
#
#  Copyright (c) 2018-2020. Fungible, inc. All Rights Reserved.
#  Copyright (c) 2023. Microsoft. All Rights Reserved.
#
##############################################################################

import os
import re
import bisect
import cgi
import traceback
import requests

URL_FMT = 'https://raw.githubusercontent.com/fungible-inc/SBPFirmware/%s/software/esec/libs/common/eSecure_secureboot.h'

BOOT_STEP_RE = re.compile('#\s*define\s+(BOOT_STEP_\w+)\s+(.*)$')

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


def interactive_boot_step(github_response, bootstep):
    # interactive query
    if github_response.status_code != 200:
        send_response_body("Git hub response for commit %s: %d" %
                           (commit_val, r.status_code))
        return

    boot_step = int(bootstep, 0)
    boot_steps = []
    for l in github_response.text.splitlines():
        m = BOOT_STEP_RE.match(l)
        if m:
            boot_steps.append((eval(m[2]), m[1]))
    boot_steps = sorted(boot_steps, key = lambda x: x[0])

    boot_step_nums = [v[0] for v in boot_steps]
    found_pos = bisect.bisect_right(boot_step_nums, boot_step)
    if found_pos == 0:
        send_response_body("Invalid boot step: %s" % args.boot_step)
        return

    found_boot_step = boot_steps[found_pos-1]
    diff = boot_step - found_boot_step[0]
    send_response_body("boot step %s (0x%x, %d) is %s %s (0x%x, %d)" %
                       (bootstep,
                        boot_step, boot_step,
                        found_boot_step[1],
                        "+ %d" % diff if diff else "",
                        found_boot_step[0],
                        found_boot_step[0]))



def process_query():
    form = cgi.FieldStorage()
    version = form.getvalue("version", None)
    # bootstep is optional -- user interactive
    bootstep = form.getvalue("bootstep", None)

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

    if bootstep is not None:
        interactive_boot_step(r, bootstep)
        return

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
