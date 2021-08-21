#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generic python command-line boilerplate with mypy annotations
 
static check:
% mypy myfile.py
 
format:
% python3 -m black myfile.py
"""
from re import M
from typing import List, Optional, Type, Dict, Any, Tuple, Set
import argparse
import parse_dasm

###
##  parse_args
#
def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()

        # Required positional argument
        parser.add_argument("dasm1", help="First DASM file")

        # Required positional argument
        parser.add_argument("dasm2", help="Second DASM file")

        args: argparse.Namespace = parser.parse_args()
        return args

###
##  helpers
#

def sorted_calls_by_size(func) -> List[Tuple[int, str]]:
        cd : Dict[str, int] = {}
        for (addr, instr, callsym) in func.calls:
                if (callsym is None):
                        cd.setdefault("<unknown>", 1)
                        continue
                cd[callsym] = cd.setdefault(callsym, 0) + 1

        clist = [(cd[sym], sym) for sym in cd.keys()]

        return sorted(clist, reverse=True)

def func_insn(func) -> int:
        return (func.end_address - func.start_address) / 4

###
##  printing
#
MAX_FUNC_STR = 200

def printsym(dasm, sym: str, prefix = "", sympr:Optional[str]=None) -> None:
        
        func = dasm.functions[sym]
        icount = func_insn(func)

        # handle the print symbol
        if (sympr is None):
                sympr = sym

        # sorted list of calls by size
        clist = sorted_calls_by_size(func)

        # make it a string
        s = ", ".join("%s[%d]" % (y, x) for (x, y) in clist)

        if (len(s) > MAX_FUNC_STR):
                s = s[:MAX_FUNC_STR] + "..."

        print("%s%s[%d ins]: %s" % (prefix, sympr, icount, s))

def dump_full_set(title: str, dasm, funcset: Set[str]) -> None:
        
        # nothing
        if (len(funcset) == 0):
                return

        print("%s:" % title)
        syms = sorted(funcset)

        for sym in syms:
                printsym(dasm, sym, "\t")

###
##  diffing
#

def check_diff(func1, func2) -> Optional[int]:

        idelta = func_insn(func2) - func_insn(func1)
        callsame = sorted_calls_by_size(func1) == sorted_calls_by_size(func2)

        if ((idelta == 0) and callsame):
                return None

        return idelta


def dump_diff(dasm1, dasm2, absdelta: int, sym: str, idelta: int, func1, func2):
        print("Function %s changed by %+d instructions" % (sym, idelta))

        printsym(dasm1, sym, "\tdasm1", "")
        printsym(dasm2, sym, "\tdasm2", "")

def dump_diffs(d1name: str, d2name: str, dasm1, dasm2, common: Set[str]) -> None:
        # build a list sorted by abs(ins_delta)
        dlist = []
        for sym in common:
                func1 = dasm1.functions[sym]
                func2 = dasm2.functions[sym]

                idelta = check_diff(func1, func2)

                if (idelta is None):
                        continue

                # put it in a list
                dlist.append((abs(idelta), sym, idelta, func1, func2))

        if (len(dlist) == 0):
                print("No differences in common function sizes or calls")
                return


        # Sort forward for heaviest last
        print("Showing %d differences in common functions" % len(dlist))
        print("dasm1: %s" % d1name)
        print("dasm2: %s" % d2name)
        print()
        for d in sorted(dlist):
                # lazy
                dump_diff(dasm1, dasm2, *d)
                print()

        print( "%d common functions changed" % len(dlist))

###
##  main
#
def main() -> int:
        args: argparse.Namespace = parse_args()

        # parse the two files
        fl1 = open(args.dasm1, 'r')
        fl2 = open(args.dasm2, 'r')
        dasm1 = parse_dasm.DasmInfo()
        dasm2 = parse_dasm.DasmInfo()
        dasm1.Read(fl1.readlines())
        dasm2.Read(fl2.readlines())

        # a set of function names for each dasm
        funcs1 = set(dasm1.functions.keys())
        funcs2 = set(dasm2.functions.keys())

        # generate useful data
        only1 = funcs1.difference(funcs2)
        only2 = funcs2.difference(funcs1)
        both = funcs1 & funcs2

        dump_full_set("only in %s" % args.dasm1, dasm1, only1)
        dump_full_set("only in %s" % args.dasm2, dasm2, only2)

        # print("both: ", len(both), "functions")
        dump_diffs(args.dasm1, args.dasm2, dasm1, dasm2, both)
                
        return 0
 
###
##  entrypoint
#
if __name__ == "__main__":
        main()
