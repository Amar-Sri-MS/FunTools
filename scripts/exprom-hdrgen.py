#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepend Fungible custom Expansion ROM Header and concatenate a zero pad 
to an EFI ROM file. Command-line arguments other than the input and output
files will generate a corrupt file.
 
The header is a 4kB blob with a 32b little endian size for the ROM.

The ROM must be power of 2 size (because PCI BAR), with size a multiple of
512B because EEPROM block size.

The custom header is prepended to the ROM so the total size need not be power-of-two, but the total size must be 512B aligned.

usage:
% exprom-hdrgen.py myrom.efi -o myrom.bin

static check:
% mypy exprom-hdrgen.py
 
format:
% python3 -m black exprom-hdrgen.py
"""
from typing import List, Optional, Type, Dict, Any, Tuple
import argparse
import struct
import math
import os

###
##  logging object
#

VERBOSITY: int = 0

def LOG(msg: str, level: int = 0) -> None:
    if (level <= VERBOSITY):
        print(msg)

def VERBOSE(msg):
    LOG(msg, 1)

def DEBUG(msg):
    LOG(msg, 2)

###
##  header generator
#

def mkheader(hdrsize: int, romsize: int) -> bytes:

    ret: bytes = struct.pack("<I", romsize)

    # make a pad for the whole header
    ret += b'\x00' * hdrsize

    # trim the whole thing to support arbitrary sizes
    ret = ret[:hdrsize]

    return ret


###
##  parse_args
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
 
    # Required positional argument
    parser.add_argument("input", help="Required positional argument")
 
    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument("-o", "--output", action="store",
                        help="Output filename")
 
    ## optional tweaks
    
    # Optional argument flag which defaults to False
    parser.add_argument("-H", "--header-only",
                        action="store_true", default=False,
                        help=("Output header only, do not concatenate"
                              "input file"))
 
    # All expansion ROM files must be a multiple of 512B
    parser.add_argument("--hdrsize",
                        action="store", default=4096,
                        help=("Size of Fungible custom header"))

    # All expansion ROM files must be a multiple of 512B
    parser.add_argument("--blockpad",
                        action="store", default=512,
                        help=("EEPROM block size to pad to"))

    # Don't round padding up to a power of two
    parser.add_argument("-P", "--no-pow",
                        action="store_true", default=False,
                        help=("Do not round up to a power of two size"))

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")
 
    args: argparse.Namespace = parser.parse_args()

    # configure logging
    global VERBOSITY
    VERBOSITY = args.verbose

    return args
 
###
##  main
#
def main() -> int:
    args: argparse.Namespace = parse_args()

    # get the file size
    fsize = os.path.getsize(args.input)
    VERBOSE("original file size: %d" % fsize)

    # pad out to the block size
    if (args.blockpad == 0):
        args.blockpad = 1
    bsize = math.ceil(fsize / args.blockpad) * args.blockpad
    VERBOSE("blocked size: %d" % bsize)

    # align size to a power of two
    if (args.no_pow):
        psize = bsize
    else:
        psize = 1 << math.ceil(math.log(bsize, 2))

    VERBOSE("power2 size: %d" % psize)

    # compute actual zero pad
    zsize = psize - fsize

    # compute final file size
    osize = psize + args.hdrsize

    VERBOSE("size of ROM pad: %d" % zsize)

    LOG("Output file size = %d + %d + %d = %d" % (args.hdrsize, fsize, zsize,
                                                  osize))

    if (args.output is None):
        LOG("no output specified, exiting")
    else:
        LOG("writing to file %s" % args.output)
        fl = open(args.output, "wb")

        # write the header
        fl.write(mkheader(args.hdrsize, psize))

        if (args.header_only):
            LOG("skipping file contents")
        else:
            rombytes = open(args.input, "rb").read()
            fl.write(rombytes)
            fl.write(b'\x00' * zsize)

            fl.close()

            # sanity
            if (os.path.getsize(args.output) != osize):
                raise RuntimeError(("Bad file generated: "
                                    "%d != %d") % (args.output, osize))

    return 0
 
###
##  entrypoint
#
if __name__ == "__main__":
    main()
