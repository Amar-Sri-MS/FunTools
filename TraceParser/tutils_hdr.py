# goal: Make this file aware of different file formats and have the tprs.py
# code stay stable

import re

trace_fmt = 'PDT'
if trace_fmt == 'SIM':
	import tutils_sim as tutils
elif trace_fmt == 'PDT':
	import tutils_pdt as tutils
else:
	print "unknown trace format"
	assert(0)

OUT_OF_RANGE = ".data ++"

def out_of_range(func):
	return func == OUT_OF_RANGE

def is_return(trace_line):
	return tutils.is_return(trace_line)

def is_data(trace_line):
	return tutils.is_data(trace_line)

def is_instruction(trace_line):
	return tutils.is_instruction(trace_line)

def get_vpid(trace_line):
	return tutils.get_vpid(trace_line)

def get_return_addr(trace_line):
	return tutils.get_return_addr(trace_line)

def get_address(trace_line):
	return tutils.get_address(trace_line)

def get_asm(trace_line):
	return tutils.get_asm(trace_line)

def get_ts(trace_line):
	return tutils.get_ts(trace_line)

def get_cycle(trace_line):
	return tutils.get_cycle(trace_line)

def data_section_start(dasm_line):
	return dasm_line.strip() == "Disassembly of section .data:"

#
#
#
def parse_item(line):
	found = False
	addr = 0
	fname = ""

	regex = r"([A-Fa-f0-9]+) <(.*)>\:"

	if (re.search(regex, line)):

		m = re.search(regex, line)

		addr = long(m.group(1), 16)
		fname = m.group(2)
		
		# ignore blocks
		if fname.startswith('$') or fname.startswith('.') or '.' in fname:
			found = False
		else:
			found = True


	return [found, addr, fname]
