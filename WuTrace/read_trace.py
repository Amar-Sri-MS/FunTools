#!/usr/bin/env python2.7

#
# Parses raw trace data that has been offloaded from the chip and
# converts it into a form that is suitable for the wu_trace.py
# script.
#
# Usage: -h for help
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import os
import re
import struct
import subprocess

# Every event is prefixed with a 64-bit header, which comprises
# two 32-bit words in big-endian order.
HDR_LEN = 8
HDR_DEF = '>LL'

LID_BASE = 8
MAX_VPS = 4
MAX_CORES = 6


class Event(object):
    """
    An event from WU tracing.

    This is the base class with common functionality across all
    event types. Subclasses perform unpacking of the additional
    words after the header.
    """

    # The number of least-significant bits that are lost from the
    # partial timestamps
    LOST_TIME_BITS = 6

    def __init__(self, hdr):
        hdr_words = struct.unpack(HDR_DEF, hdr)

        # Sanity check that we've unpacked correctly
        rsvd = hdr_words[1] & 0xfff
        if rsvd != 0:
            raise ValueError('Unexpected reserved value')

        self.partial_timestamp = hdr_words[0]
        self.evt_id = (hdr_words[1] >> 26) & 0x3f
        self.src_id = (hdr_words[1] & 0x3ff0000) >> 16
        self.addl_word_count = (hdr_words[1] & 0xf000) >> 12
        self.full_timestamp = None

    def fixup_timestamp(self, sync_timestamp):
        """
        Converts a partial timestamp to a full timestamp, given the
        sync timestamp.
        """
        time32 = self.partial_timestamp
        base32 = (sync_timestamp >> self.LOST_TIME_BITS) & 0xffffffff

        # If the time is less than the base, it means we've wrapped.
        if time32 < base32:
            sync_timestamp += (0x100000000 << self.LOST_TIME_BITS)

        high_bitmask = ~0x3fffffffff
        self.full_timestamp = ((sync_timestamp & high_bitmask)
                                  | (time32 << self.LOST_TIME_BITS))

    def get_values(self, wu_list):
        """
        Returns a dictionary that matches the data model used by the
        wu tracing script.
        """
        d = dict()
        d['timestamp'] = self.full_timestamp
        d['faddr'] = self.global_vp_to_faddr_str(self.src_id)
        return d

    @staticmethod
    def global_vp_to_faddr_str(src):
        """ Global VP number to faddr string """
        cluster = src / (MAX_CORES * MAX_VPS)
        lid = LID_BASE + (src % (MAX_CORES * MAX_VPS))
        return '%d:%d:0' % (cluster, lid)


class WuStartEvent(Event):
    """A WU START event."""

    def __init__(self, hdr, addl_words):
        super(WuStartEvent, self).__init__(hdr)

        if self.addl_word_count != 3:
            raise ValueError('Additional word count value')
        result = struct.unpack('>QQLL', addl_words)
        self.arg0 = result[0]
        self.arg1 = result[1]
        self.wuid = result[2]
        self.origin = result[3]

    def get_values(self, wu_list):
        d = super(WuStartEvent, self).get_values(wu_list)
        d['verb'] = 'WU'
        d['noun'] = 'START'
        d['arg0'] = self.arg0
        d['arg1'] = self.arg1
        d['wuid'] = self.wuid
        if self.wuid < len(wu_list):
            wu_name = wu_list[self.wuid]
        else:
            wu_name = 'out_of_range'
        d['name'] = wu_name
        return d


class WuSendEvent(Event):
    """A WU SEND event"""

    def __init__(self, hdr, addl_words):
        super(WuSendEvent, self).__init__(hdr)

        if self.addl_word_count != 4:
            raise ValueError('Additional word count value')

        # The final three short H values are padding
        result = struct.unpack('>QQLLHHHH', addl_words)
        self.arg0 = result[0]
        self.arg1 = result[1]
        self.wuid = result[2] & 0xffff
        self.dest = result[3]
        self.flags = result[4] & 0xffff

    def get_values(self, wu_list):
        d = super(WuSendEvent, self).get_values(wu_list)
        d['verb'] = 'WU'
        d['noun'] = 'SEND'
        d['arg0'] = self.arg0
        d['arg1'] = self.arg1
        d['wuid'] = self.wuid
        d['dest'] = self.faddr_to_str(self.dest)
        d['name'] = wu_list[self.wuid]
        d['flags'] = self.flags
        return d

    @staticmethod
    def faddr_to_str(faddr):
        """ faddr binary word to string """
        cluster = (faddr >> 15) & 0x1f
        lid = (faddr >> 10) & 0x1f
        return '%s:%s:0' % (cluster, lid)


class WuEndEvent(Event):
    """A WU END event."""

    def __init__(self, hdr, addl_words):
        super(WuEndEvent, self).__init__(hdr)

        if self.addl_word_count != 0:
            raise ValueError('Additional word count value')

    def get_values(self, wu_list):
        d = super(WuEndEvent, self).get_values(wu_list)
        d['verb'] = 'WU'
        d['noun'] = 'END'
        return d


class TimeSyncEvent(Event):
    """ A TIME SYNC event.

    This provides a full 64-bit timestamp so full timestamps
    from the other event types can be reconstructed from partial
    timestamps.
    """

    def __init__(self, hdr, addl_words):
        super(TimeSyncEvent, self).__init__(hdr)

        if self.addl_word_count != 1:
            raise ValueError('Additional word count value')
        result = struct.unpack('>Q', addl_words)
        self.full_timestamp = result[0]

    def fixup_timestamp(self, sync_timestamp):
        """ This already has a full timestamp """
        pass

    def get_values(self, wu_list):
        d = super(TimeSyncEvent, self).get_values(wu_list)
        d['verb'] = 'TIME'
        d['noun'] = 'SYNC'
        return d


class TraceFileParser(object):
    """ Handles raw trace file input. """

    def __init__(self, fh, wu_list):
        """ fh is a file handle to the trace file. """
        self.fh = fh
        self.wu_list = wu_list

    def parse(self):
        """ Does the parsing of the raw file.

        Returns a list of event dicts which are the data model for the
        next step in trace processing.
        """
        events = []
        sync_timestamp_by_vp = {}

        while True:
            hdr = self.fh.read(HDR_LEN)

            # EOF
            if not hdr:
                break

            hdr_words = struct.unpack(HDR_DEF, hdr)
            evt_id = (hdr_words[1] >> 26) & 0x3f
            addl_word_count = (hdr_words[1] & 0xf000) >> 12

            # Read the additional words
            content = None
            if addl_word_count > 0:
                content = self.fh.read(addl_word_count * 8)
                if not content:
                    # We have a problem: the file contents are too short
                    raise ValueError('Truncated file')

            if evt_id == 1:
                event = WuStartEvent(hdr, content)
            elif evt_id == 2:
                event = WuSendEvent(hdr, content)
            elif evt_id == 3:
                event = WuEndEvent(hdr, content)
            elif evt_id == 7:
                # This is guaranteed to be seen before any partial timestamps
                # from the same source.
                event = TimeSyncEvent(hdr, content)
                sync_timestamp_by_vp[event.src_id] = event.full_timestamp
            else:
                print 'Skip %d' % evt_id
                # raise ValueError('Unhandled event id %d' % evt_id)

            event.fixup_timestamp(sync_timestamp_by_vp[event.src_id])
            events.append(event)

        # Sort the events by timestamp
        events.sort(key=lambda et: et.full_timestamp)

        return [evt.get_values(self.wu_list) for evt in events]


class WuListExtractor(object):
    """ Extracts WU lists from a FunOS binary.

    Index in the list corresponds to WU id, value corresponds to the WU name

    TODO: figure out a common place to share this with perf
    """

    def __init__(self, image_path):
        self.funos_image_path = image_path

    def generate_wu_list(self):
        """Generates WU list from FunOS image file."""

        print 'Generating WU List'
        print

        linux_gdb_path = '/project/tools/mips/mips-img-elf/2015.06-05/bin/mips-img-elf-gdb'
        mac_gdb_path = '/Users/Shared/cross/mips64/bin/mips64-unknown-elf-gdb'
        gdb_path = mac_gdb_path if os.uname()[0] == 'Darwin' else linux_gdb_path

        gdb_command = [gdb_path,
                       '--nx',  # Do not read any .gdbinit files in any directory.
                       '-batch',  # Exit after processing options.
                       '--eval-command', 'set print elements 100000',
                       '--eval-command', 'set print repeats 0',
                       '--eval-command', 'set print array on',
                       '--eval-command', 'p wu_handlers_default',
                       self.funos_image_path]

        gdb_command_string = ' '.join(gdb_command).replace(' -', ' \\\n-')
        print 'Executing GDB as:'
        print '  ', gdb_command_string.replace('\n', '\n    ')
        print

        try:
            gdb_output = subprocess.check_output(gdb_command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            print 'GDB failed with return code %d\n' % error.returncode
            print 'GDB output:\n%s\n' % error.output
            raise error

        # GDB output is like so:
        #
        # $1 =   {0xa800000000118c38 <wuh_idle>,
        #   0xa800000000104e38 <ws_free_frame>,
        #   0xa800000000107348 <ws_free_frame_with_callback>,
        #   ...
        #   0xa800000000103e80 <invalid_runtime_wuh>,
        #   0xa800000000103e80 <invalid_runtime_wuh>}
        #

        wu_pattern = r'<(?P<wu>.+?)>'
        wu_regex = re.compile(wu_pattern)

        wu_list = []
        for line in gdb_output.split('\n'):
            match = wu_regex.search(line)
            if match:
                wu = match.group('wu')
                assert ' ' not in wu
                wu_list.append(wu)

        return wu_list
