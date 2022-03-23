
def is_return(trace_line):
    assert(0)

def is_data(trace_line):
    return False

def is_instruction(trace_line):
    return True

def is_instruction_miss(trace_line):
    return False

def is_loadstore_miss(trace_line):
    return False

def get_vpid(trace_line):
    return 0

def get_return_addr(trace_line):
    assert(0)

def get_address(trace_line):
    try:
        v = trace_line.split()[1].split('=')[1]
        v = '0x' + v
        return int(v, 16) | 0x80000000
    except:
        # XXX
        return 0

def get_asm(trace_line):
    return 0

def get_ts(trace_line):
    return 0

def get_cycle(trace_line):
    try:
        v = trace_line.split()[3].split('=')[1]
        v = '0x' + v
        return int(v, 16)
    except:
        # XXX
        return 0


# FIXME
def get_ccount(trace_line):
    return 1

def get_num_pipelines():
    return 1
