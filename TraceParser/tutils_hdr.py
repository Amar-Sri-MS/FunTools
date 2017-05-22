# goal: Make this file aware of different file formats and have the tprs.py
# code stay stable

import re, json, numpy

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

def get_ccount(trace_line):
	return tutils.get_ccount(trace_line)

def get_asm(trace_line):
	return tutils.get_asm(trace_line)

def get_ts(trace_line):
	return tutils.get_ts(trace_line)

def get_cycle(trace_line):
	return tutils.get_cycle(trace_line)

def data_section_start(dasm_line):
	return dasm_line.strip() == "Disassembly of section .data:"


# in:
# { func1: [1, 2, 6, 2, 3, 12, 123, 1, 8]
#   func2: [1, 1, 1, 1]
# }
# out:
# { functions: [
#	{name: func1, dist: {1: 2, 2:1, ...} // dist is cycle count and number of occurrences
#	XXX TBD: average, max, min, isspecial
#
def output_html(dataset, fname):
	newdict = {}

	data = dataset[0]

	newdict["name"] = "Michael"
	newdict["setup"] = {"runs": 5}
	newdict["functions"] = []

	for funcname in data.keys():
		cntdict = {"name":funcname}
		cntdict["dist"] = {}
		cntdict["avg"] = sum(data[funcname])/len(data[funcname])
		cntdict["min"] = min(data[funcname])
		cntdict["max"] = max(data[funcname])
		cntdict["std"] = numpy.std(data[funcname])

		for el in data[funcname]:
			if el in cntdict["dist"].keys():
				cntdict["dist"][el] = cntdict["dist"][el] + 1
			else:
				cntdict["dist"][el] = 1

		newdict["functions"].append(cntdict)

	f = open(fname, 'w')
	f.write(json.dumps(newdict))
	f.close()
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
