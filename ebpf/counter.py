#!/usr/bin/env python
from bpf_client import bpf

if __name__ == '__main__':
  with bpf(elf = 'kernels/counter.elf') as b:
    print "Hooking done"
    b.trace_print()
