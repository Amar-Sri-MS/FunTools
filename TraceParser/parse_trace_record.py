#!/usr/bin/env python3

#
# Parses a dump of trace record data.
#
# Usage: parse_trace_record_dump.py <input_file>
#
# Copyright (c) 2021 Fungible Inc.  All rights reserved.
#

import argparse
import binascii
import collections
import os
import struct

import csi_trace
import csi_types
from perf_sample import PerfSample


# Cluster ID is stored in 1 byte
CLUSTER_LEN = 1

# Length of a trace record in bytes
TRACE_RECORD_LEN = 64
# Length of a trace page in bytes
TRACE_PAGE_LEN = 16384

# Copy of constants in FunOS
TOPO_MAX_VPS_PER_CLUSTER = 24
TOPO_MAX_VPS_PER_CORE = 4
PERF_TOOL_ID = 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='path to input file')
    parser.add_argument('--output-dir', type=str,
                        help='path to output directory',
                        default='testoutput')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    with open(args.input_file, 'rb') as fh:
        if not verify_trace_file(fh):
            print('Problems reading trace file %s')
            return
        drop_cluster_byte(fh)
        generate_perfmon_files(fh, args.output_dir)


def generate_trace_record(fh):
    """
    Generator function that obtains the next trace record.

    Generates a tuple of (vpnum, record_bytes).
    """
    page_bytes = fh.read(TRACE_PAGE_LEN)
    pos = 0

    while page_bytes:
        header = page_bytes[0:TRACE_RECORD_LEN]
        num_records, vpnum = struct.unpack('>H4xH56x', header)
        if num_records == 0:
            # Empty trace page, skip
            page_bytes = fh.read(TRACE_PAGE_LEN)
            pos += TRACE_PAGE_LEN
            continue

        for i in range(1, num_records + 1):
            record_bytes = page_bytes[i*TRACE_RECORD_LEN:(i+1)*TRACE_RECORD_LEN]
            if not record_bytes:
                print('Problem reading record at pos %d' % pos)
                raise RuntimeError()
            yield vpnum, record_bytes

        page_bytes = fh.read(TRACE_PAGE_LEN)
        pos += TRACE_PAGE_LEN


def decode_perf_sample(vpnum, record_bytes):
    """
    Converts a trace record into a perf sample.

    Returns None if the trace record is not a perf record.
    """
    tool, ts, cp0, wu, c0, c1, c2, c3, arg0 = struct.unpack('>6xHQ6LQ16x', record_bytes)
    if tool != PERF_TOOL_ID:
        return None

    sample = PerfSample()
    sample.wuid = wu
    sample.arg0 = arg0
    sample.timestamp = ts
    sample.cp0_count = cp0
    sample.perf_counts = [c0, c1, c2, c3]
    sample.vp = vpnum
    return sample


def generate_perfmon_files(in_fh, output_dir):
    """
    Creates the raw perfmon files that are required by perf.
    """
    samples_by_cc = collections.defaultdict(list)

    for vpnum, record_bytes in generate_trace_record(in_fh):
        cluster = vpnum / TOPO_MAX_VPS_PER_CLUSTER
        vp_cluster_offset = vpnum % TOPO_MAX_VPS_PER_CLUSTER
        core = vp_cluster_offset / TOPO_MAX_VPS_PER_CORE

        perf_sample = decode_perf_sample(vpnum, record_bytes)
        if perf_sample:
            samples_by_cc[(cluster, core)].append(perf_sample)

    for cc in samples_by_cc:
        write_perfmon_file(output_dir, cc, samples_by_cc[cc])


def write_perfmon_file(output_dir, cc, samples):
    """
    Writes the perf samples to disk
    """
    fname = os.path.join(output_dir, 'put_%d_%d_perfmon.txt' % cc)
    with open(fname, 'w') as ofh:
        for s in samples:
            sample_data = s.to_perfmon_data()
            perfmon_sample = [format(d, '016x') for d in sample_data]
            ofh.write('\n'.join(perfmon_sample))
            ofh.write('\n')


def drop_cluster_byte(fh):
    """ Read and drop the (unused) cluster byte. """
    cluster = fh.read(CLUSTER_LEN)
    ascii_cluster = binascii.b2a_hex(cluster)
    return ascii_cluster


def verify_trace_file(fh):
    """ Ensures that the trace file holds trace records """
    type = csi_trace.get_trace_file_type(fh)
    if type != csi_types.CSI_TRACE_RECORD:
        print('Cannot decode: not a trace record file')
        return False

    return True


if __name__ == '__main__':
    main()
