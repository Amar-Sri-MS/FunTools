#!/usr/bin/env python3

#
# Extracts instruction samples from raw data generated by FunOS instruction
# sampling.
#

import argparse
import json
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

    def process(self):
        code_line = addr2line(self.pc)
        if code_line is None:
            code_line = '<unknown>'

        va_line = addr2line(self.va)
        if va_line is None:
            va_line = '<unknown>'
        return ('pc: %016x (%s)\n'
                'va: %016x (%s)\n'
                'wu: %s vp: %d' % (self.pc, code_line, self.va,
                                   va_line, self.wu, self.vp))

    def __str__(self):
        if not self.is_valid():
            return 'invalid sample'

        return 'pc: %016x va: %016x cycles: %d wu: %s' % (self.pc,
                                                          self.va,
                                                          self.load_cycles,
                                                          self.wu)


def addr2line(addr):
    cmd = ['/Users/Shared/cross/mips64/bin/mips64-unknown-elf-addr2line',
           '-e', '/Users/jimmyyeap/Fun/FunOS/build/funos-f1',
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
    args = parser.parse_args()

    with open('wu_table.json', 'r') as jfh:
        js = json.load(jfh)
        wu_table = js['wu_table']

    with open(args.input_file, 'rb') as fh:
        parse_trace_record.drop_cluster_byte(fh)
        samples = read_file(fh, wu_table)
        sort_samples(samples)
        summarize_samples(samples)


def read_file(fh, wu_table):
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


def parse_pcssample(sample, pcssample):
    """
    compressed va is [61:0], where bits 57 and 58 have been omitted.
    """
    new_sample = (pcssample >> 63)
    if new_sample == 0:
        return

    va_56_downto_0 = pcssample & 0x1ffffffffffffff
    va_58_downto_57 = 0
    va_63_downto_59 = (pcssample >> 57) & 0x1f

    va = ((va_63_downto_59 << 59) |
          (va_58_downto_57 << 57) |
          (va_56_downto_0))

    sample.pc = va


def parse_pcsdataaddr(sample, pcsdataaddr):
    new_sample = (pcsdataaddr >> 63)
    if new_sample == 0:
        return

    va = pcsdataaddr & 0xffffffffffff
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
    new_sample = (pcscyclecounts >> 63)
    if new_sample == 0:
        return

    loadcycles = (pcscyclecounts >> 16) & 0x3ff
    completed = (pcscyclecounts >> 31) & 0x1

    sample.load_cycles = loadcycles
    sample.load_complete = (completed == 1)


def parse_wu(sample, dcid, wu_table):
    wuid = dcid & 0xffff
    sample.wu = 'missing'# wu_table[wuid]['name']


def sort_samples(samples):

    # python sorts are stable, so we use that to our advantage here to
    # do a three-level sort (first by pc, then by va, then by wu)
    samples.sort(key=lambda sample: sample.wu)
    samples.sort(key=lambda sample: sample.va)
    samples.sort(key=lambda sample: sample.pc)


def summarize_samples(samples):

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

    for t in summary:
        print(t[0].process())
        print('Average cycle count: %f Occurrences: %d' % (t[2], len(t[1])))
        print()

    return summary


if __name__ == '__main__':
    main()
