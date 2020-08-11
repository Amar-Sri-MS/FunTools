#!/usr/bin/env python3
# Copyright (c) 2019 Fungible,inc. All Rights reserved.
#

import argparse
import struct
import sys
import firmware_signing_service as fss


NUM_MAX_KEYS_IN_BAG = 96
OFFSET_ENTRY_SIZE = 2   # offset are stored as 2 bytes -- number of 32 bit words

def round_up_32(v):
    return (v + 3) & ~3



def write_modulus(f, header_size, index, modulus):
    ''' writes the modulus at the current location, rounded up to multiple
    of 4 after updating the index array, leaves the file ptr at next
    available location for next iteration '''
    # where is the modulus written? must be a multiple of 4
    where_pos = round_up_32(f.tell())

    # write position of this key in the header (2 bytes only: 32 bits word units)
    f.seek(header_size + OFFSET_ENTRY_SIZE * index)
    f.write(struct.pack('<H', int(where_pos/4)))

    f.seek(where_pos)
    # write the modulus preceded by length -- canonical format
    f.write(struct.pack('<I', len(modulus)))
    f.write(modulus)


def create(output, keys):
    if len(keys) > NUM_MAX_KEYS_IN_BAG:
        print("No file created: too many keys specified {0}, max is {1}".
              format(len(keys), NUM_MAX_KEYS_IN_BAG))
        return False

    with open(output, "wb") as f:
        f.write(bytearray([0, len(keys), 0, 0]))  # version, number of keys, padding
        header_size = f.tell()

        # where the keys are written: version, number of keys, and offset (2 bytes) array
        # position the file ptr at the start of data
        data_start = header_size  + OFFSET_ENTRY_SIZE * len(keys)
        f.seek(data_start)

        for i, key in enumerate(keys):
            write_modulus(f, header_size, i, fss.get_modulus(key))

    return True


def main():
    parser = argparse.ArgumentParser(description="Create keys bag")

    parser.add_argument("file", help="file to create", metavar="FILE")
    parser.add_argument('key_names', nargs=argparse.REMAINDER,
                        help='A list of key names to put into the key bag')
    args = parser.parse_args()

    return create(args.file, keys=args.key_names)

if __name__ == "__main__":
    sys.exit(main())
