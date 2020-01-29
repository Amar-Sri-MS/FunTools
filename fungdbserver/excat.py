#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
excat (Executable Catalogue) -- publish and retreieve ELF files
with build notes into dochub

modes:

pub[lish]: copy files to dochub via cp/scp
get: find a file via /dogfood or http://dochub
"""
from __future__ import print_function
import uuid_extract
import subprocess
import argparse
import datetime
import socket
import json
import sys
import os

ARGS_HELP =  \
"""usage: {0} [get] <filename>
       {0} pub[lish] <filename>

Publish and retrive executable file symbols to the central
ExCat (Executable Catalogue) repository. Executables are indexed
via their uniquie build-id.

Options:
-v, --verbose       extra logging information
-n N, --network=N   specify network access:
                    yes:  also go via scp/http
                    no:   always access via nfs mounts
                    auto: access network based on machine state [default] 
-N <note>, --note   textual note to add to the metadata blob when publishing
Actions:

get\t\tFind a file with symbole for executable <filename>
pub[lish]\tPublish an executable to the executable catalog
"""

opts = None

NFS_ROOT = "/dogfood/users/cgray/excat"
HTTP_ROOT = "http://dochub.fungible.local/doc/dogfood/cgray/excat/"
FILEMASK = 0o666

###
##  logging 
#

def LOG(msg):

    sys.stderr.write(msg + "\n")

def VERBOSE(msg, level=1):

    if (opts.verbose >= level):
        LOG(msg)

###
##  helpers
# 

def file_has_symbols(fname):

    # run a shell command and get the output
    cmd = ["file", fname]
    output = uuid_extract.output4command(cmd)

    if ("not stripped" in output):
        return True

    return False

PREFIX_BYTES = 4
"82591dec-480a-d7e0-adff-ef78598a2bc1 -> 82/59/1e/ec/"
def mkrelpath(uuid):

    path = ""
    for i in range(PREFIX_BYTES):
        path = path + "%02x/" % (ord(uuid.bytes[i]))

    return path

def choose_publication_method():
    return "nfs"

###
##  get
#

def get_action(fname):
    pass

###
##  publish a binary
#


def mkmetadata(uuid, fname):
    d = {}

    d["fname"] = fname
    d["uuid"] = str(uuid)
    d["bzblob"] = d["uuid"] + ".bz"
    d["mdblob"] = d["uuid"] + ".json"
    d["timestamp"] = str(datetime.datetime.now())
    d["hostname"] = str(socket.gethostname())
    d["uname"] = " ".join(os.uname())
    d["relpath"] = mkrelpath(uuid)
    d["nfspath"] = os.path.join(NFS_ROOT, d["relpath"])
    d["user"] = os.environ.get("USER", "unknown")
    d["note"] = opts.note

    return d

def compress_file(source, dest):
    cmd = ["bzip2", "-c", source, ">", dest]
    cmd = " ".join(cmd)
    LOG("compressing %s -> %s" % (source, dest))
    os.system(cmd)
    os.chmod(dest, FILEMASK)

def save_metadata(metadata, fname):

    s = json.dumps(metadata, indent=4)
    open(fname, "w").write(s)
    os.chmod(fname, FILEMASK)


def nfs_publish(metadata, fname):

    # create the path, compress it in-place
    # and make it world readable

    omask = os.umask(0)
    if (not os.path.exists(metadata["nfspath"])):
        LOG("making path %s" % metadata["nfspath"])
        os.makedirs(metadata["nfspath"])
    
    # compress the file into it
    absblob = os.path.join(metadata["nfspath"],
                           metadata["bzblob"])
    compress_file(fname, absblob)

    # stash the metadata
    mdfile = os.path.join(metadata["nfspath"],
                          metadata["mdblob"])
    save_metadata(metadata, mdfile)

    os.umask(omask)

    LOG("published to %s" % metadata["nfspath"])
    

def do_publish(uuid, fname):

    metadata = mkmetadata(uuid, fname)

    # decide which kind of publication
    method = choose_publication_method()
    if (method == "nfs"):
        nfs_publish(metadata, fname)
    elif (method == "scp"):
        scp_publish(metadata, fname)
    else:
        raise RuntimeError("unknown publication method: %s" % method)

def pub_action(fname):

    # get the file UUID
    try:
        uuid = uuid_extract.uuid_extract(fname)
    except:
        uuid = None

    if (uuid is None):
        LOG("error: failed to get UUID for file %s" % fname)
        sys.exit(1)

    # make sure it actually has symbols
    if (not file_has_symbols(fname)):
        LOG("error: file has no symbols, cannot publish: %s" % fname)
        sys.exit(1)

    LOG("UUID %s ok to publish" % uuid)

    # the actual publish step
    do_publish(uuid, fname)


###
##  main
#

def usage():
    LOG(ARGS_HELP.format(sys.argv[0]))
    sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(add_help=False)

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument("-v", "--verbose", action="count",
                        default=0)
    parser.add_argument("-n", "--network", action="store",
                        default="auto")
    parser.add_argument("-N", "--note", action="store",
                        default="")
    parser.add_argument("-h", "--help", action="store_true")

    # Just parse everything else
    parser.add_argument('args', nargs='*',
                        help=ARGS_HELP)

    args = parser.parse_args()

    if (args.help or (len(args.args) == 0)):
        usage()

    uuid_extract.VERBOSITY = args.verbose

    return args

GET_ACTIONS = ["get", "find"]
PUB_ACTIONS = ["pub", "publish", "put"]

VALID_ACTIONS = GET_ACTIONS + PUB_ACTIONS

def main():
    global opts
    opts = parse_args()

    arglist = opts.args
    assert(len(arglist) > 0)

    action = arglist[0].lower()
    if (action not in VALID_ACTIONS):
        if (len(arglist) == 0):
            usage()
        r = get_action(arglist[0])
        sys.exit(r)


    # at least need a filename
    arglist = arglist[1:]
    if (len(arglist) == 0):
        usage()
    
    if (action in GET_ACTIONS):
        if (len(arglist) > 1):
            usage();
        r = get_action(arglist[0])
    elif (action in PUB_ACTIONS):
        if (len(arglist) > 1):
            usage();
        r = pub_action(arglist[0])
    else:
        usage()
    
    sys.exit(r)
 
###
## entrypoint
#
if __name__ == "__main__":
    main()
