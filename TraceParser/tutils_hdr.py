# goal: Make this file aware of different file formats and have the tprs.py
# code stay stable

import re

from operator import itemgetter

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
		addr = long(m.group(1), 16)
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

                        if (before_text):
                                continue

                if (not out_of_range):
		        if data_section_start(line):
			        out_of_range = True

		[found, addr, fname] = asm_get_fstart(line)

		if found:

			if len(fcurr) != 0:
				coll[len(coll)-1].append(addr-4)

			fcurr = fname

			if out_of_range == True:
				coll.append([OUT_OF_RANGE, addr, 0xffffffffffffffff])
				break

			coll.append([fname, addr])

	if not out_of_range:
		coll[len(coll)-1].append(0xffffffffffffffff)

	f.close()

	return sorted(coll, key=itemgetter(1))

def find_function(addr, ranges):

	l = 0
	r = len(ranges)

	# binary search it
	while l < r:
		m = (l + r) / 2
		start = ranges[m][1]
		end = ranges[m][2]

		if addr < start:
			r = m
		elif addr > end:
			l = m + 1
		else:
			# found it
			return (ranges[m][0], addr == start)

	return ("NOT FOUND", False)
