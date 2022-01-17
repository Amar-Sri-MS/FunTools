#!/usr/bin/env python3

#
# Extracts instruction samples from raw data generated by FunOS instruction
# sampling.
#

import argparse
import json
import os
import struct
import subprocess
import traceback


import parse_trace_record


class Sample():
    """ An instruction sample """

    __slots__ = ['vp', 'pc', 'va', 'load', 'store',
                 'load_cycles', 'load_complete', 'wu']
    def __init__(self):
        self.vp = None
        self.pc = None
        self.va = None
        self.load = False
        self.store = False
        self.load_cycles = None
        self.load_complete = False
        self.wu = '<unknown>'

    def is_valid(self):
        return (self.pc is not None and
                self.va is not None and
                self.load_cycles is not None)

    def is_same(self, other):
        return (self.pc == other.pc and self.va == other.va and
                self.load == other.load and self.wu == other.wu)

    def to_cache_miss_format(self):
        """
        Returns a string representing an entry in a cache_miss.txt file.

        Note that information is lost: this needs to be fixed by changing
        the cache_miss file format.
        """
        s = 'load' if self.load else 'store'
        return '%016x    %016x    %s' % (self.pc, self.va, s)

    def to_debug_string(self):
        """
        Returns a human readable string about this sample:
        meant for debugging the parser.
        """
        code_line = addr2line(self.pc)
        if code_line is None:
            code_line = '<unknown>'

        va_line = addr2line(self.va)
        if va_line is None:
            va_line = '<unknown>'
        return ('pc: 0x%016x (%s)\n'
                'va: 0x%016x (%s)\n'
                'wu: %s vp: %d' % (self.pc, code_line, self.va,
                                   va_line, self.wu, self.vp))


def addr2line(addr):
    """ Only used for debugging the tool: not supported on all platforms """
    ws = os.environ['WORKSPACE']
    binary = os.path.join(ws, 'FunOS/build/funos-f1')

    cmd = ['/Users/Shared/cross/mips64/bin/mips64-unknown-elf-addr2line',
           '-e', binary,
           '-ip', '%s' % hex(addr)]
    try:
        out = subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        print(e.output)
        return None

    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='path to input file')
    parser.add_argument('--output-dir', type=str,
                        help='path to output directory',
                        default='testoutput')
    parser.add_argument('--debug', action='store_true',
                        help='Print sample summaries for debugging')
    args = parser.parse_args()

    wu_table = load_wu_table_if_present()

    with open(args.input_file, 'rb') as fh:
        parse_trace_record.drop_cluster_byte(fh)
        samples = read_samples_from_file(fh, wu_table)
        write_cache_miss_files(args.output_dir, samples)

        if args.debug:
            sort_samples(samples)
            summarize_samples(samples)


def load_wu_table_if_present():
    """
    Loads a WU table dict if the source file is available, otherwise returns
    an empty dict.
    """
    wu_table = {}

    if os.path.exists('wu_table.json'):
        with open('wu_table.json', 'r') as jfh:
            js = json.load(jfh)
            wu_table = js['wu_table']

    return wu_table


def read_samples_from_file(fh, wu_table):
    samples = []
    for _, record_bytes in parse_trace_record.generate_trace_record(fh):
        sample = construct_sample(record_bytes, wu_table)

        if sample.is_valid():
            samples.append(sample)

    return samples


def construct_sample(record_bytes, wu_table):
    tool, vp, pcssample, dcid, pcscyclecounts, pcsdataaddr = struct.unpack('>6xHQQQQQ16x', record_bytes)

    sample = Sample()
    sample.vp = vp
    parse_pcssample(sample, pcssample)
    parse_pcsdataaddr(sample, pcsdataaddr)
    parse_pcscyclecounts(sample, pcscyclecounts)
    parse_wu(sample, dcid, wu_table)

    return sample


#
# PCS sampling register constants.
# (see MIPS debug specification for details)
#
PCS_NEW_SHIFT = 63
PCS_COMPLETED_SHIFT = 62


def parse_pcssample(sample, pcssample):
    """
    compressed va is [61:0], where bits 57 and 58 have been omitted.
    """
    new_sample = (pcssample >> PCS_NEW_SHIFT)
    if new_sample == 0:
        return

    # TODO(jimmy): clarify meaning of this register bit
    completed = (pcssample >> PCS_COMPLETED_SHIFT) & 0x1
    if completed == 0:
        return

    va_56_downto_0 = pcssample & 0x1ffffffffffffff
    va_58_downto_57 = 0
    va_63_downto_59 = (pcssample >> 57) & 0x1f

    va = ((va_63_downto_59 << 59) |
          (va_58_downto_57 << 57) |
          (va_56_downto_0))

    sample.pc = va


def parse_pcsdataaddr(sample, pcsdataaddr):
    new_sample = (pcsdataaddr >> PCS_NEW_SHIFT)
    if new_sample == 0:
        return

    completed = (pcsdataaddr >> PCS_COMPLETED_SHIFT) & 0x1
    if completed == 0:
        return

    va = pcsdataaddr & 0xffffffffffff  # 48-bits
    miss = (pcsdataaddr >> 49) & 0x1
    load_store = (pcsdataaddr >> 48) & 0x1
    sample.load = (load_store == 0)
    sample.store = (load_store == 1)

    seg = (pcsdataaddr >> 60) & 0x3
    cca = (pcsdataaddr >> 57) & 0x7

    # xkphys
    if seg == 0x2:

        # Something's odd about the cca: it's always a reserved value 4 when
        # it should be 5 for cached, write-allocate accesses.
        if cca == 4:
            cca = 5
        seg_cca = seg << 3 | cca
    else:
        seg_cca = seg << 3

    va = (seg_cca << 59 | va)
    sample.va = va


def parse_pcscyclecounts(sample, pcscyclecounts):
    new_sample = (pcscyclecounts >> PCS_NEW_SHIFT)
    if new_sample == 0:
        return

    loadcycles = (pcscyclecounts >> 16) & 0x7fff
    completed = (pcscyclecounts >> 31) & 0x1

    sample.load_cycles = loadcycles
    sample.load_complete = (completed == 1)


def parse_wu(sample, dcid, wu_table):
    wuid = dcid & 0xffff
    if wu_table:
        sample.wu = wu_table[wuid]['name']
    else:
        sample.wu = 'missing'


def write_cache_miss_files(dir, samples):
    """ Write the raw cache miss files for missmap, one per core """

    samples.sort(key=lambda sample: sample.vp)

    curr_cluster = 0
    curr_core = 0
    samples_this_cc = []

    os.makedirs(dir, exist_ok=True)

    for s in samples:
        cl = s.vp // parse_trace_record.TOPO_MAX_VPS_PER_CLUSTER
        offset = s.vp % parse_trace_record.TOPO_MAX_VPS_PER_CLUSTER
        co = offset // parse_trace_record.TOPO_MAX_VPS_PER_CORE

        if cl == curr_cluster and co == curr_core:
            samples_this_cc.append(s.to_cache_miss_format())
        else:
            write_samples_to_file(curr_cluster, curr_core, dir, samples_this_cc)

            samples_this_cc = [s.to_cache_miss_format()]
            curr_cluster = cl
            curr_core = co

    write_samples_to_file(cl, co, dir, samples_this_cc)


def write_samples_to_file(curr_cluster, curr_core, dir, samples_this_cc):
    """ Write a single cache miss file """
    if not samples_this_cc:
        return

    fname = os.path.join(dir, 'cache_miss_%d_%d.txt' % (curr_cluster,
                                                        curr_core))
    with open(fname, 'w') as f:
        f.write('\n'.join(samples_this_cc))
        f.write('\n')


def sort_samples(samples):

    # python sorts are stable, so we use that to our advantage here to
    # do a three-level sort (first by pc, then by va, then by wu)
    samples.sort(key=lambda sample: sample.wu)
    samples.sort(key=lambda sample: sample.va)
    samples.sort(key=lambda sample: sample.pc)


def summarize_samples(samples):
    """ Print a debug summary of all samples """

    if not samples:
        return

    curr = samples[0]
    cycles = [samples[0].load_cycles]
    summary = []

    # walk through each sample and group
    for i in range(1, len(samples)):
        if curr.is_same(samples[i]):
            cycles.append(samples[i].load_cycles)
        else:
            avg = sum(cycles) / len(cycles)
            summary.append((curr, cycles, avg))

            curr = samples[i]
            cycles = [samples[i].load_cycles]

    avg = sum(cycles) / len(cycles)
    summary.append((curr, cycles, avg))

    # sort by average
    summary.sort(key=lambda t : t[2], reverse=True)

    for s in summary:
        print(s[0].to_debug_string())
        print('Average cycle count: %f Occurrences: %d' % (s[2], len(s[1])))
        print(s[1])
        print()


if __name__ == '__main__':
    main()