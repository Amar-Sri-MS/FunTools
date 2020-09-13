#!/usr/bin/env python3
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
import tempfile
import hashlib
import urllib
import urllib.request
import urllib.error
import random
import shutil
import socket
import time
import uuid
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
--ignore-source     don't return the source binary on get (force retrieval)
--force-uuid        force uuid if a matching file exists
--metadata          dump metadata blob on get

Actions:

get\t\tFind a file with symbole for executable <filename>
pub[lish]\tPublish an executable to the executable catalog
"""

opts = None

NFS_ROOT = "/dogfood/users/cgray/excat"
HTTP_ROOT = "http://dochub.fungible.local/doc/dogfood/cgray/excat"
FILEMASK = 0o666
BLOCK_SIZE = 128 * 1024 # decent size payload

###
##  logging 
#

def LOG(msg):

    sys.stderr.write(str(msg) + "\n")

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
        path = path + "%02x/" % (uuid.bytes[i])

    return path

def choose_method(network):
    if (opts.network == "yes"):
        return network
    elif (opts.network == "no"):
        return "nfs"
    elif (opts.network != "auto"):
        raise RuntimeError("unknown network setting %s" % opts.network)

    if (os.path.exists(NFS_ROOT)):
        return "nfs"

    return network

def choose_publication_method():
    return choose_method("scp")

def choose_get_method():
    return choose_method("http")

def parse_uuid(suuid):
    try:
        uuuid = uuid.UUID(suuid)
    except ValueError:
        uuuid = None

    return uuuid

def uuid_from_file(fname):
    try:
        uuid = uuid_extract.uuid_extract(fname)
    except:
        uuid = None

    return uuid

def compress_file(source, dest):
    cmd = ["bzip2", "-c", source, ">", dest]
    cmd = " ".join(cmd)
    LOG("compressing %s -> %s" % (source, dest))
    os.system(cmd)
    os.chmod(dest, FILEMASK)

def uncompress_file(uuid, bzname):
    
    # make a destination filename
    fname = os.path.join(opts.tmpdir, str(uuid)+".excat")

    # if it's cached locally
    if (os.path.exists(fname)):
        return fname

    # uncompress it 
    cmd = ["bunzip2", "-c", bzname, ">", fname]
    cmd = " ".join(cmd)
    LOG("decompressing %s -> %s" % (bzname, fname))
    os.system(cmd)

    return fname

def read_web_file(url):
    LOG("Reading text URL %s" % url)

    s = ""
    u = urllib.request.urlopen(url)
    while True:
        buf = u.read(BLOCK_SIZE)
        if (not buf):
            break

        s += buf

    LOG("Read %d bytes from remote" % len(s))
    return s

def download_file(url, dest):

    LOG("Downloading file %s" % url)

    try:
        u = urllib.request.urlopen(url)
    except Exception as e:
        msg = "Failed to download file: %s" % e
        raise e

    f = open(dest, "wb")

    total_bytes = 0
    while True:
        buf = u.read(BLOCK_SIZE)
        if (not buf):
            break

        total_bytes += len(buf)
        f.write(buf)
        if (opts.verbose):
            sys.stderr.write("#")
            sys.stderr.flush()

    LOG("Downloaded %dkB" % (total_bytes / 1024))

    return True

def filemd5(fname):

    md5 = hashlib.md5()
    fl = open(fname, "rb")

    while (True):
        bytes = fl.read(16*1024)
        if (len(bytes) == 0):
            break
        md5.update(bytes)

    return md5.hexdigest()

###
##  get
#

def nfs_get(uuid):

    # just convert the uuid to an nfs filename
    nfspath = os.path.join(NFS_ROOT, mkrelpath(uuid))
    suuid = str(uuid)
    
    bzblob = os.path.join(nfspath, suuid + ".bz")
    mdblob = os.path.join(nfspath, suuid + ".json")

    if (not os.path.exists(bzblob)):
        raise RuntimeError("file not found: %s" % bzblob)

    if (opts.metadata):
        if (not os.path.exists(mdblob)):
            raise RuntimeError("file not found: %s" % bzblob)
        LOG(open(mdblob).readlines())

    return bzblob

def scp_get(uuid):
    pass

def http_get(uuid):

    # construct a URL
    urlpath = "%s/%s" % (HTTP_ROOT, mkrelpath(uuid))
    suuid = str(uuid)
    
    LOG("urlpath is %s" % urlpath)

    if (opts.metadata):
        mdurl = "%s%s.json" % (urlpath, uuid)
        s = read_web_file(mdurl)
        LOG(s)

    bzfile = os.path.join(opts.tmpdir, suuid + ".bz")
    
    # download the file if it's not local already
    if (not os.path.exists(bzfile)):
        bzurl = "%s%s.bz" % (urlpath, suuid)
        try:
            download_file(bzurl, bzfile)
        except urllib.error.HTTPError as e:
            if (e.code == 404):
                LOG("Download error: 404 not found")
                return None
            raise e

    # uncompress it, if it's not already
    fname = uncompress_file(uuid, bzfile)

    return fname


def do_search(uuid, path):
    if (path is None):
        return None
    if (not os.path.isdir(path)):
        return None

    LOG("Searching path %s" % path)

    fnames = os.listdir(path)
    for fname in fnames:
        fs = os.path.join(path, fname)
        if (not os.path.isfile(fs)):
            continue
        uu = uuid_extract.uuid_extract(fs, silent=True)
        if (uu is None):
            continue
        if (uu != uuid):
            continue
        # check it has symbols
        if (not file_has_symbols(fs)):
            continue

        # this file matches!
        LOG("Local file %s matches" % fs)
        return fs

    return None
    
# search local build paths etc.
def local_search_uuid(uuid):

    # see if there's something explicit
    fname = do_search(uuid, os.environ.get("FUNOS_SRC"))
    if (fname is not None):
        return fname

    if (os.environ.get("WORKSPACE") is not None):
        fname = do_search(uuid,
                          os.path.join(os.environ.get("WORKSPACE"),
                                       "FunOS/build"))
        if (fname is not None):
            return fname

    if (os.environ.get("EXCAT_SEARCH_PATH") is not None):
        toks = os.environ.get("EXCAT_SEARCH_PATH").split(":")
        for tok in toks:
            fname = do_search(uuid, tok)
            if (fname is not None):
                return fname
            
    return None


def do_get(uuid, fname):

    # short circuit if the file has symbols
    if ((not opts.ignore_source) and
        (fname is not None) and
        file_has_symbols(fname)):
        return fname

    # local search
    fname = local_search_uuid(uuid)
    if (fname is not None):
        return fname
    
    # find how to retrieve it
    method = choose_get_method()
    if (method == "nfs"):
        bzfname = nfs_get(uuid)
    elif (method == "scp"):
        bzfname = scp_get(uuid)
    elif (method == "http"):
        bzfname = http_get(uuid)
    else:
        raise RuntimeError("unknown get method: %s" % method)

    fname = bzfname
    if (fname is not None):
        # uncompress the bzip to make something useful
        fname = uncompress_file(uuid, fname)

    return fname

def get_action(fname):

    uuid = parse_uuid(fname)

    if (os.path.exists(fname) and (not opts.force_uuid)):
        # it's a file so query it
        uuid = uuid_from_file(fname)
        if (uuid is None):
            LOG("cannot retrieve uuid from file %s" % fname)
            sys.exit(1)
    elif (uuid is not None):
        # just use a raw uuid
        LOG("parsed UUID %s" % str(uuid))
        fname = None
    else:
        LOG("%s is neither a file nor a UUID" % fname)
        sys.exit(1)
      
    fname = do_get(uuid, fname)

    if (fname is None):
        print("Could not find local or published binary for uuid: %s" % uuid)
    
    return fname
    
def get_action_stdout(fname):
    # discover the UUID
    fname = get_action(fname)

    # output the actual filename
    print("%s" % fname)

    return 0

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

def metadata2str(metadata):
    return json.dumps(metadata, indent=4)

def save_metadata(metadata, fname):
    s = metadata2str(metadata)
    open(fname, "w").write(s)
    os.chmod(fname, FILEMASK)

def nfs_publish(metadata, fname, compress=True):

    # create the path, compress it in-place
    # and make it world readable

    omask = os.umask(0)
    if (not os.path.exists(metadata["nfspath"])):
        LOG("making path %s" % metadata["nfspath"])
        os.makedirs(metadata["nfspath"])
    
    # compress the file into it
    if (compress):
        absblob = os.path.join(metadata["nfspath"],
                               metadata["bzblob"])
        compress_file(fname, absblob)

        # update the metadat with the md5
        # for recipients
        metadata["bzmd5"] = filemd5(absblob)
    else:
        absblob = os.path.join(metadata["nfspath"],
                               os.path.basename(fname))
        shutil.copyfile(fname, absblob)
        os.chmod(fname, FILEMASK)

    # stash the metadata
    mdfile = os.path.join(metadata["nfspath"],
                          metadata["mdblob"])
    save_metadata(metadata, mdfile)

    os.umask(omask)

    LOG("published to %s" % metadata["nfspath"])

def wait_for_rx_ready(p):
    LOG("waiting for remote rx ready")
    while True:
        s = p.readline()
        if (s == ""):
            raise RuntimeError("EOF waiting for TX ready")
        LOG(s.strip())
        if (b"excat-pub-proxy: rx ready" in s):
            break

def drain_rx(p):
    while True:
        s = p.readline()
        if (s == b""):
            break
        LOG(s.strip())

# publish over scp via excat-scp-proxy
def scp_publish(metadata, fname):

    # original md5
    metadata["md5"] = filemd5(fname)

    tmpbz = os.path.join(tempfile.gettempdir(), metadata["bzblob"])
    compress_file(fname, tmpbz)

    # new md5
    metadata["bzmd5"] = filemd5(tmpbz)
       
    # pick a port in a 1k range -- use two so localhost works
    random.seed()
    iport = random.randint(20000, 21000)
    srcport  = str(iport)
    destport = str(iport+1)

    # run an ssh connection to get to the proxy. -R because we connect nc backwards
    cmd = ["ssh",
           "-L localhost:%s:localhost:%s" % (srcport, destport),
           "vnc-shared-06", "~cgray/fundev/FunTools/fungdbserver/excat-pub-proxy.py",
           "--version=0", "--port=%s" % destport, "-U", str(metadata["uuid"])]
    exp = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    if (exp is None):
        raise Runtimeerror("excat proxy fail")

    wait_for_rx_ready(exp.stderr)

    # send it the json file
    s = metadata2str(metadata)
    cmd = ["nc", "-w", "1", "localhost", srcport]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    if (p is None):
        raise RuntimeError("can't send metadata")
    LOG("sending metadata" )
    p.stdin.write(s.encode())
    p.stdin.close()
    r = p.wait()
    LOG("metadata returned %d" % r)

    # send it the bzfile
    wait_for_rx_ready(exp.stderr)
    LOG("sending large file")
    binfl = open(tmpbz)
    cmd = ["nc", "-w", "1", "localhost", srcport]
    p = subprocess.Popen(cmd, stdin=binfl)
    r = p.wait()
    LOG("bzfile returned %d" % r)

    os.remove(tmpbz)
    
    LOG("waiting for proxy to terminate")
    drain_rx(exp.stderr)
    exp.wait()

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
    uuid = uuid_from_file(fname)

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

def parse_args(dummy=False):
    parser = argparse.ArgumentParser(add_help=False)

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument("-v", "--verbose", action="count",
                        default=0)
    parser.add_argument("-n", "--network", action="store",
                        default="auto")
    parser.add_argument("-N", "--note", action="store",
                        default="")
    parser.add_argument("--ignore-source", action="store_true",
                        default=False)
    parser.add_argument("--force-uuid", action="store_true",
                        default=False)
    parser.add_argument("--metadata", action="store_true",
                        default=False)
    parser.add_argument("--tmpdir", action="store",
                        default=tempfile.gettempdir())
    parser.add_argument("-h", "--help", action="store_true")

    # Just parse everything else
    parser.add_argument('args', nargs='*',
                        help=ARGS_HELP)

    if (not dummy):
        args = parser.parse_args()
        if (args.help or (len(args.args) == 0)):
            usage()
    else:
        args = parser.parse_args([])


    uuid_extract.VERBOSITY = args.verbose

    global opts
    opts = args

GET_ACTIONS = ["get", "find"]
PUB_ACTIONS = ["pub", "publish", "put"]

VALID_ACTIONS = GET_ACTIONS + PUB_ACTIONS

def main():
    parse_args()

    arglist = opts.args
    assert(len(arglist) > 0)

    action = arglist[0].lower()
    if (action not in VALID_ACTIONS):
        if (len(arglist) == 0):
            usage()
        r = get_action_stdout(arglist[0])
        sys.exit(r)


    # at least need a filename
    arglist = arglist[1:]
    if (len(arglist) == 0):
        usage()
    
    if (action in GET_ACTIONS):
        if (len(arglist) > 1):
            usage();
        r = get_action_stdout(arglist[0])
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
