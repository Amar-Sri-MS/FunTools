#!/usr/bin/env python3

## read a deduped file and translate all the addresses into something
## interesting via addr2line

import os
import sys
import glob
import json
import time
import argparse

# FIXME: make this happen via FunSDK?
def TraceParserPath():
    return os.path.dirname(os.path.realpath(__file__)) + "/../TraceParser"

# grab the line2addr module
sys.path.append(TraceParserPath())
import parse_dqr_tm

IN_FILE = "addr-list.js"
OUT_FILE = "line-ident.js"
FUNOS_BINARY = "funos-f1.stripped"

###
##  make sure we're 0xfoo
#

def canonical_va(x):
    n = int(x, 16)

    # filter out things not in the binary
    b = n & 0xffffffffffffff
    if (b > (256<<20)):
        return None

    return "%016x" % n
    

###
##  use addr2line
#

def get_addr2line(va, funos_binary):
    d = parse_dqr_tm.parsed_addr2line([va], funos_binary)

    return d[va]

    
###
##  add a VA and its line info to the full list
#

def mkaddrinfo(binname, va):
    # look up all the info for a line
    info = {}

    info["line_va"] = "%016x" % (va - (va % 64)) # round to cache line
    
    # addr2line
    info["srclines"] = get_addr2line(va, binname)

    return info
    
def check_add(binname, addrinfo, sva):
    
    if (sva not in addrinfo):
        va = int(sva, 16)
        info = mkaddrinfo(binname, va)
        addrinfo[sva] = info
        if (info["line_va"] not in addrinfo):
            sva = info["line_va"]
            va = int(sva, 16)
            info = mkaddrinfo(binname, va)
            addrinfo[sva] = info


###
##
#
def do_line_ident(addrlist, outfname, binname):

    addrident = {}

    n = len(addrlist)
    f = 0
    t0 = time.time()
    t00 = t0
    for i in range(0, n):
        addr = canonical_va(addrlist[i])

        t1 = time.time()
        if ((t1 - t0) > 10):
            rate = (i - f) / (t1 - t00)
            print("complete: %.0f%% (%s/%s/%s)" % (((i * 100.0) / n), i, f, n))
            t0 = t1

        if (addr is None):
            f += 1
            continue

        check_add(binname, addrident, addr)
                

    # write it out
    fl = open(outfname, "w")
    fl.write(json.dumps(addrident, indent=4))
    print("done")

###
##  main
#

def main():

    fl = open(IN_FILE)
    addrlist = json.loads(fl.read())
    do_line_ident(addrlist, OUT_FILE, FUNOS_BINARY)

        
###
##  entrypoint
#

if (__name__ == "__main__"):
    main()
