# goal: Make this file aware of different file formats and have the tprs.py
# code stay stable

def ParseLine(trace_line):
    """Returns dictionary with values from Palladium trace line.

    This routine splits the line once, removing much duplicate work.
    """
    if trace_line[0] not in ['I', 'G']:
        return None
    args = trace_line.split()
    return {'type': args[0],
        'vpid': long(args[1]),
        'address': long(args[2], 16),
        'arg': long(args[3], 16),
        'cycle': int(args[5][6:]),
        'time': int(args[6][5:])}

def is_return(trace_line):
    return trace_line.split()[2] == "31"

def is_data(trace_line):
    return trace_line.startswith('G')

def is_instruction(trace_line):
    return trace_line.startswith('I')

def is_instruction_miss(trace_line):
    return False

def is_loadstore_miss(trace_line):
    return False

def get_vpid(trace_line):
    return int(trace_line.split()[1])

def get_return_addr(trace_line):
    return trace_line.split()[3]

def get_address(trace_line):
    try:
        return long(trace_line.split()[2], 16)
    except:
        # XXX
        return 0

def get_asm(trace_line):
    try:
        return int(trace_line.split()[3], 16)
    except:
        # XXX
        return 0

def get_ts(trace_line):
    time_txt = trace_line.split()[6]
    timev = time_txt.split('=')[1]
    return long(timev)    

def get_cycle(trace_line):
    cycle_txt = trace_line.split()[5]
    cycle = cycle_txt.split('=')[1]
    return long(cycle)    


# FIXME
def get_ccount(trace_line):
    return 1

def get_num_pipelines():
    return 1
