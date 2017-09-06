#!/usr/bin/python

# external libs
import sys, pickle, json, os

# specific imports
from optparse import OptionParser

# internal libs

from ttypes import TEntry
from ttypes import TTree

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
def read_trace(trace_fname, ranges, filter_vp, reverse_order, filterlist, quiet):

	# to be refined based on understanding of pipeline
	cycles = 0
	idles = 0
	instr_misses = 0
	nxtprint = 0

	last_found_func = ["","","",""]
	last_address = [0,0,0,0]

	if quiet:
		print "Beginning trace in quiet mode"

	if filter_vp == 15 and quiet == False:
		print "%16s | %19s | %06s | %32s | %32s | %32s | %32s |" % ("Cycle", "addr", "OP", "VP0", "VP1", "VP2", "VP3")

	# reverse order support to be re-implemented at a later date

	current_ttree = [None, None, None, None]

	saved_sz = 10000000 # XXX TMP

	with open(trace_fname) as infile:
		for line in infile:
			if tutils.is_instruction(line): # XXX rename is_instruction

				entry = TEntry(line, 0, ranges)
	
				vp = entry.get_vpid()
				cycles = cycles + entry.get_ccount()

				# XXX rewrite idle handling
				func = entry.get_func()
				if func == "idle":
					idles = idles + entry.get_ccount()

				if func in filterlist:
					continue

				if 'IM' in line.split():
					instr_misses = instr_misses + 1

#				if tutils.out_of_range(func):
#					newaddr = filter_addr(entry.get_addr())
#					entry.set_addr(newaddr, ranges)
#
				if func != last_found_func[vp]:
	
					last_found_func[vp] = func

					row_val = [tutils.get_address(line), "-", "-", "-", "-"]
					row_val[vp+1] = func

					if quiet == False:
						if filter_vp == 15:
							print "%16s | %19s | %06s | %32s | %32s | %32s | %32s |" % (cycles, hex(row_val[0]), entry.get_op(), row_val[1], row_val[2], row_val[3], row_val[4])
						elif vp == filter_vp:
							print "ENTRY: %s" % (entry)
					else:
						if (cycles / 100000) == nxtprint:
							print "Quiet mode still running; %s cycles complete" % cycles
							nxtprint = nxtprint + 1

					if entry.get_pos() == "START":

						new_ttree = TTree(func, current_ttree[vp], cycles, idles, instr_misses)

						if current_ttree[vp] != None:
							current_ttree[vp].add_call(new_ttree)

						current_ttree[vp] = new_ttree

					else:

						need_new_node = True

						# 1. pop everything we can
						if current_ttree[vp] != None:

							top_of_stack = current_ttree[vp]

							while top_of_stack != None:

								# update end stats for all funcs that are being popped
								if top_of_stack.get_name() == func:
									need_new_node = False
									current_ttree[vp] = top_of_stack
									break

								top_of_stack.set_end_cycle(cycles)
								top_of_stack.set_end_idle(idles)
								top_of_stack.set_end_instr_miss(instr_misses)

								top_of_stack = top_of_stack.get_parent()

						# 2. If we popped all the way to no root, create a new root
						if need_new_node == True:

							new_ttree = TTree(func, None, cycles, idles, instr_misses)

							if current_ttree[vp] != None:
								# if we are adding a node, it is the root
								# => it is the parent of the current root
								ccyc = current_ttree[vp].get_start_cycle()
								cid = current_ttree[vp].get_start_idle()
								cim = current_ttree[vp].get_start_instr_miss()

								new_ttree.add_call(current_ttree[vp].get_root())
								new_ttree.start_cycle = current_ttree[vp].get_start_cycle()
								new_ttree.start_idle = current_ttree[vp].get_start_cycle()
								new_ttree.start_instr_miss = current_ttree[vp].get_start_instr_miss()

								#current_ttree[vp].propagate_start(ccyc, cid, cim)

							current_ttree[vp] = new_ttree
					

				last_address[vp] = entry.get_addr()

			elif tutils.is_data(line):
				pass


	infile.close()
	roots = []

	print "Run complete..."

	for i in range(0,4):
		if current_ttree[i] != None:
			try:
				current_ttree[i].propagate_up(cycles, idles, instr_misses)
				roots.append(current_ttree[i].get_root())
				sc = roots[i].sanitycheck()
				print "Sanity check for VP %s: %s" % (i, sc)
			except:
				print "Detected insanity in the sanity check. Continuing."
				continue
		else:
			roots.append(None)
			print "No run data available for VP %s" % i

	#roots[0].print_tree(0)

	print "Total cycles: %s" % cycles
	print "Time elapsed @ 1GHz: %s seconds (%s ms)" % (cycles/float(1000000000), (cycles/float(1000000)))
	print "Max call depth: TBD"
	print "Total idles: %s" % idles

	return roots


def print_funcs(ranges):

	flist = []

	query = 0xffffffff8010e2f8

	for item in ranges:
		flag = ""
		if query >= item[1] and query < item[2]:
			flag = "*"


		print "%s\t%s\t%s\t%s" % (flag, hex(item[1]), hex(item[2]), item[0])

		if item[0] in flist:
			print "%s already in list" % item[0]
		else:
			flist.append(item[0])


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
	parser.add_option("-c", "--core", dest="core_id", help="Core ID")
	parser.add_option("-d", "--data", dest="data_f", help="Data folder", metavar="FOLDER")	
	parser.add_option("-q", "--quiet", action='store_true', default=False, dest="quiet", help="No output during parsing")

	(options, args) = parser.parse_args()

	if options.asm_f is None:
		print "ASM file is mandatory. Use -h for more information"
		sys.exit(0)

	ranges = create_range_list(options.asm_f)
	filterlist = ["idle", "sync", "mode"] # XXX we shouldn't need this, it should be handled by is_instruction (to be renamed)

	core_id = 0

	if options.core_id != None:
		core_id = int(options.core_id)

	dst = ''
	if options.data_f != None:
		dst = os.path.abspath(options.data_f)
		if not os.path.exists(dst):
			print "Invalid folder for dst"
			sys.exit(1)

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

	data = read_trace(options.trc_f, ranges, int(options.vpid), options.reverse_order, filterlist, options.quiet)

	# XXX
	f = open(os.path.join(dst, 'fundata_c%s' % core_id), 'w')
	pickle.dump(data, f)
	f.close()
	# XXX

