
# internal libraries
import tutils_hdr as tutils

class TEntry():

	def __init__(self, trace_line, ttype, ranges):
		# TBD: use different parsers for initialization
		self.vpid = tutils.get_vpid(trace_line)
		self.addr = tutils.get_address(trace_line)
		self.cycle = tutils.get_cycle(trace_line)
		self.ts = tutils.get_ts(trace_line)
		self.asm = tutils.get_asm(trace_line)

		self.func = self.find_function(self.addr, ranges)

	def __str__(self):
		return "%16s %s: %s" % (self.ts, hex(self.addr), self.func)

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

	def get_cycle(self):
		return self.cycle

	def get_ts(self):
		return self.ts

	def get_op(self):
		return ""
