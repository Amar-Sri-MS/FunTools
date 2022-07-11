#!/usr/bin/env python3

#
# Common utilities for parsing the header of a trace file.
#

import struct


# Magic bytes
MAGIC = b'\xca\xfe'
# Number of bytes in which the data type is stored
TYPE_LEN = 2


def get_trace_file_type(fh):
    """
    Reads 4 bytes from the file-like input, and determines if this is a valid
    trace file.

    Returns the type as an int, or None if this is an invalid trace.
    """
    magic = fh.read(2)
    if magic != MAGIC:
        print('Unrecognized magic header for trace file')
        return None

    type = struct.unpack('>H', fh.read(TYPE_LEN))[0]
    return type
