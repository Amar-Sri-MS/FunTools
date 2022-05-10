#!/usr/bin/env python3

import os
import sys
import csv
import json
import argparse
import datetime
import collections
from jinja2 import Environment, FileSystemLoader


# Given a miss-count list and a set of linedb/whateverdbs, spit out a
# HTML break down of all the ways the cache misses line up

MISSFILE = "miss-list.js"
LINEFILE = "line-ident.js"
GDBFILE = "gdb-ident.js"
REGIONFILE = "region-ident.js"
OUTFILE_HTML = "missmap.html"
OUTFILE_CSV = "misspivot.csv"
TOPN = 15

###
##  key transform functions
#

def _rekey_pc(d):
    return "0x%016x" % d["pc"]

def _rekey_pa(d):
    return "0x%016x" % d["pa"]

def _rekey_pa_line(d):
    pa = d["pa"]
    pa = pa - (pa % 64) # round to cache line
    return "0x%016x" % pa

def _rekey_vague(d):
    pa = d["vague_info"]
    return pa

###
##  key transforms
#

REKEY_LIST = [
    ("By PC", "srclines", _rekey_pc),
    ("By PA", "data_info", _rekey_pa),
    ("By Vague Symbol", "srclines", _rekey_vague),
    ("By PA Line", "data_info", _rekey_pa_line)
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

def do_rekey(misslist, rkfunc, info_field, max_rows):

    # refactor by new key
    d = {}

    for miss in misslist:
        newkey = rkfunc(miss)
        d.setdefault(newkey, []).append(miss)
    
    # make a list of tuples with count
    l = mkcountlist(d, info_field)
    l.sort(reverse=True)

    # trim it if requested
    if (max_rows > 0):
        l = l[:max_rows]
    
    return l

###
##  write data to HTML template
#

def abs_app_dir_path():
    return os.path.dirname(os.path.realpath(__file__))

def read_stylesheet():
    # inline the whole file for single HTML file goodness

    css_fname = os.path.join(abs_app_dir_path(), "../perf/static/style.css")
    fl = open(css_fname)
    style = "\n".join(fl.readlines())

    return style

def do_output(out_fname, sections, cores):

    # read the css formatting
    style = read_stylesheet()

    # run the template
    args = {"style": style,
            "date": str(datetime.datetime.now()),
            "sections": sections,
            "cores": cores}

    tpath = os.path.join(abs_app_dir_path(), "templates")
    file_loader = FileSystemLoader(tpath)
    env = Environment(loader=file_loader)
    template = env.get_template('missmap.html')
    output = template.render(args)

    fl = open(out_fname, 'w')
    fl.write(output)

###
##  pivot output
#

TABDEF = collections.OrderedDict([("pc_hex", "pc"),
                                  ("pa_hex", "pa"),
                                  ("pa_line_hex", "line address"),
                                  ("type", "type"),
                                  ("plane", "cluster type"),
                                  ("cluster", "cluster"),
                                  ("core", "core"),
                                  ("count", "count"),
                                  ("pa_region", "region"),
                                  ("srclines", "line info"),
                                  ("data_info", "data info"),
                                  ("vague_info", "vague info"),
])

def do_pivot(out_fname, misses):

    fl = open(out_fname, "w")
    
    keys = list(TABDEF.keys())
    writer = csv.DictWriter(fl, fieldnames=keys, extrasaction="ignore")
    
    # write the header with nice names
    writer.writerow(TABDEF)

    # now write all the rows
    for miss in misses:
        writer.writerow(miss)

    

###
##  read the region table
#

def find_region(pa, regioninfo):

    for region in regioninfo:
        if ((pa >= region[0])
            and (pa < region[1])):
            return region[2]

    return None
    
###
##  read the gdb table
#

def find_gdb(pa, gdbinfo):

    key = "0x%016x" % pa
    val = gdbinfo.get(key)
    
    if (val is None):
        return None

    return val["syminfo"]

def find_vague(pa, gdbinfo):

    key = "0x%016x" % pa
    val = gdbinfo.get(key)
    
    if (val is None):
        return None

    return val["symvague"]

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

def excel_encode_core(core):
    return "\t%s" % core

def core2cluster(core):
    return core.split(".")[0]

def core2plane(core):

    if (core2cluster(core) == "8"):
        return "CC"
    else:
        return "PC"

def mk_data_info(miss):

    rgn = miss["pa_region"]
    gdb = miss["syminfo"]

    if (gdb is not None):
        return "%s. %s" % (rgn, gdb)
    else:
        return "%s" % rgn

def mk_vague_info(miss):

    rgn = miss["pa_region"]
    gdb = miss["symvague"]

    if (gdb is not None):
        return "%s: %s" % (rgn, gdb)
    else:
        return "%s" % rgn

def mkmisses(raw_misses, lineinfo, regioninfo, gdbinfo):

    misses = []
    for raw_miss in raw_misses:

        miss = {}
        miss["pc_hex"] = raw_miss["pc"]
        miss["va_hex"] = raw_miss["vaddr"]
        miss["pc"] = int(raw_miss["pc"], 16)
        miss["va"] = int(raw_miss["vaddr"], 16)
        miss["count"] = raw_miss["count"]
        miss["type"] = raw_miss["type"]
        miss["core"] = excel_encode_core(raw_miss["core"])

        if (invalid_miss(miss)):
            continue

        miss["pa"] = va2pa(miss["va"])
        miss["pa_hex"] = "0x%016x" % miss["pa"]
        miss["pa_line"] = va2pa(miss["va"] - (miss["va"] % 64))
        miss["pa_line_hex"] = "0x%016x" % miss["pa_line"]
        miss["plane"] = core2plane(raw_miss["core"])
        miss["cluster"] = core2cluster(raw_miss["core"])
        srclines = None
        pa_region = find_region(miss["pa"], regioninfo)
        syminfo = find_gdb(miss["pa"], gdbinfo)
        symvague = find_vague(miss["pa"], gdbinfo)
        k = raw_miss["pc"]
        if (k):
            srclines = lineinfo.get(k, {}).get("srclines")
            if (srclines is not None):
                srclines = "".join(srclines)
            else:
                srclines = "unknown src: %s" % k
        
        miss["srclines"] = srclines
        miss["pa_region"] = pa_region
        miss["syminfo"] = syminfo
        miss["symvague"] = symvague
        data_info = mk_data_info(miss)
        vague_info = mk_vague_info(miss)
        miss["data_info"] = data_info
        miss["vague_info"] = vague_info

        misses.append(miss)

    return misses


def do_missmap_html(misses_raw, lineinfo, regioninfo, gdbinfo, out_fname,
                    max_rows, cores):

    misses = mkmisses(misses_raw, lineinfo, regioninfo, gdbinfo)
    # template prints a list of sections
    sections = []

    for (name, info_field, func) in REKEY_LIST:
        by_key = do_rekey(misses, func, info_field, max_rows)
        tup = (name, by_key)
        sections.append(tup)

    # make the output
    do_output(out_fname, sections, cores)


###
##  do the work
#

def do_missmap(misses_raw, lineinfo, regioninfo, gdbinfo, mode, out_fname, max_rows=0):

    if (mode == "html"):
        misslist_by_core = collections.defaultdict(list)
        for miss in misses_raw:
            core = miss["core"]
            misslist_by_core[core].append(miss)

        for core in misslist_by_core:
            out_fname = "missmap_%s.html" % core
            do_missmap_html(misslist_by_core[core], lineinfo, regioninfo,
                            gdbinfo, out_fname, max_rows, [core])

        do_missmap_html(misses_raw, lineinfo, regioninfo, gdbinfo, 'missmap.html', max_rows,
                        sorted(misslist_by_core))
    elif (mode == "csv"):
        # process misses accoriding to available info
        print("%d misses in input" % len(misses_raw))
        misses = mkmisses(misses_raw, lineinfo, regioninfo, gdbinfo)
        print("%d processed misses" % len(misses))
        do_pivot(out_fname, misses)
    else:
        raise RuntimeError("bad mode %s" % mode)
        
###
##  read a json file
#
def loadjs(fname):
    return json.loads(open(fname).read())


###
##  trivial arg parsing
#

MODES = {"html": OUTFILE_HTML,
         "csv": OUTFILE_CSV}

def usage():
    print("usage: %s {html, csv}" % sys.argv[0])
    sys.exit(1)

def getmode():
    
    if (len(sys.argv) == 1):
        mode = "html"

    if (len(sys.argv) == 2):
        mode = sys.argv[1]

    if (mode not in MODES):
        usage()

    return (mode, MODES[mode])

###
##  main
#

def main():

    (mode, outfile) = getmode()
    
    # open the miss list
    misses_raw = loadjs(MISSFILE)

    # open the source line of code db
    lineinfo = loadjs(LINEFILE)

    # open the source line of code db
    gdbinfo = loadjs(GDBFILE)
    
    # open the source region db
    regioninfo = loadjs(REGIONFILE)

    # do all the work
    do_missmap(misses_raw, lineinfo, regioninfo, gdbinfo, mode, outfile)
    

###
##  entrypoint
#

if (__name__ == "__main__"):
    main()
