#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scan files for legacy WU declarations and call sites
 
static check:
% mypy myfile.py
 
format:
% python3 -m black myfile.py
"""
from typing import List, Optional, Type, Dict, Any, Tuple, Set
import argparse
from comby import Comby # type: ignore 
 
# global comby object
comby = Comby(language=".c")

LEGACY_MATCH: str = "#include <generated/wu_ids.h>"

###
##  A WU declaration
#

class WUDecl():
    def __init__(self, fname: str, match: "Comby.match") -> None:
        self.match = match
        self.fname = fname

        self.wuname = match.environment["wuname"].fragment
        self.lineno = match.location.start.line

    def add_to_dict(self, d):
        d.setdefault(self.wuname, WUDeclList()).add_decl(self)

    def print_info(self, prefix: str="") -> None:
        print("%sDecl '%s' on line %d" % (prefix, self.wuname, self.lineno))

class WUDeclList():
    def __init__(self):
        self.decls: List[WUDecl] = []

    def add_decl(self, decl: WUDecl):
        self.decls.append(decl)

    def get_filename(self):
        fnames = set()
        for decl in self.decls:
            fnames.add(decl.fname)
        assert(len(fnames) > 0)
        if (len(fnames) > 1):
            return "<multiple>"
        else:
            return list(fnames)[0]

    def first_lineno(self):
        lineno = 99999999999
        for decl in self.decls:
            lineno = min(lineno, decl.lineno)

        return lineno

    def print_info(self, prefix: str = "") -> None:
        count = len(self.decls)
        assert(count > 0)
        dec0 = self.decls[0]

        if (len(self.decls) == 1):
            dec0.print_info(prefix)
        else:
            print("%sMulti-Decl %s" % (prefix, dec0.wuname))
            for decl in self.decls:
                decl.print_info("\t" + prefix)


###
##  A WU reference
#

class WURef():
    def __init__(self, match: "Comby.match") -> None:
        self.match = match
        self.wuname = match.environment["wuname"].fragment
        self.lineno = match.location.start.line

    def print_info(self, prefix: str="") -> None:
        print("%sRef '%s' on line %d" % (prefix, self.wuname, self.lineno))

###
##  A FunOS File
#

class FunFile():
    def __init__(self, name: str) -> None:
        self.name = name
        self.wus: Dict[str, WUDeclList] = {}
        self.refs: List[WURef] = []

        # reference buckets
        self.noref: Set[str] = set()
        self.upref: Set[str] = set()
        self.downref: Set[str] = set()
        self.crossref: Dict[str, str] = {}

    def add_ref(self, ref: WURef) -> None:
        self.refs.append(ref)

    def process_refs(self, wuinfo: "WUInfo") -> None:
        # for each ref
        for ref in self.refs:
            # lookup the WU
            wudecls = wuinfo.wus.get(ref.wuname)
            if (wudecls is None):
                self.noref.add(ref.wuname)
            elif (wudecls.get_filename() != self.name):
                self.crossref[ref.wuname] = wudecls.get_filename()
            elif (wudecls.first_lineno() < ref.lineno):
                self.upref.add(ref.wuname)
            else:
                self.downref.add(ref.wuname)


    def only_include(self) -> bool:
        if (len(self.wus) > 0):
            return False

        if (len(self.refs) > 0):
            return False

        return True

    def only_up(self) -> bool:
        if (self.only_include()):
            return False

        if (len(self.downref) > 0):
            return False

        if (len(self.noref) > 0):
            return False

        if (len(self.crossref) > 0):
            return False

        return True
    
    def only_internal(self) -> bool:
        if (self.only_up()):
            return False

        if (len(self.downref) == 0):
            return False

        return True

    def unknown_or_cross(self) -> bool:
        if (len(self.noref) > 0):
            return True

        if (len(self.crossref) > 0):
            return True

        return False

    def print_summary(self, prefix="") -> None:
        print("%sFile '%s' has %d decls, %d refs, %d up, %d down, %d cross and %d unknown" % (prefix, self.name, len(
            self.wus), len(self.refs), len(self.upref), len(self.downref), len(self.crossref), len(self.noref)))

    def print_info(self, prefix: str="") -> None:
        print("%sFile %s" % (prefix, self.name))
        print("\t%sRaw Declarations:" % prefix)
        for decl_list in self.wus.values():
            decl_list.print_info("\t\t" + prefix)
        print("\t%sRaw References:" % prefix)
        for ref in self.refs:
            ref.print_info("\t\t" + prefix)
        if (len(self.noref) > 0):
            print("\t%sUnknown References:" % prefix)
            for wuname in self.noref:
                print("\t\t%sWU '%s' never declared" % (prefix, wuname))
        if (len(self.upref) > 0):
            print("\t%sUp (good!) References:" % prefix)
            for wuname in self.upref:
                print("\t\t%sWU '%s' referenced in order" % (prefix, wuname))
        if (len(self.downref) > 0):
            print("\t%sDown References:" % prefix)
            for wuname in self.downref:
                print("\t\t%sWU '%s' referenced out of order" % (prefix, wuname))
        if (len(self.crossref) > 0):
            print("\t%sCross References:" % prefix)
            for (wuname, fname) in self.crossref.items():
                print("\t\t%sWU '%s' references other file (%s)" % (prefix, wuname, fname))

###
##  Global WUInfo object
#

class WUInfo():
    def __init__(self) -> None:
        self.files: Dict[str, FunFile] = {}
        self.wus: Dict[str, WUDeclList] = {}

    def add_file(self, fname: str) -> None:
        assert(fname not in self.files)
        self.files[fname] = FunFile(fname)

    def add_wulist(self, fname: str, declist: List[WUDecl]) -> None:
        assert(fname in self.files)

        for decl in declist:
            # add to the global list of WUs
            decl.add_to_dict(self.wus) 
            decl.add_to_dict(self.files[fname].wus)

    def add_wurefs(self, fname: str, reflist: List[WURef]) -> None:
        assert(fname in self.files)

        for ref in reflist:
            # add to the global list of WUs
            self.files[fname].add_ref(ref)

    def process_data(self) -> None:
        # process each file's references
        for file in self.files.values():
            file.process_refs(self)

    def print_info(self, prefix = ""):
        print("WUInfo: %d files, %d WUs" % (len(self.files), len(self.wus)))
        for ffile in self.files.values():
            ffile.print_info("\t" + prefix)

    def print_file_stats(self, prefix=""):
        trivial: List[str] = []
        print("Files by category...")
        print("\tFiles with no WU decls or refs...")
        for ffile in self.files.values():
            if (ffile.only_include()):
                ffile.print_summary("\t\t" + prefix)
                trivial.append(ffile.name)
        print("\tFiles with only up references...")
        for ffile in self.files.values():
            if (ffile.only_up()):
                ffile.print_summary("\t\t" + prefix)
                trivial.append(ffile.name)
        print("\tFiles with up and/or down references...")
        for ffile in self.files.values():
            if (ffile.only_internal()):
                ffile.print_summary("\t\t" + prefix)
        print("\tFiles with unknown or cross references...")
        for ffile in self.files.values():
            if (ffile.unknown_or_cross()):
                ffile.print_summary("\t\t" + prefix)


        print("Trivial conversions:")
        print(("\t\\\n").join(trivial))

###
##  helpers
#

def scan_for_legacy(input:str) -> bool:
    nmatches = len(list(comby.matches(input, LEGACY_MATCH)))

    return (nmatches > 0)

###
##  WU definition scanning
#

DECLS : List[str] = [
    "WU_HANDLER(:[attrs]) void :[wuname](:[params])",
    "WU64_HANDLER(:[attrs]) void :[wuname](:[params])",
    "CHANNEL_THREAD(:[attrs]) void :[wuname](:[params])",
    "CHANNEL(:[attrs]) void :[wuname](:[params])",
    "WU_HANDLER_REGISTER_GROUP(:[module], :[wuname], (:[fnlist]), :[attrs], :[align])",
    "WU_HANDLER_REGISTER_DMA_ERR_GROUP(:[module], :[wuname], :[fn], :[wu_attrs])",
]

def scan_file_for_decls(fname: str, input: str) -> List[WUDecl]:
    
    matches: List["Comby.match"] = []
    for decl in DECLS:
        matches += list(comby.matches(input, decl))

    return [WUDecl(fname, match) for match in matches]

###
##  WU reference scanning
#

DEST_AND_ARGS: str = ":[dest~[^,\)]+]:[comma~,?]:[args~[^\)]*]"

REFS : List[str] = [
    ## WU API
    "WUID(:[wuname])",
    "wu_send(:[wuname], " + DEST_AND_ARGS + ")",
    "wu_send_priority(:[wuname], " + DEST_AND_ARGS + ")",
    "wu_send_ungated(:[wuname], " + DEST_AND_ARGS + ")",
    "wu_send_priority_ungated(:[wuname], " + DEST_AND_ARGS + ")",
    "wu_send_ungated_nobarrier_unsafe(:[wuname], " + DEST_AND_ARGS + ")",

    ## channel  API

    "channel_push(:[channel], :[wuname], " + DEST_AND_ARGS + ")",
    # NB dest -> "callee_flow"
    "channel_flow_push(:[channel], :[wuname], " + DEST_AND_ARGS + ")",
    "channel_exception_push(:[channel], :[wuname], " + DEST_AND_ARGS + ")",
    "channel_fork(:[channel], :[framep], :[wuname], " + DEST_AND_ARGS + ")",
    "channel_exec_wu(:[wuname], " + DEST_AND_ARGS + ")",
]

def scan_file_for_refs(input: str) -> List[WURef]:
    matches: List["Comby.match"] = []
    for decl in REFS:
        matches += list(comby.matches(input, decl))

    return [WURef(match) for match in matches]


###
##  parse_args
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
 
    # Required positional argument
    parser.add_argument("files", nargs="+", help="Files to process")
 
    # Optional argument flag which defaults to False
    parser.add_argument("-o", "--output", action="store", type=str, help="Output filename",
                        default="-")
 
    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")
 
    args: argparse.Namespace = parser.parse_args()
    return args
 
###
##  main
#
def main() -> int:
    args: argparse.Namespace = parse_args()

    wuinfo = WUInfo()

    # Process all the files
    for fname in args.files:
        print("Processing file '%s'" % fname)

        input = open(fname).read()

        # see if this is even a match
        if (not scan_for_legacy(input)):
            print("File '%s' has no legacy headers" % fname)
            continue

        declist = scan_file_for_decls(fname, input)
        reflist = scan_file_for_refs(input)
        
        wuinfo.add_file(fname)
        wuinfo.add_wulist(fname, declist)
        wuinfo.add_wurefs(fname, reflist)

    
    # process the data now we have it all
    wuinfo.process_data()

    # Dump our info
    wuinfo.print_info()

    # print file stats
    wuinfo.print_file_stats()

    return 0
 
###
##  entrypoint
#
if __name__ == "__main__":
    main()
