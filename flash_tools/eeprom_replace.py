#!/usr/bin/env python3

import os
import argparse
import json
import shutil
import subprocess
import flash_utils

def replace(infile, outfile, eepr):
    parts = list([f for f in flash_utils.get_entries(infile) if f[0] == 'eepr'])
    shutil.copy2(infile, outfile)
    for p in parts:
        cmd = ['dd',
               'if={}'.format(eepr),
               'of={}'.format(outfile),
               'conv=notrunc',
               'obs=1',
               'status=none',
               'seek={}'.format(p[1])]
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
            for skuid, value in list(eeproms.items()):
                destfile = '{}.{}'.format(input, skuid)
                print('Generating {}'.format(destfile))
                replace(input, destfile, value['filename'] + '.bin')


if __name__ == "__main__":
    main()
