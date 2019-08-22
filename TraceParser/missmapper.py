#!/usr/bin/python

import os
import sys
import json
import argparse
from jinja2 import Environment, FileSystemLoader


# Given a miss-count list and a set of linedb/whateverdbs, spit out a
# HTML break down of all the ways the cache misses line up

MISSFILE = "miss-counts.js"
LINEFILE = "linedb.js"
REGIONFILE = "regiondb.js"
OUTFILE = "missmap.html"
TOPN = 15

###
##  key transform functions
#

def _rekey_pc(d):
    return d["pc"]

def _rekey_pa(d):
    return d["pa"]

def _rekey_pa_line(d):
    pa = d["pa"]
    pa = pa - (pa % 64) # round to cache line
    return pa

###
##  key transforms
#

REKEY_LIST = [
    ("By PC", "srclines", _rekey_pc),
    ("By PA", "pa_region", _rekey_pa),
    ("By PA Line", "pa_region", _rekey_pa_line)
]

###
##  re-key the list to a short list
#

def mkcountlist(d, info_field):

    # given a dict, return into a list of (count, key, [values])

    ret = []
    for key in d:
        values = d[key]
        count = sum([ v["count"] for v in values])
        info = values[0][info_field]
        t = (count, key, info, values)
        ret.append(t)
    
    return ret

def do_rekey(misslist, rkfunc, info_field):

    # refactor by new key
    d = {}

    for miss in misslist:
        newkey = rkfunc(miss)
        d.setdefault(newkey, []).append(miss)
    
    # make a list of tuples with count
    l = mkcountlist(d, info_field)
    l.sort(reverse=True)

    return l

###
##  write data
#

def abs_app_dir_path():
    return os.path.dirname(os.path.realpath(__file__))

def read_stylesheet():
    # inline the whole file for single HTML file goodness

    css_fname = os.path.join(abs_app_dir_path(), "../perf/static/style.css")
    fl = open(css_fname)
    style = "\n".join(fl.readlines())

    return style

def do_output(sections):

    # read the css formatting
    style = read_stylesheet()
    
    # run the template
    args = {"style": style,
            "sections": sections}
    
    tpath = os.path.join(abs_app_dir_path(), "template")
    file_loader = FileSystemLoader(tpath)
    env = Environment(loader=file_loader)
    template = env.get_template('missmap.html')
    output = template.render(args)

    fl = open(OUTFILE, 'w')
    fl.write(output)

###
##  read the region table
#

def find_region(pa, regioninfo):

    for region in regioninfo:
        if ((pa >= region[0], 0)
            and (pa < region[1])):
            return region[2]

    return None
    
###
##  convert raw misses to data+info
#

# xkphys address format: [2b`10][3b`CCA][11b`0][48b`paddr]
XKPHYS_UC_ADDR = 2
XKPHYS_UCA_ADDR = 7

def xkseg(va):
    # not xkseg
    if ((va >> 62) != 2):
        return None
    
    return ((va >> 59) & 0x7)
    
# filter out uncached
def invalid_miss(miss):

    cca = xkseg(miss["va"])
    if ((cca == XKPHYS_UCA_ADDR) or (cca == XKPHYS_UC_ADDR)):
        return True
            
    return False

def va2pa(x):
    # FIXME
    return x

def mkmisses(raw_misses, lineinfo, regioninfo):

    misses = []
    for raw_miss in raw_misses:

        miss = {}
        miss["pc"] = int(raw_miss["pc"], 16)
        miss["va"] = int(raw_miss["vaddr"], 16)
        miss["count"] = raw_miss["count"]

        if (invalid_miss(miss)):
            continue

        miss["pa"] = va2pa(miss["va"])
        miss["pa_line"] = va2pa(miss["va"] - (miss["va"] % 64))
        srclines = None
        pa_region = find_region(miss["pa"], regioninfo)
        k = "%d" % miss["pc"] # wtf json
        if (k):
            srclines = lineinfo.get(k)["srclines"]
            if (srclines is not None):
                srclines = "".join(srclines)
            else:
                srclines = "foo: %s" % k
        
        miss["srclines"] = srclines
        miss["pa_region"] = pa_region
        misses.append(miss)

    return misses

###
##  read a json file
#
def loadjs(fname):
    return json.loads(open(fname).read())

###
##  main
#

def main():

    # open the miss list
    misses_raw = loadjs(MISSFILE)
    print "%d misses in input" % len(misses_raw)

    # open the source line of code db
    lineinfo = loadjs(LINEFILE)

    # open the source region db
    regioninfo = loadjs(REGIONFILE)

    # process misses accoriding to available info
    misses = mkmisses(misses_raw, lineinfo, regioninfo)

    print "%d processed misses" % len(misses)
    
    # template prints a list of sections
    sections = []

    for (name, info_field, func) in REKEY_LIST:

        by_key = do_rekey(misses, func, info_field)
        tup = (name, by_key)
        sections.append(tup)
    
    # make the output
    do_output(sections)

###
##  entrypoint
#

if (__name__ == "__main__"):
    main()
