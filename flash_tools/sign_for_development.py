#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sign a single binary for F1/S1 using development keys from the network.
"""

from __future__ import print_function
import sys
import argparse
import firmware_signing_service as fsi

opts = None

###
## four-cc defaults
#


# fourcc: (sign_key, key_index)
FOURCC_DEFAULTS = {
    'fun1': ('hkey1', 0),
    'ccfg': ('hkey1', 0),
}

# match above tuple entries
IDX_SIGN_KEY = 0
IDX_KEY_INDEX = 1

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
def parse_args():
    parser = argparse.ArgumentParser()
 
    # Optional argument flag which defaults to None. Can be ignored
    parser.add_argument("--certfile", action="store", default=None)
    parser.add_argument("--customer_certfile", action="store", default=None)
    parser.add_argument("--description", action="store", default=None)
    parser.add_argument("-o", "--outfile", action="store", default=None,
                        help="output filename. defaults to $infile.signed")
 
    # Optional arguments with meaningful defaults (but rarely changed)
    parser.add_argument("--version", action="store", type=int, default=1)
    parser.add_argument("--key_index", action="store", type=int, default=0,
                        help="key index in keybag")

    # Required arguments
    parser.add_argument("--fourcc", action="store", dest="ftype",
                        help="fourcc/ftype of blob")
    parser.add_argument("--sign_key", action="store",
                        help="identifier of key to use, eg. hkey1")
    
    # Required positional argument
    parser.add_argument("infile", help="file to be signed")
 
    opts = parser.parse_args()

    # check for defaults
    opts.sign_key = check_update(opts, opts.sign_key, IDX_SIGN_KEY)
    opts.key_index = check_update(opts, opts.key_index, IDX_KEY_INDEX)
    
    # sanitise inputs
    if (opts.ftype is None):
        raise RuntimeError("fourcc must be specified")
    if (len(opts.ftype) != 4):
        raise RuntimeError("fourcc must be of length 4")
    if (opts.sign_key is None):
        raise RuntimeError("sign_key must be specified")

    if (opts.outfile is None):
        opts.outfile = opts.infile + ".signed"
    
    return opts
 
def main():
    global opts
    opts = parse_args()

    # construct the net sign
    mode = fsi.FirmwareSigningService.MOD_NET
    firmware_sign = fsi.FirmwareSigningService.create(mode)

    # do the signature
    try:
        firmware_sign.image_gen(**vars(opts))
    except Exception as e:
        raise RuntimeError("Failed to sign the image", e)

    print("signed")
    sys.exit(0)
    
###
## entrypoint
#
if __name__ == "__main__":
    main()
