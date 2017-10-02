
# internal libraries
import tutils_hdr as tutils

class TEntry():

	def __init__(self, trace_line, ttype, ranges):
		# TBD: use different parsers for initialization
		self.vpid = tutils.get_vpid(trace_line)
		self.addr = tutils.get_address(trace_line)

		# XXX make generic
		#self.cycle = cycle
		#self.cycle = tutils.get_cycle(trace_line)

		self.ts = tutils.get_ts(trace_line)
		self.asm = tutils.get_asm(trace_line)

                is_start = False
		self.ccount = tutils.get_ccount(trace_line)
		if "idle" in trace_line:
			self.func = "idle"
		elif "Sync" in trace_line:
			self.func = "sync"
		elif "mode" in trace_line:
			self.func = "mode"
		else:
			(self.func, is_start) = tutils.find_function(self.addr, ranges)

		if self.func == "NOT FOUND":
			print "NOT FOUND: %s" % trace_line
                        
                if (is_start):
		        self.pos = "START"
                else:
                        self.pos = "---"

	def __str__(self):
		return "%24s: %2s cyc %24s (%s)" % (hex(self.addr),self.ccount,self.func,self.pos)

	def get_pos(self):
		return self.pos

	def get_ccount(self):
		return self.ccount

	def get_vpid(self):
		return self.vpid

	def get_func(self):
		return self.func

	def get_addr(self):
		return self.addr

	def set_addr(self, addr, ranges):
		self.addr = addr

		self.func = "(POTENTIAL) "
		self.func = self.func + tutils.find_function(self.addr, ranges)

	def get_cycle(self):
		return self.cycle

	def get_ts(self):
		return self.ts

	def get_op(self):
		return ""



# on START, create new sub-node
# current node = newly created node
# on exit, go back to parent
# if parent is None, create one?

class TTree():

	def __init__(self, name, parent, start_cycle, start_idle, start_instr_miss, start_loadstore_miss, start_line):

		self.name = name
		self.parent = parent
		self.calls = []

		self.start_cycle = start_cycle
		self.end_cycle = start_cycle

		self.start_idle = start_idle
		self.end_idle = start_idle

		self.start_instr_miss = start_instr_miss
		self.end_instr_miss = start_instr_miss

		self.start_loadstore_miss = start_loadstore_miss
		self.end_loadstore_miss = start_loadstore_miss

		self.start_line = start_line
		self.end_line = start_line

		#print "TTREE: init %s" % name

	def get_calls(self):
		return self.calls

	def add_call(self, ttree):
		self.calls.append(ttree)

		#print "TTREE: %s add %s" % (self.entry.get_func(), ttree.get_name())


	def get_start_cycle(self):
		return self.start_cycle

	def get_end_cycle(self):
		return self.end_cycle

	def get_start_idle(self):
		return self.start_idle

	def get_idle_count(self):
		return self.end_idle - self.start_idle

	def get_end_cycle(self):
		return self.end_idle

	def get_ccount(self):
		#assert(self.end_cycle - self.start_cycle > 0)
		#print "getting ccount: %s to %s" % (self.start_cycle, self.end_cycle)
		return self.end_cycle - self.start_cycle + 1

	def get_start_instr_miss(self):
		return self.start_instr_miss

	def get_end_instr_miss(self):
		return self.end_instr_miss

	def get_imcount(self):
		return self.end_instr_miss - self.start_instr_miss

	def get_name(self):
		return self.name

	def set_end_cycle(self, cycle):
		self.end_cycle = cycle

	def set_end_idle(self, idle):
		self.end_idle = idle

	def set_end_instr_miss(self, im):
		self.end_instr_miss = im

	def set_end_loadstore_miss(self, lsm):
		self.end_loadstore_miss = lsm

	def get_start_loadstore_miss(self):
		return self.start_loadstore_miss

	def get_end_loadstore_miss(self):
		return self.end_loadstore_miss

	def set_end_line(self, line_num):
		self.end_line = line_num

	def get_entry(self):
		return self.entry

	def get_parent(self):
		if (self.parent == self):
			return None # XXX?
		return self.parent

	def get_start_line(self):
		return self.start_line

	def get_end_line(self):
		return self.end_line

	def __html(self, filterlist, indent):
		filtertext = ""

		if self.name in filterlist:
			filtertext = "(filtered)"

		print "<tr>"
		print "  <a name=\"%s\"></a>" % self.start_cycle
		print "  <td class=\"cycleCol\">%s</td>" % self.start_cycle
		print "  <td class=\"functionCol\">%s+ %s %s</td>" % ("&nbsp;"*4*indent, self.name, filtertext)
		print "  <td>%s cycle, %s idle, %s instr miss</td>" % (self.get_ccount(), self.get_idle_count(), self.get_imcount())
		print "</tr>"

	def __html_start(self, filterlist, indent, excl_sub_calls):
		symbol = '-'
		style = "block"

		cycle_count = self.get_ccount()
		idle_count = self.get_idle_count()
		instr_miss_count = self.get_imcount()

		if (excl_sub_calls):
			for subcall in self.calls:
				cycle_count = cycle_count - subcall.get_ccount()
				idle_count = idle_count - subcall.get_idle_count()
				instr_miss_count = instr_miss_count - subcall.get_imcount()

		if self.name in filterlist:
			symbol = '+'
			style = "none"

		st =  "<div class=\"line\"><span class=\"timestamp\">%s</span> %s<span class=\"collapseButton\" onclick=\"Collapse(this);\">%s</span> %s (%s cycles, %s idle, %s instr misses)\n" % (self.start_cycle, "&nbsp;"*4*indent, symbol, self.name, cycle_count, idle_count, instr_miss_count)
		st = st +  "<div class=\"collapse\" style=\"display : %s;\">\n" % (style)

		#st = st + "<div class=\"line\">%s %s<a href=\"#\" onclick=\"Collapse(this);\">--</a> %s (%s cycles, %s idle, %s instr misses)" % (self.start_cycle, "&nbsp;"*4*indent, self.name, self.get_ccount(), self.get_idle_count(), self.get_imcount())
		return st

	def __html_end(self):
		return "</div></div>\n"

	def html_tree(self, filterlist, depth, exclude_filtered, exclude_sub_calls):

		if self.name in filterlist and exclude_filtered == True:
			return ""

		ht = self.__html_start(filterlist, depth, exclude_sub_calls)

		#if self.name not in filterlist:
		for subcall in self.calls:
			ht = ht + subcall.html_tree(filterlist, depth+1, exclude_filtered, exclude_sub_calls)

		ht = ht + self.__html_end()

		return ht

	def print_tree_annotated(self, depth, refobj):
		ann = ""

		if self is refobj:
			ann= "*"

		print "%s%s%s%s-> %s [%s cycle, %s idle, %s instr miss]" % (ann, '\t',' '*depth, depth, self.name, self.get_ccount(), self.get_idle_count(), self.get_imcount())

		for subcall in self.calls:
			subcall.print_tree_annotated(depth+1, refobj)

	def print_tree(self, depth):

		print "[%12s]\t%s%s-> %s [%s cycle, %s idle, %s instr miss]" % (self.get_start_cycle(), ' '*depth, depth, self.name, self.get_ccount(), self.get_idle_count(), self.get_imcount())

		for subcall in self.calls:
			subcall.print_tree(depth+1)

	def print_tree_ltd(self, startdepth, maxdepth):

		if maxdepth == 0:
			return

		print "%s%s-> %s [%s cycle, %s idle, %s instr miss]" % (' '*startdepth, startdepth, self.name, self.get_ccount(), self.get_idle_count(), self.get_imcount())

		for subcall in self.calls:
			subcall.print_tree_ltd(startdepth+1, maxdepth-1)

	def print_context(self):

		if self.parent == None:
			print "----Context----"
			self.print_tree(0)
		else:
			self.get_parent().print_context()


	def propagate_start(self, cycle, idle, im):

		self.start_cycle = cycle
		self.start_idle = idle
		self.start_instr_miss = im

		if self.get_parent() != None:
			self.get_parent().propagate_start(cycle, idle, im)

	def propagate_up(self, cycles, idles, instr_misses):

		self.set_end_cycle(cycles)
		self.set_end_idle(idles)
		self.set_end_instr_miss(instr_misses)

		if self.get_parent() != None:
			self.get_parent().propagate_up(cycles,idles,instr_misses)

	# XXX verify
	def sanitycheck(self):
		subcount = 0
		for el in self.calls:
			subcount = subcount + el.get_ccount()

		if self.get_ccount() < subcount:
			print "sanity check issue:"
			print "[%s] ccount %s subcount %s" % (self.name, self.get_ccount(), subcount)
			return False
		else:
			return True


	def get_root(self):
		if self.parent == None:
			return self
		else:
			return self.parent.get_root()

