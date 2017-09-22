# goal: Make this file aware of different file formats and have the tprs.py
# code stay stable

import re

# gotta load 'em all (well we don't, but this is easier)
import tutils_sim
import tutils_pdt
import tutils_qmu

# default to nothing
tutils = None

# list of valid formats we support
FORMAT_DECODER = {"sim": tutils_sim,
                  "pdt": tutils_pdt,
                  "qemu": tutils_qmu }
VALID_FORMATS = FORMAT_DECODER.keys()

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

def text_section_start(dasm_line):
	return dasm_line == "Disassembly of section .text:"

def data_section_start(dasm_line):
	return dasm_line == "Disassembly of section .data:"

#
#
#
REGEX = re.compile(r"([A-Fa-f0-9]+) <(.*)>\:")

def parse_item(line):
	found = False
	addr = 0
	fname = ""

	m = REGEX.search(line)
	if m is not None:

		addr = long(m.group(1), 16)
		fname = m.group(2)
		
		# ignore blocks
		#if fname.startswith('$') or fname.startswith('.') or '.' in fname:
		if fname.startswith('$') or fname.startswith('.'):
			found = False
		else:
			found = True


	return [found, addr, fname]
