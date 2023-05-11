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
import json

from common import (
    log,
    send_response_body,
)

def parse_version(version):
    VER_RE = r'(bld_(\d+))*-*([0-9a-fA-F]+)*'
    m = re.match(VER_RE, version)
    if not m:
       raise ValueError("Invalid version format")
    return m[2], m[3]


def interactive_boot_step(bootsteps, step):
    boot_step_nums = [v[0] for v in bootsteps]
    found_pos = bisect.bisect_right(boot_step_nums, step)
    if found_pos == 0:
        send_response_body(f"Invalid boot step: {step}")
        return

    found_boot_step = bootsteps[found_pos-1]
    diff = step - found_boot_step[0]
    send_response_body(f"boot step {step}({step:#x}) is "
        f"{found_boot_step[1]} {found_boot_step[0]}({found_boot_step[0]:#x})"
        f" + {diff}")


def process_bootsteps_header(h):
    # old SBP code - bootsteps are defined as CPP Macros
    boot_steps = []
    BOOT_STEP_RE = re.compile(r'#\s*define\s+(BOOT_STEP_\w+)\s+(.*)$')

    for l in h.splitlines():
        m = BOOT_STEP_RE.match(l)
        if m:
            boot_steps.append((eval(m[2]), m[1]))

    return sorted(boot_steps, key = lambda x: x[0])


def process_bootsteps_json(s):
    # new SBP code - bootsteps are defined in interface json
    bootsteps = json.loads(s)

    # depending on the SBP build version, the json may be present
    # but it might not contain bootstep entries
    b = bootsteps.get('sbp', {}).get('bootstep', {}).get('values', {})

    boot_steps = []
    for e in b:
        boot_steps.append((e['value'], e['key']))

    return sorted(boot_steps, key = lambda x: x[0])


# list of (uri, parser) pairs, ordered in the preference order
bootsteps_uris = (
    ('https://raw.githubusercontent.com/fungible-inc/SBPFirmware/%s/software/esec/esec_interface.json', process_bootsteps_json),
    ('https://raw.githubusercontent.com/fungible-inc/SBPFirmware/%s/software/esec/libs/common/eSecure_secureboot.h', process_bootsteps_header)
)

def get_bootstep_list(version):
    with open('/etc/github_auth') as f:
        lines = f.readlines()

    github_user = lines[0].strip()
    github_token = lines[1].strip()

    errors = [ f"Commit {version}" ]

    for (uri,handler) in bootsteps_uris:
        r = requests.get(uri % version, auth=(github_user, github_token))
        if r.status_code != 200:
            errors.append(f"uri:...{uri[-15:]}: github http err: {r.status_code}")
            # try next method
            continue

        bootsteps = handler(r.text)
        if bootsteps:
            return bootsteps

    raise ValueError('\n'.join(errors))



def process_query():
    form = cgi.FieldStorage()
    version = form.getvalue("version", None)
    # bootstep is optional -- user interactive
    bootstep = form.getvalue("bootstep", None)

    if not version:
        raise ValueError("Missing version argument")

    _, commit_val = parse_version(version)
    if not commit_val:
        raise ValueError("Invalid version")

    all_bootsteps = get_bootstep_list(commit_val)

    if bootstep:
        interactive_boot_step(all_bootsteps, int(bootstep, base=0))
        return

    for e in all_bootsteps:
        if e[1] == 'BOOT_STEP_PUF_INIT':
            send_response_body(f"{e[0]:#x}")
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
