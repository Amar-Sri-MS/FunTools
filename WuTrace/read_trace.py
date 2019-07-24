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
import sys

import event

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

    def __init__(self, timestamp, src_faddr):
        # Full timestamp when event was recorded.
        self.timestamp = timestamp
        # FabricAddress where event was logged.
        self.src_faddr = src_faddr

    def get_values(self, wu_list):
        """
        Returns a dictionary that matches the data model used by the
        wu tracing script.
        """
        d = dict()
        d['timestamp'] = self.timestamp
        d['faddr'] = str(self.src_faddr)
        return d

class WuStartEvent(Event):
    """A WU START event."""

    def __init__(self, timestamp, src_faddr, arg0, arg1, wuid, origin_faddr):
        super(WuStartEvent, self).__init__(timestamp, src_faddr)
        # Argument 0 of arriving WU.  Often frame.
        self.arg0 = arg0
        # Argument 1 of arriving WU.
        self.arg1 = arg1
        # Ordinal value of WU being run.
        self.wuid = wuid
        # FabricAddress of unit scheduling WU.
        self.origin_faddr = origin_faddr


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
        d['origin'] = str(self.origin_faddr)
        return d


class WuSendEvent(Event):
    """A WU SEND event"""
    def __init__(self, timestamp, src_faddr, arg0, arg1, wuid,
                 dest_faddr, flags):
        """Creates a WU SEND event from all arguments logged."""
        super(WuSendEvent, self).__init__(timestamp, src_faddr)
        # Argument 0 for sent WU.
        self.arg0 = arg0
        # Argument 1 for sent WU.
        self.arg1 = arg1
        # Ordinal number for the WU being sent.  Does not include prefetch
        # bits.
        self.wuid = wuid
        # Destination fabric address where WU should run.
        self.dest_faddr = dest_faddr
        # Additional flags describing WU.
        # bit 0 = gated WU.
        # bit 1 = Fake WU short-circuiting hardware request.
        self.flags = flags

    def get_values(self, wu_list):
        d = super(WuSendEvent, self).get_values(wu_list)
        d['verb'] = 'WU'
        d['noun'] = 'SEND'
        d['arg0'] = self.arg0
        d['arg1'] = self.arg1
        d['wuid'] = self.wuid
        d['dest'] = str(self.dest_faddr)
        d['name'] = wu_list[self.wuid]
        d['flags'] = self.flags
        return d


class WuEndEvent(Event):
    """A WU END event."""

    def __init__(self, timestamp, src_faddr):
        super(WuEndEvent, self).__init__(timestamp, src_faddr)

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

    def __init__(self, timestamp, src_faddr, full_timestamp):
        super(TimeSyncEvent, self).__init__(timestamp, src_faddr)
        self.fulltimestamp = full_timestamp

    def get_values(self, wu_list):
        d = super(TimeSyncEvent, self).get_values(wu_list)
        d['verb'] = 'TIME'
        d['noun'] = 'SYNC'
        return d

class TraceFileParser(object):
    """ Handles raw trace file input. """

    # The number of least-significant bits that are lost from the
    # partial timestamps
    LOST_TIME_BITS = 6

    def __init__(self, fh, wu_list):
        """ Create a new TraceFileParser.

        fh is a file handle to the trace file.
        wu_list is a list of names of wu names in wu id order, used
        for mapping wu_id to wu name.
        """
        self.fh = fh
        self.wu_list = wu_list
        # Map from source id to last full timestamp.
        self.last_full_timestamp = {}

    def parse_header(self, hdr):
        """Gathers information common to all trace events.

        hdr is header word as 64 bit integer.

        Returns (partial timestamp, source fabric address where event
        was logged, and number of additional words described in header.)
        """
        hdr_words = struct.unpack(HDR_DEF, hdr)

        # Sanity check that we've unpacked correctly
        rsvd = hdr_words[1] & 0xfff
        if rsvd != 0:
            raise ValueError('Unexpected reserved value 0x%x' % rsvd)

        partial_timestamp = hdr_words[0]
        src_id = (hdr_words[1] & 0x3ff0000) >> 16
        addl_count = (hdr_words[1] & 0xf000) >> 12

        src_faddr = event.FabricAddress.from_ordinal(src_id)

        return (partial_timestamp, src_faddr, addl_count)

    def parse_start_event(self, hdr, addl_words):
        """Parses a WuStart event from the binary trace data.

        Returns a WuStartEvent for the described event.
        """
        (partial_timestamp, src_faddr, addl_count) = self.parse_header(hdr)

        if addl_count != 3:
            raise ValueError('Additional word count value')
        result = struct.unpack('>QQLL', addl_words)
        arg0 = result[0]
        arg1 = result[1]
        wuid = result[2]
        origin = result[3]

        # Chop off high bits.
        wuid = wuid & 0xfffff

        origin_faddr = event.FabricAddress.from_faddr(origin)

        timestamp = self.full_timestamp(src_faddr, partial_timestamp)
        return WuStartEvent(timestamp, src_faddr, arg0, arg1,
                            wuid, origin_faddr)

    def parse_send_event(self, hdr, addl_words):
        """Parses a WU SEND event from the binary trace data.

        Returns a WuSendEvent for the described event.
        """
        (partial_timestamp, src_faddr, addl_count) = self.parse_header(hdr)

        if addl_count != 4:
            raise ValueError('Additional word count value')

        # The final three short H values are padding
        result = struct.unpack('>QQLLHHHH', addl_words)
        arg0 = result[0]
        arg1 = result[1]
        wuid = result[2] & 0xffff
        dest = result[3]
        flags = result[4] & 0xffff

        # Chop off high bits.
        wuid = wuid & 0xfffff

        dest_faddr = event.FabricAddress.from_faddr(dest)

        timestamp = self.full_timestamp(src_faddr, partial_timestamp)
        return WuSendEvent(timestamp, src_faddr, arg0, arg1, wuid,
                           dest_faddr, flags)

    def parse_end_event(self, hdr, addl_words):
        """Parses a WU END event from the binary trace data.

        Returns a WuEndEvent for the described event.
        """
        (partial_timestamp, src_faddr, addl_count) = self.parse_header(hdr)

        if addl_count != 0:
            raise ValueError('Additional word count value')

        timestamp = self.full_timestamp(src_faddr, partial_timestamp)
        return WuEndEvent(timestamp, src_faddr)

    def parse_time_sync_event(self, hdr, addl_words):
        """Parses a TIME SYNC event from the binary trace data.

        Updates the parser's idea of the full timestamp.

        Returns a TimeSyncEvent for the described event.
        """
        (partial_timestamp, src_faddr, addl_count) = self.parse_header(hdr)

        if addl_count != 1:
            raise ValueError('Additional word count value')

        result = struct.unpack('>Q', addl_words)
        full_timestamp = result[0]
        self.last_full_timestamp[src_faddr] = full_timestamp

        return TimeSyncEvent(partial_timestamp, src_faddr, self.full_timestamp)

    def full_timestamp(self, src_faddr, partial_timestamp):
        """ Converts a partial timestamp to a full timestamp.

        src_faddr is the processor where the event with the partial time
        was generated.
        partial_timestamp is the timestamp recorded in the event.

        Returns an absolute timestamp based on the TIME SYNC events seen
        recently.
        """
        if src_faddr not in self.last_full_timestamp:
            raise ValueError('No recent full timestamp to fix partial.')

        full_timestamp = self.last_full_timestamp[src_faddr]
        base32 = (full_timestamp >> self.LOST_TIME_BITS) & 0xffffffff

        # If the time is less than the base, it means we've wrapped.
        if partial_timestamp < base32:
            partial_timestamp += 0x100000000

        high_bitmask = ~0x3fffffffff
        timestamp = ((full_timestamp & high_bitmask)
                     | (partial_timestamp << self.LOST_TIME_BITS))
        return timestamp

    def parse(self):
        """ Does the parsing of the raw trace file in binary format.

        Returns a list of event dicts which are the data model for the
        next step in trace processing.
        """
        events = []

        while True:
            hdr = self.fh.read(HDR_LEN)

            # EOF
            if not hdr:
                break

            hdr_words = struct.unpack(HDR_DEF, hdr)
            evt_id = (hdr_words[1] >> 26) & 0x3f
            addl_count = (hdr_words[1] & 0xf000) >> 12

            # Read the additional words
            content = None
            if addl_count > 0:
                content = self.fh.read(addl_count * 8)
                if not content:
                    # We have a problem: the file contents are too short
                    raise ValueError('Truncated file')

            if evt_id == 1:
                event = self.parse_start_event(hdr, content)
            elif evt_id == 2:
                event = self.parse_send_event(hdr, content)
            elif evt_id == 3:
                event = self.parse_end_event(hdr, content)
            # TODO(bowdidge): Handle timer events.
            elif evt_id == 7:
                # This is guaranteed to be seen before any partial
                # timestamps from the same source.
                event = self.parse_time_sync_event(hdr, content)
            else:
                print 'Skip %d' % evt_id
                # raise ValueError('Unhandled event id %d' % evt_id)
            events.append(event)

        # Sort the events by timestamp
        events.sort(key=lambda et: et.timestamp)

        all_events = [evt.get_values(self.wu_list) for evt in events]
        # for e in all_events:
        #     print e['timestamp'], e['faddr'], e['verb'], e['noun']
        return all_events


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
