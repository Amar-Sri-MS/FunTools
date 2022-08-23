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
import hashlib
import subprocess
import queue
import threading
import pickle

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
        self.md5: str = "<unknown>"
        self.has_legacy: bool = False

        # reference buckets
        self.noref: Set[str] = set()
        self.upref: Set[str] = set()
        self.downref: Set[str] = set()
        self.crossref: Dict[str, str] = {}

        # match counts
        self.decl_counts: Dict[str, int] = {}
        self.ref_counts: Dict[str, int] = {}

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

    def add_decl_matches(self, id, count):
        self.decl_counts[id] = self.decl_counts.setdefault(id, 0) + count

    def add_ref_matches(self, id, count):
        self.ref_counts[id] = self.ref_counts.setdefault(id, 0) + count

    def only_include(self) -> bool:
        if (not self.has_legacy):
            return False
    
        if (len(self.wus) > 0):
            return False

        if (len(self.refs) > 0):
            return False

        return True

    def only_up(self) -> bool:
        if (not self.has_legacy):
            return False

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
        if (not self.has_legacy):
            return False

        if (self.only_up()):
            return False

        if (len(self.downref) == 0):
            return False

        return True

    def unknown_or_cross(self) -> bool:
        if (not self.has_legacy):
            return False

        if (len(self.noref) > 0):
            return True

        if (len(self.crossref) > 0):
            return True

        return False

    def only_in(self) -> bool:
        return False

    def cross(self) -> bool:
        if (not self.has_legacy):
            return False

        if (len(self.crossref) == 0):
            return False

        return True

    def unknown(self) -> bool:
        if (not self.has_legacy):
            return False

        if (len(self.noref) == 0):
            return False

        return True
    
    def print_unknowns(self, prefix="") -> None:
        for unk in self.noref:
            print("%s: %s" % (prefix, unk))

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

    def add_file(self, fname: str, fl: FunFile) -> None:
        assert(fname not in self.files)
        self.files[fname] = fl

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
        print("Files by category...")
        print("\tClean files (no legacy)...")
        for ffile in self.files.values():
            if (not ffile.has_legacy):
                ffile.print_summary("\t\t" + prefix)
        print("\tFiles with no WU decls or refs...")
        for ffile in self.files.values():
            if (ffile.only_include()):
                ffile.print_summary("\t\t" + prefix)
        print("\tFiles with only up references...")
        for ffile in self.files.values():
            if (ffile.only_up()):
                ffile.print_summary("\t\t" + prefix)
        print("\tFiles with up and/or down references...")
        for ffile in self.files.values():
            if (ffile.only_internal()):
                ffile.print_summary("\t\t" + prefix)
        print("\tFiles with only in references...")
        for ffile in self.files.values():
            if (ffile.only_in()):
                ffile.print_summary("\t\t" + prefix)
        print("\tFiles cross references...")
        for ffile in self.files.values():
            if (ffile.cross()):
                ffile.print_summary("\t\t" + prefix)
        print("\tFiles unknown references...")
        for ffile in self.files.values():
            if (ffile.unknown()):
                ffile.print_summary("\t\t" + prefix)
                ffile.print_unknowns("\t\t\t" + prefix)


###
##  helpers
#

def scan_for_legacy(input:str) -> bool:
    nmatches = len(list(comby.matches(input, LEGACY_MATCH)))

    return (nmatches > 0)

###
##  Pattern object
#

class Pattern():
    def __init__(self, id: str, match: str) -> None:
        self.match: str = match
        self.id:str = id

    def matches(self, input: str):
        l = list(comby.matches(input, self.match))
        return l   

###
##  WU definition scanning
#

DECLS : List[Pattern] = [
    Pattern("WU_HANDLER", "WU_HANDLER(:[attrs]) void :[wuname](:[params])"),
    Pattern("WU64_HANDLER", "WU64_HANDLER(:[attrs]) void :[wuname](:[params])"),
    Pattern("CHANNEL_THREAD", "CHANNEL_THREAD(:[attrs]) void :[wuname](:[params])"),
    Pattern("CHANNEL", "CHANNEL(:[attrs]) void :[wuname](:[params])"),
    Pattern("WU_HANDLER_REGISTER_GROUP", "WU_HANDLER_REGISTER_GROUP(:[module], :[wuname], (:[fnlist]), :[attrs], :[align])"),
    Pattern("WU_HANDLER_REGISTER_DMA_ERR_GROUP", "WU_HANDLER_REGISTER_DMA_ERR_GROUP(:[module], :[wuname], :[fn], :[wu_attrs])"),
]

def scan_file_for_decls(fl: FunFile, input: str) -> List[WUDecl]:
    
    matches: List["Comby.match"] = []
    for decl in DECLS:
        decl_matches = decl.matches(input)
        fl.add_decl_matches(decl.id, len(decl_matches))
        matches += decl_matches

    return [WUDecl(fl.name, match) for match in matches]

###
##  WU reference scanning
#

DEST_AND_ARGS: str = ":[dest~[^,\)]+]:[comma~,?]:[args~[^\)]*]"

REFS : List[str] = [
    ## WU API
    Pattern("WUID", "[~\bWUID](:[wuname])"),
    Pattern("wu_send", "[~\bwu_send](:[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("wu_send_priority",
            "[~\bwu_send_priority](:[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("wu_send_ungated",
            "[~\bwu_send_ungated](:[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("wu_send_priority_ungated", 
            "[~\bwu_send_priority_ungated](:[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("wu_send_ungated_nobarrier_unsafe",
            "[~\bwu_send_ungated_nobarrier_unsafe](:[wuname], " + DEST_AND_ARGS + ")"),

    ## Timers?
    Pattern("wu_timer_start",
            "[~\bwu_timer_start](:[id], :[wuname], :[dest], :[arg], :[delay])"),

    ## channel  API

    Pattern("channel_push",
            "[~\bchannel_push](:[channel], :[wuname], " + DEST_AND_ARGS + ")"),
    # NB dest -> "callee_flow"
    Pattern("channel_flow_push",
            "[~\channel_flow_push](:[channel], :[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("channel_exception_push",
        "[~\channel_exception_push](:[channel], :[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("channel_fork",
            "[~\channel_fork](:[channel], :[framep], :[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("channel_exec_wu",
            "[~\channel_exec_wu](:[wuname], " + DEST_AND_ARGS + ")"),
]

def scan_file_for_refs(fl: FunFile, input: str) -> List[WURef]:
    matches: List["Comby.match"] = []
    for decl in REFS:
        matches += decl.matches(input)
        fl.add_ref_matches(decl.id, len(matches))

    return [WURef(match) for match in matches]


###
##  parse_args
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
 
    # Optional argument flag which defaults to False
    parser.add_argument("-o", "--output", action="store", type=str, 
                        help="Output filename",
                        default="-")
 
     # Optional argument flag which defaults to False
    parser.add_argument("-n", "--nthreads", action="store", type=int, 
                        help="Number of threads",
                        default=32)

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
##  file processing worker
#

def file_worker(wuinfo: WUInfo, fileinfo: Dict[str, FunFile], fq):

    while (True):

        # get an item
        try:
            fname = fq.get(False)
        except queue.Empty:
            # done here
            return

        # print("Hashing file '%s'" % fname)

        input = open(fname).read()

        # add the file        
        fl = fileinfo.get(fname)
        if (fl is None):
            print("File not in cache: %s" % fname)
            fl = FunFile(fname)

        # check MD5
        md5 = hashlib.md5(input.encode()).hexdigest()

        # file needs updaring 
        if ((fl.md5 != md5) and (len(input) > 0)):
            print("Processing file '%s'" % fname)
            fl = FunFile(fname)
            fileinfo[fname] = fl

            # see if this is even a match
            if (scan_for_legacy(input)):
                print("File '%s' has no legacy headers" % fname)
                fl.has_legacy = True
                fl.declist = scan_file_for_decls(fl, input)
                fl.reflist = scan_file_for_refs(fl, input)
            else:
                fl.declist = None
                fl.reflist = None

            fl.md5 = md5
            
        wuinfo.add_file(fname, fl)
        if (fl.declist is not None):
            wuinfo.add_wulist(fname, fl.declist)
        if (fl.reflist is not None):
            wuinfo.add_wurefs(fname, fl.reflist)

        # mark it done
        fq.task_done()


###
##  main
#
def main() -> int:
    args: argparse.Namespace = parse_args()

    try:
        fileinfo = pickle.load(open("legacy-wuinfo.p", "rb"))
        # print(fileinfo)
    except:
        print("Bad pickle file, starting new...")
        fileinfo: Dict[str, FunFile] = {}
        
    wuinfo = WUInfo()

    print("Finding C files...")
    # make the list of all the files
    output = subprocess.run(["find", ".", "-name", "*.c"],
                            capture_output=True).stdout
    flist = output.decode().strip().split("\n")

    print("Found %d files" % len(flist))

    fq = queue.Queue()

    # add everyting to the list
    for fname in flist:
        if (fname.startswith("./build/")):
            continue
        if (fname.startswith("./.git/")):
            continue
        fq.put(fname)

    # process the list in parallel
    print("Creating threads...")
    for i in range(args.nthreads):
        threading.Thread(target=file_worker, daemon=True,
                         args=(wuinfo, fileinfo, fq)).run()

    # wait for the processing to be done
    fq.join()

    print("Files processed, saving file contents...")

    # save dump file
    pickle.dump(fileinfo, open("legacy-wuinfo.p", "wb"))

    # process the data now we have it all
    wuinfo.process_data()

    # Dump our info
    wuinfo.print_info()

    # print file stats
    wuinfo.print_file_stats()

    # dump the decl/ref stats
    print("Pattern Matching:")
    matchcounts = {}
    for pattern in DECLS + REFS:
        matchcounts[pattern.id] = 0

    for fl in fileinfo.values():
        for (id, count) in fl.decl_counts.items():
            #print("File %s has pattern %s matched %d times" % (fl.name, id, count))
            matchcounts[id] += count
        for (id, count) in fl.ref_counts.items():
            #print("File %s has pattern %s matched %d times" % (fl.name, id, count))
            matchcounts[id] += count

    for (id, count) in matchcounts.items():
        print("\tPattern %s matched %d" % (id, count))

    return 0
 
###
##  entrypoint
#
if __name__ == "__main__":
    main()
