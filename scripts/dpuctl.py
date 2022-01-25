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


def httpreq_json(api: str, js=None, timeout=None, method=requests.post, **kwargs) -> Dict[Any, Any]:
    kwargs.update(API_FORMAT_DICT)
    DEBUG(kwargs)
    url = api.format(**kwargs)

    DEBUG("request '%s'" % url)

    r = method(url, json=js, verify=False, timeout=timeout)
    
    DEBUG("Return status %s" % r.status_code)
    if (r.status_code == 200):
        DEBUG(r.json())
        return r.json()
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

def cmd_restart() -> None:
    wait_for_version()

    # make the reqeuest
    try:
        httpreq_json(API_FAST_RESTART, timeout=0.01)
    except requests.exceptions.ReadTimeout: 
        pass

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
                                default="~/.ssh/id_rsa.pub",
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
                                default="~/.ssh/id_rsa.pub",
                                help="SSH Public key file")
    parser_ssh.add_argument("-P", "--privkey", action="store",
                            help="SSH Private key file override")
    parser_ssh.add_argument("-N", "--no-check", action="store_true",
                                default=False,
                                help="Don't check for key existence before adding")
    parser_ssh.set_defaults(func=cmd_ssh)

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
 
###
##  main
#
def main() -> int:
    global args
    args = parse_args()

    if (args.dpu is None):
        LOG("Required --dpu option missing")
        sys.exit(1)

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
