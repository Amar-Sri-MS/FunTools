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

def image_details(fname, fourcc, offset):
    res = {}
    valid = False
    with open(fname, 'r+b') as f:
        f.seek(offset + 4096, os.SEEK_SET)
        funhdr = f.read(76)
        vals = struct.unpack('<2I4s3B29s32s', funhdr)
        keys = ( 'size', 'version', 'fourcc', 'dpu_family', 'dpu_device', 'dpu_revision',
            'attributes', 'description')
        assert len(keys) == len(vals)
        for i, k in enumerate(keys):
            res[keys[i]] = vals[i]

    try:
        res['fourcc'] = res['fourcc'].decode()
        if res['fourcc'] == fourcc:
            valid = True
            # fixup empty bytes for readability
            if res['attributes'] == b'\xff' * 29 or res['attributes'] == b'\x00' * 29:
                res['attributes'] = ""
            res['description'] = res['description'].decode().rstrip('\x00')
            res['offset'] = offset
    except:
        # this doesn't look like a valid nor flash entry so
        # just create a dummy entry without usual details
        res = {}
        res['fourcc'] = fourcc
        res['offset'] = offset
        pass

    return valid, res



def save_image_as_file(fname, section, id):
    with open(fname, 'rb') as f:
        with open('{}_{}_{}'.format(fname, section['fourcc'], id), 'w+b') as out:
            f.seek(section['offset'], os.SEEK_SET)
            out.write(f.read(section['size'] + 4172)) # size + sizeof(header)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input-file', help='Input flash image', required=True)
    parser.add_argument('-f', '--fourcc', help='Use only selected fourcc code')
    parser.add_argument('-d', '--dump', action='store_true', help='Dump image section to a file')
    args = parser.parse_args()

    entries = get_entries(args.input_file)
    entries.sort(key=lambda x: x[1])

    for i, e in enumerate([f for f in entries if (f[0] == args.fourcc if args.fourcc else True)]):
        valid, value = image_details(args.input_file, e[0], e[1])
        print("{}: {}".format(e[0], value))

        if args.dump and valid:
            save_image_as_file(args.input_file, value, i)


if __name__ == "__main__":
    main()
