#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-line utility to control Fungible DPU via REST interfaces

static check:
% mypy dpuctl.py

format:
% python3 -m black dpuctl.py
"""
from typing import List, Optional, Type, Dict, Any, Tuple
import argparse
import requests
import pprint
import time
import os
import sys
import threading
import shutil
import shlex
import socket
import subprocess
import json
import warnings
import urllib3
from http.server import BaseHTTPRequestHandler, HTTPServer


### List of API endpoints
API_VERSION = 'http://{target}:{port}/platform/version'
API_BOOT_DEFAULTS = 'http://{target}:{port}/platform/boot_defaults'
API_FAST_RESTART = 'http://{target}:{port}/storage_agent/fast_restart'
API_UPGRADE_INIT = 'http://{target}:{port}/platform/upgrade/init'
API_UPGRADE_START = 'http://{target}:{port}/platform/upgrade/{proc}/start'
API_UPGRADE_STATUS = 'http://{target}:{port}/platform/upgrade/{proc}/status'
API_UPGRADE_COMPLETE = 'http://{target}:{port}/platform/upgrade/{proc}/complete'
API_HBMDUMP_LIST = 'http://{target}:{port}/platform/core_dump/list'
API_HBMDUMP_GET = 'http://{target}:{port}/platform/core_dump/download/0'
API_HBMDUMP_CLEAR = 'http://{target}:{port}/platform/core_dump/clear/0'

# POST, DELETE and GET ops for SSH keys
API_SSHKEY = "https://{target}:{sport}/v1/opsec-agent/ssh"


###
##  global args dict. default empty.
#
args: argparse.Namespace = argparse.Namespace()

###
##  Log & Debug
#
VERBOSITY: int = 0

def LOG(msg: str, verbosity: int = 0) -> None:
    if (verbosity <= VERBOSITY):
        print(msg)

def LOG_JSON(js: Dict[str, Any], verbosity: int = 0) -> None:
    if (verbosity <= VERBOSITY):
        print(json.dumps(js, indent=4, sort_keys=True))

def VERBOSE(msg: str) -> None:
    LOG(msg, 1)

def DEBUG(msg: str) -> None:
    LOG(msg, 2)

###
##  low-level http details
#

API_FORMAT_DICT: Dict[str, str] = {}

def mk_api_format_dict() -> None:
    API_FORMAT_DICT["target"] = args.dpu
    API_FORMAT_DICT["port"] = args.port
    API_FORMAT_DICT["sport"] = args.sport


def httpreq_json(api: str, js=None, timeout=None, method=requests.post, **kwargs) -> Optional[Dict[Any, Any]]:
    kwargs.update(API_FORMAT_DICT)
    DEBUG(kwargs)
    url = api.format(**kwargs)

    DEBUG("request '%s'" % url)

    r = method(url, json=js, verify=False, timeout=timeout)

    DEBUG("Return status %s" % r.status_code)
    if (r.status_code == 200):
        try:
            DEBUG(r.json())
            return r.json()
        except ValueError:
            return None
    else:
        LOG(r.reason)
        return None

def httpreq_file(api: str, js=None, timeout=None, method=requests.post, **kwargs) -> Optional[urllib3.response.HTTPResponse]:
    kwargs.update(API_FORMAT_DICT)
    DEBUG(kwargs)
    url = api.format(**kwargs)

    DEBUG("request '%s'" % url)

    r = method(url, json=js, verify=False, timeout=timeout, stream=True)
    
    DEBUG("Return status %s" % r.status_code)
    if (r.status_code == 200):
        return r.raw
    else:
        LOG(r.reason)
        return None

###
##
#
def wait_for_version(logver: bool = False) -> Dict[str, Any]:
    failed = True
    while (failed):
        try:
            js = httpreq_json(API_VERSION)
            if (logver):
                LOG_JSON(js)
            break
        except KeyboardInterrupt:
            sys.exit(1)
        except:
            print("Failed to get version, still waiting...")

        time.sleep(1)

    return js

###
##  default command
#

def cmd_empty() -> None:
    wait_for_version(True)

###
##  misc commands
#

def cmd_restart() -> None:
    wait_for_version()

    # make the reqeuest
    try:
        httpreq_json(API_FAST_RESTART, timeout=0.01)
    except requests.exceptions.ReadTimeout:
        pass

###
##  ssh commands
#

def _list_keys():
    reqjs = {"key": "ALL"}
    return httpreq_json(API_SSHKEY, method=requests.get, js=reqjs)

def cmd_ssh_list() -> None:
    wait_for_version()

    # make the reqeuest
    js = _list_keys()
    LOG_JSON(js)

def cmd_ssh_add() -> None:
    wait_for_version()

    # read the public key file
    fl = open(os.path.expanduser(args.pubkey))
    key = fl.read().strip()

    DEBUG("key: %s" % key)

    # get the list of keys
    if (not args.no_check):
        js = _list_keys()
        rkeys = js.get("data")
        if (rkeys is not None):
            for rkey in rkeys:
                if (rkey.strip() == key.strip()):
                    LOG("Key exists in dpu already")
                    return

    # make the request
    reqjs = {"key": key}
    js = httpreq_json(API_SSHKEY, method=requests.post, js=reqjs)
    LOG("Key added...")
    LOG_JSON(js)

def cmd_ssh_clear() -> None:
    wait_for_version()

    # make the reqeuest
    reqjs = {"key": "ALL"}
    js = httpreq_json(API_SSHKEY, method=requests.delete, js=reqjs)
    LOG_JSON(js)

def cmd_ssh() -> None:

    # wait for the device and make sure the key is added
    cmd_ssh_add()

    # derive the private key file from the public key file
    privkey = args.privkey
    if (privkey is None):
        privkey = os.path.splitext(args.pubkey)[0]

    # run ssh
    cmd = "ssh -i %s root@%s" % (privkey, args.dpu)
    DEBUG(cmd)
    os.system(cmd)

###
##  hbmdump commands
#

def cmd_hbmdump_list():
    wait_for_version()

    js = httpreq_json(API_HBMDUMP_LIST, method=requests.get)
    print(js)

def _hbmdump_get(overwrite: bool):

    # find the filename
    js = httpreq_json(API_HBMDUMP_LIST, method=requests.get)

    if (len(js) == 0):
        LOG("No hbmdumps")
        return

    # download the first one
    dump = js[0]
    ts = dump["timestamp"] / 1e9

    stime = time.strftime('%Y%m%d-%H:%M:%S', time.gmtime(ts))

    # get the raw socket of the file
    sock = httpreq_file(API_HBMDUMP_GET, method=requests.get)

    fname = "{}-{}-{}.gz".format(args.output, stime, args.dpu)

    if (os.path.exists(fname) and not overwrite):
        print("file '%s' exists" % fname)
        sys.exit(1)

    # try and open a file
    fl = open(fname, "wb")

    if (fl is None):
        print("failed to GET hbmdump")
        sys.exit(1)

    # copy the data
    print("downloading %s" % fname)

    t0 = time.time()
    sys.stdout.write(".")
    sys.stdout.flush()
    while True:
        t1 = time.time()
        if ((t1 - t0) > 3):
            sys.stdout.write(".")
            sys.stdout.flush()
            t0 = t1
        buf = sock.read(16<<10)
        if (len(buf) == 0):
            break
        fl.write(buf)
    print()

    sock.close()
    fl.close()

    print("hbmdump downloaded OK")

def cmd_hbmdump_get():
    wait_for_version()
    _hbmdump_get(args.overwrite)

def cmd_hbmdump_clear():
    wait_for_version()

    js = httpreq_json(API_HBMDUMP_CLEAR, method=requests.post)
    print(js)

def cmd_hbmdump_collect():
    wait_for_version()

    # find the filename
    js = httpreq_json(API_HBMDUMP_LIST, method=requests.get)

    if (len(js) == 0):
        LOG("No hbmdumps")
        return

    # download the first one
    dump = js[0]
    if (dump["occupied"] == 1):
        print("Uncollected dump found, collecting...")
        _hbmdump_get(True)

        # now clear it
        httpreq_json(API_HBMDUMP_CLEAR, method=requests.post)
    else:
        print("No new dumps available")
    
###
##  parse_args
#
DESC = "Command-line utility to control Fungible DPU via REST interfaces"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESC)

    # Main DPU argument
    parser.add_argument('--dpu',
                        action='store', default=None,
                        help='target dpu cclinux address')

    # Ports
    parser.add_argument("--port", action="store", type=int, default=9332,
                        help="Port for HTTP requests")
    parser.add_argument("--sport", action="store", type=int, default=8001,
                            help="Port for HTTPS requests")
    parser.set_defaults(func=cmd_empty)

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")

    # various sub-commands
    subparsers = parser.add_subparsers()

    # list ssh keys in the dpu
    parser_ssh_list = subparsers.add_parser('ssh_list',
    help="List SSH keys in the DPU")
    parser_ssh_list.set_defaults(func=cmd_ssh_list)

    # add a key to the DPU
    parser_ssh_add = subparsers.add_parser('ssh_add')
    parser_ssh_add.add_argument("-k", "--pubkey", action="store",
                                help="SSH Public key file")
    parser_ssh_add.add_argument("-N", "--no-check", action="store_true",
                                default=False,
                                help="Don't check for key existence before adding")
    parser_ssh_add.set_defaults(func=cmd_ssh_add)

    # clear all keys in the dpu
    parser_ssh_clear = subparsers.add_parser('ssh_clear')
    parser_ssh_clear.set_defaults(func=cmd_ssh_clear)

    # add a key and ssh to the DPU
    parser_ssh = subparsers.add_parser('ssh')
    parser_ssh.add_argument("-k", "--pubkey", action="store",
                                help="SSH Public key file")
    parser_ssh.add_argument("-P", "--privkey", action="store",
                            help="SSH Private key file override")
    parser_ssh.add_argument("-N", "--no-check", action="store_true",
                                default=False,
                                help="Don't check for key existence before adding")
    parser_ssh.set_defaults(func=cmd_ssh)

    # hbmdump
    parser_hbm_list = subparsers.add_parser('hbmdump_list')
    parser_hbm_list.set_defaults(func=cmd_hbmdump_list)

    parser_hbm_get = subparsers.add_parser('hbmdump_get')
    parser_hbm_get.add_argument("-o", "--output", action="store",
                                default="hbmdump",
                                help="output hbmdump filename prefix")
    parser_hbm_get.add_argument("-w", "--overwrite", action="store_true",
                                help="overwrite existing file")
    parser_hbm_get.set_defaults(func=cmd_hbmdump_get)

    parser_hbm_clear = subparsers.add_parser('hbmdump_clear')
    parser_hbm_clear.set_defaults(func=cmd_hbmdump_clear)

    parser_hbm_collect = subparsers.add_parser('hbmdump_collect')
    parser_hbm_collect.set_defaults(func=cmd_hbmdump_collect)


    # fast restart
    parser_restart = subparsers.add_parser('restart')
    parser_restart.set_defaults(func=cmd_restart)

    # do the actual parse
    args: argparse.Namespace = parser.parse_args()

    # set the verbosity
    global VERBOSITY
    VERBOSITY = args.verbose
    DEBUG("verbose = %s" % VERBOSITY)

    return args

def get_default_sshkey(dpu: str) -> str:
    default = "~/.ssh/id_rsa.pub"
    try:
        ids = subprocess.check_output(['ssh', '-G', dpu])
    except subprocess.CalledProcessError:
        return default

    pubkeys = []
    # find all identity files for a given host
    for e in ids.splitlines():
        kv = e.split(b" ", 1)
        if kv[0] == b"identityfile":
            pubkeys.append(kv[1].decode())

    # return first found path
    for key in pubkeys:
        p = "{}.pub".format(os.path.expanduser(key))
        if os.path.exists(p):
            return p

    return default



###
##  main
#
def main() -> int:
    global args
    args = parse_args()

    if (args.dpu is None):
        LOG("Required --dpu option missing")
        sys.exit(1)

    if hasattr(args, 'pubkey') and not args.pubkey:
        args.pubkey = get_default_sshkey(args.dpu)

    warnings.simplefilter('ignore',
                          category=urllib3.exceptions.InsecureRequestWarning)
    # setup the http boilerplate
    mk_api_format_dict()

    # call the func
    args.func()

    return 0

###
##  entrypoint
#
if __name__ == "__main__":
    main()
