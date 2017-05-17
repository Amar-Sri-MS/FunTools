# goal: Make this file aware of different file formats and have the tprs.py
# code stay stable

import re

def is_return(trace_line):
	assert(0)

def is_data(trace_line):
	# XXX
	return False

def is_instruction(trace_line):
	# TM+DASM format

	regex = r"^\d+\.\d\d\d.*"

	return re.search(regex, trace_line.strip())


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

#1.075  0 0 0                 idle cycles 3
#1.085  0 0 0                 S1 idle slot
def get_ccount(trace_line):

	ccount = 1
	regex = r"idle cycles (\d+)"

	if (re.search(regex, trace_line)):
		m = re.search(regex, trace_line)

		ccount = int(m.group(1))
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


