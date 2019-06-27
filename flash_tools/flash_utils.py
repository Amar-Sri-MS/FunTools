#!/usr/bin/env python3

""" Copyright (c) 2019 Fungible, Inc. All Rights reserved """

import binascii
import struct
import sys
import os
import argparse
import shutil
import tempfile


def get_entries(fname):
    ret = []
    with open(fname, 'r+b') as f:
        hdr = f.read(12)
        crc = binascii.crc32(hdr[4:]) & 0xFFFFFFFF
        hdr_crc, p1, p2 = struct.unpack('<3I', hdr)
        assert crc == hdr_crc, "Invalid CRC in header"

        f.seek(p1)
        puf_hdr = f.read(16)
        hdr_crc, pufr1, pufr2, _ = struct.unpack('<4I', puf_hdr)
        ret.append(('pufr', pufr1))
        ret.append(('pufr', pufr2))

        while True:
            vhdr = f.read(12)
            addr1, addr2, name = struct.unpack('<2I4s', vhdr)
            if addr1 == addr2 and \
               addr1 == 0 or \
               addr1 == 0xFFFFFFFF:
                break
            ret.append((name.decode(), addr1))
            ret.append((name.decode(), addr2))

    return ret


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input-file', help='Input flash image', required=True)
    parser.add_argument('-f', '--fourcc', help='Use only selected fourcc code')
    args = parser.parse_args()

    entries = get_entries(args.input_file)
    entries.sort(key=lambda x: x[1])

    for e in filter(lambda f: f[0] == args.fourcc if args.fourcc else True, entries):
        if args.fourcc:
            print("{}".format(e[1]))
        else:
            print("{}: {}".format(e[0], e[1]))


if __name__ == "__main__":
    main()
