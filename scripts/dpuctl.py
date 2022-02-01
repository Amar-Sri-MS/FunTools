#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-line utility to control Fungible DPU via REST interfaces
 
static check:
% mypy dpuctl.py
 
format:
% python3 -m black dpuctl.py
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import List, Optional, Type, Dict, Any, Tuple

import logging.handlers
import threading
import argparse
import requests
import warnings
import logging
import urllib3
import socket
import select
import shutil
import pprint
import shlex
import json
import time
import sys
import os
import re

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

def LOG(msg: Any, verbosity: int = 0) -> None:
    if (verbosity <= VERBOSITY):
        print(msg)

def LOG_JSON(js: Optional[Dict[str, Any]], verbosity: int = 0) -> None:
    if (verbosity <= VERBOSITY):
        if (js is None):
            print("{NULL json}")
        else:
            print(json.dumps(js, indent=4, sort_keys=True))

def VERBOSE(msg: Any) -> None:
    LOG(msg, 1)

def DEBUG(msg: Any) -> None:
    LOG(msg, 2)

def DIE(msg: str) -> None:
    sys.stderr.write(msg + "\n")
    sys.exit(1)

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
        DEBUG(r.json())
        return r.json()
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
ANIM = "/-\|"
def wait_for_version(logver: bool = False) -> Optional[Dict[str, Any]]:
    failed = True
    count = 0
    while (failed):
        try:
            js = httpreq_json(API_VERSION)
            if (logver):
                LOG_JSON(js)
            break
        except KeyboardInterrupt:
            sys.exit(1)
        except:
            sys.stdout.write("\rFailed to get version, still waiting %s" % ANIM[count%len(ANIM)])
            sys.stdout.flush()
            count += 1

        time.sleep(1)

    if(count > 0):
        print()
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

    if (js is None):
        LOG("Error on http request")
        return
    elif (len(js) == 0):
        LOG("No hbmdumps")
        return

    # download the first one
    dump = js[0]
    ts = dump["timestamp"] / 1e9

    stime = time.strftime('%Y%m%d-%H:%M:%S', time.gmtime(ts))

    # get the raw socket of the file
    sock = httpreq_file(API_HBMDUMP_GET, method=requests.get)

    if (sock is None):
        LOG("Error opening hbmdump data")
        return

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
##  logserver functionality
#

def parse_ports(s: str) -> List[int]:

    l = s.split(",")
    ret = []
    for p in l:
        try:
            n = int(p)
        except:
            DIE("Bad port list: %s" % s)
        ret.append(n)

    return ret

def tcp_server_socket(port: int) -> socket.socket:

    tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tsock.bind(("", port))
    tsock.listen(10)

    return tsock

def udp_server_socket(port: int) -> socket.socket:

    usock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    usock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = ("", port)
    usock.bind(server_address)

    return usock

def mklogger(address:str, mode: str) -> logging.Logger:

    path = "{}{}-{}".format(args.output, address, mode)

    logger = logging.getLogger("Rotating %s Log" % mode)
    logger.setLevel(logging.INFO)
    handler = logging.handlers.TimedRotatingFileHandler(path,
                                                       when="h",
                                                       interval=1,
                                                       backupCount=48)
    handler.terminator = ""
    logger.addHandler(handler)

    return logger

BOOT_RE = "\[[^\]]+\] \[kernel\] Welcome (back )?to FunOS"

def new_udp_log(address: str, fd: socket.socket) -> logging.Logger:
    return mklogger(address, "udp")

def new_tcp_log(address: str) -> logging.Logger:
    return mklogger(address, "tcp")

def handle_udp_data(fd, udp_logs):
    # read some data 
    (data, address) = fd.recvfrom(16<<10, socket.MSG_DONTWAIT)

    data = str(data.decode("ascii", errors='replace'))

    if (address not in udp_logs):
        LOG("New UDP log from %s" % (address, ))
        udp_logs[address] = new_udp_log(address[0], fd)
    else:
        # check if this is a reboot
        if(re.match(BOOT_RE, data) is not None):
            LOG("Detected FunOS UDP reboot on %s" % (address, ))
            udp_logs[address].handlers[0].doRollover()

    # log it
    udp_logs[address].info(data)

def handle_tcp_connect(fd: socket.socket, tcp_logs):
    # accept the connection
    conn, address = fd.accept()
    conn.setblocking(False)

    # make a new log
    LOG("New TCP log from %s on %s" % (address, conn.fileno()))
    tcp_logs[conn] = new_tcp_log(address[0])

def handle_tcp_data(fd, tcp_logs):
    # lookup the log
    assert(fd in tcp_logs.keys())
    close = False

    try:
        bs = fd.recv(16<<10, socket.MSG_DONTWAIT)
    except ConnectionError:
        close = True

    if (close or (len(bs) == 0)):
        # close it
        tcp_logs[fd].info("{Socket closed}")
        LOG("Closing TCP socket %s" % fd.fileno())
        del(tcp_logs[fd])
        fd.close()
        return

    tcp_logs[fd].info(str(bs.decode("ascii", errors='replace')))


def cmd_logserver() -> None:

    # parse the prot numbers
    udp_portnums = parse_ports(args.udp)
    tcp_portnums = parse_ports(args.tcp)

    # open all the server sockets
    udp_socks = [udp_server_socket(x) for x in udp_portnums]
    tcp_socks = [tcp_server_socket(x) for x in tcp_portnums]

    # open logs / tcp sockets
    tcp_logs: Dict[socket.socket, logging.Logger] = {}
    udp_logs: Dict[socket.socket, logging.Logger] = {}

    # main listen loop
    LOG("Listening on %d ports..." % (len(udp_socks) + len(tcp_socks)))
    while True:
        # make the list of sockets to care about
        rdlist: List[Any] = udp_socks + tcp_socks + list(tcp_logs.keys())

        # wait for activity 
        (r, w, x) = select.select(rdlist, [], [], 300.0)
        if len(r) == 0:
            print("tick")

        # decode it
        for fd in r:
            if (fd in udp_socks):
                handle_udp_data(fd, udp_logs)
            elif (fd in tcp_socks):
                handle_tcp_connect(fd, tcp_logs)
            elif (fd in tcp_logs.keys()):
                handle_tcp_data(fd, tcp_logs)
            else:
                raise RuntimeError("bad socket??")

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
    parser.set_defaults(dpuarg="1")

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
    parser.set_defaults(dpuarg="0")

    # Simple TCP and UDP logging server
    parser_logserver = subparsers.add_parser('logserver')
    parser_logserver.add_argument("-o", "--output", action="store",
                                default="./dpulog-",
                                help="prefix for logfiles")
    parser_logserver.add_argument("-T", "--tcp", action="store",
                                  default="6666",
                                  help="comma separated list of TCP ports to listen on")
    parser_logserver.add_argument("-U", "--udp", action="store",
                                  default="2661,6666",
                                  help="comma separated list of TCP ports to listen on")
    parser_logserver.set_defaults(func=cmd_logserver)


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

    if (args.dpuarg == "1" and args.dpu is None):
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
