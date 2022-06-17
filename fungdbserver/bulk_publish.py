#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish files from a build directory or a range of files from FunSDK builds
"""

import argparse
import tempfile
import shutil
import json
import sys
import os

opts = None

###
##  publish
#

FUNOS_TGZS = [
    "funos.mips64-base.tgz",
    "funos.mips64-extra.tgz",
]

CHIPS = ["f1", "s1", "f1d1", "s2"]

FUNOS_FLAVOURS = [
    "funos-%s",
    "funos-%s-release",
    "funos-%s-emu",
    "funos-%s-emu-release",
    "funos-%s-qemu",
    "funos-%s-qemu-release",
]

FUNOS_BINARIES = sum([[flav % chip for chip in CHIPS] for flav in FUNOS_FLAVOURS], [])

PATHS = [ "./",
          os.path.dirname(os.path.abspath(__file__))
]

def excat_py():
    for path in PATHS:
        excat = os.path.join(path, "excat.py")
        if (os.path.exists(excat)):
            return excat

    raise RuntimeError("could not find excat.py")

def publish_path(binpath):

    # check it exists
    if (not os.path.exists(binpath)):
        raise RuntimeError("specified path does not exist: %s" % binpath)

    # scrape any binaries
    for bin in FUNOS_BINARIES:
        p = os.path.join(binpath, bin)
        if (not os.path.exists(p)):
            continue
        print("Publishing file %s" % p)
        cmd = [excat_py(), "pub", p]
        cmd = " ".join(cmd)
        os.system(cmd)
        print("Done publishing file %s" % p)

def publish_tgz(tgzpath):
    # see if it exists
    if (not os.path.exists(tgzpath)):
        return

    print("Checking tgz %s" % tgzpath)
    ldir = tempfile.mkdtemp()

    # decompress it
    cmd = ["tar", "-C", ldir, "-zxf", tgzpath]
    cmd = " ".join(cmd)
    os.system(cmd)

    binpath = os.path.join(ldir, "bin")
    publish_path(binpath)

    # clean it up
    print("Cleaning up %s" % ldir)
    shutil.rmtree(ldir)
    

def publish_os_path(sdkpath, bld):

    for tgz in FUNOS_TGZS:
        path = os.path.join(sdkpath, bld, tgz)
        publish_tgz(path)

def publish_sdk(i):

    print("Publishing sdk %s" % i)

    sdkpath = "/project/users/doc/jenkins/funsdk/%s" % i

    publish_os_path(sdkpath, "Linux")
    publish_os_path(sdkpath, "Darwin")

###
##  bundle searching
#

BUNDLE_ROOT = "/project/users/doc/jenkins/master"
PROPS_FILE = "bld_props.json"

def check_bundle(i):
    path = os.path.join(BUNDLE_ROOT, opts.flavour, str(i), PROPS_FILE)

    if (not os.path.exists(path)):
        return None

    d = json.loads(open(path).read())

    return d["components"]["funsdk"]

###
##  main
#

def usage():
    LOG(ARGS_HELP.format(sys.argv[0]))
    sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--count", help="Number of SDKs to scrape (default=1)", type=int, default=1)
    parser.add_argument("--min-sdk", help="Minimum SDK number", type=int, default=0)
    parser.add_argument("--max-sdk", help="Maximum SDK number", type=int, default=None)
    parser.add_argument("--dir", help="A specific directory", action="store", default=None)
    parser.add_argument("--min-bundle", help="Minimum bundle number", type=int, default=0)
    parser.add_argument("--max-bundle", help="Maximum bundle number", type=int, default=None)
    parser.add_argument("-f", "--flavour", help="Bundle flavour", default="fs1600")
    parser.add_argument("-r", "--retention", help="Retention period")

    args = parser.parse_args()

    return args

def main():
    global opts
    opts = parse_args()

    if (opts.dir is not None):
        publish_path(opts.dir)
    elif (opts.max_sdk is not None):
        mx = opts.max_sdk
        if (opts.min_sdk >0):
            mn = opts.min_sdk
        else:
            mn = mx - opts.count + 1

        assert(mn > 0)

        for i in range(mn, mx+1):
            publish_sdk(i)
    elif (opts.max_bundle is not None):
        mx = opts.max_bundle
        if (opts.min_bundle >0):
            mn = opts.min_bundle
        else:
            mn = mx - opts.count + 1

        assert(mn > 0)

        s = set([])
        for i in range(mn, mx+1):
            s.add(check_bundle(i))
        if (None in s):
            s.remove(None)
        es = list(s)
        es.sort(reverse=True)
        for e in es:
            publish_sdk(e)

        sys.exit(0)
    else:
        print("Need SDK max, bundle max or a directory to process")
        sys.exit(1)

    print("done")


###
## entrypoint
#
if __name__ == "__main__":
    main()
