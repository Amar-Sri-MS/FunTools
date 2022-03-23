# goal: Make this file aware of different file formats and have the tprs.py
# code stay stable

import re

def is_return(trace_line):
    assert(0)

def is_data(trace_line):
    # XXX
    regex = r"^\d+\.\d\d\d  \d \d \d.*(\bld|\bst).*"

    rm = re.search(regex, trace_line.strip())

    return rm

def is_instruction(trace_line):
    # TM+DASM format
    noerr = True

    regex = r"^\d+\.\d\d\d  \d \d \d.*pc.*"

    rm = re.search(regex, trace_line.strip())

    # Sample error messages as of 6/2/17
    # We do not want to parse these...
    # 76.121  0 0 0                 **** Unresolved Branch: ******
    # 76.132  0 0 0                 **** Trace Message buffer limit reached*****
    if "****" in trace_line:
        noerr = False

    # XXX to be investigated
    if "no trace cycles" in trace_line:
        noerr = False

    return rm and noerr

def is_instruction_miss(trace_line):
    return 'IM' in trace_line.split()

def is_loadstore_miss(trace_line):
    return 'LSM' in trace_line.split()

def get_vpid(trace_line):
    return int(trace_line.split()[2])

def get_return_addr(trace_line):
    assert(0)

def get_address(trace_line): 
    # TM+DASM format
    addr = 0

    regex = "pc\s+(0x[A-Fa-f0-9]+)"

    if (re.search(regex, trace_line)):

        m = re.search(regex, trace_line)

        addr = long(m.group(1),16)

    return addr

def get_num_pipelines():
    return 2

#1.075  0 0 0                 idle cycles 3
#1.085  0 0 0                 S1 idle slot
def get_ccount(trace_line):

    ccount = 1
    regex = r"idle cycles (\d+)"

    if (re.search(regex, trace_line)):
        m = re.search(regex, trace_line)

        ccount = int(m.group(1))
        ccount = ccount*2 # both pipelines are stalled
    elif "Sync" in trace_line:
        ccount = 0
    elif "mode" in trace_line:
        ccount = 0

    return ccount

def get_asm(trace_line):
    # XXX
    return 0

def get_ts(trace_line):
    # XXX
    return 0

def get_cycle(trace_line):
    # XXX
    return 0

def get_num_pipelines():
    return 2

