#!/usr/bin/python

# external libs
import sys

# specific imports
from optparse import OptionParser

# internal libs

from ttypes import TEntry


import tutils_hdr as tutils
#
# 
# Create an entry with [funcname, start addr, end addr]
def create_range_list(dasm_fname):

	f = open(dasm_fname)

	linenum = 0

	fcurr = ""

	coll = []

	out_of_range = False

	for line in f.readlines():

		if tutils.data_section_start(line):
			out_of_range = True

		[found, addr, fname] = tutils.parse_item(line)

		if found:

			if len(fcurr) != 0:
				coll[len(coll)-1].append(addr-4)

			fcurr = fname

			if out_of_range == True:
				coll.append([tutils.OUT_OF_RANGE, addr, 0xffffffffffffffff])
				break

			coll.append([fname, addr])

	if not out_of_range:
		coll[len(coll)-1].append(0xffffffffffffffff)

	f.close()

	return coll


# input and output are numbers, not strings
def filter_addr(addr):
	return (addr & 0xffffffffdfffffff)

#
#
#
def read_trace(trace_fname, ranges, vp, reverse_order, filterlist):

	last_found_func = ["","","",""]

	if vp == 15:
		print "%16s | %19s | %06s | %32s | %32s | %32s | %32s |" % ("Cycle", "addr", "OP", "VP0", "VP1", "VP2", "VP3")

	# reverse order support to be re-implemented at a later date

	with open(trace_fname) as infile:
		for line in infile:
			if tutils.is_instruction(line):
				entry = TEntry(line, 0, ranges)
	
				if entry.get_func() in filterlist:
					continue
	
				if entry.get_func() == "NOT FOUND":
					print "NF: %s" % line

				if tutils.out_of_range(entry.get_func()):
					newaddr = filter_addr(entry.get_addr())
					entry.set_addr(newaddr, ranges)

				if entry.get_func() != last_found_func[entry.get_vpid()]:
	
					last_found_func[entry.get_vpid()] = entry.get_func()
	
					row_val = [tutils.get_address(line), "-", "-", "-", "-"]
					row_val[entry.get_vpid()+1] = entry.get_func()				

					if vp == 15:
						print "%16s | %19s | %06s | %32s | %32s | %32s | %32s |" % (entry.get_cycle(), hex(row_val[0]), entry.get_op(), row_val[1], row_val[2], row_val[3], row_val[4])
					elif entry.get_vpid() == vp:
						print "%s" % (entry)

				last_entry = entry

			elif tutils.is_data(line):
				pass

	return []

def print_funcs(ranges):

	for item in ranges:
		print "%s\t%s\t%s" % (hex(item[1]), hex(item[2]), item[0])

#
#
#
if __name__ == "__main__":

	parser = OptionParser()

	parser.add_option("-a", "--asm", dest="asm_f", help="asm file", metavar="FILE")
	parser.add_option("-t", "--trace", dest="trc_f", help="trace file", metavar="FILE")
	parser.add_option("-v", "--vpid", dest="vpid", help="VP to show (omit to show all)", default=15)
	parser.add_option("-r", "--reverse", dest="reverse_order", help="order last instruction first", action="store_true")
	parser.add_option("-f", "--filter", dest="filter_f", help="filter file", metavar="FILE")

	(options, args) = parser.parse_args()

	if options.asm_f is None:
		print "ASM file is mandatory. Use -h for more information"
		sys.exit(0)

	ranges = create_range_list(options.asm_f)
	filterlist = []

	if options.trc_f is None:
		print_funcs(ranges)
		sys.exit(0)

	if options.filter_f:
		f = open(options.filter_f)
		for line in f.readlines():
			filterlist.append(line.strip())
		f.close()

		print "Filter list: %s" % filterlist

	if options.reverse_order:
		print "Reverse order not currently supported, my apologies."
		sys.exit(0)

	table = read_trace(options.trc_f, ranges, int(options.vpid), options.reverse_order, filterlist)


