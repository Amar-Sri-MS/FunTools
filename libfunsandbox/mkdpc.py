#!/usr/bin/env python2.7

###
##  make the necessary dpc transactions to load a sandbox
#

import sys

###
##  main function
#

def main():

    if (len(sys.argv) < 4):
        print "usage: %s <name> <binfile> <nmfile>" % sys.argv[0]
        return 1

    sname = sys.argv[1]
    binfile = sys.argv[2]
    nmfile = sys.argv[3]

    base = None
    funclist = []
    for line in open(nmfile).readlines():
        line = line.strip()
        toks = line.split(" ")
        name = toks[-1]

        if (name[0] == "$"):
            continue

        if (name == "_ftext"):
            base = int(toks[0], 16)

        if (name[0] == "_"):
            continue

        funclist.append((name, int(toks[0], 16)))

    if (base is None):
        print "failed to find base symbol?"
        return 1

    bin = open(binfile, mode='rb').read()
    print "# binary length is %d bytes" % len(bin)

    # now write details
    print "sandbox create shared %s %s" % (sname, len(bin))

    # turn bin to string
    first = True
    s = "["
    for b in bin:
        if (not first):
            s += ", "
        s += "0x%x" % ord(b)
        first = False
    s += "]"
    print "sandbox addbytes %s 0 %s" % (sname, s)

    for (func, addr) in funclist:
        print "sandbox addfunc %s %s %s" % (sname, func, addr-base)
    
    return 0
###
##  command-line entrypoint
# 
if (__name__ == "__main__"):
    r = main()
    sys.exit(r)
