#!/usr/bin/env python2.7
from __future__ import print_function
import sys

from bpf_elf import extract_function_ptr

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: ' + sys.argv[0] + ' <binary> <function_name>')
        sys.exit(1)

    print(extract_function_ptr(sys.argv[1], sys.argv[2]))