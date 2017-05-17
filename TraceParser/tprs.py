#!/usr/bin/python

# external libs
import sys, pickle, json

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
def read_trace(trace_fname, ranges, filter_vp, reverse_order, filterlist):

	# to be refined based on understanding of pipeline
	cycles = [0,0,0,0]
	idles = 0
	instr_misses = 0

	last_found_func = ["","","",""]
	last_address = [0,0,0,0]

	if filter_vp == 15:
		print "%16s | %19s | %06s | %32s | %32s | %32s | %32s |" % ("Cycle", "addr", "OP", "VP0", "VP1", "VP2", "VP3")

	# reverse order support to be re-implemented at a later date

	callstack = [[],[],[],[]]
	funcstats = [{},{},{},{}]

	current_ttree = [None, None, None, None]

	with open(trace_fname) as infile:
		for line in infile:
			if tutils.is_instruction(line): # XXX rename is_instruction


				entry = TEntry(line, 0, ranges)
	
				vp = entry.get_vpid()
				cycles[vp] = cycles[vp] + entry.get_ccount()

				# XXX !! make sure we're not double counting idles
				if entry.get_func() == "idle":
					idles = idles + entry.get_ccount()

				if entry.get_func() in filterlist:
					continue

				if 'IM' in line.split():
					instr_misses = instr_misses + 1

#				if tutils.out_of_range(entry.get_func()):
#					newaddr = filter_addr(entry.get_addr())
#					entry.set_addr(newaddr, ranges)
#
				if entry.get_func() != last_found_func[vp]:
	
					last_found_func[vp] = entry.get_func()

					row_val = [tutils.get_address(line), "-", "-", "-", "-"]
					row_val[vp+1] = entry.get_func()

					if filter_vp == 15:
						print "%16s | %19s | %06s | %32s | %32s | %32s | %32s |" % (cycles[vp], hex(row_val[0]), entry.get_op(), row_val[1], row_val[2], row_val[3], row_val[4])
					elif vp == filter_vp:
						print "%s" % (entry)

					if entry.get_pos() == "START":
						callstack[vp].append(entry)

						new_ttree = TTree(entry.get_func(), current_ttree[vp], cycles[vp], idles, instr_misses)

						if current_ttree[vp] != None:
							current_ttree[vp].add_call(new_ttree)

						current_ttree[vp] = new_ttree

					else:
						# gather stats on the function as it exits

						if len(callstack[vp]) != 0:
							top_of_stack = callstack[vp][-1]

							while top_of_stack.get_func() != entry.get_func():

								# everything that pops gets a stat
								current_ttree[vp].set_end_cycle(cycles[vp])
								current_ttree[vp].set_end_idle(idles)
								current_ttree[vp].set_end_instr_miss(instr_misses)

								# XXX should top of stack & current tree have same name?

								if top_of_stack.get_func() in funcstats[vp].keys():
									funcstats[vp][top_of_stack.get_func()].append(current_ttree[vp].get_ccount())
								else:
									funcstats[vp][top_of_stack.get_func()] = [current_ttree[vp].get_ccount()]

								callstack[vp].pop()
								parent_ttree = current_ttree[vp].get_parent()

								# we might have started in the middle of a tree, add nodes on the way up
								if parent_ttree is None:
									new_ttree = TTree(entry.get_func(), None, current_ttree[vp].get_start_cycle(), current_ttree[vp].get_start_idle(), current_ttree[vp].get_start_instr_miss())
									new_ttree.add_call(current_ttree[vp])
									current_ttree[vp] = new_ttree
								else:
									current_ttree[vp] = current_ttree[vp].get_parent()

								if len(callstack[vp]) == 0:
									break

								top_of_stack = callstack[vp][-1]


				last_address[vp] = entry.get_addr()

			elif tutils.is_data(line):
				pass


	roots = []

	for i in range(0,4):
		if current_ttree[i] != None:
			current_ttree[i].propagate_up(cycles[i], idles, instr_misses)
			roots.append(current_ttree[i].get_root())
			sc = roots[i].sanitycheck()
			print "Sanity check for VP %s: %s" % (i, sc)
		else:
			print "No tree available for VP %s" % i

	print_stats(funcstats[0])

	statf = open('stats.json', 'w')
	statf.write(json.dumps(funcstats[0]))
	statf.close()

	tutils.output_html(funcstats[0], 'stats2.json')

	print "Total cycles: %s" % cycles[0]
	print "Time elapsed @ 1GHz: %s seconds (%s ms)" % (cycles[0]/float(1000000000), (cycles[0]/float(1000000)))
	print "Max call depth: TBD"
	print "Total idles: %s" % idles

	# XXX
	f = open('fundata', 'w')
	pickle.dump(roots, f)
	f.close()
	# XXX

	return []

def print_funcs(ranges):

	for item in ranges:
		print "%s\t%s\t%s" % (hex(item[1]), hex(item[2]), item[0])

def print_stats(funcstats):

	for k in funcstats.keys():
		lst = funcstats[k]
		print "[%24s] # : %s | avg %s | min %s | max %s" % (k, len(lst), sum(lst)/float(len(lst)), min(lst), max(lst))
		print "="*80


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
	filterlist = ["idle", "sync", "mode"] # XXX we shouldn't need this, it should be handled by is_instruction (to be renamed)

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


