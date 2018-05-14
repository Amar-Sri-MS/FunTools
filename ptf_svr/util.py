#!/usr/bin/env python
#
#  util.py
#
#  Created by eddie.ruan@fungible.com on 2018 05-11
#
#  Copyright 2018 Fungible Inc. All rights reserved.
#

#
# Convert Raw Packet from ASCII byte string to hex encoding String
# Example: input packet would change to forwar
# 00 DE AD BE EF 00 FE DC BA 44 55 77 08 00 45 00 00 BA
# 00 69 00 00 40 06 62 D2 01 01 01 01 14 01 01 01 04 D2
# 00 50 00 00 00 00 00 00 00 00 50 02 20 00 D6 45 00 00
# ...
#
def pkt_encode(src):
    chars = src[0:len(src)]
    hex = ' '.join(["%02X"% ord(x) for x in chars])
    return hex

#
# Convert hex encoding String back to raw packet
#
def pkt_decode(src):
    chars = src.split()
    ret = bytearray()
    for x in chars:
        x='0x'+x
        i = int(x, 16)
        ret.append(i)
    final="".join(map(chr, ret))
    return final
