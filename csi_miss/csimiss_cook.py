#!/usr/bin/env python2.7

import sys
import glob
import json
import argparse

## Convert raw trace (pc, vaddr, load/store) files to a list of
## dictionaries and a list of addresses that need identifiying

RAW_GLOB = "cache_miss_?_?.txt"

OUT_MISS = "miss-list.js"
OUT_ADDR = "addr-list.js"

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
##  parse trace files to a miss list
#

def mkmisslist(globstr):
    
    # find all the files
    missfiles = glob.glob(globstr)

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

    return misses


# convert a raw miss list into a list of miss dicts and a list of
# interesting addresses

def disect_misslist(rawmisses):
    
    # dict -> list because json
    out = []
    addrs = []
    for key in rawmisses:
        k = key[0]
        d = {"pc": k,
             "vaddr": key[1],
             "type": "L1-"+key[2],
             "core": key[3],
             "count": rawmisses[key]}
        out.append(d)
        addrs.append(k)
        addrs.append(key[1])

    return (out, addrs)

def do_disect(sglob):
    
    rawmisses = mkmisslist(sglob)

    # split into data and addresses to identify
    return disect_misslist(rawmisses)

###
##  write some json
#

def save_json(fname, addrlist):
    fl = open(fname, "w")
    fl.write(json.dumps(addrlist, indent=4))
    
    

###
##  main
#

def main():

    # make a raw miss list
    rawmisses = mkmisslist(RAW_GLOB)

    # split into data and addresses to identify
    (misslist, addrlist) = disect_misslist(rawmisses)
    
    # write out the miss list
    save_json(OUT_MISS, misslist)

    # write out the address list
    save_json(OUT_ADDR, addrlist)
    print "done"
    
###
##  entrypoint
#

if (__name__ == "__main__"):
    main()
