# goal: Make this file aware of different file formats and have the tprs.py
# code stay stable

import re

from operator import itemgetter

# gotta load 'em all (well we don't, but this is easier)
import tutils_sim
import tutils_pdt
import tutils_qmu
import tutils_sbp

# default to nothing
tutils = None

# list of valid formats we support
FORMAT_DECODER = {"sim": tutils_sim,
                  "pdt": tutils_pdt,
                  "qemu": tutils_qmu,
          "sbp": tutils_sbp}
VALID_FORMATS = list(FORMAT_DECODER.keys())

# called by the trace parser when we know the user's intent
def set_format(fname):
        global tutils
        tutils = FORMAT_DECODER[fname]


LIVE_DEBUG = False


OUT_OF_RANGE = ".data ++"

def out_of_range(func):
    return func == OUT_OF_RANGE

def is_return(trace_line):
    return tutils.is_return(trace_line)

def is_data(trace_line):
    return tutils.is_data(trace_line)

def is_instruction(trace_line):
    return tutils.is_instruction(trace_line)

def is_instruction_miss(trace_line):
    return tutils.is_instruction_miss(trace_line)

def is_loadstore_miss(trace_line):
    return tutils.is_loadstore_miss(trace_line)

def get_vpid(trace_line):
    return tutils.get_vpid(trace_line)

def get_return_addr(trace_line):
    return tutils.get_return_addr(trace_line)

def get_address(trace_line):
    return tutils.get_address(trace_line)

def get_ccount(trace_line):
    return tutils.get_ccount(trace_line)

def get_asm(trace_line):
    return tutils.get_asm(trace_line)

def get_ts(trace_line):
    return tutils.get_ts(trace_line)

def get_cycle(trace_line):
    return tutils.get_cycle(trace_line)

def get_num_pipelines():
    return tutils.get_num_pipelines()

def text_section_start(dasm_line):
    # catches the case where we have .text_*
    return dasm_line.startswith("Disassembly of section .text")

def exception_vector_start(dasm_line):
    return dasm_line.startswith("Disassembly of section .exception_vector")

def data_section_start(dasm_line):
    return dasm_line == "Disassembly of section .data:"

#
#
#
REGEX = re.compile(r"([A-Fa-f0-9]+) <(.*)>\:")

def asm_isfunc(line):
    found = False
    addr = 0
    fname = ""

    m = REGEX.search(line)
    if m is not None:
        addr = int(m.group(1), 16)
        fname = m.group(2)
        found = True

    return [found, addr, fname]

def asm_get_fstart(line):

    [found, addr, fname] = asm_isfunc(line)

    if fname.startswith('$') or fname.startswith('.'):
        found = False

    return [found, addr, fname]

# Create an entry with [funcname, start addr, end addr]
def create_range_list(dasm_fname):
    print("creating range list")
    f = open(dasm_fname)

    linenum = 0

    fcurr = ""

    coll = []

    before_text = True
    out_of_range = False

    for line in f.readlines():
        line = line.strip()

        if (before_text):
            if text_section_start(line):
                before_text = False

            if exception_vector_start(line):
                before_text = False

            if (before_text):
                continue
                
        if (not out_of_range):
            if data_section_start(line):
                out_of_range = True

        [found, addr, fname] = asm_get_fstart(line)

        if found:

            if len(fcurr) != 0:
                coll[len(coll)-1].append(addr-2)

            fcurr = fname

            if out_of_range == True:
                coll.append([OUT_OF_RANGE, addr, 0xffffffffffffffff])
                break

            coll.append([fname, addr])

    if not out_of_range:
        coll[len(coll)-1].append(0xffffffffffffffff)

    f.close()
    print("done creating range list")
    return sorted(coll, key=itemgetter(1))

def find_function(addr, dasm_info):
    """ Returns the name of the function at the address.

    Returns None if no function is known at the given address.
    """
    # Boot code runs in two separate address ranges that represent
    # the same memory, one non-cached, one cached.  Convert non-cached
    # addresses to the equivalent cached address so lookups work.
    # TODO(bowdidge): Abstract away address space issues.
    if addr & 0x20000000:
        addr = addr & 0xffffffffdfffffff

    func_info = dasm_info.FindFunction(addr)
    if not func_info:
        return None

    return func_info.name
