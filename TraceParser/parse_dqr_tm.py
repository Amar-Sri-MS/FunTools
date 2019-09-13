#!/usr/bin/env python2.7

#
# Parses MIPS dequeuer trace message output.
#
# Produces output suitable for perf or cache miss tracing, depending
# on provided arguments to the script.
#
# Usage: parse_dqr_tm.py -h for help
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import argparse
import json
import os
import platform
import re
import subprocess
import select
import tr_formats

MAX_VPS_PER_CORE = 4
MAX_VPS_PER_CLUSTER = 24

###
##  Module exports
#

# cache of addr2line processes, indexed by path name
A2LPROC = {}

def _run_addr2line(funos_binary_path):
    """
    Make an addr2line process we can talk to via stdin/stdout
    """

    current_os = platform.system()
    if current_os == 'Darwin':
        addr2line_tool = ('/Users/Shared/cross/mips64/binutils-2.31/bin/'
                          'mips64-unknown-linux-addr2line')
    else:
        addr2line_tool = ('/opt/cross/mips64/bin/'
                          'mips64-unknown-elf-addr2line')

    cmd_array = [addr2line_tool,
                 '-e',
                 funos_binary_path,
                 '-a',
                 '-p',
                 '-i',
                 '-f']
  
    try:
        proc = subprocess.Popen(cmd_array,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print 'Failed to run addr2line: code %d msg %s' % (e.returncode,
                                                           e.message)
        proc = None

    return proc

DONEADDR = "0xabcdef"
DONELINE = "0x0000000000abcdef: ?? ??:0\n"

def do_addr2line(proc, addrs):

    lines = []

    for addr in addrs:
        # drain any existing output
        # print "selecting"
        while (select.select([proc.stdout],[],[],0)[0]!=[]):
            # print "reading"
            s = proc.stdout.readline()
            # print "read: %s" % s.strip()
            lines.append(s)

        # send more input
        s = "0x%016x\n" % addr
        # print "write: %s" % s.strip()
        proc.stdin.write(s)

    # send a finish token
    proc.stdin.write("%s\n" % DONEADDR)
    proc.stdin.flush()
    
    # drain everyting left
    while True:
        line = proc.stdout.readline()
        # print "read: %s" % line.strip()
        if (line == DONELINE):
            break
        lines.append(line)

    return lines
            
def raw_addr2line(addrs, funos_binary_path):
    """
    Runs MIPS addr2line on the list of provided addresses and returns
    the text output containing address and function names, and keep
    the process lying around for more
    """

    if (A2LPROC.get(funos_binary_path) is None):
        proc = _run_addr2line(funos_binary_path)
        assert (proc is not None)
        A2LPROC[funos_binary_path] = proc
    
    output = do_addr2line(A2LPROC[funos_binary_path], addrs)
        
    return output


# Attempts to match lines that look like:
#
# 0xa800000000427658: /funos/platform/include/platform/lock.h:62
# 0xa800000000427558: /funos/platform/mips64/bzero.c:58 (discriminator 1)
START_RE = "(0x[0-9a-f]+):(.*:[0-9\?]+( \(discriminator \d+\))?\n)"
NOINFO = " ?? ??:0\n"


def parse_next_addr(lines, addrs):

    line = lines.pop(0)
    m = re.match(START_RE, line)
    if (m is None):
        raise RuntimeError("failed to match address line on '%s'" % line)
    addr = int(m.group(1),16)
    info = [m.group(2)]
    
    while (len(lines) > 0):
        if (re.match(START_RE, line[0]) is not None):
            break
        line = lines.pop(0)
        info.append(line)

    if ((len(info) == 1) and(info[0] == NOINFO)):
        # not a valid code address
        addrs[addr] = None
    else:
        addrs[addr] = info
    
    return lines

def parsed_addr2line(addrs, funos_binary):

    ret = {}
    
    # get all the input
    lines = raw_addr2line(addrs, funos_binary)

    # parse it
    while (len(lines)):
        lines = parse_next_addr(lines, ret)
    
    return ret
    
###
##  Classes
#


class PerfParser:
    """
    Parses the dequeuer trace for trace messages which represent
    perf samples.

    TODO: consider changing the input to work on frame objects
    """

    # Parser state identifiers. Python 2.7 does not have enum types.
    TMOAS = 'tmoas'
    TPC = 'tpc'
    WORD0 = 'word0'
    WORD1 = 'word1'
    WORD2 = 'word2'
    WORD3 = 'word3'
    WORD4 = 'word4'

    # Various bit shifts and masks to extract data from trace.
    VP_MASK = 0x3

    def __init__(self, cluster, core):
        self.frames = []
        self.samples = []
        self.cluster = cluster
        self.core = core
        self.fr_idx = 0
        self.tf_idx = 0
        self.fr_valid = True
        self.overflow_frames = []

    def parse_trace_messages(self, fh):
        self.frames = parse_and_group_trace_formats(fh)

        # The sequence we are looking for is:
        # word0 = TF3 (TU2): timestamp[53:0], arg0[63:56], vp[1:0]
        # word1 = TF3 (TU1): arg0[55:0], zero[5:0], vp[1:0]
        # word2 = TF3 (TU1): perf_cnt0[31:0], zero[13:0], wuid[15:0], vp[1:0]
        # word3 = TF3 (TU1): perf_cnt1[29:0], perf_cnt2[31:0], vp[1:0]
        # word4 = TF3 (TU1): perf_cnt3[29:0], cp0_count[31:0], vp[1:0]
        #
        # The header is a timestamp, which is of type TU2 instead of
        # TU1. This allows recovery from overflow frames where traces
        # are lost.
        #
        # This part of the code is written like a finite state automaton
        # which processes each trace format in turn. State is maintained
        # per-VP.

        state = [PerfParser.WORD0] * MAX_VPS_PER_CORE
        next_state = [PerfParser.WORD0] * MAX_VPS_PER_CORE
        sample_builder = [None] * MAX_VPS_PER_CORE

        while self.fr_idx != len(self.frames):
            frame = self.frames[self.fr_idx]
            tf = frame.tfs[self.tf_idx]

            # If this frame has an overflow message we need to ignore all
            # entries until we find a TMOAS-TPC pair, which indicates tracing
            # has restarted (this is documented in MIPS PDTrace).
            #
            # Because overflow drops an unknown number of traces we reset all
            # states: there is no way to recover partial perf samples.
            if frame.overflow:
                state = [PerfParser.TMOAS] * MAX_VPS_PER_CORE
                self.fr_valid = False
                if (not self.overflow_frames or
                        self.overflow_frames[-1] != self.fr_idx):
                    self.overflow_frames.append(self.fr_idx)

            # Skip trace formats if the frame is marked as invalid. At the
            # end of frame we reset the status to valid.
            if not self.fr_valid:
                self._advance_tf()
                continue

            # This block handles the recovery states after overflow.
            #
            # All VP states must agree that they're looking for TMOAS-TPC, so
            # we only need to check VP 0
            if state[0] == PerfParser.TMOAS:
                if tr_formats.is_tmoas(tf):
                    state = [PerfParser.TPC] * MAX_VPS_PER_CORE
                self._advance_tf()
                continue
            elif state[0] == PerfParser.TPC:
                if tr_formats.is_tpc(tf):
                    state = [PerfParser.WORD0] * MAX_VPS_PER_CORE
                self._advance_tf()
                continue

            # The following code handles normal operation where we build up
            # perf samples per-VP.
            #
            # If this is not a valid TU2 or TU1 format skip it. The most
            # common reason for this is the TMOAS format, which also shows up
            # on processor mode changes.
            if not tr_formats.is_tu1(tf) and not tr_formats.is_tu2(tf):
                self._advance_tf()
                continue

            # Extract the VP from the data because pdtrace hardware seems
            # to give bogus vpid values. Sigh.
            vp = tf.addr & self.VP_MASK

            if state[vp] == PerfParser.WORD0:
                if tr_formats.is_tu2(tf):
                    sample_builder[vp] = PerfSampleBuilder(vp)
                    sample_builder[vp].add_tf(tf)
                    next_state[vp] = PerfParser.WORD1
                else:
                    next_state[vp] = PerfParser.WORD0

            elif state[vp] == PerfParser.WORD1:
                if tr_formats.is_tu1(tf):
                    sample_builder[vp].add_tf(tf)
                    next_state[vp] = PerfParser.WORD2
                else:
                    next_state[vp] = PerfParser.WORD0

            elif state[vp] == PerfParser.WORD2:
                if tr_formats.is_tu1(tf):
                    sample_builder[vp].add_tf(tf)
                    next_state[vp] = PerfParser.WORD3
                else:
                    next_state[vp] = PerfParser.WORD0

            elif state[vp] == PerfParser.WORD3:
                if tr_formats.is_tu1(tf):
                    sample_builder[vp].add_tf(tf)
                    next_state[vp] = PerfParser.WORD4
                else:
                    next_state[vp] = PerfParser.WORD0

            elif state[vp] == PerfParser.WORD4:
                if tr_formats.is_tu1(tf):
                    sample_builder[vp].add_tf(tf)
                    sample = sample_builder[vp].process_tfs()
                    self.samples.append(sample)
                next_state[vp] = PerfParser.WORD0

            else:
                raise RuntimeError('illegal parser state %s' % state[vp])

            state[vp] = next_state[vp]
            self._advance_tf()

    def _advance_tf(self):
        self.tf_idx += 1
        if self.tf_idx == len(self.frames[self.fr_idx].tfs):
            self.tf_idx = 0
            self.fr_idx += 1
            self.fr_valid = True

    def get_perfmon_samples(self):
        """
        Returns the samples, encoded in perfmon format.

        The return type is a list of list of strings. Each sublist is a perf
        sample.
        """
        cluster_offset = self.cluster * MAX_VPS_PER_CLUSTER
        core_offset = self.core * MAX_VPS_PER_CORE

        # Converts the local VP identifier at the lowest 8 bits of each
        # value into a global VP identifier, and formats for perfmon use.
        result = []
        local_samples = [s.to_perfmon_data() for s in self.samples]
        for sample_with_local_vp in local_samples:
            sample_with_global_vp = [cluster_offset + core_offset + val
                                     for val in sample_with_local_vp]
            perfmon_sample = [format(s, '016x') for s in sample_with_global_vp]
            result.append(perfmon_sample)

        return result

    def get_overflow_frames(self):
        """ Returns a list of overflow frame indices """
        return self.overflow_frames

    def get_total_frame_count(self):
        return len(self.frames)


class PerfSampleBuilder:
    """
    Internal class that helps to build a perf sample from traces.
    See the documentation in PerfParser for the description of
    how the bits are packed into user trace format data.
    """

    # The following constants apply to WU sample data.
    WORD0_TIMESTAMP_SHIFT = 10
    WORD0_ARG0_SHIFT = 2
    WORD0_ARG0_LEN = 8

    WORD1_ARG0_SHIFT = 8

    WORD2_PERF0_SHIFT = 32
    WORD2_WUID_SHIFT = 2
    WORD2_WUID_MASK = 0xffff

    WORD3_PERF1_SHIFT = 34
    WORD3_PERF2_SHIFT = 2
    WORD3_PERF2_MASK = 0xffffffff

    WORD4_PERF3_SHIFT = 34
    WORD4_CP0_SHIFT = 2
    WORD4_CP0_MASK = 0xffffffff

    # The following constants apply to custom sample data.
    WORD2_CUSTOM_ID_SHIFT = 18
    WORD2_CUSTOM_ID_MASK = 0x3fff
    WORD3_CUSTOM_DATA_MASK = 0xffffffff00000000
    WORD4_CUSTOM_DATA_SHIFT = 32

    def __init__(self, vp):
        self.tfs = []
        self.vp = vp

    def add_tf(self, tf):
        self.tfs.append(tf)

    def process_tfs(self):
        """
        Returns a perf sample from the trace formats.
        """
        sample = PerfSample()
        sample.vp = self.vp

        self._process_entry0(sample)
        self._process_entry1(sample)
        self._process_entry2(sample)
        self._process_entry3(sample)
        self._process_entry4(sample)

        return sample

    def _process_entry0(self, sample):
        sample.timestamp = self.tfs[0].addr >> self.WORD0_TIMESTAMP_SHIFT
        arg0_part = (self.tfs[0].addr >> self.WORD0_ARG0_SHIFT)
        arg0_part = arg0_part & 0xff
        arg0_part = arg0_part << (64 - self.WORD0_ARG0_LEN)
        sample.arg0 = arg0_part

    def _process_entry1(self, sample):
        sample.arg0 |= (self.tfs[1].addr >> self.WORD1_ARG0_SHIFT)

    def _process_entry2(self, sample):
        magic_num = ((self.tfs[2].addr >> self.WORD2_CUSTOM_ID_SHIFT)
                     & self.WORD2_CUSTOM_ID_MASK)
        if magic_num == 0xacc:
            sample.is_custom_data = True
            return

        sample.perf_counts[0] = self.tfs[2].addr >> self.WORD2_PERF0_SHIFT
        sample.wuid = ((self.tfs[2].addr >> self.WORD2_WUID_SHIFT) &
                       self.WORD2_WUID_MASK)

    def _process_entry3(self, sample):
        if sample.is_custom_data:
            sample.custom_data = (self.tfs[3].addr &
                                  self.WORD3_CUSTOM_DATA_MASK)
            return

        sample.perf_counts[1] = self.tfs[3].addr >> self.WORD3_PERF1_SHIFT
        sample.perf_counts[2] = ((self.tfs[3].addr >> self.WORD3_PERF2_SHIFT) &
                                 self.WORD3_PERF2_MASK)

    def _process_entry4(self, sample):
        if sample.is_custom_data:
            sample.custom_data = (sample.custom_data
                                  | (self.tfs[4].addr
                                     >> self.WORD4_CUSTOM_DATA_SHIFT))
            return

        sample.perf_counts[3] = self.tfs[4].addr >> self.WORD4_PERF3_SHIFT
        sample.cp0_count = ((self.tfs[4].addr >> self.WORD4_CP0_SHIFT) &
                            self.WORD4_CP0_MASK)


class PerfSample:
    """
    Represents a perf sample.
    """
    def __init__(self):
        self.wuid = None
        self.arg0 = None
        self.timestamp = None
        self.cp0_count = None
        self.perf_counts = [None, None, None, None]
        self.vp = None

        # True if this is a custom data sample, else False
        self.is_custom_data = False
        self.custom_data = None

    def __str__(self):
        return ('%s = wu: %s  '
                'time: %s  '
                'cycle: %s  ' 
                'perf0: %s  '
                'perf1: %s  '
                'perf2: %s  '
                'perf3: %s' % (self.vp,
                               format(self.wuid, '>4d'),
                               self.timestamp,
                               format(self.cp0_count, '>7d'),
                               format(self.perf_counts[0], '>6d'),
                               format(self.perf_counts[1], '>6d'),
                               format(self.perf_counts[2], '>6d'),
                               format(self.perf_counts[3], '>10d')))

    def to_perfmon_data(self):
        """
        Returns a representation of the data in this perf sample that
        is close to the perfmon format for perf visualization tools.

        The only difference is that instead of a global VP number, we only
        provide a local VP number in the lowest 8 bits. Callers must
        read and modify the lower 8 bits to set the global VP.

        C code from FunOS describing the format for perf samples:
        vpnum_t vp = vplocal_vpnum();
        cp0_kscratch6_write((timestamp) << 8 | vp);
        cp0_kscratch6_write((cp0_count) << 8 | vp);
        cp0_kscratch6_write((perf_cnt0) << 8 | vp);
        cp0_kscratch6_write((perf_cnt1) << 8 | vp);
        cp0_kscratch6_write((perf_cnt2) << 8 | vp);
        cp0_kscratch6_write((perf_cnt3) << 8 | vp);
        cp0_kscratch6_write(((arg0) >> 56) << 24 | ((wuid) << 8) | vp);
        cp0_kscratch6_write((arg0) << 8 | vp);
        """

        if self.is_custom_data:
            return self.to_custom_perfmon_data()

        # Note: in some cases we can avoid masking because the values are
        # 32-bits or less.
        vals = list()
        vals.append((self.timestamp << 8) & 0xffffffffffffffff | self.vp)
        vals.append(self.cp0_count << 8 | self.vp)
        vals.append(self.perf_counts[0] << 8 | self.vp)
        vals.append(self.perf_counts[1] << 8 | self.vp)
        vals.append(self.perf_counts[2] << 8 | self.vp)
        vals.append(self.perf_counts[3] << 8 | self.vp)
        vals.append((self.arg0 >> 56 << 24) | (self.wuid << 8) | self.vp)
        vals.append((self.arg0 << 8) & 0xffffffffffffffff | self.vp)
        return vals

    def to_custom_perfmon_data(self):
        """
        C code describing the format for custom data samples
        vpnum_t vp = vplocal_vpnum();
        cp0_kscratch6_write((timestamp) << 8 | vp);
        cp0_kscratch6_write((0xaccell << 32) << 8 | vp);
        cp0_kscratch6_write(((user_data) >> 56) << 8 | vp);
        cp0_kscratch6_write((user_data) << 8 | vp);
        cp0_kscratch6_write((0) << 8 | vp);
        cp0_kscratch6_write((0) << 8 | vp);
        cp0_kscratch6_write(((arg0) >> 56) << 24 | ((0) << 8) | vp);
        cp0_kscratch6_write((arg0) << 8 | vp);
        """
        vals = list()
        vals.append((self.timestamp << 8) & 0xffffffffffffffff | self.vp)
        vals.append((0xacce << 32) << 8 | self.vp)
        vals.append((self.custom_data >> 56) << 8 | self.vp)
        vals.append((self.custom_data << 8) & 0xffffffffffffffff | self.vp)
        vals.append(0 << 8 | self.vp)
        vals.append(0 << 8 | self.vp)
        vals.append((self.arg0 >> 56 << 24) | (0 << 8) | self.vp)
        vals.append((self.arg0 << 8) & 0xffffffffffffffff | self.vp)
        return vals


class CacheMissEntry(object):
    """
    Represents information about an instance of a cache miss.
    """
    def __init__(self, pc):
        self.pc = pc
        self.addr = None
        self.type = None

    def set_store_addr(self, addr):
        self.addr = addr
        self.type = 'store'

    def set_load_addr(self, addr):
        self.addr = addr
        self.type = 'load'

    def to_columns(self):
        return '%016x    %016x    %s' % (self.pc, self.addr, self.type)


class CacheMissParser(object):
    """
    Parser that records the PC where cache misses occur.

    TODO (jimmy): extend to record load/store address of cache misses.
    """

    # Parser state identifiers. A state represents the "type" of format
    # the parser is looking for at that time.
    #
    # TMOAS occurs at the start of tracing, and is always followed by TPC.
    # They come together, double trouble, Bonnie and Clyde. Even if the
    # trace buffer has overwritten early entries, the pair may show up at
    # odd times (typically because of processor mode changes).
    #
    # CM_TPC and CM_TA are the TPC and TLA/TSA pairs. These always seem to
    # come back-to-back. The VP appears to be irrelevant for TPC/TA pairs
    # as they are part of a different "stream". If we need to identify the
    # VP where the miss occurred we'll have to track the instruction stream.
    #
    # TODO (jimmy): handle the fact that we may lose TMOAS, but not its
    #               partner TPC at the start
    STATE_CM_TPC_OR_TMOAS = 1
    STATE_TMOAS_TPC = 2
    STATE_CM_TA = 3

    def __init__(self):
        self.entries = []
        self.state = self.STATE_CM_TPC_OR_TMOAS
        self.current_entry = None

    def parse_trace_messages(self, fh):
        """
        Extracts all TPC messages from the stream and records their
        addresses.
        """
        frames = parse_and_group_trace_formats(fh)
        for frame in frames:
            for tf in frame.tfs:
                self.process_tf(tf, frame.frame_index)

    def process_tf(self, tf, frame_index):
        next_state = self.state

        if self.state == self.STATE_CM_TPC_OR_TMOAS:
            if tr_formats.is_tmoas(tf):
                next_state = self.STATE_TMOAS_TPC
            elif tr_formats.is_tpc(tf):
                self.current_entry = CacheMissEntry(tf.addr)
                next_state = self.STATE_CM_TA

        elif self.state == self.STATE_TMOAS_TPC:
            next_state = self.STATE_CM_TPC_OR_TMOAS

        elif self.state == self.STATE_CM_TA:
            if tr_formats.is_tla(tf):
                self.current_entry.set_load_addr(tf.addr)
            elif tr_formats.is_tsa(tf):
                self.current_entry.set_store_addr(tf.addr)
            else:
                raise RuntimeError('frame %d: should have either TLA or TSA '
                                   'after TPC: %s' % (frame_index, tf))
            self.entries.append(self.current_entry)
            next_state = self.STATE_CM_TPC_OR_TMOAS

        self.state = next_state

    def get_entries(self):
        return self.entries

    @staticmethod
    def _run_addr2line(addrs, funos_binary_path):
        return raw_addr2line(addrs, funos_binary_path)


class PDTParser:
    """
    TODO: implement PC tracing here
    """
    def __init__(self):
        pass


class Frame:
    """
    A group of trace formats that belong to the same frame
    (i.e. the same 32-byte trace word).
    """
    def __init__(self, frame_index):
        self.tfs = []
        self.overflow = False
        self.frame_index = frame_index

    def add_tf(self, tf):
        self.tfs.append(tf)
        if tf.tf_type == 5:
            self.overflow = True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='path to input file')
    parser.add_argument('--parse-mode', type=str, help='type of parser to run',
                        default='perf',
                        choices=['perf', 'cache_miss'])
    parser.add_argument('--cluster', type=int, help='cluster id',
                        required=True)
    parser.add_argument('--core', type=int, help='core id',
                        required=True)
    parser.add_argument('--output-dir', type=str,
                        help='path to output directory',
                        default='testoutput')
    args = parser.parse_args()

    if args.parse_mode == 'perf':
        run_perf_parser(args)
    elif args.parse_mode == 'cache_miss':
        run_cache_miss_parser(args)


def run_perf_parser(args):
    trace_parser = PerfParser(args.cluster, args.core)
    perfmon_samples = None
    with open(args.input_file, 'r') as fh:
        trace_parser.parse_trace_messages(fh)
        perfmon_samples = trace_parser.get_perfmon_samples()
    if not perfmon_samples:
        print 'No samples'
        return
    out_file = 'put_%s_%s_perfmon.txt' % (str(args.cluster),
                                          str(args.core))
    out_path = os.path.join(args.output_dir, out_file)
    with open(out_path, 'w') as fh:
        for sample in perfmon_samples:
            fh.write('\n'.join(sample))
            fh.write('\n')

    report_overflow_frames(args, trace_parser)


def report_overflow_frames(args, trace_parser):
    overflow_frames = trace_parser.get_overflow_frames()
    total_frames = trace_parser.get_total_frame_count()

    if overflow_frames:
        overflow_file = 'overflow_%s_%s.txt' % (str(args.cluster),
                                                str(args.core))
        overflow_path = os.path.join(args.output_dir, overflow_file)
        with open(overflow_path, 'w') as fh:
            info = {'total_frames': total_frames,
                    'dropped_frames': overflow_frames}
            fh.write(json.dumps(info))


def run_cache_miss_parser(args):
    """
    Runs the cache miss parser on the trace files.

    Produces a file with columns for PC, load/store address and whether
    this was a load/store instruction.
    """
    parser = CacheMissParser()
    print 'Running cache miss parser on %s' % args.input_file
    with open(args.input_file, 'r') as fh:
        parser.parse_trace_messages(fh)

    entries = parser.get_entries()
    out_filename = 'cache_miss_%d_%d.txt' % (args.cluster, args.core)
    out_file = os.path.join(args.output_dir, out_filename)
    with open(out_file, 'w') as fh:
        lines = [e.to_columns() for e in entries]
        fh.write('\n'.join(lines))


FRAME_AND_TF_PATTERN = re.compile(r'^\s*([\d]+)\.([\d]+):.*TF(\d)')


def parse_and_group_trace_formats(fh):
    """
    Parses each line for trace formats, grouping by frame.

    Returns a list of frames, where each frame contains a list of
    trace format objects that have the same trace frame. e.g.
    [
       frameX  : [ tf1 tf2 tf2 ]
       frameX+n: [ tf3 tf3 ]
       ...
    ]

    Grouping the trace formats by frame is useful because we may have to drop
    or mark the frames where TF5 overflow occurs.

    TODO: wrap as an object when it is widely used
    """
    frames = []
    last_frame_index = None

    for line in fh.readlines():
        match = FRAME_AND_TF_PATTERN.match(line)
        if match:
            frame_index = match.group(1)
            tf_type = int(match.group(3))
            if frame_index != last_frame_index:
                frame_index_int = int(frame_index)
                frames.append(Frame(frame_index_int))
                last_frame_index = frame_index

            tf = _parse_message(line, tf_type)
            frames[-1].add_tf(tf)

    return frames


def _parse_message(message, tf_type):
    if tf_type == 2:
        return tr_formats.TF2()
    elif tf_type == 3:
        tf = tr_formats.TF3()
        tf.init_from_msg(message)
        return tf
    elif tf_type == 4:
        return tr_formats.TF4()
    elif tf_type == 5:
        return tr_formats.TF5()
    elif tf_type == 6:
        return tr_formats.TF6()
    elif tf_type == 7:
        return tr_formats.TF7()
    elif tf_type == 8:
        return tr_formats.TF8()

    raise ValueError('unknown TF type %d' % tf_type)


if __name__ == '__main__':
    main()
