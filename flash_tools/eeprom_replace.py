#!/usr/bin/env python3

import os
import argparse
import shutil
import subprocess
import flash_utils


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--eepr', metavar='FILE', required=True, help='New eepr image to use')
    parser.add_argument('input', action='store', nargs=1, help='Flash image to use')

    args = parser.parse_args()

    input = args.input[0]

    parts = list(filter(lambda f: f[0] == 'eepr', flash_utils.get_entries(input)))

    destfile = input + '_' + os.path.basename(args.eepr)
    shutil.copy2(input, destfile)
    for p in parts:
        cmd = ['dd',
               'if={}'.format(args.eepr),
               'of={}'.format(destfile),
               'conv=notrunc',
               'obs=1',
               'seek={}'.format(p[1])]
        subprocess.call(cmd)


if __name__ == "__main__":
    main()
