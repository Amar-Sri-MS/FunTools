#!/usr/bin/env python3

#
# Wrapper around the processing pipeline that generates a completion
# file to serve as success/failure notice.
#
# Production stuff would use a database instead of such a file....
#
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
        dump_completion_file(directory, False, 'Internal problem processing traces', [])
        sys.exit(1)

    results = glob.glob(os.path.join(directory, 'odp', 'cache_miss_*.txt'))
    results = [os.path.basename(r) for r in results]

    dump_completion_file(directory, True, 'OK', results)


def dump_completion_file(directory, ret, msg, result_files):
    js = json.dumps({'ret': ret, 'msg': msg, 'files': result_files})
    with open(os.path.join(directory, 'odp', 'process.json'), 'w') as f:
        f.write(js)


if __name__ == '__main__':
    main()

