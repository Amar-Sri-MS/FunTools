#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert a generic .gz file to an indexed .gz file
 
static check:
% mypy myfile.py
 
format:
% python3 -m black gz2idgz.py
"""
from typing import List, Optional, Type, Dict, Any, Tuple
import argparse
import locale
import gzip
import idzip # type: ignore
import sys
import os
 
###
##  main
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
 
    # two simple arguments
    parser.add_argument("src", help="Source gzip")
    parser.add_argument("dest", nargs="?", help="Dest idgzip [optional]",
                        default=None)
 
    args: argparse.Namespace = parser.parse_args()
    return args
 
def main() -> int:
    args: argparse.Namespace = parse_args()

    if (args.dest is None):
        args.dest = args.src + ".idgz"

    if (os.path.exists(args.dest)):
        print("Error: destination file %s exists" % args.dest)
        sys.exit(1)
        
    print("Convert %s -> %s" % (args.src, args.dest))

    # open src and dest
    src = gzip.open(args.src)
    idzip.Writer.enforce_extension = False
    dest = idzip.Writer(args.dest)

    # add all the data
    nbytes = 0
    while (True):
        data = src.read(10*1024*1024)
        if (len(data) == 0):
            break
        dest.write(data)
        nbytes += len(data)

    print("Converted {:,} bytes".format(nbytes))
    
    return 0
 
###
##  entrypoint
#
if __name__ == "__main__":
    main()
