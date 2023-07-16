#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fixup FunOS SDK headers

General concept:

Three main invocations:

1. Re-shuffle the FunOS headers to sdk_include/
    1.1 Write out a json descriptor of what files got moved where
    2.2 Allow committing to git and fixing of Makefile, templates etc.
2. Fixup the include lines inside FunOS
3. Fixup the include lines in clients

 
static check:
% mypy myfile.py
 
format:
% python3 -m black myfile.py
"""
from typing import List, Optional, Type, Dict, Any, Tuple
import argparse
import sys
import shutil
import subprocess
import os
import json
import glob
import re

###
##  log functions
#
 
VERBOSITY: int = 0
    
def LOG(msg: str, level: int = 0) -> None:
    if(level <= VERBOSITY):
        print(msg)

def VERBOSE(msg: str) -> None:
    LOG(msg, 1)

def DEBUG(msg: str) -> None:
    LOG(msg, 2)

###
##  Renaming files in FunOS
#

# list of make rules to scrape and their destinations
# make the all headers last so files default to there if in both lists
TARGETS: List[Tuple[str, str]] = [
    (".ALL_PRIVATE_HEADERS", "FunOS/legacy"),
    (".ALL_DPUSIM_HEADERS", "dpusim"),
    (".ALL_SDK_HEADERS", "FunOS"),
]

INCROOT = "sdk_include"
    

def rename_file_for_sdk(fname: str) -> str:
    # strip "platform/include" off platform files
    if (fname.startswith("platform/include/")):
        fname = fname[17:]
    # strip "include" off other files
    elif (fname.startswith("include/")):
        fname = fname[8:]

    return fname

def do_rename(args: argparse.Namespace) -> None:
    LOG("Renaming files in FunOS")

    to_rename: Dict[str, str] = {}

    # clear out the existing sdk_dir, if sure
    if (os.path.exists(INCROOT)):
        if (args.sure):
            LOG("Clearing out " + args.sdk_dir)
            shutil.rmtree(args.sdk_dir)
        else:
            LOG("Skipping clear of " + args.sdk_dir)
    else:
        LOG(f"{INCROOT} does not exist")

    # for each TARGET, run make and collect the output, split it on whitespace
    for target in TARGETS:
        cmd = ["make", target[0]]
        LOG(" ".join(cmd))
        output: str = subprocess.check_output(cmd).decode("utf-8")
        DEBUG(output)
        # split the output on whitespace
        files: List[str] = output.split()
        # for each file, add it to the to_rename dict
        for file in files:
            # clean up for paths
            if (file.startswith("./")):
                file = file[2:]

            DEBUG(f"Found file {file}")

            # clean up for better names
            new = rename_file_for_sdk(file)            
            new = os.path.join(target[1], new)

            to_rename[file] = new
    
    dirset = set()
    # for each file, create a path and rename it
    for old, new in to_rename.items():
        new = os.path.join(INCROOT, new)
        would: str = "Would " if not args.sure else ""
        VERBOSE(f"{would}rename " + old + " to " + new)
        # add the directory to the set
        dirset.add(os.path.dirname(new))
        if args.sure:
            os.makedirs(os.path.dirname(new), exist_ok=True)
            # use git to rename the file
            cmd = ["git", "mv", old, new]
            LOG(" ".join(cmd))
            subprocess.check_output(cmd)

    # print all the directories we in dirset
    dirlist: List[str] = sorted(dirset)
    for dir in dirlist:
        print(f"Creating sdk_include path {dir}")  
    
    # write out the json descriptor
    with open(args.rename_json, "w") as f:
        json.dump(to_rename, f, indent=4)

    LOG("Done renaming files in FunOS")

###
##  Fixing up files in FunOS or clients
#

def update_includes(pincludes: Dict[str, str], old: str, new: str) -> None:
    DEBUG(f"\tAdding  {old} -> {new}")
    pincludes[old] = new
                        
def add_alts_for_rename(pincludes: Dict[str, str], new: str, old: str,
                        fix_locals: bool) -> None:
    
    # Externals: add all the possible symlinks
    update_includes(pincludes, os.path.join("FunOS", old), new)
    update_includes(pincludes, os.path.join("FunOSPrivate", old), new)
    update_includes(pincludes, os.path.join("private", old), new)
    update_includes(pincludes, os.path.join("dpusim", old), new)

    if (fix_locals or old.startswith("platform/")):
        # just add the raw name
        update_includes(pincludes, old, new)

    if (old.startswith("platform/include")):
        # strip the prefix
        plat = old[17:]
    
        # add all the short versions
        add_alts_for_rename(pincludes, new, plat, fix_locals)
    
            
PREFIXES: List[str] = ["", "include", "hw/pfm", "hw/hsu", "platform/include"]

def fixup_file(fname: str, renames: Dict[str, str], pincludes: Dict[str, str],
               args: argparse.Namespace) -> None:

    if (fname.startswith(".git")):
        return  

    if (fname.startswith("./")):
        fname = fname[2:]
    
    VERBOSE(f"Checking file {fname}")

    # strip the sdk_include prefix
    ofname = fname
    if (ofname.startswith("sdk_include")):
        fname = fname[12:]
        for old, new in renames.items():
            if (new == fname):
                VERBOSE(f"\tUsing old name for relative headers: {old}")
                fname = old
                break

    # read the file
    with open(ofname, "r") as f:
        fbuf = f.read()

    # regex for all the includes:
    # #include "foo.h" or #include <foo.h>
    #capturing the quote or bracket
    inc_re = re.compile(r'(#\s*include)\s+([<"])([^>"]+)([>"])')

    # get all the matches
    matches = inc_re.finditer(fbuf)
    
    # for each match
    for match in reversed(list(matches)):
        # make sure the brackets or quotes match
        assert((match[2] == '"' and match[4] == '"')
               or (match[2] == '<' and match[4] == '>'))

        # get the include name
        can_rel = (match[2] == '"')
        inc = match[3]

        # clean up the include name
        while "//" in inc:
            inc = inc.replace("//", "/")
        
        VERBOSE(f"\tIn {fname} found include {inc} as {match[2]}")
        
        # generate a list of possible names
        pnames = []
        for prefix in PREFIXES:
            pnames.append(os.path.join(prefix, inc))
            
        if (can_rel):
            # if it's relative, make it absolute
            absinc = os.path.normpath(os.path.join(os.path.dirname(fname), inc))
            VERBOSE(f"\tResolved to absolute {inc}")
            pnames.append(absinc)

        # see if any of them are in pincludes
        inc = None
        for pname in pnames:
            if (pname in pincludes):
                VERBOSE(f"\tHeader {pname} is in rename list")
                inc = pname
                break
            else:
                VERBOSE(f"\tHeader {pname} is not in rename list")
                continue
            
        if (inc is None):
            # if not, skip it
            VERBOSE(f"\tNo renamed header found, skipping")
            continue

        # get the new name
        new = pincludes[inc]
        
        # replace regex match with new name
        i0 = match.start(1)
        i3 = match.end(4)
        sub = f"#include <{new}>"
        DEBUG(f"\tReplacing {fbuf[i0:i3]} with {sub}")        
        fbuf = fbuf[:i0] + sub + fbuf[i3:]

    # write the file back out
    if (args.sure):
        with open(ofname, "w") as f:
            f.write(fbuf)
    
SUFFIXES: List[str] = [".c", ".h", ".s", ".g", ".jinj",
                       "_h.tmpl", "_c.tmpl", "fep_filter.py"]
def do_fixup(args: argparse.Namespace) -> None:
    LOG("Fixing up includes")

    # load the json descriptor
    with open(args.rename_json, "r") as f:
        renames: Dict[str, str] = json.load(f)

    # for each rename, generate the list of all possible includes that
    # could have lead to it and create a dictionary of those
    # includes to the new name
    pincludes: Dict[str, str] = {}
    for old, new in renames.items():
        add_alts_for_rename(pincludes, new, old, args.fix_locals)

    LOG(f"Found {len(pincludes)} possible includes")
    
    # search each .c and .h file in the source tree for includes
    for root, dirs, files in os.walk("."):
        for file in files:
            VERBOSE(f"Checking file {file}")
            for suffix in SUFFIXES:
                if (file.endswith(suffix)):
                    file = os.path.join(root, file)
                    fixup_file(file, renames, pincludes, args)
                    break
                     

    LOG("Done fixing up includes")

###
##  parse_args
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
 
    # Argument "--rename" sets args.mode to "rename"
    parser.add_argument("--rename", action="store_const", dest="mode",
                        const="rename")
 
    # Argument "--fixup" sets args.mode to "fixup"
    parser.add_argument("--fixup", action="store_const", dest="mode",
                        const="fixup")

    # Tristate argument (none, true, false) for whether we're in FunOS
    parser.add_argument("--fix-locals", action="store_const", dest="fix_locals",
                        const=True, default=None)
 
    # --sure command line argument
    parser.add_argument("--sure", action="store_true", dest="sure",
                        default=False)

    # --rename-json command line argument
    parser.add_argument("--rename-json", action="store", dest="rename_json",
                        default="renames.json")

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")
 
    args: argparse.Namespace = parser.parse_args()

    global VERBOSITY
    VERBOSITY = args.verbose
    
    if (args.fix_locals is None):
        # if --fix-locals is not specified, try to guess
        args.fix_locals = os.path.basename(os.getcwd()) == "FunOS"
        LOG(f"Guessing --fix-locals={args.fix_locals}")

    return args
 
###
##  main
#
def main() -> int:
    args: argparse.Namespace = parse_args()
    
    if (args.mode == "rename"):
        do_rename(args)
    elif (args.mode == "fixup"):
        do_fixup(args)
    else:
        print("must specify --rename or --fixup")
        return 1

    return 0
 
###
##  entrypoint
#
if __name__ == "__main__":
    sys.exit(main())
