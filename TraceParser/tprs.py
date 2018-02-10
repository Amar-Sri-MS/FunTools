#!/usr/bin/python

# external libs
import sys, pickle, json, os, time

# specific imports
from optparse import OptionParser

# internal libs

import ttypes
from ttypes import TEntry
from ttypes import TTree

import tutils_hdr as tutils
#
# 

def make_stat():
	"""Create an empty stat dictionary for a single function.
	We initialize all possible values so we know that the resulting JSON
	will always have some value for each key.
	"""
	return {'calls': 0,
		# Total cycles for function and callers.
		'cycles': 0 ,
		# Total idle time for tree.
		'tree_idle': 0,
		'instr_miss': 0,
		'loadstore_miss': 0,
		'cycle_values': [],
		'cycles_average': 0,
		'cycles_max': 0,
		'cycles_min': 0,
		'cycles_std_dev': 0 }

def gather_stats_in_tree(root, stats):
	"""Update stats for every function in the tree.
	root is the root of the call tree to process.
	stats is the dictionary mapping function names to stats that receives the
	statistics.
	"""
	worklist = [root]
	while worklist:
		next = worklist.pop()
		if next.name not in stats:
			stats[next.name] = make_stat()

		call_cycles = next.end_cycle - next.start_cycle
		stats[next.name]['calls'] += 1
		stats[next.name]['cycles'] += call_cycles
		stats[next.name]['cycle_values'].append(call_cycles)
		stats[next.name]['tree_idle'] += (next.end_idle - next.start_idle)
		stats[next.name]['instr_miss'] += (next.end_instr_miss -
							next.start_instr_miss)
		stats[next.name]['loadstore_miss'] += (
			next.end_loadstore_miss - next.start_loadstore_miss)

		if next.calls:
			worklist += next.calls

def generate_function_stats_dict(roots):
	"""Returns dictionary summarizing behavior of each function.

	The result is a map of function names to dictionary of stat values for
	that function.
	"""
	stats = {}
	for root in roots:
		gather_stats_in_tree(root, stats)
		for fn_name in stats:
			cycles_min = min(stats[fn_name]['cycle_values'])
			cycles_max = max(stats[fn_name]['cycle_values'])
			stats[fn_name]['cycles_min'] = cycles_min
			stats[fn_name]['cycles_max'] = cycles_max
			average = (sum(stats[fn_name]['cycle_values']) /
				   stats[fn_name]['calls'])
			stats[fn_name]['cycles_average'] = average
	return stats

def output_trace_as_json(output_stream, roots, stats):
	"""Outputs trace information as JSON.
	output_stream is the stream to write the output.
	root is an array of the roots of the call trees.
	stats is a map of function names to stats for the function.
	"""
	first = True
	root_ids_str = ','.join([str(root.id) for root in roots])
	out_stream.write('{"roots": [%s],\n' % root_ids_str)
	out_stream.write(' "call_trees": [')
	for root in roots:
		if not first:
			out_stream.write(',\n')
		first = False
		ttypes.write_nodes_as_json(root, out_stream)
	out_stream.write('],\n')
	out_stream.write('"function_stats": %s\n' % json.dumps(stats))
	out_stream.write('}\n')

# input and output are numbers, not strings
def filter_addr(addr):
	return (addr & 0xffffffffdfffffff)


def read_a_line(infile, follow):

	# easy case
	if (not follow):
		return infile.readline()

	# follow case
	do_pause = False
	line = ""
	while (True):

		if (do_pause):
			time.sleep(1)

		part_line = infile.readline()

		do_pause = True

		# if we read nothing
		if (part_line == ""):
			continue

		line += part_line

		# if we read a newline, we're good
		if (line[-1] == "\n"):
			return line
			
		# go back and try for more

#
#
#
def read_trace(trace_fname, ranges, filter_vp, reverse_order, filterlist, quiet, follow):

	# to be refined based on understanding of pipeline
	cycles = 0
	real_cycles = 0
	idles = 0
	real_idles = 0
	instr_misses = 0
	loadstore_misses = 0
	nxtprint = 0
	line_num = 0

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
		while (True):

			line = read_a_line(infile, follow)
			if not line:
				break

			line_num = line_num + 1
      
			# handle the actual line, now we have one

			if tutils.is_instruction(line): # XXX rename is_instruction

				entry = TEntry(line, 0, ranges)
	
				vp = entry.get_vpid()
				cycles = cycles + entry.get_ccount()
				real_cycles = cycles/tutils.get_num_pipelines()

				#print "%s: cycles %s real_cycles %s\t\t%s" % (line_num, cycles, real_cycles, line)

				# XXX rewrite idle handling
				func = entry.get_func()
				if func == "idle":
					idles = idles + entry.get_ccount()
					real_idles = idles/tutils.get_num_pipelines()

				if func in filterlist:
					continue

				if tutils.is_instruction_miss(line):
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
							print "%16s | %19s | %06s | %32s | %32s | %32s | %32s |" % (real_cycles, hex(row_val[0]), entry.get_op(), row_val[1], row_val[2], row_val[3], row_val[4])
						elif vp == filter_vp:
							print "ENTRY: %s" % (entry)
					else:
						if (real_cycles / 100000) == nxtprint:
							print "Quiet mode still running; %s cycles complete" % real_cycles
							nxtprint = nxtprint + 1

					if entry.get_pos() == "START":

						new_ttree = TTree(func, current_ttree[vp], real_cycles, real_idles, instr_misses, loadstore_misses, line_num)

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

								top_of_stack.set_end_cycle(real_cycles)
								top_of_stack.set_end_idle(real_idles)
								top_of_stack.set_end_instr_miss(instr_misses)
								top_of_stack.set_end_loadstore_miss(loadstore_misses)
								top_of_stack.set_end_line(line_num)

								top_of_stack = top_of_stack.get_parent()

						# 2. If we popped all the way to no root, create a new root
						if need_new_node == True:

							new_ttree = TTree(func, None, real_cycles, real_idles, instr_misses, loadstore_misses, line_num)

							if current_ttree[vp] != None:
								# if we are adding a node, it is the root
								# => it is the parent of the current root

								#ccyc = current_ttree[vp].get_start_cycle()
								#cid = current_ttree[vp].get_start_idle()
								#cim = current_ttree[vp].get_start_instr_miss()

								new_ttree.add_call(current_ttree[vp].get_root())
								new_ttree.start_cycle = current_ttree[vp].get_start_cycle()
								new_ttree.start_idle = current_ttree[vp].get_start_cycle()
								new_ttree.start_instr_miss = current_ttree[vp].get_start_instr_miss()
								new_ttree.start_loadstore_miss = current_ttree[vp].get_start_loadstore_miss()
								new_ttree.start_line = current_ttree[vp].get_start_line()

								#current_ttree[vp].propagate_start(ccyc, cid, cim)

							current_ttree[vp] = new_ttree
					

				last_address[vp] = entry.get_addr()

			elif tutils.is_data(line):
				if tutils.is_loadstore_miss(line):
					loadstore_misses = loadstore_misses + 1

			


	infile.close()
	roots = []

	print "Run complete..."

	for i in range(0,4):
		if current_ttree[i] != None:
			try:
				current_ttree[i].propagate_up(real_cycles, real_idles, instr_misses)
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

	print "Total cycles: %s" % real_cycles
	print "Time elapsed @ 1GHz: %s seconds (%s ms)" % (real_cycles/float(1000000000), (real_cycles/float(1000000)))
	print "Max call depth: TBD"
	print "Total idles: %s" % real_idles
	print "Total load/store misses: %s" % loadstore_misses

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
	sys.setrecursionlimit(0x1000000)
	parser = OptionParser()

	parser.add_option("-a", "--asm", dest="asm_f", help="asm file", metavar="FILE")
	parser.add_option("-t", "--trace", dest="trc_f", help="trace file", metavar="FILE")
	parser.add_option("-v", "--vpid", dest="vpid", help="VP to show (omit to show all)", default=15)
	parser.add_option("-r", "--reverse", dest="reverse_order", help="order last instruction first", action="store_true")
	parser.add_option("-f", "--filter", dest="filter_f", help="filter file", metavar="FILE")
	parser.add_option("-c", "--core", dest="core_id", help="Core ID")
	parser.add_option("-d", "--data", dest="data_f", help="Data folder", metavar="FOLDER")
        parser.add_option("-F", "--format", dest="format", help="Trace file format %s" % tutils.VALID_FORMATS, metavar="FORMAT", default=None)
        parser.add_option("-w", "--follow", dest="follow", help="Keep polling trace file for new data to process", default=False, action="store_true")
	parser.add_option("-q", "--quiet", action='store_true', default=False, dest="quiet", help="No output during parsing")

	(options, args) = parser.parse_args()

	if options.asm_f is None:
		print "ASM file is mandatory. Use -h for more information"
		sys.exit(1)

        if options.format not in tutils.VALID_FORMATS:
		print "Format must be one of %s" % tutils.VALID_FORMATS
		sys.exit(1)

        # set the format
        tutils.set_format(options.format)

	ranges = tutils.create_range_list(options.asm_f)
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

	roots = read_trace(options.trc_f, ranges, int(options.vpid),
			   options.reverse_order, filterlist,
			   options.quiet, options.follow)
	next_id = 1

	for root in roots:
		next_id = ttypes.number_nodes(root, next_id)

	function_stats = generate_function_stats_dict(roots)

	# Output the data in JSON format for consumption by the web pages.
	out_path = os.path.join(dst, 'fundata_c%s.json' % core_id)
	out_stream = open(out_path, 'w')
	output_trace_as_json(out_stream, roots, function_stats)
	out_stream.close()
	
	# Output the original pickle data for processing by tdec.
	# TODO(bowdidge): Eventually use JSON as interchage - it's easier to
	# test and mock up for testing.
	f = open(os.path.join(dst, 'fundata_c%s' % core_id), 'w')
	pickle.dump(roots, f)
	f.close()
	# XXX
 
