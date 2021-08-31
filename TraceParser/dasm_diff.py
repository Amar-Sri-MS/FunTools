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

SLOWPATH_SYMBOLS = [
        "printf",
        "vfprintf",
        "snprintf",
        "sprintf",
        "_abort_msg",
        "syslog",
        "_maybe_log_and_send_wu",
        "_maybe_log_wu",
        "trace_wu_send",
        "wuthread_sleep",
        "fun_json",
        "_fun_json_dict",
        "fun_props",
        "fun_malloc",
        "fun_free",
        "free_multiple",
        "fun_recycler",
        "fun_calloc",
        "fun_magent",
        "fun_mcache",
        "biggies_allocate",
        "abort",
        "channel_parallelize_push",
        "print_nu_debug_stats"]

###
##  parse_args
#
def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()

        # First dasm file
        parser.add_argument("dasm1", help="First DASM file")

        # Second dasm file
        parser.add_argument("dasm2", help="Second DASM file")

        # All functions instead of just WU handlers
        parser.add_argument("-a", "--all", action="store_true", default=False)

        # Max depth of recursion (0=flat) 
        parser.add_argument("-d", "--depth", action="store", default=5)

        args: argparse.Namespace = parser.parse_args()
        return args


###
##  helpers
#

def is_slowpath(sym):
        for ssym in SLOWPATH_SYMBOLS:
                if (sym.startswith(ssym)):
                        return True
        return False

def sorted_calls_by_size(func) -> List[Tuple[int, str]]:
        cd : Dict[str, int] = {}
        for (addr, instr, callsym) in func.calls:
                if (callsym is None):
                        cd.setdefault("<unknown>", 1)
                        continue
                cd[callsym] = cd.setdefault(callsym, 0) + 1
        for (addr, instr, callsym) in func.jumps:
                if (callsym is None):
                        cd.setdefault("<unknown>", 1)
                        continue
                cd[callsym] = cd.setdefault(callsym, 0) + 1

        clist = [(cd[sym], sym) for sym in cd.keys()]

        return sorted(clist, reverse=True)

def func_insn(func) -> int:
        return (func.end_address - func.start_address) / 4


def anon_name(s: str) -> str:
        p = s.find(".")
        if (p != -1):
                s = s[:p] + "<constprop>"

        return s

def anon_constprop(scalls:List[Tuple[int, str]]) -> List[Tuple[int, str]]:

        rcalls = []
        for (n, s) in scalls:
                rcalls.append((n, anon_name(s)))

        return rcalls

def filter_wus(funcs: List[str]) -> List[str]:
        l: List[str] = []
        l += filter(lambda x : x.startswith("__wu_handler__"), funcs)
        l += filter(lambda x : x.startswith("__channel__"), funcs)
        l += filter(lambda x : x.startswith("__thread__"), funcs)

        return l

def all_insns(dasm) -> int:
        total = 0
        for func in dasm.functions.values():
                n = func_insn(func)
                # done_start_vps has negative size -1585267068431761408
                n = max(0, n)
                total += n

        return total


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
##  Function stats roll-up
#

class FuncStats:
        def __init__(self, dasm, sym, depth:int = 0, recursion :List[str]=[]):
                
                # lookup our function 
                func = dasm.functions[sym]
                
                self.dasm = dasm
                self.name: str = sym
                self.anonname: str = anon_name(self.name)
                self.func = func
                self.nunknown: int = 0
                self.refcount: int = 1
                self.recursion: int = 0
                self.maxdepth: bool = False
                self.slowpath: bool = False
                
                self._total_ins = None
                self._children_fp = None

                # instructions in this function
                self.insns = func_insn(self.func)

                # add ourself to the recursion list
                recursion = list(recursion)
                recursion.append(self.name)

                # recurse into all calls and jumps
                children = func.calls + func.jumps
                self.children: Dict[str, FuncStats] = {}

                # check if we're slowpath
                if (is_slowpath(self.name)):
                        self.slowpath = True
                        return

                # Bail out now if we've hit the max depth
                if (depth == 0):
                        self.maxdepth = True
                        return

                # find all the children
                for (addr, instr, callsym) in children:
                        if (callsym is None):
                                #fixme
                                #cd.setdefault("<unknown>", 1)
                                self.nunknown += 1
                                continue
                        if (callsym in recursion):
                                self.recursion += 1
                                continue
                        if (callsym in self.children):
                                self.children[callsym].incref()
                                continue
                        # actually construct a child recursively
                        child = FuncStats(dasm, callsym, depth-1, recursion)

                        # add it to the list
                        self.children[callsym] = child

        def incref(self):
                self.refcount += 1

        def total_insns(self):
                # sum all our childrens' instructions
                if (self._total_ins is None):
                        self._total_ins = sum([x.total_insns() for x in self.children.values()]) + self.insns
                return self._total_ins

        def attrsuffix(self):
                suffix = ""
                if (self.refcount > 1):
                        suffix += "[%d]" % self.refcount
                if (self.recursion > 0):
                        suffix += "<recursion %d>" % self.recursion
                if (self.maxdepth):
                        suffix += "<max depth reached>"
                if (self.slowpath):
                        suffix += "<SLOWPATH>"
                return suffix

        def fingername(self):
                # make a name for our fingerprint
                fname = self.anonname + self.attrsuffix()
                return fname

        def children_fp(self) -> List["Fingerprint"]:
                if (self._children_fp is None):
                        cs = []

                        # collect & sort the fingerprint of all our children
                        for child in self.children.values():
                                fp = child.fingerprint()
                                cs.append(fp)
                        cs.sort(reverse=True)
                        self._children_fp = cs

                return self._children_fp
              
        def fingerprint(self) -> "Fingerprint":
                # add our contribution 
                return Fingerprint(self)

        def print_callgraph(self, prefix = "", pname = None) -> None:
                if (pname is None):
                        pname = self.name

                print("%s%s%s: %d ins, %s total" % (prefix, pname, self.attrsuffix(), self.insns, self.total_insns()))

                # iterate over all the children in fingerprint order
                cs = self.children_fp()

                for c in cs:
                        c.fstat.print_callgraph(prefix+"\t")

class Fingerprint:
        def __init__(self, fstat: FuncStats) -> None:
                self.fstat:FuncStats  = fstat
                self.insns:int = fstat.insns
                self.totalins: int = fstat.total_insns()
                self._fp = (self.insns, self.totalins, self.fstat.name, self.fstat.children_fp())

        def idelta(self, other:"Fingerprint") -> int:
                return self.insns - other.insns

        def idelta_total(self, other:"Fingerprint") -> int:
                return self.totalins - other.totalins

        def __eq__(self, other: "Fingerprint") -> bool:
                return self._fp == other._fp
        def __lt__(self, other: "Fingerprint") -> bool:
                return self._fp < other._fp
        def __lt__(self, other: "Fingerprint") -> bool:
                return self._fp > other._fp
                

###
##  diffing
#

def check_diff(func1, func2) -> Optional[int]:

        idelta = func_insn(func2) - func_insn(func1)
        anon1 = anon_constprop(sorted_calls_by_size(func1))
        anon2 = anon_constprop(sorted_calls_by_size(func2))
        callsame = anon1 == anon2

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

def dump_recursive_diff(absdelta: int, fp1: Fingerprint, fp2: Fingerprint):
        print("Function %s changed by %+d instructions, %d total instructions" % (fp1.fstat.name, fp2.idelta(fp1), fp2.idelta_total(fp1)))

        fp1.fstat.print_callgraph("\t", "dasm1")
        fp2.fstat.print_callgraph("\t", "dasm2")


def dump_diffs_recursive(d1name: str, d2name: str, dasm1, dasm2, common: Set[str]) -> None:

        # build a list sorted by abs(ins_delta)
        dlist = []
        for sym in common:
                fstat1 = FuncStats(dasm1, sym, 5)
                fstat2 = FuncStats(dasm2, sym, 5)

                fp1 = fstat1.fingerprint()
                fp2 = fstat2.fingerprint()

                # compare fingerprints
                if (fp1 == fp2):
                        continue

                # put it in a list
                dlist.append((abs(fp2.idelta(fp1)), fp1, fp2))

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
                dump_recursive_diff(*d)
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

        # trim out anything that's not a WU handler named
        if (not args.all):
                funcs1 = set(filter_wus(list(funcs1)))
                funcs2 = set(filter_wus(list(funcs2)))

        # generate useful data
        only1 = funcs1.difference(funcs2)
        only2 = funcs2.difference(funcs1)

        dump_full_set("only in %s" % args.dasm1, dasm1, only1)
        dump_full_set("only in %s" % args.dasm2, dasm2, only2)

        # common symbols
        both = funcs1 & funcs2

        # print("both: ", len(both), "functions")
        #dump_diffs(args.dasm1, args.dasm2, dasm1, dasm2, both)
        dump_diffs_recursive(args.dasm1, args.dasm2, dasm1, dasm2, both)

        # count all the instructions
        count1: int = all_insns(dasm1)
        count2: int = all_insns(dasm2)

        print("Total instructions %d -> %d, delta %+d" %
              (count1, count2, count2 - count1))

        return 0
 
###
##  entrypoint
#
if __name__ == "__main__":
        main()
