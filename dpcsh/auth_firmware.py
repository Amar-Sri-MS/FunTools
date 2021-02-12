#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify a Fungible signed firmware image

Read a few fields from the image header, and then run the SHA512 hash
over the protected content.  Verify that the hash matches the
signature block in the image by sending the signature, key-index and
SHA512 to the SBP via DPC.

Exit with 0 if the SHA512 is good, otherwise exit with 1.

If -o is specified, the authenticated image is written to the named file.

"""

from typing import List, Optional, Type, Dict, Any, Tuple
import argparse
import struct
import sys
import hashlib
import json

import dpc_client

FW_IMAGE_KEY_INDEX_OFF: int = 0x800
FW_IMAGE_SIG_SIZE_OFF: int =  0xdfc
FW_IMAGE_SIG_OFF: int =  0xe00
FW_IMAGE_SIGNED_DATA_OFF: int =  0x1000

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("file", type=argparse.FileType('rb'), help="Input file")

    parser.add_argument("-o", "--out-file", type=argparse.FileType('wb'), help="Output file")

    parser.add_argument("-u", "--unix", action='store_true', help="Use unix domain socket for communication with dpc server")

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")

    args: argparse.Namespace = parser.parse_args()
    return args

def main() -> None:
    args: argparse.Namespace = parse_args()
    ifile = args.file;
    ofile = args.out_file;
    v = args.verbose;

    ifile.seek(FW_IMAGE_KEY_INDEX_OFF)
    ki_raw = ifile.read(4)
    (ki, fill, ki_tag) = struct.unpack('<HBB', ki_raw)
    if (ki_tag != 0x80):
        print("Invalid Key Index tag: %x" % ki_tag)
        sys.exit(1)

    if (v):
        print("Key Index %d" % ki)

    ifile.seek(FW_IMAGE_SIG_SIZE_OFF)
    sig_size_raw = ifile.read(4)
    sig_size = struct.unpack('<I', sig_size_raw)[0]
    if (v):
        print("signature size %d" % sig_size)
    if (sig_size != 256):
        print("Invalid signature size: %d" % sig_size)
        sys.exit(1)

    ifile.seek(FW_IMAGE_SIG_OFF)
    sig_raw = ifile.read(sig_size)

    hash = hashlib.sha512()

    ifile.seek(FW_IMAGE_SIGNED_DATA_OFF)
    payload_size_raw = ifile.read(4)
    hash.update(payload_size_raw)
    payload_size = struct.unpack('<I', payload_size_raw)[0]

    payload_version_raw = ifile.read(4)
    hash.update(payload_version_raw)
    payload_version = struct.unpack('<I', payload_version_raw)[0]

    payload_4cc_raw = ifile.read(4)
    hash.update(payload_4cc_raw)
    (payload_4cc0, payload_4cc1, payload_4cc2, payload_4cc3) = struct.unpack('BBBB', payload_4cc_raw)

    if (v):
        print("Size: %d, Version: %d, 4cc: [%c%c%c%c]" %
              (payload_size, payload_version, payload_4cc0, payload_4cc1, payload_4cc2, payload_4cc3))

    signed_attr_raw = ifile.read(64)
    hash.update(signed_attr_raw)

    current_pos = 0;
    while (current_pos < payload_size):
        nread = min(0x10000, payload_size - current_pos)
        seg = ifile.read(nread)
        hash.update(seg)
        if (ofile):
            ofile.write(seg)
        current_pos += len(seg)

    if (ofile):
        ofile.close()

    client = dpc_client.DpcClient(legacy_ok = False, unix_sock = args.unix)
    params = {'key_id' : ki, 'signature': list(sig_raw), 'sha512': list(hash.digest())}
    verify_cmd = ['rsa_verify_hash', params]

    ret = client.execute('pke', verify_cmd)

    if (v):
        print("returns:" + str(ret))

    if (v > 1):
        print("pke rsa_verify_hash " + json.dumps(params))

    if (ret):
        sys.exit(0)
    else:
        sys.exit(1)

###
##  entrypoint
#
if __name__ == "__main__":
    main()
