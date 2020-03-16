#!/usr/bin/env python2.7

#
# Parses dumps of HW WU trace data and generates a report file.
#
# TODO (jimmy): generate something better than a text report blob
#
# Usage: hw_wu_trace.py -h
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import argparse
import collections
import event
import glob
import json
import os
import struct
import sys

# Length in bytes of a WU and its metadata
WU_LEN = 32
METADATA_LEN = 8

# A trace buffer is divided into 10 segments. The top 8 segments contain data,
# the bottom 2 contain metadata.
SEGMENTS = 10


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', type=str, 
                        help='input directory containing trace files')
    parser.add_argument('output_file', type=str, 
                        help='path to output file')
    parser.add_argument('wu_json_file', type=str, 
                        help='path to JSON file with list of WUs')

    args = parser.parse_args()

    wu_list = read_and_validate_wu_list(args.wu_json_file)
    trace_files = find_and_validate_trace_files(args.input_dir)

    print 'Extracting WUs from %s' % trace_files

    # First grab all the WUs in all the trace files.
    wus = []
    for tf in trace_files:
        fp = TraceFileParser(tf, wu_list)
        wus_from_file = fp.parse()
        wus.extend(wus_from_file)

    # Then only keep normal WUs because we know arg0 is the frame
    normal_wus = [w for w in wus if isinstance(w, NormalWU)]

    # Then group the WUs that share the same stack
    grouper = StackGrouper(wus)
    wu_groups = grouper.group()

    # Sort the WUs by timestamp in each group
    for group in wu_groups:
        group.sort(key=lambda wu_inst: wu_inst.time)

    # Convert each group into a series of lines, one line per WU.
    res = ''
    for group in wu_groups:
        wus_str = [str(wu) for wu in group]
        res += '\n'.join(wus_str)
        res += '\n-------------------------------------------------------\n\n'

    with open(args.output_file, 'w') as out_fh:
        out_fh.write(res)


def read_and_validate_wu_list(wu_json_file):
    """
    Reads the wu list from the specified file.

    Exits immediately if the list is empty, else returns the list.
    """
    with open(wu_json_file, 'r') as wu_fh:
        json_contents = json.load(wu_fh)
        wu_list = json_contents['wu_table']

    if not wu_list:
        print 'Error: empty WU list from %s' % wu_json_file
        sys.exit(1)

    return wu_list


def find_and_validate_trace_files(input_dir):
    """
    Looks for trace files, and exits immediately if none are found.

    Returns a list of the files if they exist.
    """

    glob_path = os.path.join(input_dir, 'trace_dump_*')
    trace_files = glob.glob(glob_path)

    if len(trace_files) == 0:
        print 'Error: no trace_dump_* files in %s' % input_dir
        sys.exit(1)

    return trace_files


class TraceFileParser(object):
    """
    Parses a trace file and builds WU objects from the contents.
    """
    def __init__(self, trace_file_path, wu_list):
        self.trace_file = trace_file_path
        self.wu_list = wu_list

    def parse(self):
        tf = self.trace_file

        fsize = os.path.getsize(tf)
        if fsize % SEGMENTS:
            print 'Error: file size for %s should be a multiple of the segment count' % tf
            return []

        # The idea here is to maintain two pointers: one at the
        # data section, and the other at the metadata section.
        #
        # The top 80% will be data, the remaining 20% is metadata.
        with open(tf, 'r') as data_fh, open(tf, 'r') as meta_fh:
            meta_pos = fsize // 10 * 8
            meta_fh.seek(meta_pos, 0)
            return self.build_wus(data_fh, meta_fh)

    def build_wus(self, data_fh, meta_fh):
        """
        Each 8-bytes of metadata correspond to a 32-byte chunk of
        data, which conveniently is a WU.
        """
        wus = []
        metadata = meta_fh.read(METADATA_LEN)
        while metadata:
            wu_data = data_fh.read(WU_LEN)
            wu = WUFactory.create(wu_data, metadata, self.wu_list)
            if wu:
                wus.append(wu)
            metadata = meta_fh.read(METADATA_LEN)
        return wus


class WU(object):
    """
    Base class for all WUs.
    """

    CMD_SHIFT = 59
    SGID_SHIFT = 51
    SLID_SHIFT = 46
    DGID_SHIFT = 41

    CMD_MASK = 0x1f
    GID_MASK = 0x1f
    LID_MASK = 0x1f

    def __init__(self, action, w0, w1, w2):
        self.action = action
        self.arg0 = w0
        self.arg1 = w1
        self.arg2 = w2
        self.cmd = (action >> WU.CMD_SHIFT) & WU.CMD_MASK
        self.time = None
        self.trace_location = None

    def set_trace_time(self, time):
        """
        Sets the time in ns at which this WU was traced.
        """
        self.time = time

    def set_trace_location(self, trace_location):
        """
        Sets the location which traced this WU.

        This can either be 0 for CMH ingress, or 1 for SNX egress.
        """
        self.trace_location = trace_location

    def __str__(self):
        return ('%d: act %s arg0 %s arg1 %s arg2 %s' % (
                self.time, hex(self.action), hex(self.arg0), 
                hex(self.arg1), hex(self.arg2)))


class NormalWU(WU):
    """
    A bog-standard, normal WU generated by VPs
    """

    DLID_SHIFT = 36

    WUID_MASK = 0xffff

    def __init__(self, action, w0, w1, w2, wu_list):
        super(NormalWU, self).__init__(action, w0, w1, w2)

        self.wuid = self.action & NormalWU.WUID_MASK
        if self.wuid >= len(wu_list):
            self.wu_name = 'unrecognized WU'
        else:
            wu_entry = wu_list[self.wuid]
            self.wu_name = wu_entry['name']
        self.sgid = (self.action >> WU.SGID_SHIFT) & WU.GID_MASK
        self.slid = (self.action >> WU.SLID_SHIFT) & WU.LID_MASK
        self.dgid = (self.action >> WU.DGID_SHIFT) & WU.GID_MASK
        self.dlid = (self.action >> NormalWU.DLID_SHIFT) & WU.LID_MASK

    def get_src_faddr(self):
        """
        Gets the source fabric address.

        TODO (jimmy): handle queues
        """
        faddr_int = self.sgid << 15 | self.slid << 10
        return event.FabricAddress.from_faddr(faddr_int)

    def get_dst_faddr(self):
        """
        Gets the destination fabric address.

        TODO (jimmy): handle queues
        """
        faddr_int = self.dgid << 15 | self.dlid << 10
        return event.FabricAddress.from_faddr(faddr_int)

    def __str__(self):
        saddr = self.get_src_faddr()
        daddr = self.get_dst_faddr()
        path = '%s -> %s' % (saddr, daddr)
        return ('%d: %d %s %s act %s arg0 %s arg1 %s arg2 %s' % (
            self.time, self.trace_location, self.wu_name, path,
            hex(self.action), hex(self.arg0),
            hex(self.arg1), hex(self.arg2)))


class WUFactory(object):
    """
    Creates the right WU given 32-byte data and 8-byte metadata.
    """

    # Command values that identify the WU type
    NORMAL_WU_CMD = 16

    @staticmethod
    def create(wu_data, metadata, wu_list):
        time_ns, loc = WUFactory.extract_time_and_trace_location(metadata)
        if time_ns == 0:
            return None

        # unpack the 8-byte words
        action = struct.unpack('>Q', wu_data[0:8])[0]
        w0 = struct.unpack('>Q', wu_data[8:16])[0]
        w1 = struct.unpack('>Q', wu_data[16:24])[0]
        w2 = struct.unpack('>Q', wu_data[24:32])[0]

        cmd = (action >> WU.CMD_SHIFT) & WU.CMD_MASK
        if cmd == WUFactory.NORMAL_WU_CMD:
            wu = NormalWU(action, w0, w1, w2, wu_list)
        else:
            print 'Unhandled cmd: %d' % cmd
            return None

        wu.set_trace_time(time_ns)
        wu.set_trace_location(loc)
        return wu

    @staticmethod
    def extract_time_and_trace_location(metadata):
        mdata_64 = struct.unpack('>Q', metadata)[0]
        time_ns = (mdata_64 & 0xfffffffffffffff) << 2
        loc = (mdata_64 >> 60) & 0x3
        return time_ns, loc


class StackGrouper(object):
    """
    Attempts to group WUs that are on the same stack
    """
    def __init__(self, wus):
        self.wus = wus
        self.wus_by_base_frame = collections.defaultdict(list)

    def group(self):
        """
        Returns a list of WU groups. Each WU group is itself a list of WUs
        that share the same stack. Note that the order of the WUs in the
        group is not that of the actual WU stack. Also, if the stack is
        reused then WUs from multiple "transactions" may be grouped
        together.

        TODO (jimmy): fix the clunky return type.
        """
        for wu in self.wus:
            # Mask off the lower 11-bits (2KB) to find WUs with a common stack
            frame = wu.arg0 & 0xfffffffffffff800
            self.wus_by_base_frame[frame].append(wu)

        stack_groups = []
        for frame in self.wus_by_base_frame:
            wus_in_stack = self.wus_by_base_frame[frame]
            stack_groups.append(wus_in_stack)
        return stack_groups


if __name__ == '__main__':
    main()

