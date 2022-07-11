#!/usr/bin/env python3

import sys
from bpf_elf import extract_hook

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: ' + sys.argv[0] + ' <ELF>')
        sys.exit(1)

    print(extract_hook(sys.argv[1]))