#!/usr/bin/python

import sys
import glob
import json
import argparse

## Convert raw trace (pc, vaddr, load/store) files to
## a deduped list of dictionaries with a count.
## From there we can compute 

OUT_FILE = "miss-counts.js"

###
##  line parsing
#

def parse_line(line):

    toks = line.split()
    return (toks[0], toks[1], toks[2])

###
##  fname parsing
#

def file2core(fname):

    toks = fname.split("_")
    cluster = toks[2]
    core = toks[3][:1]

    return "%s.%s" % (cluster, core)

###
##  main
#

def main():

    # find all the files
    missfiles = glob.glob("cache_miss_?_?.txt")

    if (len(missfiles) == 0):
        raise RuntimeError("no cache_miss* files found")

    misses = {}

    for mfile in missfiles:
        core = file2core(mfile)
        fl = open(mfile)
        print "parsing %s (%s)" % (mfile, core)

        for line in fl.readlines():
            toks = parse_line(line.strip())
            
            key = toks + (core, )
            misses[key] = misses.get(key, 0) + 1


    # dict -> list because json
    out = []
    for key in misses:
        d = {"pc": key[0],
             "vaddr": key[1],
             "type": "L1-"+key[2],
             "core": key[3],
             "count": misses[key]}
        out.append(d)
            
    fl = open(OUT_FILE, "w")
    fl.write(json.dumps(out, indent=4))
    print "done"
    
###
##  entrypoint
#

if (__name__ == "__main__"):
    main()
