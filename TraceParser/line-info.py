#!/usr/bin/python

import sys
import glob
import json
import time
import argparse
import parse_dqr_tm

## read a deduped file and translate all the addresses into something
## interesting

IN_FILE = "miss-counts.js"
OUT_FILE = "linedb.js"
FUNOS_BINARY = "funos-f1.stripped"

###
##  use addr2line
#

def get_addr2line(va, funos_binary):
    d = parse_dqr_tm.parsed_addr2line([va], funos_binary)

    return d[va]

    
###
##  add a VA and its line info to the full list
#

def mkaddrinfo(va):
    # look up all the info for a line
    info = {}

    info["line_va"] = va - (va % 64) # round to cache line
    
    # addr2line
    info["srclines"] = get_addr2line(va, FUNOS_BINARY)

    # gdb

    # regions

    return info
    
def check_add(addrinfo, va):        
    if (va not in addrinfo):
        info = mkaddrinfo(va)
        addrinfo[va] = info
        if (info["line_va"] not in addrinfo):
            va = info["line_va"]
            info = mkaddrinfo(va)
            addrinfo[va] = info


###
##  main
#

def main():

    fl = open(IN_FILE)

    misslist = json.loads(fl.read())
    addrinfo = {}

    n = len(misslist)
    t0 = time.time()
    for i in range(0, n):
        miss = misslist[i]
        pc = miss["pc"]
        va = miss["vaddr"]

        t1 = time.time()
        if ((t1 - t0) > 10):
            print "complete: %f%%" % ((i * 100.0) / n)
            t0 = t1
        check_add(addrinfo, int(pc, 16))
        check_add(addrinfo, int(va, 16))
                

    # write it out
    fl = open(OUT_FILE, "w")
    fl.write(json.dumps(addrinfo, indent=4))
    print "done"

        
###
##  entrypoint
#

if (__name__ == "__main__"):
    main()
