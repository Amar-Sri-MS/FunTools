#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix mangling call sites for FunOS/FunSDK code based on gcc error messages

How to use:

### Simple self-test, run the unit tests:
./mangflefix.py -U

### loop to iterate on fixing mangles:

 # cd into your project (note, requires latest FunTools also in $WORKSPACE)
 1. cd ${WORKSPACE}/{FunOS, FunBlockDev,...}
 # clean build results so bad deps don't kill you
 2. make clean
 # try and build every target for a given machine and capture errors to log file
 3. make -j8 MACHINE=s2 -k >minmangle.err 2>&1
 # check status
 4. echo $?
 # inspect errors
 5. cat minmangle.err | grep "error:" | less
 # run the mangle fixer
 6. time ${WORKSPACE}/FunTools/scripts/manglefix.py --errfile minmangle.err
 # re-run the make to see what's needs hand fixing (rinse and repeat)
 7. make -j8 MACHINE=s2

 # pro-tip: the vscode "Changed lines" lines feature is super helpful when reviewing
 # manglefix changes. It's the blue-and-white diagonally striped side-bar on the
 # left next to the line number. Click the vertical bar and it will show you the
 # changes since the last commit and you can copy the previous code / use it as a
 # reference to tweak by hand.

static check:
% mypy manglefile.py
 
format:
% python3 -m black manglefix.py
"""
from typing import List, Optional, Type, Dict, Any, Tuple
import argparse
import re
from comby import Comby # type: ignore 
import os
import pickle
import glob
import fnmatch

comby = Comby(language=".c")

## parse the following line with regex:
## accelerators/crypto_hostif.c:3567:22: error: ‘struct fun_req_common’ has no member named ‘op’; did you mean ‘op_l’?
## <filname>:<line>:<col>: error: ‘struct <struct>’ has no member named ‘<member>’; did you mean ‘<member>_l’?

## Just the regext for the file, line and maybe column and a space
RE_FILE: str = r"([\.\/a-zA-Z0-9_-]+):(\d+):(\d+:)? "
RE_ERR: str = RE_FILE + r"error: .(?:const )?struct (\w+). has no member named .(\w+).; did you mean .(\w+)_[a-zA-Z].\?"


MAX_LOG_LEVEL: int = 0
DEFAULT_TEST_CASES: int = 3

def LOG(msg: str, level: int = 0) -> None:
    if level <= MAX_LOG_LEVEL:
        print(msg)

def VERBOSE(msg: str) -> None:
    LOG(msg, 1)

def DEBUG(msg: str) -> None:
    LOG(msg, 2)

###
##  sdk dir finding
#

def find_sdkdir() -> str:
    # check for env var
    if 'SDKDIR' in os.environ:
        return os.environ['SDKDIR']

    # check for workspace
    if 'WORKSPACE' in os.environ:
        return os.path.join(os.environ['WORKSPACE'], "FunSDK")

    # guess root based on script path
    scriptpath = os.path.realpath(__file__)
    scriptdir = os.path.dirname(scriptpath)

    # $WORKSPACE/FunTools/scripts -> $WORKSPACE/FunSDK
    sdkdir = os.path.join(scriptdir, "..", "..", "FunSDK")

    if os.path.exists(sdkdir):
        VERBOSE(f"Guessed SDKDIR: {sdkdir}")
        return sdkdir

    # random junk
    return "/does_not_exist"    
    

def get_test_dir(args: argparse.Namespace) -> str:
    # "manglefix_test" directory in the same directory as the script
    scriptpath = os.path.realpath(__file__)
    scriptdir = os.path.dirname(scriptpath)
    testdir = os.path.join(scriptdir, "manglefix_test")
    return testdir

###
##   classes
#
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
                        line: str,
                        lineno: int,
                        col: int,
                        struct: str,
                        member: str):
        self.filename: str = filename
        self.line: str = line
        self.lineno: int = lineno
        self.col: int = col
        self.struct: str = struct
        self.member: str = member

    def __str__(self) -> str:
        return f"{self.line}: {self.stname}"


def add_fixup_for_error(fixups: Optional[Dict[str, List[Fixup]]], filename: str, errtext: str) -> Fixup:
    # match the error text
    match = re.match(RE_ERR, errtext)
    if match is None:
        raise RuntimeError(f"Error parsing error text: {errtext} in {filename}")

    filename = match.group(1)
    lineno = int(match.group(2))
    try:
        col = int(match.group(3))
    except:
        col = -1
    struct = match.group(4)
    member = match.group(5)
    member_l = match.group(6)

    # ensure member == member_l
    if member != member_l:
        VERBOSE(f"member != member_l: {member} != {member_l}")
        return

    # add it to fixups, if we're collecting
    fixup = Fixup(filename, errtext, lineno, col, struct, member)
    if (fixups is not None):
        fixups.setdefault(filename, list()).append(fixup)

    return fixup

###
##  line rewrite logic
#

class Testcase():
    def __init__(self, name: str, intext: str, outtext: str, fixup: Fixup,
                filename: Optional[str] = None, nooutfile: bool = False):
        self.name: str = name
        self.filename: Optional[str] = filename
        self.new = self.filename is None
        self.intext: str = intext
        self.outtext: str = outtext
        self.errtext: str = fixup.line
        self.nooutfile: bool = nooutfile

    def is_new(self):
        return self.new

class Rewrite():
    def __init__(self, name: str, match: str, replace: str):
        self.name: str = name
        self.match: str = match
        self.replace: str = replace
        self.tests: List[Testcase] = []
        self.usedcount = 0

    def inctests(self):
        self.testcount += 1

    def testcase(self, args: argparse.Namespace, intext: str,
                    outtext: str, fixup: Fixup) -> None:
        if ((len(args.line) == 0) and (len(self.tests) >= DEFAULT_TEST_CASES)):
            return

        tc: Testcase = Testcase(self.name, intext, outtext, fixup)
        LOG(f"Created new test case {tc.name}")
        self.tests.append(tc)

    def incused(self):
        self.usedcount += 1

    def newtestcases(self):
        count = 0
        for tc in self.tests:
            if (tc.is_new()):
                count += 1

        return count

    def __str__(self) -> str:
        return f"{self.name}: {self.match} -> {self.replace}"

# rewrites for lines missing accessors (usually arrays)
ARRAY_REWRITES: List[Tuple[str, str, str]] = [
    # take precidence over the other rewrites
    Rewrite("array-4", "&:[expr:e]->{member}[0]", "hci_array_access(:[expr]->{member})"),
    Rewrite("array-5", "&:[expr:e].{member}[0]", "hci_array_access(:[expr].{member})"),

    # simple array accesses via pointer
    Rewrite("array-0", ":[expr:e]->{member};", "hci_array_access(:[expr]->{member});"),
    Rewrite("array-1", ":[expr:e]->{member}", "hci_array_access(:[expr]->{member})"),
    
    # simple array accesses via member
    Rewrite("array-2", ":[expr:e].{member};", "hci_array_access(:[expr].{member});"),
    Rewrite("array-3", ":[expr:e].{member}", "hci_array_access(:[expr].{member})"),

]

# rewrites for lines with nested accessors (type mismatch)
NESTED_REWRITES: List[Tuple[str, str, str]] = [
    Rewrite("nest-0", ":[expr:e]->:[nest:e].{member}:[semi~;?]",
        "{struct}_get_{member}(:[expr]):[semi]"),

    Rewrite("nest-1", "(:[expr:e]->:[nest:e].{member}):[semi~;?]",
        "({struct}_get_{member}(:[expr])):[semi]"),

    Rewrite("nest-2", ":[expr:e]->{member}:[semi~;?]",
        "{struct}_get_{member}(:[expr]):[semi]"),

    Rewrite("nest-3", "(:[expr:e].{member}):[semi~;?]",
        "({struct}_get_{member}(:[expr])):[semi]"),
]

# catch-all rewrites for general field access
REWRITES: List[Tuple[str, str, str]] = [
    # Ambiguous assignments where "member" is on both sides. re-write to a
    # macro accessor we can resolve later
    Rewrite("amgib-0", ":[expr0:e]->{member} = :[expr1:e]->{member}:[semi~;?]",
                "HCI_AMBIGUOUS_ASSIGN(UNK, {struct}, {member}, :[expr0], ->, :[expr1], ->):[semi]"),

    Rewrite("amgib-1", ":[expr0:e].{member} = :[expr1:e]->{member}:[semi~;?]",
                "HCI_AMBIGUOUS_ASSIGN(UNK, {struct}, {member}, :[expr0], ., :[expr1], ->):[semi]"),

    # regular assignments -> set accessor
    # need a variant with semicolon and without because of the way comby parses weird
    Rewrite("set-0", ":[expr:e]->{member} = :[value];", "{struct}_set_{member}(:[expr], :[value]);"), # XXX: semicolon
    Rewrite("set-1", ":[expr:e]->{member} = :[value:e]", "{struct}_set_{member}(:[expr], :[value])"),
    Rewrite("set-2", ":[expr:e].{member} =:[sp~[ \t\n]+]:[value:e];",
            "{struct}_set_{member}(&:[expr],:[sp]:[value]);"), # XXX: semicolon
    Rewrite("set-3", ":[expr:e].{member} =:[sp~[ \t\n]+]:[value:e]",
            "{struct}_set_{member}(&:[expr],:[sp]:[value])"),

    # or-equals (|=) assignments -> expand to a set and a get, eg.
    # foo->bar |= expr; -> foo_set_bar(foo_get_bar(foo) | expr);
    Rewrite("oreq-0", ":[expr:e]->{member} |= :[value:e];",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) | :[value]);"), # XXX: semicolon
    Rewrite("oreq-1", ":[expr:e]->{member} |= :[value:e]",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) | :[value])"),

    # and-equals (&=) assignments -> expand to a set and a get, eg.
    # foo->bar &= expr; -> foo_set_bar(foo_get_bar(foo) & expr);
    Rewrite("andeq-0", ":[expr:e]->{member} &= :[value:e];",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) & :[value]);"), # XXX: semicolon
    Rewrite("andeq-1", ":[expr:e]->{member} &= :[value:e]",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) & :[value])"),

    # plus-equals (+=) assignments -> expand to a set and a get, eg.
    # foo->bar += expr; -> foo_set_bar(foo_get_bar(foo) + expr);
    Rewrite("addeq-0", ":[expr:e]->{member} += :[value:e];",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) + :[value]);"), # XXX: semicolon
    Rewrite("addeq-1", ":[expr:e]->{member} += :[value:e]",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) + :[value])"),
    Rewrite("subeq-0", ":[expr:e]->{member} -= :[value:e];",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) - :[value]);"), # XXX: semicolon
    Rewrite("subeq-1", ":[expr:e]->{member} -= :[value:e]",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) - :[value])"),

    # postinc (++) assignments -> expand to a set and a get, eg.
    # foo->bar++; -> foo_set_bar(foo_get_bar(foo) + 1);
    Rewrite("postinc-0", ":[expr:e]->{member}++;",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) + 1);"), # XXX: semicolon
    Rewrite("postinc-1", ":[expr:e]->{member}++",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) + 1)"),
    Rewrite("postsub-0", ":[expr:e]->{member}--;",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) - 1);"), # XXX: semicolon
    Rewrite("postsub-1", ":[expr:e]->{member}--",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) - 1)"),


    # shift-equals (>>=) assignments -> expand to a set and a get, eg.
    # foo->bar >>= expr; -> foo_set_bar(foo_get_bar(foo) >> expr);
    Rewrite("shifteq-0", ":[expr:e]->{member} >>= :[value:e];",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) >> :[value]);"), # XXX: semicolon
    Rewrite("shifteq-1", ":[expr:e]->{member} >>= :[value:e]",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) >> :[value])"),
    Rewrite("shifteq-2", ":[expr:e]->{member} <<= :[value:e];",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) << :[value]);"), # XXX: semicolon
    Rewrite("shifteq-3", ":[expr:e]->{member} <<= :[value:e]",
        "{struct}_set_{member}(:[expr], {struct}_get_{member}(:[expr]) << :[value])"),

    # address-of accessors
    Rewrite("addrof-0", "&:[expr:e]->{member}", "hci_addressof(:[expr]->{member})"),
    Rewrite("addrof-1", "&:[expr:e].{member}", "hci_addressof(:[expr].{member})"),
    Rewrite("addrof-2", "&(:[expr:e]->{member})", "hci_addressof(:[expr]->{member})"),
    Rewrite("addrof-3", "&(:[expr:e].{member})", "hci_addressof(:[expr].{member})"),

    # get accessors with "!" on the front. comby weird parsing again
    Rewrite("not-0", "!:[expr:e]->{member}", "!{struct}_get_{member}(:[expr])"), # XXX: exclamation
    Rewrite("not-1", "!:[expr:e].{member}", "!{struct}_get_{member}(&:[expr])"), # XXX: exclamation

    # get accessors. The suble differeneces in casts confuse comby, so we enumerate the possibilities
    Rewrite("get-ptr-0", "(:[cast])->:[expr:e]->{member}",
            "{struct}_get_{member}(&(:[cast])->:[expr])"), # XXX: cast type
    Rewrite("get-ptr-1", "(:[cast])->:[expr:e].{member}",
            "{struct}_get_{member}(&(:[cast])->:[expr])"), # XXX: cast type
    Rewrite("get-ptr-2", "(:[cast]):[expr:e]->{member}",
            "(:[cast]){struct}_get_{member}(:[expr])"), # XXX: cast result
    Rewrite("get-ptr-3", ":[expr:e]->{member}", "{struct}_get_{member}(:[expr])"),

    # get accessors. The suble differeneces in casts confuse comby, so we enumerate the possibilities
    Rewrite("get-mem-0", "(:[cast]).:[expr:e].{member}",
            "{struct}_get_{member}(&(:[cast]).:[expr])"), # XXX: cast type
    Rewrite("get-mem-1", "(:[cast]).:[expr:e]->{member}",
            "{struct}_get_{member}(&(:[cast]).:[expr])"), # XXX: cast type
    Rewrite("get-mem-2", "(:[cast]):[expr:e].{member}",
            "(:[cast]){struct}_get_{member}(&:[expr])"), # XXX: cast result
    Rewrite("get-mem-3", ":[expr:e].{member}", "{struct}_get_{member}(&:[expr])"),
]

ALL_REWRITES: List[Rewrite] = ARRAY_REWRITES + NESTED_REWRITES + REWRITES

def fixup_line(args: argparse.Namespace, accessors: Dict[str, Accessor],
                lines: List[str], fixup: Fixup) -> None:

    LOG(f"Fixing up line: {fixup.line.strip()} for {fixup.struct}.{fixup.member}")

    # assume base accessor names
    gettr = f"{fixup.struct}_get_{fixup.member}"
    settr = f"{fixup.struct}_set_{fixup.member}"

    # assume the full member name
    member = fixup.member

    if (gettr  in accessors.keys()) and (settr  in accessors.keys()):
        if (accessors[gettr].structarg != fixup.struct):
            # no type match, so likely a nested accessor
            VERBOSE(f'\tAppears to be a nested accessor {accessors[gettr].structarg} != {fixup.struct}')
            rewrite_list = NESTED_REWRITES
        else:
            # accessor with type match, so use regular rewrites
            VERBOSE('\tAppears to be a regular accessor')
            rewrite_list = REWRITES
    else:
        rewrite_list = None

        # otherwise, try the "_pack" suffix
        if (fixup.member.endswith("_pack")):
            memnopack = fixup.member[:-5]
            gettr = f"{fixup.struct}_get_{memnopack}"
            settr = f"{fixup.struct}_set_{memnopack}"

            # assume we're just doing this crazy with regular rewrites
            if (gettr  in accessors.keys()) and (settr  in accessors.keys()):
                # update member and use the normal rewrites
                member = memnopack
                rewrite_list = REWRITES

        if (rewrite_list is None):
            # no accessor, so try array rewrites
            VERBOSE('\tAppears to be an array')
            rewrite_list = ARRAY_REWRITES

    # get the line
    line = lines[fixup.lineno - 1]

    # see if it needs to become multi-line
    inputlines: int = 1
    if (line.strip()[-1] == "="):
        VERBOSE(f"Multi-line assignment: {line.strip()}")
        offset = 0
        while True:
            addline = lines[fixup.lineno + offset]
            line += addline
            offset += 1
            if (";" in addline):
                inputlines = offset + 1
                break

        assert inputlines > 1
        VERBOSE(f"Identified multi-line assignment: {inputlines} lines")

    for rewrite in rewrite_list:

        matchstr = rewrite.match.format(member=fixup.member, struct=fixup.struct)
        replacestr = rewrite.replace.format(member=member, struct=fixup.struct)

        oline = line
        line = comby.rewrite(line, matchstr, replacestr)

        if (line == oline):
            # next
            continue

        LOG(f"Rewrite {rewrite.name}: {oline} -> {line}")

        # re-write each line into the result
        newlines = line.split("\n")
        if (newlines[-1] == ""):
            newlines = newlines[:-1]
        outputlines = len(newlines)
        assert outputlines <= inputlines
        if (outputlines < inputlines):
            LOG(f"Lost input lines {inputlines} -> {outputlines}, appending empty lines")
            newlines += [""] * (inputlines - outputlines)
        # re-append the newlines
        newlines = [line + "\n" for line in newlines]
        offset = -1
        for nline in newlines:
            lines[fixup.lineno + offset] = nline
            offset += 1
        
        rewrite.incused()
        rewrite.testcase(args, oline, line, fixup)

        # only allow a single rewrite per fixup on a line
        break

def fixup_file(args: argparse.Namespace, accessors: Dict[str, Accessor],
                filename: str, fixup_list: List[Fixup]) -> None:
    LOG(f"Fixing up file: {filename}")

    # read the file
    fl = open(filename, "r")
    lines = fl.readlines()
    fl.close()

    # for each line, fix it up
    for fixup in fixup_list:
        # skip if we're filtering by line
        if (args.line) and (fixup.lineno not in args.line):
            VERBOSE(f"Skipping line {fixup.lineno} due to --line")
            continue

        # do the actual fixup
        fixup_line(args, accessors, lines, fixup)

    if (not args.unit_test_mode):
        if (args.no_write):
            VERBOSE(f"Not writing file {filename} due to --no-write")
        else:
            # operational mode: write back the file
            fl = open(filename, "w")
            for line in lines:
                fl.write(line)
            fl.close()
    else:
        # unit test mode: validate the file against the .out file
        outfilename = filename.replace(".in", ".out")
        if (not os.path.exists(outfilename)):
            LOG(f"Missing model output file {outfilename} for {filename}, skipping validation")
        else:
            fl = open(outfilename, "r")
            outlines = fl.readlines()
            fl.close()

            # compare inlines and outlines
            for (inline, outline) in zip(lines, outlines):
                if (inline != outline):
                    LOG(f"Validation failed: '{repr(inline)}' ({len(inline)}) != '{repr(outline)}' ({len(outline)})")
                    raise RuntimeError("Test failed!")

            LOG(f"Validation passed for {filename}")

        

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
def load_accessors(hciheaders: str) -> Dict[str, Accessor]:

    # check the timestamp on hciheader
    # if it's newer than PKLFILE, regenerate PKLFILE
    # if PKLFILE exists, load it
    # otherwise, parse hciheader and save PKLFILE

    if os.path.exists(PKLFILE):
        LOG(f"Loading cached accessors from {PKLFILE}")
        try:
            with open(PKLFILE, "rb") as fl:
                accessors = pickle.load(fl)
                return accessors
        except Exception as e:
            LOG(f"Error loading pickle file: {e}")
            pass

    acc_files = glob.glob(hciheaders)

    if len(acc_files) == 0:
        raise RuntimeError(f"No headers found matching {hciheaders}")

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
##  test case reading, writing and re-evaluating
#

def write_test_cases(args: argparse.Namespace, rewrite: Rewrite) -> None:
    VERBOSE(f"Writing test cases for {rewrite.name}")

    # get the path to the tests
    testdir = get_test_dir(args)

    # first work out the existing max test case number
    globstr = f"{testdir}/{rewrite.name}--*.in"
    files = glob.glob(globstr)
    maxnum = -1
    for file in files:
        # LOG(f"Found test case {file}")
        match = re.match(f".*/{rewrite.name}--(\\d+).in", file)
        # LOG(f"Match: {match}")
        if match:
            num = int(match.group(1))
            if num > maxnum:
                maxnum = num

    # account for the new test cases
    testnum = maxnum + 1

    ## FIXME: testnum is coming up broken!!
    LOG(f"Starting testnum at {testnum}")

    # write out the test cases
    for tc in rewrite.tests:

        # mint a new filename
        if (not tc.is_new()):
            print(f"Skipping existing test case {tc.filename}")
            assert os.path.exists(f"{tc.filename}")
            continue
        else:
            tc.filename = f"{rewrite.name}--{testnum}"
            testnum += 1

        LOG(f"Writing new test case for {tc.filename}")

        # fixup the error text to `{TESTDIR}/{tc.filename.in}:1[column:] `
        lineinfo = re.match(RE_FILE, tc.errtext)

        # fail if we didn't match
        assert lineinfo is not None

        # construct the new line info
        colinfo = ""
        if (lineinfo.group(3) is not None):
            colinfo = lineinfo.group(3)
        newlineinfo = f"{{TESTDIR}}/{tc.filename}.in:1:{colinfo} "

        # replace the line info in the error text      
        newerrtext = newlineinfo + tc.errtext[len(lineinfo.group(0)):]

        # write the test case, making sure not to overwrite anything
        LOG(f"Writing test case {tc.filename}")

        infilename = f"{testdir}/{tc.filename}.in"
        assert not os.path.exists(infilename)

        fl = open(infilename, "w")
        fl.write(tc.intext)
        fl.close()

        fl = open(f"{testdir}/{tc.filename}.out", "w")
        fl.write(tc.outtext)
        fl.close()

        fl = open(f"{testdir}/{tc.filename}.err", "w")
        fl.write(newerrtext)
        fl.close()

def parse_unit_tests(args: argparse.Namespace, fixups: Optional[Dict[str, List[Fixup]]]) -> None:
    LOG("Parsing all unit tests")

    # test case directory
    testdir = get_test_dir(args)

    # find all the test cases
    globstr = f"{testdir}/*.in"
    files = glob.glob(globstr)

    # number of tests without a home
    tests_no_rewrites: int = 0
    total_tests: int = 0

    # for each test case, read it in and re-evaluate
    for file in files:
        # extract the rewrite name from the filename
        match = re.match(f"{testdir}/(.*)--\\d+.in", file)
        if match is None:
            tests_no_rewrites += 1
            rewriter = None
        else:
            rewriter = match.group(1)
        VERBOSE(f"Reading test case: {file} (rewrite = {rewriter})")

        # read the actual files
        fl = open(file, "r")
        intext = fl.read()
        fl.close()

        # read the out file
        nooutfile = False
        outfname = file.replace(".in", ".out")
        if os.path.exists(outfname):
            fl = open(outfname, "r")
            outtext = fl.read()
            fl.close()
        else:
            outtext = ""
            nooutfile = True


        # read the err file
        fl = open(file.replace(".in", ".err"), "r")
        errtext = fl.read()
        fl.close()

        # format error text to test paths
        errtext = errtext.format(TESTDIR=testdir)

        # maybe add it to the fixup list
        fixup = add_fixup_for_error(fixups, file, errtext)

        # construct the test case for it
        tc = Testcase(file, intext, outtext, fixup, file, nooutfile=nooutfile)

        # add the test case to the rewrite
        if (rewriter is not None):
            for rewrite in ALL_REWRITES:
                if (rewrite.name != rewriter):
                    continue
                rewrite.tests.append(tc)

        total_tests += 1

    LOG(f"Read {total_tests} tests, {tests_no_rewrites} without rewrites")

###
##   reading compiler error logs 
#

def parse_errfile(args: argparse.Namespace, fixups: Dict[str, List[Fixup]]) -> None:

    LOG(f"Reading compiler error log {args.errfile}")
    fl = open(args.errfile, "r")
    lines = fl.readlines()

    matched: int = 0

    seen: List[str] = []

    for line in lines:
        # match line against RE
        match = re.match(RE_ERR, line)

        # continue if no match
        if match is None:
            continue

        # continue if we've seen it
        if line in seen:
            continue

        # add it to the seen list
        seen.append(line)

        VERBOSE(f"Matched line: {line.strip()}")
        matched += 1

        add_fixup_for_error(fixups, args.errfile, line)

    LOG(f"Matched {matched} lines")

###
##  parse_args
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
 
    # File full of errors
    parser.add_argument("--errfile", help="gcc error file to process")
 
    # Unit test mode
    parser.add_argument("-U", "--unit-test", action="store_true", default=False)

    # Just parse the error file and exit
    parser.add_argument("-J", "--just-parse", action="store_true", default=False)
 
    # Filter files to process
    parser.add_argument("--filter", action="store", default=None)

    # Filter files to process
    parser.add_argument("--line", action="append", default=[], type=int)

    # Generate test cases
    parser.add_argument("-G", "--generate-tests",
                        action="store_true", default=False)

    # Don't write anything
    parser.add_argument("-N", "--no-write",
                        action="store_true", default=False)

    # Number of test cases to generate up to
    parser.add_argument("-T", "--test-cases",
                        action="store", default=DEFAULT_TEST_CASES)

    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument("--sdkdir", action="store", default=find_sdkdir());

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

    args.unit_test_mode = False

    return args
 
###
##  main
#
def main() -> int:
    args: argparse.Namespace = parse_args()
 
    if not args.just_parse:
        headerglob = os.path.join(args.sdkdir, "FunSDK", "hci", "include", "FunHCI", "*.h")
        accessors: Dict[str, Accessor] = load_accessors(headerglob)

    # list of fixups to do
    fixups: Dict[str, List[Fixup]] = {}

    if args.unit_test:
        # load the unit tests and inject all the fixups
        args.unit_test_mode = True
        args.load_unit_tests = True
        parse_unit_tests(args, fixups)
    elif args.generate_tests:
        # just load the tests so we can save the delta
        args.load_unit_tests = True
        parse_unit_tests(args, None)

    # load the error file
    if args.errfile is not None:
        parse_errfile(args, fixups)

    # early out for quick parsing testing
    if args.just_parse:
        LOG("Early exit for matching errors only")
        return -1

    VERBOSE(f"Using {accessors.keys()} accessors")

    # Run all the fixups
    try:
        for filename, fixup_list in fixups.items():
            # filter
            if (args.filter is not None) and (not fnmatch.fnmatch(filename, args.filter)):
                VERBOSE(f"Skipping {filename} due to filter")
                continue

            # actual match
            fixup_file(args, accessors, filename, fixup_list)
    except KeyboardInterrupt:
        LOG(f"Keyboard interrupt while processing {filename}")

    # Dump the rewrite stats
    print()
    print("Dumping stats:")    
    for rewrite in ALL_REWRITES:
        snew = ""
        if (rewrite.newtestcases() > 0):
            snew = f", {rewrite.newtestcases()} new."
        LOG(f"Rewrite: {rewrite.name:15} used {rewrite.usedcount} times. {len(rewrite.tests)} test cases{snew}")

    # write out test cases
    if args.generate_tests:
        if (args.no_write):
            LOG("Not writing test cases due to --no-write")
        else:
            for rewrite in ALL_REWRITES:
                write_test_cases(args, rewrite)

    return 0
 
###
##  entrypoint
#
if __name__ == "__main__":
    main()
