#! /usr/bin/env python3
#
# trngjson2bin.py
# Extract data from TRNG data json file to binary file for
# use with the SP800-90B entropy assessment tool.
#
# Copyright (c) 2021. Fungible, Inc. All rights reserved.
#

import os
import sys
import binascii
import json


for fname in sys.argv[1:]:
    with open(fname, 'r') as fd:
        all_data = json.load(fd)

    bin_data = binascii.a2b_hex(all_data['data'])
    bin_fname = os.path.splitext(fname)[0] + '.bin'
    with open(bin_fname,'wb') as fd:
        for b in bin_data:
            for i in range(7, -1, -1):
                byteval = (b >> i) & 1
                fd.write(byteval.to_bytes(1, byteorder='big'))

    print("%s saved" % bin_fname)
