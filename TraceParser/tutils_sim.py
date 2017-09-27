# goal: Make this file aware of different file formats and have the tprs.py
# code stay stable

def is_return(trace_line):
	return trace_line.split()[2] == "31"

def is_data(trace_line):
	return trace_line.startswith('G')

def is_instruction(trace_line):
	return trace_line.startswith('I')


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
