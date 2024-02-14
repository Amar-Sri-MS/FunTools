#!/usr/bin/env python3

import os
import argparse
import json
import shutil
import subprocess
import flash_utils
import tempfile

SECTOR_SIZE = 64*1024

def replace(infile, outfile, replacement_bin, replacement_fourcc='eepr'):
    parts = list(filter(lambda f: f[0] == replacement_fourcc, flash_utils.get_entries(infile)))

    if outfile:
        shutil.copy2(infile, outfile)
    else:
        outfile = infile

    with tempfile.NamedTemporaryFile('wb') as tmp, open(replacement_bin, 'rb') as infile:
        data = infile.read()
        tmp.write(data)
        # pad up to a full sector
        tmp.write(bytes([0xff] * (SECTOR_SIZE - (len(data) % SECTOR_SIZE))))
        tmp.flush()
        size = 4096

        for p in parts:
            seek = p[1] // 4096
            assert p[1] % SECTOR_SIZE == 0

            cmd = ['dd',
               'if={}'.format(tmp.name),
               'of={}'.format(outfile),
               'conv=notrunc',
               'bs={}'.format(size),
               'status=none',
               'seek={}'.format(seek)]
            subprocess.call(cmd)

def main():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--eepr', metavar='FILE', help='New eepr image to use')
    group.add_argument('--eepr-list', metavar='FILE', help='Eepr list json to use')

    parser.add_argument('input', action='store', nargs=1, help='Flash image to use')

    args = parser.parse_args()
    input = args.input[0]

    if args.eepr:
        destfile = '{}.{}'.format(input, os.path.basename(args.eepr))
        print('Generating {}'.format(destfile))
        replace(input, destfile, args.eepr)
    else:
        with open(args.eepr_list) as f:
            eeproms = json.load(f)
            for skuid, value in eeproms.items():
                destfile = '{}.{}'.format(input, skuid)
                print('Generating {}'.format(destfile))
                replace(input, destfile, value['filename'] + '.bin')


if __name__ == "__main__":
    main()
