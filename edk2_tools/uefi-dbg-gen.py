#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""uefi-dbg-gen.py

Generate GDB add-symbol-file commands derived from EDK2 "Loading driver" debug messages.

For each loaded .EFI image we use the peinfo helper program to find
the virtual address of the module. The virtual address is added to the
load address to specify the GDB add-symbol-file location of the
corresposning .debug image (which is an ELF file that GDB can consume)


static check:
% mypy uefi-dbg-gen.py

"""
import argparse
import os.path
import re
import subprocess
import sys
from typing import List, Optional, Type, Dict, Any, Tuple

line_splitter = re.compile(r'\n')
va_pattern = re.compile(r'^VirtualAddress: (0x[0-9A-Fa-f]+)')

def gen_one_cmd(args: argparse.Namespace, name: str, loc: str) -> str:
    efi_path = os.path.join(args.exe_dir, "%s.%s" % (name, "efi"))
    debug_path = os.path.join(args.exe_dir, "%s.%s" % (name, "debug"))
    peinfo = subprocess.run([args.peinfo, efi_path], stdout = subprocess.PIPE);
    peinfo_lines = line_splitter.split(peinfo.stdout.decode())

    found_text = False
    for pi_line in peinfo_lines:
        if (pi_line == "Name: .text"):
            found_text = True
            continue
        if (found_text):
            va_match = va_pattern.match(pi_line)
            if (va_match):
                va = va_match.group(1)
                dbg_loc = int(loc, 0) + int(va, 0)
                dest = sys.stdout
                if (args.output):
                    dest = args.output
                print("add-symbol-file %s %s" % (debug_path, hex(dbg_loc)), file=dest)
                break

    return efi_path

###
##  parse_args
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument('-P', '--peinfo', default = "peinfo", help = "peinfo executable helper program");

    parser.add_argument('-d', '--exe-dir', required = True, help = "Directory containing EFI and debug images");

    parser.add_argument('-o', '--output', type=argparse.FileType('w'), help = "GDB script output file");

    # Required positional argument
    parser.add_argument("logfile", type=argparse.FileType('r'), help = "Logfile to parse")


    args: argparse.Namespace = parser.parse_args()
    return args

###
##  main
#
def main() -> int:
    load_pattern = re.compile(r'^Loading driver at (0x[0-9A-Fa-f]+) EntryPoint=\S+ (\S+).efi')
    load_dxecore_pattern = re.compile(r'^Loading (DxeCore) at (0x[0-9A-Fa-f]+) EntryPoint=\S+')

    args = parse_args()

    f = args.logfile

    for line in f:
        m_load = load_pattern.match(line)
        m_dxecore = load_dxecore_pattern.match(line)
        if (m_load):
            print("File %s -> %s" % (m_load.group(2), m_load.group(1)))
            gen_one_cmd(args, m_load.group(2), m_load.group(1))
        if (m_dxecore):
            print("File %s -> %s" % (m_dxecore.group(1), m_dxecore.group(2)))
            gen_one_cmd(args, m_dxecore.group(1), m_dxecore.group(2))

    return 0

##
##  entrypoint
#
if __name__ == "__main__":
    main()
