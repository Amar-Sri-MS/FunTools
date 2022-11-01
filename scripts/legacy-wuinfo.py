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
from comby import Comby # type: ignore 
import multiprocessing
import subprocess
import datetime
import argparse
import hashlib
import pickle
import os

# global comby object
comby = Comby(language=".c", timeout=300)


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

    def decl_str(self) -> str:
        return self.match.matched

    def print_info(self, prefix: str="") -> None:
        print("%sDecl '%s' on line %d" % (prefix, self.wuname, self.lineno))

class WUDeclList():
    def __init__(self):
        self.decls: List[WUDecl] = []

    def add_decl(self, decl: WUDecl):
        self.decls.append(decl)

    def get_filenames(self) -> List[str]:
        fnames = set()
        for decl in self.decls:
            fnames.add(decl.fname)
        assert(len(fnames) > 0)
        return fnames

    def get_filename(self) -> str:
        fnames = self.get_filenames()
        if (len(fnames) > 1):
            return "<multiple>"
        else:
            return list(fnames)[0]

    def decl_strs(self) -> str:
        dsl = [decl.decl_str() for decl in self.decls]
        return dsl

    def decl_str(self) -> str:
        if (len(self.decls) != 1):
            print(f"ERROR: {self.decls[0].decl_str()}")
            raise RuntimeError("Mutliple-declared down reference. Cannot fix")
        return self.decl_strs()[0]

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
        self.inref: Dict[str, Set[str]] = {}
        self.downref: Set[str] = set()
        self.crossref: Dict[str, str] = {}
        self.crossreffl: Dict[str, List[str]] = {}

        # match counts
        self.decl_counts: Dict[str, int] = {}
        self.ref_counts: Dict[str, int] = {}

    def add_ref(self, ref: WURef) -> None:
        self.refs.append(ref)

    def add_inref(self, inwu: str, infile: str) -> None:
        flist: Set[str] = self.inref.setdefault(inwu, set())
        flist.add(infile)

    def get_inref(self):
        return self.inref

    def process_refs(self, wuinfo: "WUInfo") -> None:
        # for each ref
        for ref in self.refs:
            # lookup the WU
            wudecls = wuinfo.wus.get(ref.wuname)
            if (wudecls is None):
                self.noref.add(ref.wuname)
            elif (wudecls.get_filename() != self.name):
                self.crossref[ref.wuname] = wudecls.get_filename()
                self.crossreffl[ref.wuname] = wudecls.get_filenames()
                for decl in wudecls.decls:
                    wuinfo.files[decl.fname].add_inref(ref.wuname, self.name)
            elif (wudecls.first_lineno() < ref.lineno):
                self.upref.add(ref.wuname)
            else:
                self.downref.add(ref.wuname)

    def add_decl_matches(self, id, count):
        self.decl_counts[id] = self.decl_counts.setdefault(id, 0) + count

    def add_ref_matches(self, id, count):
        self.ref_counts[id] = self.ref_counts.setdefault(id, 0) + count

    def legacy(self) -> bool:
        return self.has_legacy

    def no_legacy(self) -> bool:
        return not self.legacy()

    def only_include(self) -> bool:
        if (not self.has_legacy):
            return False
    
        if (len(self.wus) > 0):
            return False

        if (len(self.refs) > 0):
            return False

        if (len(self.get_inref()) > 0):
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

        if (len(self.get_inref()) > 0):
            return False

        return True
    
    def only_internal(self) -> bool:
        if (not self.has_legacy):
            return False

        if (self.only_up()):
            return False

        if (len(self.downref) == 0):
            return False

        if (self.unknown_or_cross()):
            return False

        if (len(self.get_inref()) > 0):
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
        if (self.unknown_or_cross()):
            return False

        if (len(self.get_inref()) == 0):
            return False

        return True

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
        print("%sFile '%s' has %d decls, %d refs, %d up, %d down, %d cross, %d in and %d unknown" % (prefix, self.name, len(
            self.wus), len(self.refs), len(self.upref), len(self.downref), len(self.crossref), len(self.get_inref()), len(self.noref)))

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

# given a list of sets, find the set in the list
# containing "needle"
def set_for_file(haystacks: List[Set[str]], needle: str) -> Set[str]:
    for haystack in haystacks:
        if (needle in haystack):
            return haystack

    raise RuntimeError("File not found in any xref set: %s" % needle)

class WUInfo():
    def __init__(self) -> None:
        self.files: Dict[str, FunFile] = {}
        self.wus: Dict[str, WUDeclList] = {}
        self.xrefsets: List[Set[str]] = []

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

    def print_file_list(self, title, check, prefix="", summary: bool= True, unknowns: bool=False) -> None:
        flist = list(filter(check, self.files.values()))
        print(f'{prefix}{title} [{len(flist)}]')
        for ffile in flist:
            if (summary):
                ffile.print_summary(f'\t{prefix}')
            if (unknowns):
                ffile.print_unknowns(f'\t\t{prefix}')

    def print_file_stats(self, prefix=""):
        print("Files by category...")
        subprefix = f'\t{prefix}'
        self.print_file_list("Clean files (no legacy)...",
                             FunFile.no_legacy, subprefix, summary=False)
        self.print_file_list("Files with no WU decls or refs...",
                             FunFile.only_include, subprefix)
        self.print_file_list("Files with only up references...",
                             FunFile.only_up, subprefix)
        self.print_file_list("Files with up and/or down references...",
                             FunFile.only_internal, subprefix)
        self.print_file_list("Files with only in references...",
                             FunFile.only_in, subprefix)
        self.print_file_list("Files cross references...",
                             FunFile.cross, subprefix)
        self.print_file_list("Files unknown references...",
                             FunFile.unknown, subprefix, unknowns=True)


    def process_xref_info(self, prefix=""):
        print("Cross reference groups...")

        # clean out the list in case
        self.xrefsets = []

        # make a list of all the only_in and cross files
        flist = list(filter(FunFile.only_in, self.files.values()))
        flist += list(filter(FunFile.cross, self.files.values()))

        # add them to the set
        for ff in flist:
            self.xrefsets.append(set([ff.name]))

        # for each file, make sure cross referenced files are in
        # the same set
        for ff in flist:
            # list of filenames, then flatten it
            xrefsls = list(ff.crossreffl.values())          
            xrefs = [fname for sublist in xrefsls for fname in sublist]

            # print("Processing xrefs for %s" % ff.name)
            # print(xrefs)

            # find the set for the current file
            # (updates in place)
            cset = set_for_file(self.xrefsets, ff.name)

            # process all the references
            while (len(xrefs) > 0):

                # get the reference
                fname = xrefs.pop()

                refset = set_for_file(self.xrefsets, fname)

                # already in the same set, skip
                if (cset == refset):
                    continue

                # combine the set
                cset.update(refset)

                # remove the stale set from the list
                self.xrefsets.remove(refset)

        print(f"Crossrefs reduced to {len(self.xrefsets)} ref sets")
        for xset in self.xrefsets:
            print(f"{len(xset)}: {xset}")



###
##  helpers
#

def scan_for_legacy(input:str) -> bool:
    nmatches = len(HEADER_MATCH.matches(input))

    return (nmatches > 0)

###
##  Pattern object
#

class Pattern():
    def __init__(self, id: str, match: str,
                 rewrite: Optional[str] = None) -> None:
        self.match: str = match
        self._rewrite: Optional[str] = rewrite
        self.id:str = id

    def matches(self, input: str):
        l = list(comby.matches(input, self.match))
        return l   

    def rewrite(self, input: str):
        assert(self._rewrite is not None)

        return comby.rewrite(input, self.match, self._rewrite)

    def fwdrewrite(self, input: str) -> str:
        # just pass through since we don't know
        return input

class NoRewritePattern(Pattern):
    def rewrite(self, input: str):
        # do nothing
        return input

class MultipassPattern(Pattern):
    def __init__(self, id: str, match: str,
                 rewrites: List[Tuple[Optional[str], str]],
                 fwdrewrites: Optional[List[Tuple[Optional[str], str]]] = None):
        self.match: str = match
        self.rewrites = rewrites
        self.id: str = id
        self.fwdrewrites = fwdrewrites

    def _do_rewrite_list(self, rewrites: List[Tuple[Optional[str], str]], input: str) -> str:
        for (match, rewrite) in rewrites:
            if (match is None):
                match = self.match

            input = comby.rewrite(input, match, rewrite)
            
        return input

    def rewrite(self, input: str):
        return self._do_rewrite_list(self.rewrites, input)

    def fwdrewrite(self, input: str) -> str:
        # just pass through if we don't know
        if (self.fwdrewrites is None):
            return input

        return self._do_rewrite_list(self.fwdrewrites, input)


GROUP_CUSTOM_MATCH: str = "WU_HANDLER_REGISTER_GROUP(:[module], {wuname}, (:[fnlist]), :[attrs], :[align])"
GROUP_CUSTOM_REWRITE: str = "WU_HANDLER_ALIGNED_GROUP({wuname}, :[attrs], {fnlist})"

def pad_fnlist(fnlist: str):
    # size the existing list
    fns = fnlist.split(",")
    fns = [fn.strip() for fn in fns]
    pads = 16 - len(fns)
    assert(pads >= 0)

    # if the list is full, just go with it
    if (pads == 0):
        return fnlist
    
    # append to the fnlist
    for _ in range(pads):
        fnlist += f",\n                          padding_wuh"

    return fnlist

class GroupPattern(Pattern):
    def __init__(self, id: str, match: str, fwdrewrite: Optional[str]) -> None:
        self.match: str = match
        self.id:str = id
        self._fwdrewrite = fwdrewrite

    def rewrite(self, input: str):

        # find all the matches
        ms = list(comby.matches(input, self.match))

        # nothing to do
        if (len(ms) == 0):
            return input

        # make a pair of patterns for each match
        rewrites: List[Tuple[Optional[str], str]] = []
        for m in ms:
            d = {}
            # print(m)
            d["wuname"] = m.environment["wuname"].fragment
            d["fnlist"] = pad_fnlist(m.environment["fnlist"].fragment)

            match = GROUP_CUSTOM_MATCH.format(**d)
            rewrite = GROUP_CUSTOM_REWRITE.format(**d)
            rewrites.append((match, rewrite))


        # run all the replacements via a multipass
        mp = MultipassPattern("group", "", rewrites)
        return mp.rewrite(input)

    def fwdrewrite(self, input: str) -> str:
        if (self._fwdrewrite is None):
            return input

        return comby.rewrite(input, self.match, self._fwdrewrite)

HEADER_MATCH: Pattern = Pattern("header", "#include <generated/wu_ids.h>",
                                rewrite="#include <nucleus/wu_register.h>")

###
##  WU definition scanning
#

DECLS : List[Pattern] = [
    # first rewrite to add attributes if they're missing, then just rewrite
    MultipassPattern("WU_HANDLER",
                     "WU_HANDLER(:[attrs]) void :[wuname]:[~[ \t]*](:[params])",
                     [ ("WU_HANDLER() void :[wuname]:[~[ \t]*](:[params])",
                        "WU_HANDLER(WU_ATTR_NONE) void :[wuname](:[params])"),

                        ("WU_HANDLER(:[attrs]) void :[[wuname]]:[~[ \t]*](:[~(void)?])",
                        "WU_HANDLER(:[wuname], :[attrs])"),

                        (None, "WU_HANDLER(:[wuname], :[attrs], :[params])")
                     ],
                     [
                       (None, "DECLARE_WU_HANDLER(:[wuname], :[params])")
                     ]
                     ),

    MultipassPattern("WU64_HANDLER",
                     "WU64_HANDLER(:[attrs]) void :[wuname]:[~[ \t]*](:[params])",
                     [ ("WU64_HANDLER() void :[wuname]:[~[ \t]*](:[params])",
                        "WU64_HANDLER(WU_ATTR_NONE) void :[wuname](:[params])"),
                       (None, 'WU64_HANDLER(:[wuname], :[attrs], :[params])'),
                     ],
                     [
                        (None, "DECLARE_WU64_HANDLER(:[wuname], :[params])")
                     ]
                     ),

    # rewrite all the attrs, rewrite void/empty and not void separately
    MultipassPattern("CHANNEL_THREAD",
                     "CHANNEL_THREAD(:[attrs]) void :[[wuname]]:[~[ \t]*](:[params])",
                     [ 
                        ("CHANNEL_THREAD() void :[[wuname]]:[~[ \t]*](:[params])",
                        "CHANNEL_THREAD(WU_ATTR_NONE) void :[wuname](:[params])"),

                        ("CHANNEL_THREAD(:[attrs]) void :[[wuname]]:[~[ \t]*](:[~(void)?])",
                        "CHANNEL_THREAD(:[wuname], :[attrs])"),

                        (None,
                        "CHANNEL_THREAD(:[wuname], :[attrs], :[params])"),
                     ],
                     [
                         ("CHANNEL_THREAD(:[attrs]) void :[[wuname]](void)",
                          "DECLARE_CHANNEL_THREAD_HANDLER(:[wuname])"),
                         (None, "DECLARE_CHANNEL_THREAD_HANDLER(:[wuname], :[params])")
                     ]
                     ),

    # first rewrite to add attributes if they're missing, then just rewrite
    MultipassPattern("CHANNEL",
                     "CHANNEL(:[attrs]) void :[[wuname]]:[~[ \t]*](:[params])",
                     [ ("CHANNEL() void :[[wuname]]:[~[ \t]*](:[params])",
                        "CHANNEL(WU_ATTR_NONE) void :[wuname](:[params])"),
                        (None,
                        "CHANNEL_HANDLER(:[wuname], :[attrs], :[params])")
                     ],
                     [
                         (None, "DECLARE_CHANNEL_HANDLER(:[wuname], :[params])")
                     ]
                     ),

    GroupPattern("WU_HANDLER_REGISTER_GROUP",
                 "WU_HANDLER_REGISTER_GROUP(:[module], :[wuname], (:[fnlist]), :[attrs], :[align])",
                 "DECLARE_WU_GROUP(:[wuname])"),

    # we want to track these for references, but this macro is just what
    # we need for SDK WUs
    NoRewritePattern("WU_HANDLER_REGISTER_DMA_ERR_GROUP",
                     "WU_HANDLER_REGISTER_DMA_ERR_GROUP(:[module], :[wuname], :[fn], :[wu_attrs])"),
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

REFS : List[Pattern] = [
    ## WU API
    Pattern("WUID",
            ":[~\\bWUID](:[wuname])"),
    Pattern("WUATTR",
            ":[~\\bWUATTR](:[wuname])"),
    Pattern("WUGID",
            ":[~\\bWUGID](:[wuname])"),
    Pattern("wu_send",
            ":[~\\bwu_send](:[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("wu_send_priority",
            ":[~\\bwu_send_priority](:[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("wu_send_ungated",
            ":[~\\bwu_send_ungated](:[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("wu_send_priority_ungated", 
            ":[~\\bwu_send_priority_ungated](:[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("wu_send_ungated_nobarrier_unsafe",
            ":[~\\bwu_send_ungated_nobarrier_unsafe](:[wuname], " + DEST_AND_ARGS + ")"),

    ## Timers
    Pattern("wu_timer_start",
            ":[~\\bwu_timer_start](:[id], :[wuname], :[dest], :[arg], :[delay])"),

    ## Flow
    Pattern("flow_push_resume_wu",
            ":[~\\bflow_push_resume_wu](:[callerf], :[wuname], :[rest])"),

    Pattern("flow_push_continuation",
            ":[~\\bflow_push_continuation](:[callerf], :[wuname], :[frame], :[calleef], :[arg2])"),

    Pattern("flow_push_continuation64",
            ":[~\\bflow_push_continuation64](:[callerf], :[wuname], :[frame], :[calleef], :[args])"),

    ## channel  API

    Pattern("channel_push",
            ":[~\\bchannel_push](:[channel], :[wuname], " + DEST_AND_ARGS + ")"),
    # NB dest -> "callee_flow"
    Pattern("channel_flow_push",
            ":[~\\bchannel_flow_push](:[channel], :[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("channel_exception_push",
        ":[~\\bchannel_exception_push](:[channel], :[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("channel_fork",
            ":[~\\bchannel_fork](:[channel], :[framep], :[wuname], " + DEST_AND_ARGS + ")"),
    Pattern("channel_exec_wu",
            ":[~\\bchannel_exec_wu](:[wuname], " + DEST_AND_ARGS + ")"),
]

def scan_file_for_refs(fl: FunFile, input: str) -> List[WURef]:
    matches: List["Comby.match"] = []
    for decl in REFS:
        ref_matches = decl.matches(input)
        fl.add_ref_matches(decl.id, len(ref_matches))
        matches += ref_matches

    return [WURef(match) for match in matches]


###
##  header fixups
#

def fixup_match(fixup: str, fname: str) -> bool:

    if (fixup == '*'):
        return True

    if (fname == fixup):
        return True

    if (fname.startswith("./")):
        fname = fname[2:]

    if (fname.startswith(fixup)):
        return True

    return False

def set_fixup_match(fixup:str, xset: Set[str]) -> bool:
    for x in xset:
        if (fixup_match(fixup, x)):
            return True

    return False

def do_fixup_headers(wuinfo: WUInfo, fileinfo: Dict[str, FunFile], fixup: str):

    # make the list of files that would be fixed up
    flist = list(filter(FunFile.only_include, wuinfo.files.values()))

    count = 0
    for fl in flist:
        if (not fixup_match(fixup, fl.name)):
            print(f'Skipping header fix for file {fl.name}')
            continue

        print(f'Fixing headers for file {fl.name}')
        
        input = open(fl.name, "r").read()
        input = HEADER_MATCH.rewrite(input)
        open(fl.name, "w").write(input)
        count += 1

    print(f"Fixed up headers for {count} files")

def do_fixup_ups(wuinfo: WUInfo, fileinfo: Dict[str, FunFile], fixup: str):

    # firstly we need to fixup all the headers
    # make the list of files that would be fixed up
    flist = list(filter(FunFile.only_up, wuinfo.files.values()))

    count = 0
    for fl in flist:
        if (not fixup_match(fixup, fl.name)):
            print(f'Skipping ups fix for file {fl.name}')
            continue

        print(f'Fixing ups for file {fl.name}')
        input = open(fl.name, "r").read()
    
        # rewrite the header
        input = HEADER_MATCH.rewrite(input)

        # rewrite all the decls
        for decl in DECLS:
            input = decl.rewrite(input)

        open(fl.name, "w").write(input)
        count += 1

    print(f"Fixed up headers for {count} files")
        


class SplitPattern():
    def __init__(self, start:str, ):
        self.start = Pattern("split_start", start)

    def match(self, orig_input: str) -> Optional[Tuple[str, str]]:

        # wrap input in something balanced so comby will do the right thing
        input = f"{{{orig_input}}}"

        starts = self.start.matches(input)
        if (len(starts) == 0):
            return None

        assert(len(starts) == 1)

        rest = starts[0].environment["rest"].fragment
        start = starts[0].matched[:-len(rest)]

        # trim the curly braces we added
        start = start[1:]
        rest = rest[:-1]

        # fixup for las line diff annoyance
        if ((orig_input[-1] == "\n") and (rest[-1] != "\n")):
            rest += '\n'

        return (start, rest)


# Find the end of the module part / declaration so we can split around
# that. comby won't match "everything" for start/rest unless we wrap the
# whole input in something balanced, so we wrap the whole file in {}
SPLIT_PATTERNS: List[SplitPattern] = [
            SplitPattern("{:[start]MODULE_PART(...):[~;?]:[rest]}"),
            SplitPattern("{:[start]MODULE_DEF_END():[~;?]:[rest]}"),
            SplitPattern("{:[start]MODULE_END_SDK():[~;?]:[rest]}")
]

def split_input_for_fwd(fname: str, input: str) -> Tuple[str, str]:

    # apply patterns until we find a match
    for sp in SPLIT_PATTERNS:
        tup = sp.match(input)
        if (tup is None):
            continue

        return tup

    raise RuntimeError(f"Could not split file {fname}!")

SPLIT_INCL = SplitPattern("{:[start]#include <nucleus/wu_register.h>:[rest]}")

def split_input_for_includes(input: str) -> Tuple[str, str]:
    assert(input.find("wu_register.h") != -1)
    tup = SPLIT_INCL.match(input)
    assert(tup is not None)
    return tup


# python regex from legacy generate-wutab.py 
# m = re.match(r"^(const )?struct (?P<struct_name>[a-zA-Z0-9_]+)", arg)

STRUCT_PAT = Pattern("structs", "struct :[[structname]]")
KNOWN_STRUCTS = set(["frame", "channel", "flow", "ws_exception", "timer_arg"])
def scrape_structs(decl: str) -> Set[str]:

    ret = set()
    matches = STRUCT_PAT.matches(decl)

    for match in matches:
        # print(match.environment["structname"].fragment)
        ret.add(match.environment["structname"].fragment)

    return ret - KNOWN_STRUCTS

# foward declaration header template
FWD_TEMPL = """
/* These are automagically generated forward declarations for legacy WU
 * handlers. These declarations are only needed because these WUs are
 * referenced in this file before they are declared. Forward declarations
 * are not needed for properly ordered code (unless in the case of a 
 * legitimate circular reference).
 */
"""

def fwd_decls_for_wus(wuinfo: WUInfo, refs: Set[str]) -> str:

    wu_fwd = ""
    struct_fwd = set();
    for wuname in refs:
        print(f"\tReference to {wuname} found")

        # generate the declarations for it
        decl_strs = wuinfo.wus[wuname].decl_strs()

        # just run all the rewrites over them
        for wu_str in decl_strs:
            orig = wu_str
            for decl in DECLS:
                wu_str = decl.fwdrewrite(wu_str)
            
            if (wu_str == orig):
                print(f"WU {wuname} did not get rewritten for forward declaration. Assuming group")
                continue

            # scrape any struct types. This is ugly, but no way to change old code without it
            struct_fwd.update(scrape_structs(wu_str))

            # append the declaration
            wu_fwd += f'{wu_str};\n'

    # make the struct forward declarations
    for sname in struct_fwd:
        wu_fwd = f"struct {sname};\n" + wu_fwd

    return wu_fwd

def fixup_file_internal(wuinfo: WUInfo, fl: FunFile):
    print(f'Fixing internals for file {fl.name}')
    input = open(fl.name, "r").read()

    # rewrite the header
    input = HEADER_MATCH.rewrite(input)

    # generate the actual declarations, but only for things that won't
    # appear an an xref header
    wu_fwd = fwd_decls_for_wus(wuinfo, fl.downref - set(fl.inref.keys()))

    # add the wu declarations
    all_fwd = FWD_TEMPL + wu_fwd

    # patch them into the file
    if (len(fl.downref) > 0):
        (first, last) = split_input_for_fwd(fl.name, input)
        input = first + all_fwd + last

    # now rewrite all the decls
    for decl in DECLS:
        input = decl.rewrite(input)

    open(fl.name, "w").write(input)

def do_fixup_internal(args, wuinfo: WUInfo, fileinfo: Dict[str, FunFile], fixup: str):

    # firstly we need to fixup all the headers
    # make the list of files that would be fixed up
    flist = list(filter(FunFile.only_internal, wuinfo.files.values()))

    if (args.force):
        flist.append(fileinfo[fixup])

    count = 0
    for fl in flist:
        if (not fixup_match(fixup, fl.name)):
            print(f'Skipping ups fix for file {fl.name}')
            continue
        
        fixup_file_internal(wuinfo, fl)
        count += 1


    print(f"Fixed up internals for {count} files")


def hfile_for_filename(flname: str) -> str:
    fname = os.path.splitext(flname)[0] + ".wuids.h"
    if (fname.startswith("./")):
        fname = fname[2:]
    return fname

def hfile_for_file(fl: FunFile) -> str:
    return hfile_for_filename(fl.name)

def hguard_for_file(fl: FunFile) -> str:
    fname = os.path.splitext(fl.name)[0]
    if (fname.startswith("./")):
        fname = fname[2:]
    fname = fname.upper()
    fname.replace(".", "_")
    fname = fname.replace("/", "_")
    fname = f"__{fname}_LEGACY_WUIDS_H__"
    return fname

WU_HEADER_TEMPL = f"""/*
 *  {{hname}}
 *
 *  Machine generated on on {datetime.date.today().isoformat()}.
 *  Copyright © {datetime.date.today().year} Fungible. All rights reserved.
 *
 *
 * WARNING: This file is machine generated!!!!
 *
 * This file contains WU declarations for legacy WUs that were not using
 * push functions and were referenced from other C files.
 *
 * Do not add new declarations or other code to this file, they will be
 * overwritten and deleted.
 *
 * Do not copy the style in this file. All code should be using push functions.
 *
 * _Do_ convert the WUs in this file to push functions and update the callers,
 * then remove this file.
 *
 * You have been forewarned.
 */

#ifndef {{hguard}}
#define {{hguard}}

{{hcontents}}

#endif /* {{hguard}} */
"""

INCL_TEMPL = "#include <{hname}> /* XXX: external WU references should be replaced with push functions / API */"

def include_wuid_headers_in_file(fl: FunFile, hnames: Set[str]):

    inclist: List[str] = []
    for hname in hnames:
        inclist.append(INCL_TEMPL.format(hname=hname))

    incls: str = "\n".join(inclist)

    print(f"Adding includes to file {fl.name}: \n{incls}")

    # read the file
    fd = open(fl.name, "r")
    input = fd.read()

    # do the patching
    (first, last) = split_input_for_includes(input)
    output = first + incls + last

    # write it back
    fd = open(fl.name, "w")
    fd.write(output)

def publish_inrefs(wuinfo: WUInfo, fl: FunFile) -> None:    
    hname = hfile_for_file(fl)
    print(f"\t\t\tpublishing inrefs {fl.inref} for {fl.name} to {hname}")

    # generate declarations for all the in references
    declstr = fwd_decls_for_wus(wuinfo, set(fl.inref.keys()))

    # prepare the format arguments
    hargs = {}
    hargs["hguard"] = hguard_for_file(fl)
    hargs["hname"] = hname
    hargs["hcontents"] = declstr

    # generate the file contents
    s = WU_HEADER_TEMPL.format(**hargs)

    # write out the file
    fd = open(hname, "w")
    fd.write(s)

    # add the header to the source file itself
    include_wuid_headers_in_file(fl, set([hname]))

    # now add it to git
    subprocess.run(["git", "add", hname])



def add_xref_headers_to_file(wuinfo: WUInfo, fl: FunFile) -> None:
    print(f"\t\t\tadding headers to file {fl.name} for xrefs {fl.crossreffl}")

    # make the list of headers we expect
    hnames = set()

    for fset in fl.crossreffl.values():
        for fname in fset:
            hnames.add(hfile_for_filename(fname))

    # add the header to the file
    include_wuid_headers_in_file(fl, hnames)

def fixup_file_xrefs(wuinfo: WUInfo, fileinfo: Dict[str, FunFile], fname: str):

    print(f"\tfixing xrefs for file {fname}")

    # lookup the file for the name
    fl = fileinfo[fname]

    print(f"\t\tdownrefs: {fl.downref}")
    print(f"\t\tinrefs: {fl.inref}")
    print(f"\t\txrefs: {fl.crossreffl}")

    # convert the internals of the file
    fixup_file_internal(wuinfo, fl)

    # publish in-refs to extenal
    if (len(fl.inref) > 0):
        publish_inrefs(wuinfo, fl)
    else:
        print(f"\t\t\tNo inrefs for file {fl.name}")

    # if we reference any externals
    if (len(fl.crossreffl) > 0):
        # include headers for externals
        add_xref_headers_to_file(wuinfo, fl)
    else:
        print(f"\t\t\tNo xrefs for file {fl.name}")

def do_fixup_xrefs(wuinfo: WUInfo, fileinfo: Dict[str, FunFile], fixup: str):
        
    # get the list of sets from the wuinfo
    xrefsets = wuinfo.xrefsets

    # loop over it, check for fixups
    for xset in xrefsets:
        if (not set_fixup_match(fixup, xset)):
            # print(f'Skipping fix ups for set {xset}')
            continue

        print(f'\tProcessing fix ups for set {xset}')

        # for each file
        for fname in xset:
            # fixup the file
            fixup_file_xrefs(wuinfo, fileinfo, fname)

###
##  Depd
#

def fixname(fname: str) -> str:
    if (fname.startswith("./")):
        fname = fname[2:]
    return fname

def do_file_deps(wuinfo: WUInfo, fl: FunFile):

    # iterate over all the cross-references and
    # generate a link per WU file
    for (wuname, fnames) in fl.crossreffl.items():
        for fname in fnames:
            print(f'\t"{fixname(fl.name)}" -> "{fixname(fname)}";')

def do_deps(wuinfo: WUInfo, fileinfo: Dict[str, FunFile], fixup: str):

    # get the list of sets from the wuinfo
    xrefsets = wuinfo.xrefsets

    # loop over it, check for fixups
    for xset in xrefsets:
        if (not set_fixup_match(fixup, xset)):
            # print(f'Skipping fix ups for set {xset}')
            continue

        print(f'\tProcessing fix ups for set {xset}')

        # for each file
        for fname in xset:
            # fixup the file
            do_file_deps(wuinfo, fileinfo[fname])



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
    parser.add_argument("-P", "--path", action="store", type=str, 
                        help="Path to scan",
                        default=".")

    # Number of parallel processes
    parser.add_argument("-n", "--nprocs", action="store", type=int, 
                        help="Number of processes for file parsing",
                        default=4)

    # Where to stash pre-processed files
    parser.add_argument("-T", "--tmpdir", action="store", type=str, 
                        help="Temporary path for parsing info",
                        default="build-legacy")

    # Dump a dependecy graph of xrefs
    parser.add_argument("-D", "--deps", action="store", type=str, 
                        help="Dependency graph", default=None)

    # Whether to fixup anything 
    parser.add_argument("-F", "--fixup", action="store", type=str, 
                        help="Path to fixup as much as possible",
                        default=None)

    parser.add_argument("--fixup-headers", action="store_true",
                       help="Fixup headers")

    parser.add_argument("--fixup-ups", action="store_true",
                       help="Fixup up-only files")

    parser.add_argument("--fixup-internal", action="store_true",
                       help="Fixup up-and-down (internal-only) files")

    parser.add_argument("--fixup-xrefs", action="store_true",
                       help="Fixup cross-referenced files")

    parser.add_argument("--force", action="store_true",
                       help="Force fixing up the specified file")


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

def file_worker(argtup: Tuple[str, str]) -> None:


    # source filename an pickle filename
    (fname, pname) = argtup

    # print("File worker starting on %s" % fname)

    # print("Hashing file '%s'" % fname)
    input = open(fname).read()

    try:
        fl = pickle.load(open(pname, "rb"))
    except:
        print("File not cached: %s" % fname)
        fl = FunFile(fname)

    # check MD5
    md5 = hashlib.md5(input.encode()).hexdigest()

    # file needs updaring 
    if ((fl.md5 != md5) and (len(input) > 0)):
        print("Processing file '%s'" % fname)
        fl = FunFile(fname)

        # see if this is even a match
        if (scan_for_legacy(input)):
            print("File '%s' has legacy headers" % fname)
            fl.has_legacy = True
            fl.declist = scan_file_for_decls(fl, input)
            fl.reflist = scan_file_for_refs(fl, input)
        else:
            fl.declist = None
            fl.reflist = None

        fl.md5 = md5
            
    # save the file
    os.makedirs(os.path.dirname(pname), exist_ok=True)
    pickle.dump(fl, open(pname, "wb"))

def picklefile(args, fname):
    return os.path.join(args.tmpdir, fname) + ".pickle"

###
##  main
#
def main() -> int:
    args: argparse.Namespace = parse_args()

    wuinfo = WUInfo()

    print("Finding C files...")
    # make the list of all the files
    output = subprocess.run(["find", args.path, "-name", "*.c"],
                            capture_output=True).stdout
    fnames = output.decode().strip().split("\n")

    print("Found %d files" % len(fnames))

    flist: List[Tuple[str, str]] = []

    # add everyting to the list
    for fname in fnames:
        if (fname.startswith("./build/")):
            continue
        if (fname.startswith("./.git/")):
            continue
        flist.append((fname, picklefile(args, fname)))

    # process the list in parallel
    if (args.nprocs > 1):
        print("Forking off file parsing...")
        multiprocessing.Pool(args.nprocs).map(file_worker, flist)
    else:
        print("Processing files inline...")
        for f in flist:
            file_worker(f)

    # parse all the pickle files
    print("Files processed, loading contents...")
    fileinfo = {}
    for (fname, pname) in flist:
        fl = pickle.load(open(pname, "rb"))
        #assert(fname == fl.name)
        fileinfo[fname] = fl
        wuinfo.add_file(fname, fl)
        if (fl.declist is not None):
            wuinfo.add_wulist(fname, fl.declist)
        if (fl.reflist is not None):
            wuinfo.add_wurefs(fname, fl.reflist)
    
    print("Pickle files loaded, processing the data...")

    # process the data now we have it all
    wuinfo.process_data()

    # Dump our info
    wuinfo.print_info()

    # print file stats
    wuinfo.print_file_stats()

    # print xref info
    wuinfo.process_xref_info()

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

    if (args.deps is not None):
        print(f"Attempting deps on {args.deps}")
        do_deps(wuinfo, fileinfo, args.deps)


    if (args.fixup is not None):
        print(f"Attempting fixups on {args.fixup}")

        if (args.fixup_headers):
            do_fixup_headers(wuinfo, fileinfo, args.fixup)

        if (args.fixup_ups):
            do_fixup_ups(wuinfo, fileinfo, args.fixup)

        if (args.fixup_internal):
            do_fixup_internal(args, wuinfo, fileinfo, args.fixup)

        if (args.fixup_xrefs):
            do_fixup_xrefs(wuinfo, fileinfo, args.fixup)

    return 0
 
###
##  entrypoint
#
if __name__ == "__main__":
    main()
