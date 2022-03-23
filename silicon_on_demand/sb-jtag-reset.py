#!/usr/bin/env python3

# Use jtag via codescape to reset a target F1 device

import sys
from codescape_survival import *
from imgtec.console import *

def main():
    if (len(sys.argv) != 2):
        print("usage: %s <sb-xx>" % sys.argv[0])
        sys.exit(1)

    print("connecting...")
    connect_to_sb_probe(sys.argv[1], no_detect=True)
    
    #print "resetting probe..."
    reset(probe)
    #print "ticking"
    tckrate(25000000)
    print("resetting target...")
    scanonly()
    reset(hard_run)
    print("reset done")
    
if (__name__ == "__main__"):
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)
        
