#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Convert Fungible UART log output with intermingled packet data dumps
# to PCAP format for analysis in Wireshark.
#
#
#
# Sample log looks like:
# .
# .
# .
# [333.376496 8.0.0] RX(0,60): ff ff ff ff ff ff 00 04-96 8b de 78 08 06 00 01
# [333.376519 8.0.0] RX(16,60): 08 00 06 04 00 01 00 04-96 8b de 78 0a 01 6a 0a
# [333.376539 8.0.0] RX(32,60): 00 00 00 00 00 00 0a 01-6a 14 00 00 00 00 00 00
# [333.376559 8.0.0] RX(48,60): 00 00 00 00 00 00 00 00-00 00 00 00 2f c5 97 1c
# .
# .
# .
#
import argparse
import re
import array
import struct
from typing import Dict, ClassVar, Optional, BinaryIO

snaplen: int = 65535

class Packet:
    total_len: int
    data_len: int
    sec: int
    micro: int
    data: bytearray
    complete: bool
    string_splitter: ClassVar[re.Pattern] = re.compile(r'[ -]+')

    def __init__(self, total_len: int, sec: int, micro: int) -> None:
        self.total_len = total_len
        self.sec = sec
        self.micro = micro
        self.data = bytearray(total_len)
        self.data_len = 0
        self.complete = False

    def add_bytes(self, index: int, byte_string: str, sec: int, micro: int) -> None:
        self.sec = sec
        self.micro = micro
        elts = self.string_splitter.split(byte_string)
        while index < self.total_len and elts:
            elt = elts.pop(0)
            self.data[index] = int(elt, 16)
            index += 1
        self.data_len = index
        if (index == self.total_len):
            self.complete = True

    def write_pcap(self, f: BinaryIO) -> None:
        f.write(struct.pack('<I', self.sec))
        f.write(struct.pack('<I', self.micro))
        f.write(struct.pack('<I', self.data_len))
        f.write(struct.pack('<I', self.total_len))
        f.write(self.data[0:self.data_len])

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("in_file", type=argparse.FileType('r'), help="input file")
    parser.add_argument("out_file", type=argparse.FileType('wb'), help="output pcap file")
    args = parser.parse_args()

    matcher = re.compile(r'^\[(\d+)\.(\d+) (\d\.\d\.\d)\].*(RX|TX|Send)\((\d+)[,/](\d+)\): ([^"]*)')

    src = args.in_file
    dst = args.out_file
    current_packets: Dict[str,Packet] = {}
    packet_count = 0

    # Write PCAP header
    dst.write(struct.pack('<I', 0xa1b2c3d4)) # magic_number
    dst.write(struct.pack('<HH', 2, 4)) # version_major, version_minor
    dst.write(struct.pack('<i', 0)) # thiszone
    dst.write(struct.pack('<I', 0)) # sigfigs
    dst.write(struct.pack('<I', snaplen)) # snaplen
    dst.write(struct.pack('<I', 1)) # network: 1-Ethernet


    # Find and write out packets
    for line in src:
        m = matcher.match(line)
        if m:
            sec = int(m.group(1))
            micro = int(m.group(2))
            vp = m.group(3)
            start = int(m.group(5))
            total = int(m.group(6))
            data = m.group(7).strip()

            current_packet: Optional[Packet] = current_packets.get(vp)
            if start == 0:
                if (current_packet):
                    current_packet.write_pcap(dst)
                    packet_count += 1
                current_packet = Packet(min(total, snaplen), sec, micro)
                current_packets[vp] = current_packet
            if (current_packet):
                current_packet.add_bytes(start, data, sec, micro)
                if (current_packet.complete):
                    current_packet.write_pcap(dst)
                    packet_count += 1
                    current_packet = None
                    del current_packets[vp]

    if (current_packet):
        current_packet.write_pcap(dst)
        packet_count += 1

    dst.close()
    src.close()

    print(f"Wrote {packet_count} packets")
    return 0

###
## entrypoint
#
if __name__ == "__main__":
    main()
