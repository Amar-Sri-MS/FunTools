# goal: Make this file aware of different file formats and have the tprs.py
# code stay stable

def DEBUG(x):
    # print x
    pass

def is_return(trace_line):
    # FIXME
    raise RuntimeError("is_return NYI")

def is_data(trace_line):
    return False

def is_instruction(trace_line):
    is_inst = trace_line.startswith('Trace CPU')
    if (not is_inst):
        DEBUG("Not an instruction line")
    return is_inst

def is_instruction_miss(trace_line):
    return False

def is_loadstore_miss(trace_line):
    return False

def get_vpid(trace_line):
    vpid = int(trace_line.split()[2])
    DEBUG("Returning vpid: %s" % vpid)
    return vpid

def get_return_addr(trace_line):
    # FIXME
    raise RuntimeError("is_return NYI")

def get_address(trace_line):
    try:
        saddr = trace_line.split()[4]
        saddr = saddr[1:-1]
        naddr = int(saddr, 16)
        DEBUG("address: 0x%x ('%s')" % (naddr, saddr))
        return naddr
    except:
    # XXX
        DEBUG("Exception getting address '%s'" % saddr)
    return 0

def get_asm(trace_line):
    return None # nothing?

def get_ts(trace_line):
    cycle = trace_line.split()[-1]
    return int(cycle)    

def get_cycle(trace_line):
    cycle = trace_line.split()[-1]
    return int(cycle)    


# FIXME
def get_ccount(trace_line):
    return 1

def get_num_pipelines():
    return 1
