#!/usr/bin/env python3

#
# Parses perf trace record data from the trace demux.
#

import argparse
import collections
import os
import struct

from perf_sample import PerfSample


# Length of a trace record in bytes
TRACE_RECORD_LEN = 64

# Copy of constants in FunOS
TOPO_MAX_VPS_PER_CLUSTER = 24
TOPO_MAX_VPS_PER_CORE = 4
PERF_TOOL_ID = 4


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='path to input file')
    parser.add_argument('--output-dir', type=str,
                        help='path to output directory',
                        default='testoutput')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    with open(args.input_file, 'rb') as fh:
        generate_perfmon_files(fh, args.output_dir)


def generate_trace_record(fh):
    """
    Generator function that obtains the next trace record.

    Generates a tuple of (vpnum, record_bytes).
    """
    read_len = 1 + TRACE_RECORD_LEN
    record_bytes = fh.read(read_len)

    while record_bytes:
        yield record_bytes[0], record_bytes[1:]
        record_bytes = fh.read(read_len)


def decode_perf_sample(vpnum, record_bytes):
    """
    Converts a trace record into a perf sample.

    Returns None if the trace record is not a perf record.
    """
    tool, ts, cp0, wu, c0, c1, c2, c3, arg0 = struct.unpack('>B7xQ6LQ16x', record_bytes)
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


if __name__ == '__main__':
    main()
