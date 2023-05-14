#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish or change retention for files from a build directory or
a range of files from FunSDK builds
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

FUNOS_TGZ_FLAVOURS = [
    "funos~%s.tgz",
    "funos~%s-release.tgz",
    "funos~%s-emu.tgz",
    "funos~%s-qemu.tgz"
]

CHIPS = ["f1", "s1", "f1d1", "s2"]
PKGS = ["core", "storage", "pkgdemo"]

FUNOS_FLAVOURS = [
    "funos-{pkg}-{chip}",
    "funos-{pkg}-{chip}-release",
    "funos-{pkg}-{chip}-emu",
    "funos-{pkg}-{chip}-emu-release",
    "funos-{pkg}-{chip}-qemu",
    "funos-{pkg}-{chip}-qemu-release",
]

# build the full compliment of possible FunOS binaries to publish
FUNOS_BINARIES = []
for chip in CHIPS:
    d = {"chip": chip}
    for pkg in PKGS:
        d["pkg"] = pkg
        FUNOS_BINARIES += [flav.format(**d) for flav in FUNOS_FLAVOURS]

FUNOS_TGZS = sum([[flav % chip for chip in CHIPS] for flav in FUNOS_TGZ_FLAVOURS], [])

PATHS = [ "./",
          os.path.dirname(os.path.abspath(__file__))
]

ACTION_TO_STR = {
    "pub": "publishing",
    "ret": "retaining"
}

def excat_py():
    for path in PATHS:
        excat = os.path.join(path, "excat.py")
        if (os.path.exists(excat)):
            return excat

    raise RuntimeError("could not find excat.py")

def scan_path(binpath):

    # check it exists
    if (not os.path.exists(binpath)):
        raise RuntimeError("specified path does not exist: %s" % binpath)

    # scrape any binaries
    for bin in FUNOS_BINARIES:
        p = os.path.join(binpath, bin)
        if (not os.path.exists(p)):
            continue

        verb = ACTION_TO_STR[opts.action]
        print("%s file %s" % (verb.capitalize(), p))

        cmd = [excat_py(), opts.action, p]
        if opts.retention:
            cmd.extend(["--retention", opts.retention])
        cmd = " ".join(cmd)
        os.system(cmd)
        print("Done %s file %s" % (verb, p))

def scan_tgz(tgzpath):
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
    scan_path(binpath)

    # clean it up
    print("Cleaning up %s" % ldir)
    shutil.rmtree(ldir)
    

def scan_os_path(sdkpath, bld):

    for tgz in FUNOS_TGZS:
        path = os.path.join(sdkpath, bld, tgz)
        scan_tgz(path)

def scan_sdk(sdkpath):
    print("Scanning sdk %s" % sdkpath)
    scan_os_path(sdkpath, "Linux")
    scan_os_path(sdkpath, "Darwin")


###
##  main
#

def usage():
    LOG(ARGS_HELP.format(sys.argv[0]))
    sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--dir", help="A specific directory containing FunOS binaries",
                        action="store", default=None)
    parser.add_argument("--sdk-dir", help="An SDK directory to search for FunOS binaries",
                        action="store", default=None)
    parser.add_argument("--action", default="pub", choices=["pub", "ret"],
                        help="Publish (pub) or change retention period (ret)")
    parser.add_argument("-r", "--retention", help="Retention period")

    args = parser.parse_args()

    return args

def main():
    global opts
    opts = parse_args()

    if (opts.dir is not None):
        scan_path(opts.dir)
    elif (opts.sdk_dir is not None):
        scan_sdk(opts.sdk_dir)
    else:
        print("Need dir or sdk-dir to process")
        sys.exit(1)

    print("done")


###
## entrypoint
#
if __name__ == "__main__":
    main()
