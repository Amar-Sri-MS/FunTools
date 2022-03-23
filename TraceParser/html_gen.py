
from datetime import date
import json
import math

def standard_deviation(values):
       """Returns the standard deviation for a set of values.

       values is assumed to be floating point or integer.
       """
       # TODO(bowdidge): Implemented because numpy isn't installed on some
       # versions of Python on the lab machines.
       count = 0
       sum = 0.0
       sum_squares = 0.0
       for val in values:
              count += 1
              sum += val
              sum_squares += val * val

       if count < 2:
              return 0.0

       variance = (sum_squares - ((sum * sum) / count)) / (count - 1)
       return math.sqrt(variance)

# in:
# { func1: [1, 2, 6, 2, 3, 12, 123, 1, 8]
#   func2: [1, 1, 1, 1]
# }
# out:
# { functions: [
#    {name: func1, dist: {1: 2, 2:1, ...} // dist is cycle count and number of occurrences
#    XXX TBD: average, max, min, isspecial
#
def vpstats_output_html(data):

    newdict = {}

    oh = ""

    newdict["name"] = "Michael"
    newdict["setup"] = {"runs": 5}
    newdict["functions"] = []

    for funcname in list(data.keys()):
        cntdict = {"name":funcname}
        cntdict["dist"] = {}
        cntdict["avg"] = sum(data[funcname])/len(data[funcname])
        cntdict["min"] = min(data[funcname])
        cntdict["max"] = max(data[funcname])
        cntdict["std"] = standard_deviation(data[funcname])
        
        for el in data[funcname]:
            if el in list(cntdict["dist"].keys()):
                cntdict["dist"][el] = cntdict["dist"][el] + 1
            else:
                cntdict["dist"][el] = 1

        newdict["functions"].append(cntdict)

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


def core_html_hdr():
    return """
<html>
<head>
<title>Core view</title>
</head>
<body>
"""

def vp_html_hdr():
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

def generic_html_end():
    return """<br>
</body>
</html>
"""
