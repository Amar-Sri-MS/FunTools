
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

		self.ccount = tutils.get_ccount(trace_line)
		if "idle" in trace_line:
			self.func = "idle"
		elif "Sync" in trace_line:
			self.func = "sync"
		elif "mode" in trace_line:
			self.func = "mode"
		else:
			self.func = self.find_function(self.addr, ranges)

		self.pos = self.find_func_pos(self.addr, ranges)

	def __str__(self):
		return "%24s: %2s cyc %24s (%s)" % (hex(self.addr),self.ccount,self.func,self.pos)

	def find_function(self, addr, ranges):

		for item in ranges:
	
			start = item[1]
			end = item[2]
	
			try:
				if addr >= start and addr <= end:
					return item[0]
			except:
				return "INVALID"

		return "NOT FOUND"

	# XXX duplicate code
	def find_func_pos(self, addr, ranges):
		for item in ranges:
			if addr == item[1]:
				return "START"

		return "---"

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
		self.func = self.func + self.find_function(self.addr, ranges)

	def get_ts(self):
		return self.ts

	def get_op(self):
		return ""




# on START, create new sub-node
# current node = newly created node
# on exit, go back to parent
# if parent is None, create one?

class TTree():

	def __init__(self, name, parent, start_cycle, start_idle, start_instr_miss):

		self.name = name
		self.parent = parent
		self.calls = []

		self.start_cycle = start_cycle
		self.end_cycle = start_cycle

		self.start_idle = start_idle
		self.end_idle = start_idle

		self.start_instr_miss = start_instr_miss
		self.end_instr_miss = start_instr_miss

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
		assert(self.end_cycle - self.start_cycle > 0)
		return self.end_cycle - self.start_cycle

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

	def get_entry(self):
		return self.entry

	def get_parent(self):
		return self.parent

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

	def __html_start(self, filterlist, indent):
		symbol = '-'
		style = "block"
		if self.name in filterlist:
			symbol = '+'
			style = "none"

		st =  "<div class=\"line\"><span class=\"timestamp\">%s</span> %s<span class=\"collapseButton\" onclick=\"Collapse(this);\">%s</span> %s (%s cycles, %s idle, %s instr misses)\n" % (self.start_cycle, "&nbsp;"*4*indent, symbol, self.name, self.get_ccount(), self.get_idle_count(), self.get_imcount())
		st = st +  "<div class=\"collapse\" style=\"display : %s;\">\n" % (style)

		#st = st + "<div class=\"line\">%s %s<a href=\"#\" onclick=\"Collapse(this);\">--</a> %s (%s cycles, %s idle, %s instr misses)" % (self.start_cycle, "&nbsp;"*4*indent, self.name, self.get_ccount(), self.get_idle_count(), self.get_imcount())
		return st

	def __html_end(self):
		return "</div></div>\n"

	def html_tree(self, filterlist, depth):

		ht = self.__html_start(filterlist, depth)

		#if self.name not in filterlist:
		for subcall in self.calls:
			ht = ht + subcall.html_tree(filterlist, depth+1)

		ht = ht + self.__html_end()

		return ht


	def print_tree(self, depth):

		print "%s%s-> %s [%s cycle, %s idle, %s instr miss]" % (' '*depth, depth, self.name, self.get_ccount(), self.get_idle_count(), self.get_imcount())

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
			print "[%s] ccount %s subcount %s" % (self.name, self.ccount, subcount)
			return False
		else:
			return True


	def get_root(self):
		if self.parent == None:
			return self
		else:
			return self.parent.get_root()

