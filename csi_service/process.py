#!/usr/bin/env python3

import argparse
import glob
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str)

    args = parser.parse_args()
    directory = args.directory

    rc = os.system('./process_local_cm.sh %s' % directory)
    if rc != 0:
        sys.exit(1)

    results = glob.glob(os.path.join(directory, 'odp', 'cache_miss_*.txt'))
    results = [os.path.basename(r) for r in results]

    js = json.dumps({'files': results})
    with open(os.path.join(directory, 'odp', 'process.json'), 'w') as f:
        f.write(js)


if __name__ == '__main__':
    main()

