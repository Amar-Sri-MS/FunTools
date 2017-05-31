# goal: Make this file aware of different file formats and have the tprs.py
# code stay stable

import re, json, numpy
from datetime import date

trace_fmt = 'PDT'
if trace_fmt == 'SIM':
	import tutils_sim as tutils
elif trace_fmt == 'PDT':
	import tutils_pdt as tutils
else:
	print "unknown trace format"
	assert(0)


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
def output_html(data):

	newdict = {}

	oh = ""

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
		
		#print "found function %s" % funcname

		for el in data[funcname]:
			if el in cntdict["dist"].keys():
				cntdict["dist"][el] = cntdict["dist"][el] + 1
			else:
				cntdict["dist"][el] = 1

		newdict["functions"].append(cntdict)

	#f = open(fname, 'w')
	#f.write(json.dumps(newdict))
	#f.close()
	oh = oh +  """
<div class="json-div" id="functions">
  <div class="json-div-prototype">
    <h1><span class="json-span" id="name">function name here</span></h1>
    <!-- Histogram showing distribution of cycle counts for execution of the function. -->
    Runs were on the Palladium system.
    <div class="json-graph" id="dist">
      <div class="graph" graph-type='histogram'
            x-title="Cycle Count" y-title="Occurrences">
      </div>
    </div>
  </div>
</div>
<script> allData ="""
	oh = oh + json.dumps(newdict)
	oh = oh +  "</script>"

	return oh


def html_hdr():
	return """
<html>
<head>
<!-- Plot.ly JavaScript library.  Served from Robert's personal
     domain until we have our own local web server. -->
<script src="http://dochub.fungible.local/doc/Scripts/plotly-latest-min.js">
</script>
<!-- The FunTmpl code depends on JQuery, a commonly-used JavaScript library
     for manipulating web pages. -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js">
</script>
<!-- FunJSONTemplate - client side templating to fill in values. -->
<script src="http://dochub.fungible.local/doc/Scripts/funTmpl.js">
</script>
<title>Function calls</title>
<style>
/* Tone down the cycle number - it's less important than the function name */
.cycleCol {
  color: gray;
}
.collapseButton {
  color: red;
  text-decoration: underline;
  cursor: pointer;
}

/* Function column add space to the right so names are readable. */
.functionCol {
  padding-right: 50px;
}
/* Highlight surprising numbers . */
.scary {
  color: red;
}

.graph {
  border: 1px solid black;
  width: 400px;
  height: 300px;
}

.timestamp {
  float: left;
  width: 150px;
  padding-right: 10px;
  text-align: right;
}

#butterBar {
  position: absolute;
  display: hidden;
  width: 60%%;
  height: 5%%;
  left: 20%%;
  background-color: gold;
  text-align: center;
}

</style>
<script>
function Collapse(sender) {
  var collapseDivs = sender.parentNode.getElementsByClassName("collapse");
  if (collapseDivs.length == 0) {
    return;
  }
  var first = collapseDivs[0];
  if (first.style.display == "none") {
    first.style.display = "block";
    sender.innerHTML = "-";
  } else {
    first.style.display = "none";
    sender.innerHTML = "+";
  }
}
</script>
</head>
<body onload="Reload();">
<div id="butterBar">Loading stuff</div>
<h1>Run: %s</h1>
(some overview stats)
<br>
<br>
""" % str(date.today())

def html_end():
	return """<br>
</body>
</html>
"""



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
		#if fname.startswith('$') or fname.startswith('.') or '.' in fname:
		if fname.startswith('.'):
			found = False
		else:
			found = True


	return [found, addr, fname]
