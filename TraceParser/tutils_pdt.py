# goal: Make this file aware of different file formats and have the tprs.py
# code stay stable

def is_return(trace_line):
	assert(0)

def is_data(trace_line):
	# XXX
	return False

def is_instruction(trace_line):
	# TM format
	tpc_found = False
	va_found = False

	tokens = trace_line.split()
	for token in tokens:
		if 'tpc' in token.split('='):
			tpc_found = True
		if 'va[56]' in token.split('='):
			va_found = True

	return tpc_found and va_found


def get_vpid(trace_line):
	# XXX
	return 0

def get_return_addr(trace_line):
	assert(0)

def get_address(trace_line): 
	# TM format
	# tightly coupled to tt=ipc in TF3
	tokens = trace_line.split()
	for token in tokens:
		if 'va[56]' in token.split('='):
			return long(token.split('=')[1], 16)

	return 0

def get_asm(trace_line):
	# XXX
	return 0

def get_ts(trace_line):
	# XXX
	return 0

def get_cycle(trace_line):
	# XXX
	return 0


