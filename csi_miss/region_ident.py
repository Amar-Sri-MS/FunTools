#!/usr/bin/env python2.7

import re
import sys
import json
import argparse

IN_FILE = "uartout0.0.txt"
OUT_FILE = "region-ident.js"

###
##  regex work
#

# no newlines because \m
LINE_HDR_RE = "\[[0-9 \.]+\] "
START_RE = LINE_HDR_RE + "region[ \t]+start[ \t]+end[ \t]+size"
DASHES_RE = LINE_HDR_RE + "[- \t]+"
REGION_RE = LINE_HDR_RE + "([a-z0-9-_]+)[ \t]+(0x[a-f0-9]+)[ \t](0x[a-f0-9]+)[ \t].*"
EMPTY_REGION_RE = LINE_HDR_RE + "([a-z0-9-_]+)[ \t]+_+[ \t]_+[ \t]0 bytes.*"

def find_first_region(lines):

    # header, dashes, one region 
    while (len(lines) >= 3):

        # take the first line and see if it's the header
        line = lines.pop(0)
        if ("region" in line):
            print line
        m = re.match(START_RE, line.strip())
        if (m is None):
            continue

        print "found header"
        
        # inspect next line and see if it's dashes
        line = lines[0]
        m = re.match(DASHES_RE, line.strip())
        if (m is None):
            continue
        lines.pop(0)

        # Make sure the next line matches the regions
        line = lines[0]
        m = re.match(REGION_RE, line.strip())
        assert (m is not None)
        return lines

    return None

def parse_region_line(line):
    m = re.match(REGION_RE, line)
    if (m is not None):
        return (m.group(1), int(m.group(2), 16), int(m.group(3), 16))

    m = re.match(EMPTY_REGION_RE, line)
    if (m is not None):
        return (m.group(1), 0, 0)

    return None
    
###
##  real work
#

def find_regions(fname):

    fl = open(fname)

    lines = fl.readlines()
    lines = find_first_region(lines)

    if (lines is None):
        raise RuntimeError("Could not find any regions")
    
    regions = []
    toks = parse_region_line(lines.pop(0))
    while (toks is not None):
        # start, end, name
        regions.append((toks[1], toks[2], toks[0]))
        toks = parse_region_line(lines.pop(0))

    regions.sort()
    print "found %d regions" % len(regions)

    return regions

###
##  main
#

def main():

    regions = find_regions(IN_FILE)

    fl = open(OUT_FILE, "w")
    fl.write(json.dumps(regions, indent=4))
    print "done"

    
###
##  entrypoint
#

if (__name__ == "__main__"):
    main()

