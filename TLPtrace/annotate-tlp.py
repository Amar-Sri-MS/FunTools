#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Annotate Palladium TLP trace files.

PCIe Transaction Layer Protocol (TLP) packets are the L2 protocol
packets that transit a PCIe tree. In Palladium emulation it is
possible to capture a log file contain the TLPs that move through
various parts of the system. This program adds annotations to these
log files to make it easier to understand the contents of the TLPs.

The first three or four DW are decoded, the rest of the text of the
TLP trace is emitted unchanged.

"""

import argparse
import re
from typing import Tuple

###
##  parse_args
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("tlp_file",
                        type=argparse.FileType('rt', bufsize=1),
                        help="TLP transaction log to parse")

    args: argparse.Namespace = parser.parse_args()
    return args

def decode_dw0(dw0: int) -> Tuple[str, int, bool, bool]:
    words = 3
    fmt = (dw0 >> 29) & 7
    type = (dw0 >> 24) & 0x1f
    length = dw0 & 0x3ff
    fmt_str = 'Unknown Format'
    type_str = ', Unknown Type'
    has_data = False
    is_completion = False
    is_config = False
    if fmt == 0:
        fmt_str = '3-DW No Data'
        if type == 0:
            type_str = ', MRd'
        elif type == 1:
            type_str = ', MRdLk'
        elif type == 2:
            type_str = ', IORd'
        elif type == 4:
            type_str = ', CfgRd0'
            is_config = True
        elif type == 5:
            type_str = ', CfgRd1'
            is_config = True
        elif type == 10:
            type_str = ', Cpl'
            is_completion = True
        elif type == 11:
            type_str = ', CplLk'
            is_completion = True
    elif fmt == 1:
        fmt_str = '4-DW No Data'
        if type == 0:
            type_str = ', MRd'
        elif type == 1:
            type_str = ', MRdLk'
        elif (type & 0x18) == 0x10:
            type_str = ', Msg'
        words = 4
    elif fmt == 2:
        fmt_str = '3-DW With Data'
        if type == 0:
            type_str = ', MWr'
        elif type == 2:
            type_str = ', IOWr'
        elif type == 4:
            type_str = ', CfgWr0'
            is_config = True
        elif type == 5:
            type_str = ', CfgWr1'
            is_config = True
        elif type == 10:
            is_completion = True
            type_str = ', CplD'
        elif type == 11:
            type_str = ', CplDLk'
            is_completion = True
        has_data = True
    elif fmt == 3:
        fmt_str = '4-DW With Data'
        if type == 0:
            type_str = ', MWr'
        elif (type & 0x18) == 0x10:
            type_str = ', MsgD'
        words = 4
        has_data = True
    elif fmt == 4:
        fmt_str = 'TLP Prefix'
    if has_data:
        if length == 0:
            length = 1024
        length_str = ', len: %d DW' % length
    else:
        length_str = ''
    return fmt_str + type_str + length_str, words, is_completion, is_config

def decode_completion_status(status: int) -> str:
    if status == 0:
        return 'SC'
    elif status == 1:
        return 'UR'
    elif status == 2:
        return 'CRS'
    elif status == 4:
        return 'CA'
    else:
        return 'Reserved Status'

def decode_dw1(dw1: int, is_completion: bool) -> str:
    if (is_completion):
        cid = (dw1 >> 16) & 0xffff
        status = (dw1 >> 13) & 7
        byte_count = dw1 & 0xfff
        return ' CID: %08x, Status: %s, Byte Count %d' % (cid, decode_completion_status(status), byte_count)
    else:
        rid = (dw1 >> 16) & 0xffff
        tag = (dw1 >> 8) & 0xff
        lbe = (dw1 >> 4) & 0xf
        fbe = dw1 & 0xf
        return ' RID: %08x, Tag: %04x, LBE: %x, FBE: %x' % (rid, tag, lbe, fbe)

def decode_dw2(dw2: int, is_completion: bool, is_config: bool, header_len: int) -> str:
    if (is_completion):
        rid = (dw2 >> 16) & 0xffff
        tag = (dw2 >> 8) & 0xff
        la = dw2 & 0x7f
        return ' RID: %08x, Tag: %04x, LA: %x' % (rid, tag, la)
    elif is_config:
        bus = (dw2 >> 24) & 0xff
        dev = (dw2 >> 19) & 0x1f
        fn = (dw2 >> 16) & 7
        reg = dw2 & 0xfff
        return ' %d:%d.%d, Reg: %03x' % (bus, dev, fn, reg)
    else:
        return ' AddrLo: %08x' % dw2

def decode_dw3(dw3: int, is_completion: bool, is_config: bool, header_len: int) -> str:
    if not is_completion and not is_config and header_len == 4:
        return ' AddrHi: %08x' % dw3
    else:
        return ''

###
##  main
#
def main() -> int:
    dw0_expr = re.compile(r'(^.*)\sTLP-DW0 = ([0-9a-fA-F]{8}).*')
    dwX_expr = re.compile(r'(^.*)(TLP-DW([1-9])) = ([0-9a-fA-F]{8}).*')

    args: argparse.Namespace = parse_args()
    #print("hello world", args.tlp_file.readline())
    in_completion = False
    in_config = False
    logfile = args.tlp_file;
    while True:
        line = logfile.readline()
        if ('' == line):
            break
        line = line.rstrip()
        dw0_match = dw0_expr.fullmatch(line)
        if dw0_match:
            dw0_str = dw0_match.group(2)
            dw0 = int(dw0_str, 16)
            print(dw0_match.group(1).rstrip())
            (desc, header_len, in_completion, in_config) = decode_dw0(dw0)
            print('TLP-DW0 = ' + dw0_str + ' ' + desc)
            continue
        dwX_match = dwX_expr.fullmatch(line)
        if dwX_match:
            dwX_str = dwX_match.group(4)
            dwX = int(dwX_str, 16)
            dwX_desc = ''
            dw_number = int(dwX_match.group(3))
            if dw_number == 1:
                dwX_desc = decode_dw1(dwX, in_completion)
            elif dw_number == 2:
                dwX_desc = decode_dw2(dwX, in_completion, in_config, header_len)
            elif dw_number == 3:
                dwX_desc = decode_dw3(dwX, in_completion, in_config, header_len)
            print(dwX_match.group(2) + ' = ' + dwX_str + dwX_desc)
            continue
        print(line)
    return 0

###
##  entrypoint
#
if __name__ == "__main__":
    main()
