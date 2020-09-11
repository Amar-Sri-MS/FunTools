#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
remote publish proxy for excat.

expects to be run on the far size of of an ssh port
with tunneled ports to netcat files through
"""
from __future__ import print_function
import uuid_extract
import subprocess
import argparse
import tempfile
import excat
import uuid
import json
import time
import sys
import os

# global options
opts = None

###
##  logging 
#

def LOG(msg):
    sys.stderr.write("excat-pub-proxy: " + msg + "\n")

def VERBOSE(msg, level=1):

    if (opts.verbose >= level):
        LOG(msg)

###
##  proxy functionality
#

def do_proxy_v0():
    
    LOG("running excat pub proxy v0")

    # netcat the metadata
    sport = "%s" % opts.port
    sjson = "%s.json" % str(opts.uuid)
    sbzfile = "%s.bz" % str(opts.uuid)

    sjson = os.path.join(tempfile.gettempdir(), sjson)
    sbzfile = os.path.join(tempfile.gettempdir(), sbzfile)

    # get the json metadata
    cmd = ["nc", "-l", "localhost", sport]
    fljson = open(sjson, "w")
    LOG("receive metadata: %s" % sjson)
    LOG(" ".join(cmd))
    p = subprocess.Popen(cmd, stdout=fljson)
    LOG("rx ready") # important signal to the other side
    r = p.wait()
    fljson.close()
    if (r != 0):
        raise RuntimeError("json download failed")

    # get the actual binary
    LOG("receive binary: %s" % sbzfile)
    cmd = ["nc", "-l", "localhost", sport]
    flbzfile = open(sbzfile, "w")
    LOG(" ".join(cmd))
    p = subprocess.Popen(cmd, stdout=flbzfile)
    LOG("rx ready")  # important signal to the other side
    r = p.wait()
    if (r != 0):
        raise RuntimeError("bzblob download failed")

    # call it done for now
    LOG("files received, validating")
    metadata = json.load(open(sjson))

    # if the other end just silently didn't send the whole file,
    # we don't want to publish it
    md5 = excat.filemd5(sbzfile)
    if (md5 != metadata["bzmd5"]):
        raise RuntimeException("executable file transfer error - bad md5")
    else:
        LOG("executable md5 OK: %s" % md5)

    LOG("publishing file")
    excat.nfs_publish(metadata, sbzfile, compress=False)

    # clean up
    LOG("cleaning up...")
    os.remove(sjson)
    os.remove(sbzfile)
    LOG("done")

def do_proxy():

    # for now, only a single version
    assert(opts.version == 0)

    do_proxy_v0()

###
##  main entrypoint
#

def parse_args():

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-v", "--verbose", action="count",
                        default=0)
    parser.add_argument("-V", "--version", action="store", type=int,
                        required=True, help="proxy protocol version")
    parser.add_argument("-P", "--port", action="store",
                        type=int, required=True,
                        help="port for netcat to listen to")
    parser.add_argument("-U", "--uuid", action="store",
                        type=uuid.UUID, required=True,
                        help="uuid of the executable")

    args = parser.parse_args()

    return args

def main():
    # parse the arge
    global opts
    opts = parse_args()

    do_proxy()
    LOG("done")

if __name__ == '__main__':
    main()
