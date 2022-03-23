#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Push hbmdump files to an s3 server
"""

import argparse
import os
import sys

## find the s3util in the sdk
SCRIPTDIR = os.path.dirname(sys.argv[0])
SDKDIR = os.environ.get("SDKDIR",
                        os.environ.get("WORKSPACE",
                                       SCRIPTDIR + "/../..") + "/FunSDK")
sys.path.append(os.path.join(SCRIPTDIR, "../scripts"))
sys.path.append(os.path.join(SDKDIR, "bin/scripts"))

import s3util

HOST = "cgray-vm0:9000"
BUCKET = "hbmdumps"
    
###
##  upload a file
#
def upload_file(filename):
    # upload the file
    s3util.upload_file(filename, HOST, BUCKET)

    # remove the file
    print("File uploaded, removing %s" % filename)
    os.remove(filename)
    
###
##  upload a progress report json
#
def upload_progress(filename, progress):

    # make a progress dict
    d = {"prefix": filename, "pct": progress}

    s3util.upload_json(d, HOST, BUCKET, filename+"-progress.json")


###
##  main
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
 
    # Required positional argument
    parser.add_argument("filename", help="File to upload")
 
    # If it's still downloading
    parser.add_argument("-p", "--progress", action="store", default=None)

    args: argparse.Namespace = parser.parse_args()
    return args
 
def main() -> int:
    args: argparse.Namespace = parse_args()

    if (args.progress is None):
        upload_file(args.filename)
    else:
        upload_progress(args.filename, args.progress)
        
    return 0
 
###
##  entrypoint
#
if __name__ == "__main__":
    main()
