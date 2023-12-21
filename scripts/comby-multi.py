#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comby wrapper to make it easy to replace code in C and header files.

usage:

    comby-multi.py -d my_rules.json <path1> [[file1] path2] ...

Applies rules in "my_rules.json" to all specified files and recursive
searches of all subdirectories for .c and .h files.

The json rules is a list of dictionaries with match/replace pairs, eg:

    [
       {
            "match": "pattern(:[args])",
            "rewrite": "substitute(:[args])",
            "type": "rewrite"
       },
       {
            "match": "oldfuncname",
            "rewrite": "newfuncname",
            "type": "function"
        },
    ]

Type "type" field specifies the action of the match and rewrite. "rewrite" rules
are literal comby rules. "function" rules are special rules that match things
that look like functions, eg:

     x = oldfuncname(y);
     y = oldfuncname (y);
     y = oldfuncname(a,
                b, c
                d /* comment */ );

comby-multi takes care of turning the function name into a flexible comby
rewrite string for you.

All evaluations are done in parallel with many worker threads because comby
is slow. Progress is reported as files are processed.
                
static check:
% mypy myfile.py
 
format:
% python3 -m black myfile.py
"""
from typing import List, Optional, Type, Dict, Any, Tuple
import argparse
import os
import subprocess
import json
import multiprocessing
import queue

###
##  logging
#

VERBOSITY: int = 0

def LOG(s: str, verbosity:int = 0) -> None:
    if verbosity <= VERBOSITY:
        print(s)

def VERBOSE(s: str) -> None:
    LOG(s, 1)

def DEBUG(s: str) -> None:
    LOG(s, 2)


###
##  descriptors
#

class CombyDesc:
    def __init__(self, jsdesc: Dict[str, Any]) -> None:
        self.match: str = jsdesc["match"]
        self.rewrite: str = jsdesc["rewrite"]
        self.add_includes: Optional[str] = jsdesc.get("add_includes", [])

    def comby_fixup(self, path: str, print_only: bool) -> None:

        # assemble the comby command
        cmd: List[str] = ["comby"]
        if (not print_only):
            cmd += ["-in-place"]

        cmd += ["-timeout", "300"]
        cmd += [self.match]
        cmd += [self.rewrite]
        cmd += [path]

        # run the command
        DEBUG("\t" + " ".join(cmd))
        subprocess.run(cmd, check=True)

    # see about headers
    def add_include(path: str, include: str, print_only: bool) -> None:
        DEBUG(f"\tadding include {include} to {path}")

        with open(path, "r+") as f:
            lines = f.readlines()

        # find the first include
        first:int = -1
        for lineno in range(len(lines)):
            if ("#include" in line):
                first = lineno
                break

        if (first == -1):
            LOG(f"\t\t{path} has no includes! ignoring addition")
            return

        # find a gap of 20 lines to the next include
        for lineno in range(first, len(lines)):
            if (lineno - last > 20):
                gap = lineno
                break

            if ("#include" in line):
                last = lineno

    def do_fixups(self, path: str, print_only: bool) -> None:
        self.comby_fixup(path, print_only)

        # FIXME: enable headers
        #for include in self.add_includes:
        #    self.add_include(path, include, print_only)

class CombyFunctionCallDesc(CombyDesc):
    def __init__(self, jsdesc: Dict[str, Any]) -> None:
        self.match = self.fixup_match(jsdesc["match"])
        self.rewrite = self.fixup_rewrite(jsdesc["rewrite"])
        self.add_includes = jsdesc.get("add_includes", [])

    def fixup_match(self, match: str) -> str:
        # :[h0~[->.]*]:[~\b{match}](:[args])

        # prefix to filter out "." and "->"
        prefix = ":[prefix~[->.]*]"

        # name starting on a whole word
        func = f":[~\\b{match}]"

        # optional whitespace
        ws = ":[~\\s*]"

        # arguments
        args = "(:[args])"
        return prefix + func + ws + args
    
    def fixup_rewrite(self, rewrite: str) -> str:
        # FIXME: What was this?!
        # return f":[prefix]_legacy_{rewrite}_unsafe(:[args])"
        return f":[prefix]{rewrite}(:[args])"

DESC_HANDLERS: Dict[str, Type[CombyDesc]] = {
    "rewrite": CombyDesc,
    "function": CombyFunctionCallDesc
}

def jsdesc2desc(jsdesc: List[Dict[str, Any]]) -> List[CombyDesc]:
    desc: List[CombyDesc] = []

    # validate that the desciptor is a list of lists, each with two strings
    if not isinstance(desc, list):
        raise RuntimeError("descriptor must be a list")
    
    for d in jsdesc:
        if not isinstance(d, dict):
            raise RuntimeError(f"descriptor must be a list of dictionaries. fail: {d}")
        
        type = d.get("type", "rewrite")
        handler = DESC_HANDLERS.get(type, None)
        if handler is None:
            raise RuntimeError(f"unknown descriptor type {type} for {d}")
        desc.append(handler(d))

    return desc

###
##  parse_args
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
 

    # replacement json file
    parser.add_argument("-d", "--desc", action="store",
                         help="json descriptor", required=True)
 
    # print only parameter
    parser.add_argument("-p", "--print-only", action="store_true",
                        default=False,
                        help="don't rewrite files, just print the output")

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")
 
    # parse all remaining non-options    
    parser.add_argument("paths", nargs="+", help="paths to process")

    args: argparse.Namespace = parser.parse_args()
    global VERBOSITY
    VERBOSITY = args.verbose
    DEBUG(f"VERBOSITY={VERBOSITY}")
    return args
 

###
##  process a file
#

def process_file(path: str, descs: List[List[str]],
                 print_only: bool) -> None:

    prestat = os.stat(path)

    for cdesc in descs:
        VERBOSE(f"\tprocessing {path} with {cdesc.match} -> {cdesc.rewrite}")
        cdesc.do_fixups(path, print_only)


    poststat = os.stat(path)

    if ((prestat.st_size != poststat.st_size)
        or (prestat.st_mtime != poststat.st_mtime)):
        return "changed"

    return "unchanged"

def worker(file_list: multiprocessing.Queue, descs: List[List[str]],
           doneq: multiprocessing.Queue,
           args: argparse.Namespace) -> None:
    
    global VERBOSITY
    VERBOSITY = args.verbose
    VERBOSE("worker started")
    while True:
        try:
            path = file_list.get(block=False)
        except queue.Empty:
            break

        result = process_file(path, descs, args.print_only)

        # push something on the doneq
        doneq.put(result)

    VERBOSE("worker done")


###
##  main
#
def main() -> int:
    args: argparse.Namespace = parse_args()

    if args.desc is None:
        print("missing required JSON descriptor")
        return 1

    # parse the descriptor
    jsdesc: List[Dict[str, Any]]
    with open(args.desc) as f:
        jsdesc = json.load(f)

    # make the list of descriptor objects
    desc: List[CombyDesc] = jsdesc2desc(jsdesc)
        
    # iterate over all the paths
    count = 0
    file_list: multiprocessing.Queue = multiprocessing.Queue()
    for path in args.paths:

        # if it's a file, just process it
        LOG(f"adding {path}")
        if os.path.isfile(path):
            count += 1
            file_list.put(path)
            continue

        # if it's not a directory, skip it
        if not os.path.isdir(path):
            LOG(f"skipping unknown path {path}")
            continue

        # iterate over all the .c and .h files recursively
        for root, dirs, files in os.walk(path):

            # call a rewrite function for each file
            for file in files:
                if not (file.endswith(".c") or file.endswith(".h")):
                    continue

                LOG(f"adding {os.path.join(root, file)}")
                count += 1
                file_list.put(os.path.join(root, file))


    # fork off the workers
    doneq: multiprocessing.Queue = multiprocessing.Queue()
    max_workers = min(count, 32)
    procs = []
    for i in range(0, max_workers):
        p = multiprocessing.Process(target=worker,
                                    args=(file_list, desc, doneq, args))
        procs.append(p)
        p.start()


    # wait for all the workers to finish
    #LOG(f"waiting for {len(procs)} workers to finish {file_list.qsize()} files")
    LOG(f"waiting for {len(procs)} workers to finish {count} files")

    completed: int = 0
    changed: int = 0
    plist = procs.copy()
    while len(plist) > 0:
        for p in plist:
            if not p.is_alive():
                plist.remove(p)
        if len(plist) > 0:
            plist[0].join(1)

        while True:
            try:
                result = doneq.get(block=False)
                completed += 1
                if result == "changed":
                    changed += 1
            except queue.Empty:
                break

        LOG(f"Completed {completed}/{count} files, {changed} changed")
    LOG("all workers finished")

    return 0
 
###
##  entrypoint
#
if __name__ == "__main__":
    main()