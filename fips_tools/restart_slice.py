#! /usr/bin/env python3
#
# restart_slice.py
# Extract data from restart binary file for
# use with the SP800-90B entropy assessment tool.
#
# Copyright (c) 2021. Fungible, Inc. All rights reserved.
#
# The restart tool requires 1000 samples of length 1000
# This tool will reduce the length of each samples if necessary
# It assumes that there are 1000 samples of identical length
#


import os
import sys

for fname in sys.argv[1:]:
    with open(fname, 'rb') as fd:
        fd.seek(0, os.SEEK_END)
        len_data = fd.tell()
        fd.seek(0, os.SEEK_SET)

        q,mod = divmod(len_data, 1_000_000)
        if mod:
            print("Length of not a multiple of 1000000")
            sys.exit(1)

        # slice: read q * 1000 samples, write the first 1000 ones
        slice_fname = os.path.splitext(fname)[0] + '_sliced.bin'
        slices = 0
        with open(slice_fname,'wb') as fdout:
            data = fd.read(q * 1000)
            while data:
                fdout.write(data[:1000])
                slices = slices + 1
                data = fd.read(q * 1000)

    print("%d slices written, %s saved" % (slices, slice_fname))
