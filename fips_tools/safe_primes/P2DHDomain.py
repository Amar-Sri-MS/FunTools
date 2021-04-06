#! /usr/bin/env python3

import os
import sys
import textwrap

def print_b(name, byte_val):
    print("\nuint8_t %s[] =\n{" % name)
    c_bytes = ", ".join("0x%02X" % b for b in byte_val)
    print(textwrap.fill(c_bytes, 60))
    print("};")

def print_struct(name, p, q):
    p_name = name + "_p"
    q_name = name + "_q"
    print_b(p_name, p)
    print_b(q_name, q)
    print("\nstruct safe_prime %s = { sizeof(%s), %s, %s};" %
          (name, p_name, p_name, q_name))

for fname in sys.argv[1:]:
    p_b = open(fname, "rb"). read()
    p = int.from_bytes(p_b, 'big')
    q = (p - 1) // 2
    q_b = q.to_bytes(len(p_b), 'big')

    root = os.path.splitext(os.path.basename(fname))[0]
    print_struct(root, p_b, q_b)
