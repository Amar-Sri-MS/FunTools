#!/usr/bin/env python3

import optparse
import string


# canonical command to make a mask of everything except bottom 16k
# ./serialgen.py -s 0xffff0000 -p 0xffffff -w 0xff -y 0xff -f 0xf -d 0xf -o 0xffffff -l 0xff  -m

# canonical command to make a serial number of all zeros except part
# serial number
# ./serialgen.py -s 1234


###
##  make a hex string
#

def genb(raw_val, nbits, default = "0"):

    if ((nbits % 4) != 0):
        raise RuntimeError("non-nibble aligned value")

    if (raw_val is None):
        raw_val = default

    if (raw_val is None):
        raise RuntimeError("mandatory value not specified")

    try:
        tval = int(raw_val, 0)
    except:
        raise RuntimeError("Bad input: %s" % raw_val)

    mask = (1 << nbits) - 1
    val = tval & mask

    if (val != tval):
        raise RuntimeError("Value to wide for field: 0x%x / 0x%x" % (val, mask))

    s = ""
    for i in range(nbits, 0, -4):
        n = i - 4
        nval = val >> n
        nval = nval & 0xf

        s = s + string.hexdigits[nval]

    return s
        
    
###
##  serial gen
#

def gen_serial(opts):

    pts = genb(opts.serial, 32)
    part = genb(opts.part, 24)
    wk = genb(opts.week, 8)
    yr = genb(opts.year, 8)
    fb = genb(opts.fab, 4)
    fn = genb(opts.foundry, 4)
    if (not opts.mask):
        reserved = genb("0", 48)
    else:
        reserved = genb("0xffffffffffff", 48)

    s = part + fn + fb + yr + wk + reserved + pts
    
    if (opts.verbose):
        print("serial pts=0x%s, part=0x%s, wk=0x%s, yr = 0x%s, fb=0x%s, fn=0x%s" % (pts, part, wk, yr, fb, fn))
        print("serial", s)

    return s
    
###
##  info gen
#

def gen_info(opts):

    lc = genb(opts.lc, 8)
    if (not opts.mask):
        reserved = genb("0", 32)
    else:
        reserved = genb("0xffffffff", 32)
    oid = genb(opts.oid, 24) 

    s = lc + reserved + oid
    
    if (opts.verbose):
        print("info part: oid 0x%s, lc 0x%s" % (oid, lc))
        print("info", s)

    return s

###
##  argument parsing
#

def parse_args():
    parser = optparse.OptionParser(description='F1 serial fuse-bit generator')

    parser.add_option("-s", "--serial", help="32b part serial number",
                      default=None)
    parser.add_option("-p", "--part", help="24b part number", default=None)
    parser.add_option("-w", "--week", help="8b WK", default=None)
    parser.add_option("-y", "--year", help="8b YR")
    parser.add_option("-f", "--fab", help="4b Fab")
    parser.add_option("-d", "--foundry", help="4b Foundry")
    parser.add_option("-o", "--oid", help="24b organization ID")
    parser.add_option("-l", "--lc", help="8b lifecycle bits")

    parser.add_option("-m", "--mask", action="store_true", default=False,
                      help="generate reserved masks")

    parser.add_option("-v", "--verbose", action="store_true", default=False,
                      help="enable debug output")

    ret = parser.parse_args()

    return ret
    
###
##  Entrypoint
#

def main():
    (opts, args) = parse_args()

    info = gen_info(opts)
    serial = gen_serial(opts)

    s = info + serial

    if (len(s) != (2 * 24)):
        raise RuntimeError("failed to generate correct fuse length")
    
    print(s)
    
# boilerplate
if (__name__ == "__main__"):
    main()
