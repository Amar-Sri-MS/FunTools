#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sign a single binary for F1/S1 using development keys from the network.
"""

from __future__ import print_function
import sys
import argparse
import firmware_signing_service as fsi

###
## four-cc defaults
#


# fourcc: (sign_key, key_index)
FOURCC_DEFAULTS = {
    'fun1': ('hkey1', 0, 1),
    'ccfg': ('hkey1', 0, 512),
}

# match above tuple entries
IDX_SIGN_KEY = 0
IDX_KEY_INDEX = 1
IDX_PAD = 2

def check_update(opts, the_opt, idx):
    # user can always override
    if (the_opt is not None):
        return the_opt

    # check if the four-cc has defaults
    if (opts.ftype not in FOURCC_DEFAULTS):
        return the_opt

    # override it
    return FOURCC_DEFAULTS[opts.ftype][idx]


###
## main
#

def check_len_4(s):
    if (len(s) == 4):
        return s

    raise argparse.ArgumentTypeError("fourcc must be of length 4")

def parse_args():
    parser = argparse.ArgumentParser()

    # Optional argument flag which defaults to None. Can be ignored
    parser.add_argument("--certfile", action="store", default=None)
    parser.add_argument("--customer_certfile", action="store", default=None)
    parser.add_argument("--description", action="store", default=None)
    parser.add_argument("-o", "--outfile", action="store", default=None,
                        help="output filename. defaults to $infile.signed")
    parser.add_argument("-p", "--pad", action="store", default=None,
                        type=int,
                        metavar="SIZE",
                        help="pad outfile to be a multiple of SIZE bytes")

    # Optional arguments with meaningful defaults (but rarely changed)
    parser.add_argument("--version", action="store", type=int, default=1)
    parser.add_argument("--key_index", action="store", type=int, default=0,
                        help="key index in keybag")

    # Required arguments
    parser.add_argument("--fourcc", action="store", dest="ftype",
                        type=check_len_4,
                        help="required: fourcc/ftype of blob", required=True)
    parser.add_argument("--sign_key", action="store",
                        help="identifier of key to use, eg. hkey1")
    parser.add_argument('--chip', dest='chip_type', choices=['f1', 's1', 'f1d1', 's2'],
                        required=True, help='Target chip')


    # Required positional argument
    parser.add_argument("infile", help="file to be signed")

    opts = parser.parse_args()

    # check for defaults
    opts.sign_key = check_update(opts, opts.sign_key, IDX_SIGN_KEY)
    opts.key_index = check_update(opts, opts.key_index, IDX_KEY_INDEX)
    opts.pad = check_update(opts, opts.pad, IDX_PAD)

    # sanitise inputs
    if (opts.sign_key is None):
        parser.error("sign_key must be specified")

    if (opts.outfile is None):
        opts.outfile = opts.infile + ".signed"

    if (opts.pad is None):
        opts.pad = 1

    return opts

def main():
    opts = parse_args()

    # do the signature
    try:
        fsi.image_gen(**vars(opts))
    except Exception as e:
        print("Failed to sign the image: {}".format(e))
        sys.exit(1)


    print("signed")
    sys.exit(0)

###
## entrypoint
#
if __name__ == "__main__":
    main()
