#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generic python command-line boilerplate with mypy annotations
 
static check:
% mypy myfile.py
 
format:
% python3 -m black myfile.py
"""
from typing import List, Optional, Type, Dict, Any, Tuple
import argparse
import re
from comby import Comby # type: ignore 
import os
import pickle
import glob

comby = Comby(language=".c")

## parse the following line with regex:
## accelerators/crypto_hostif.c:3567:22: error: ‘struct fun_req_common’ has no member named ‘op’; did you mean ‘op_l’?
## <filname>:<line>:<col>: error: ‘struct <struct>’ has no member named ‘<member>’; did you mean ‘<member>_l’?
RE: str = r"([\.\/a-zA-Z0-9_-]+):(\d+):(\d+:)? error: .(?:const )?struct (\w+). has no member named .(\w+).; did you mean .(\w+)_l.\?"

MAX_LOG_LEVEL: int = 0

def LOG(msg: str, level: int = 0) -> None:
    if level <= MAX_LOG_LEVEL:
        print(msg)

def VERBOSE(msg: str) -> None:
    LOG(msg, 1)

def DEBUG(msg: str) -> None:
    LOG(msg, 2)

class Accessor:
    def __init__(self, func: str, struct: str, flavour: str, member: str, structarg: str):
        self.func: str = func
        self.struct: str = struct
        self.flavour: str = flavour
        self.member: str = member
        self.structarg: str = structarg

    def __str__(self) -> str:
        return f"{self.func}: {self.struct}.{self.flavour}.{self.member}"

class Fixup:
    def __init__(self, filename: str,
                        line: int,
                        col: int,
                        struct: str,
                        member: str):
        self.filename: str = filename
        self.line: int = line
        self.col: int = col
        self.struct: str = struct
        self.member: str = member

    def __str__(self) -> str:
        return f"{self.line}: {self.stname}"

###
##  line rewrite logic
#

# rewrites for lines missing accessors (usually arrays)
ARRAY_REWRITES: List[Tuple[str, str]] = [
    (":[expr:e]->{member};", "hci_array_access(:[expr]->{member});"),
    (":[expr:e]->{member}", "hci_array_access(:[expr]->{member})"),
    
    (":[expr:e].{member};", "hci_array_access(:[expr].{member});"),
    (":[expr:e].{member}", "hci_array_access(:[expr].{member})"),
]

# rewrites for lines with nested accessors (type mismatch)
NESTED_REWRITES: List[Tuple[str, str]] = [
    (":[expr:e]->:[nest:e].{member}:[semi~;?]",
        "({struct}_get_{member}(:[expr])):[semi]"),

    ("(:[expr:e]->:[nest:e].{member}):[semi~;?]",
        "({struct}_get_{member}(:[expr])):[semi]"),

]

# catch-all rewrites for general field access
REWRITES: List[Tuple[str, str]] = [
    # regular assignments -> set accessor
    # need a variant with semicolon and without because of the way comby parses weird
    (":[expr:e]->{member} = :[value];", "{struct}_set_{member}(:[expr], :[value]);"), # XXX: semicolon
    (":[expr:e]->{member} = :[value:e]", "{struct}_set_{member}(:[expr], :[value])"),
    (":[expr:e].{member} = :[value];", "{struct}_set_{member}(&:[expr], :[value]);"), # XXX: semicolon
    (":[expr:e].{member} = :[value:e]", "{struct}_set_{member}(&:[expr], :[value])"),

    # or-equals (|=) assignments -> expand to a set and a get, eg.
    # foo->bar |= expr; -> foo_set_bar(foo_get_bar(foo) | expr);
    (":[expr:e]->{member} |= :[value:e];",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) | :[value]);"), # XXX: semicolon
    (":[expr:e]->{member} |= :[value:e]",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) | :[value])"),

    # and-equals (&=) assignments -> expand to a set and a get, eg.
    # foo->bar &= expr; -> foo_set_bar(foo_get_bar(foo) & expr);
    (":[expr:e]->{member} &= :[value:e];",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) & :[value]);"), # XXX: semicolon
    (":[expr:e]->{member} &= :[value:e]",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) & :[value])"),

    # address-of accessors
    ("&:[expr:e]->{member}", "hci_addressof(:[expr]->{member})"),
    ("&:[expr:e].{member}", "hci_addressof(:[expr].{member})"),

    # get accessors with "!" on the front. comby weird parsing again
    ("!:[expr:e]->{member}", "!{struct}_get_{member}(:[expr])"), # XXX: exclamation
    ("!:[expr:e].{member}", "!{struct}_get_{member}(&:[expr])"), # XXX: exclamation

    # get accessors. The suble differeneces in casts confuse comby, so we enumerate the possibilities
    ("(:[cast])->:[expr:e]->{member}", "{struct}_get_{member}(&(:[cast])->:[expr])"), # XXX: cast type
    ("(:[cast])->:[expr:e].{member}", "{struct}_get_{member}(&(:[cast])->:[expr])"), # XXX: cast type
    ("(:[cast]):[expr:e]->{member}", "(:[cast]){struct}_get_{member}(:[expr])"), # XXX: cast result
    (":[expr:e]->{member}", "{struct}_get_{member}(:[expr])"),

    # get accessors. The suble differeneces in casts confuse comby, so we enumerate the possibilities
    ("(:[cast]).:[expr:e].{member}", "{struct}_get_{member}(&(:[cast]).:[expr])"), # XXX: cast type
    ("(:[cast]).:[expr:e]->{member}", "{struct}_get_{member}(&(:[cast]).:[expr])"), # XXX: cast type
    ("(:[cast]):[expr:e].{member}", "(:[cast]){struct}_get_{member}(&:[expr])"), # XXX: cast result
    (":[expr:e].{member}", "{struct}_get_{member}(&:[expr])"),
]

def fixup_line(accessors: Dict[str, Accessor], lines: List[str], fixup: Fixup) -> None:

    LOG(f"Fixing up line: {fixup.line} for {fixup.struct}.{fixup.member}")

    gettr = f"{fixup.struct}_get_{fixup.member}"
    settr = f"{fixup.struct}_set_{fixup.member}"

    if (gettr not in accessors.keys()) and (settr not in accessors.keys()):
        # no accessor, so try array rewrites
        VERBOSE('\tAppears to be an array')
        rewrite_list = ARRAY_REWRITES
    elif (accessors[gettr].structarg != fixup.struct):
        # no type match, so likely a nested accessor
        VERBOSE('\tAppears to be a nested accessor')
        rewrite_list = NESTED_REWRITES
    else:
        # accessor with type match, so use regular rewrites
        VERBOSE('\tAppears to be a regular accessor')
        rewrite_list = REWRITES

    # get the line
    line = lines[fixup.line - 1]

    for rewrite in rewrite_list:

        matchstr = rewrite[0].format(member=fixup.member, struct=fixup.struct)
        replacestr = rewrite[1].format(member=fixup.member, struct=fixup.struct)

        oline = line
        line = comby.rewrite(line, matchstr, replacestr)

        if (line == oline):
            # next
            continue
        LOG(f"Rewrote: {oline} -> {line}")
        lines[fixup.line - 1] = line

        # only allow a single rewrite per fixup on a line
        break

def fixup_file(accessors: Dict[str, Accessor], filename: str, fixup_list: List[Fixup]) -> None:
    LOG(f"Fixing up file: {filename}")

    # read the file
    fl = open(filename, "r")
    lines = fl.readlines()
    fl.close()

    # for each line, fix it up
    for fixup in fixup_list:
        fixup_line(accessors, lines, fixup)

    # write the file
    fl = open(filename, "w")
    for line in lines:
        fl.write(line)
    fl.close()

###
##  parsing accessors
#

ACCESSORS: List[str] = [
    (" :[struct:e]_get_:[member](...struct :[structarg] ...)", "get"),
    (" :[struct:e]_set_:[member](...struct :[structarg] ...)", "set"),
]

def parse_accessor(line: str) -> List[Accessor]:
    accessors: List[Accessor] = []
    for (accessor, flavour) in ACCESSORS:
        DEBUG(f"Trying to match {accessor}")
        matches = list(comby.matches(line, accessor))
        DEBUG(f"Found {len(matches)} matches")
        if len(matches) == 0:
            continue
        
        # otherwise make an accessor for each match
        for match in matches:
            structname = match['struct'].fragment
            member = match['member'].fragment
            structarg = match['structarg'].fragment
            func = f"{structname}_{flavour}_{member}"
            DEBUG(f"Found accessor: {func}")
            accessors.append(Accessor(func, structname, flavour, member, structarg))

    return accessors

PKLFILE: str = "/tmp/accessors.pkl"
STRIDE: int = 5000
def load_accessors(hciheader: str) -> Dict[str, Accessor]:

    # check the timestamp on hciheader
    # if it's newer than PKLFILE, regenerate PKLFILE
    # if PKLFILE exists, load it
    # otherwise, parse hciheader and save PKLFILE

    # assert os.path.exists(hciheader), f"File {hciheader} does not exist"

    if os.path.exists(PKLFILE):
        LOG(f"Loading accessors from {PKLFILE}")
        try:
            with open(PKLFILE, "rb") as fl:
                accessors = pickle.load(fl)
                return accessors
        except Exception as e:
            LOG(f"Error loading pickle file: {e}")
            pass

    acc_files = glob.glob(hciheader)

    LOG(f'Regenerating accessors from {", ".join(acc_files)}, this may take a while')
    for header in acc_files:
        fl = open(header, "r")
        lines = fl.readlines()

        accessors: Dict[str, Accessor] = {}

        account: int = 0
        lcount: int = 0
        while True:
            # make a bunch of text
            line = "".join(lines[lcount:lcount+STRIDE])

            # print(line)
            if (lcount > len(lines)):
                break

            # parse the text
            accs = parse_accessor(line)

            for acc in accs:
                VERBOSE(f"Found Accessor: {acc.func}")
                accessors[acc.func] = acc
                account += 1

            if (lcount % 1000) == 0:
                LOG(f"{lcount}/{len(lines)} lines processed, {account} accessors found")
            lcount += STRIDE

    LOG(f"Found {account} ({len(accessors)}) accessors, saving pickle file {PKLFILE}")

    with open(PKLFILE, "wb") as fl:
        pickle.dump(accessors, fl)

    return accessors

###
##  parse_args
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
 
    # We need to header file to scrape valid accessor functions
    parser.add_argument("hciheader", help="funhci.h header file glob")

    # File full of errors
    parser.add_argument("errfile", help="Error file")
 
    # Just parse the error file and exit
    parser.add_argument("-J", "--just-errs", action="store_true", default=False)
 
    # Optional argument which requires a parameter (eg. -d test)
    #parser.add_argument("-n", "--name", action="store", dest="name")
 
    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")
 
    args: argparse.Namespace = parser.parse_args()

    global MAX_LOG_LEVEL
    MAX_LOG_LEVEL = args.verbose

    return args
 
###
##  main
#
def main() -> int:
    args: argparse.Namespace = parse_args()
 
    if not args.just_errs:
        accessors: Dict[str, Accessor] = load_accessors(args.hciheader)

    LOG(f"Reading file {args.errfile}")
    fl = open(args.errfile, "r")
    lines = fl.readlines()

    fixups: Dict[str, List[Fixup]] = {}
    
    matched: int = 0

    for line in lines:
        # match line against RE
        match = re.match(RE, line)

        # continue if no match
        if match is None:
            continue

        VERBOSE(f"Matched line: {line.strip()}")
        matched += 1

        # extract match groups
        filename: str = match.group(1)
        line: int = int(match.group(2))
        try:
            col: int = int(match.group(3))
        except:
            col = -1
        struct: str = match.group(4)
        member: str = match.group(5)
        member_l: str = match.group(6)

        DEBUG(f"Found line: filename: {filename}, line: {line}, col: {col}, struct: {struct}, member: {member}, member_l: {member_l}")
        
        # ensure member == member_l
        if member != member_l:
            VERBOSE(f"member != member_l: {member} != {member_l}")
            continue
        
        # add it to fixups
        fixups.setdefault(filename, list()).append(Fixup(filename, line, col, struct, member))

    LOG(f"Matched {matched} lines")

    if args.just_errs:
        LOG("Early exit for matching errors only")
        return -1

    VERBOSE(f"Found accessors: {accessors.keys()}")

    for filename, fixup_list in fixups.items():
        fixup_file(accessors, filename, fixup_list)

    return 0
 
###
##  entrypoint
#
if __name__ == "__main__":
    main()
