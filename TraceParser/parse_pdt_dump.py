#!/usr/bin/env python2.7

#
# Parses a dump of PDTrace data from a cluster.
#
# Supports output formats for the MIPS dequeuer as well as our own
# home-grown C version.
#
# Usage: parse_pdt_dump.py <input_file>
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import argparse
import binascii
import os
import subprocess
import tempfile

# Cluster ID is stored in 1 byte at the start of each file
CLUSTER_LEN = 1
# The width of the funnel in bytes, which dictates the frame length
PDT_FRAME_LEN = 32


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='path to input file')
    parser.add_argument('--output-dir', type=str,
                        help='path to output directory',
                        default='testoutput')
    parser.add_argument('--format', type=str,
                        help='dqr for MIPS dequer format,'
                             'trc for internal C tools format',
                        default='trc')
    args = parser.parse_args()

    if args.format == 'trc':
        _write_trc_file(args.input_file, args.output_dir)
    elif args.format == 'dqr':
        _write_dqr_file(args.input_file, args.output_dir)


def _write_trc_file(input_file, output_dir):
    with open(input_file, 'rb') as fh:
        cluster, contents = generate_trc_contents(fh)

    output_name = 'trc_%s.trc' % cluster
    output_path = os.path.join(output_dir, output_name)
    with open(output_path, 'wb') as fh:
        fh.write(contents)


def generate_trc_contents(fh):
    """
    Creates a string that is suitable as input to the C++ trace
    dequeuer.

    The C dequeuer expects a cluster id at the top, followed by
    a newline-separated sequence of 8-byte hex values (ASCII, not binary).

    Returns (cluster_id, content_string).
    """
    cluster_data = []
    cluster = _read_cluster(fh)

    # Gather cluster data.
    frame = fh.read(PDT_FRAME_LEN)
    while frame:
        cluster_data.extend(frame)
        frame = fh.read(PDT_FRAME_LEN)

    # Dump to a temp file and then hexdump it.
    fd, temp_path = tempfile.mkstemp('.rawbin', 'pdt')
    with os.fdopen(fd, 'wb') as temp_fh:
        temp_fh.write(''.join(cluster_data))
        temp_fh.flush()
    hexdump = subprocess.check_output(['xxd', '-ps', '-c', '8',
                                       temp_path])
    os.unlink(temp_path)

    result = 'cluster: %s\n\n' % cluster
    result += hexdump
    return cluster, result


def _write_dqr_file(input_file, output_dir):
    with open(input_file, 'rb') as fh:
        cluster = _read_cluster(fh)
        data = generate_dqr_contents(fh)

    out_filename = 'dqr_%s.rtd' % cluster
    out_filepath = os.path.join(output_dir, out_filename)
    with open(out_filepath, 'wb') as fh:
        fh.write(''.join(data))


def _read_cluster(fh):
    cluster = fh.read(CLUSTER_LEN)
    ascii_cluster = binascii.b2a_hex(cluster)
    return ascii_cluster


def generate_dqr_contents(fh):
    """
    Creates a byte array suitable as input to the Java MIPS dequeuer.

    The MIPS dequeuer expects a little-endian 4-byte frame index
    followed by a 32-byte frame containing data. The frame data is
    in big-endian order. All values are in binary.
    """
    data = []
    frame_num = 0

    frame = fh.read(PDT_FRAME_LEN)
    while frame:
        data.extend(_frame_to_bytes(frame_num))
        new_frame = _change_endianness(frame)
        data.extend(new_frame)
        frame_num = frame_num + 1
        frame = fh.read(PDT_FRAME_LEN)

    return data


def _frame_to_bytes(frame_num):
    frame_str = '%08x' % frame_num
    result = []
    for i in range(0, 4):
        ascii_byte = binascii.a2b_hex(frame_str[i*2:i*2+2])
        result.append(ascii_byte)

    return result


def _change_endianness(frame):
    """
    This reverses the 8-byte word order in a 32-byte frame.

    The dequeuer expects its traces in a big-endian order, where the
    first 8-byte word is at the end of the frame. That is the opposite
    of how we offload the words.
    """
    new_frame = frame[24:32] + frame[16:24] + frame[8:16] + frame[0:8]
    return new_frame


if __name__ == '__main__':
    main()

