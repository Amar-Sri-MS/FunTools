#!/usr/bin/env python2.7
#
# Parse trace data, either from raw trace data offloaded from the chip,
# or from console log messages.  Convert into a form that can be used for
# better processing of the trace.
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

def clean_string(label_str):
    """Cleans annotation strings of non-ascii characters."""
    clean_label = ''
    for c in label_str:
        if ord(c) == 0:
            break
        if ord(c) < 32 or ord(c) > 127:
            c = '0x%x' % ord(c)
        clean_label += c
    return clean_label


def clean_wu_name(wu_name):
    # Remove mangled names from WU names.
    bad_prefixes = ['__thread____channel__',
                    '__thread__', '__channel__', '__wu_handler__']
    for prefix in bad_prefixes:
        if wu_name.startswith(prefix):
            return wu_name.replace(prefix, '')
    return wu_name


class TraceFileParser(object):
    """ Handles raw trace file input. """

    # The number of least-significant bits that are lost from the
    # partial timestamps
    LOST_TIME_BITS = 6

    def __init__(self, wu_list):
        """ Create a new TraceFileParser.

        fh is a file handle to the trace file.
        wu_list is a list of names of wu names in wu id order, used
        for mapping wu_id to wu name.
        """
        self.wu_list = wu_list
        # Map from source id to last full timestamp.
        self.last_full_timestamp = {}

    def wu_name(self, wu_id):
        """Returns the name of the wu associated with the WU id."""
        # TODO(bowdidge): be more forgiving of unknown WUs.
        if wu_id >= len(self.wu_list):
            return 'unknown_wu_0x%x' % wu_id
        return clean_wu_name(self.wu_list[wu_id])

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

        faddr = event.FabricAddress.from_ordinal(src_id)

        return (partial_timestamp, faddr, addl_count)

    def parse_start_event(self, hdr, addl_words):
        """Parses a WuStart event from the binary trace data.

        Returns a WuStartEvent for the described event.
        """
        (partial_timestamp, faddr, addl_count) = self.parse_header(hdr)

        if addl_count != 3:
            raise ValueError('parse_start_event: expected addl_count == 3, but got %d' % addl_count)
        result = struct.unpack('>QQLL', addl_words)
        arg0 = result[0]
        arg1 = result[1]
        wuid = result[2]
        origin = result[3]

        # Chop off high bits.
        wuid = wuid & 0xfffff

        try:
            origin_faddr = event.FabricAddress.from_faddr(origin)
        except ValueError as e:
            sys.stderr.write('Problems parsing start event: bad faddr: %s' % e)
            return None

        timestamp = self.full_timestamp(faddr, partial_timestamp)
        return event.WuStartEvent(timestamp, faddr, arg0, arg1,
                                  wuid, self.wu_name(wuid), origin_faddr)

    def parse_send_event(self, hdr, addl_words):
        """Parses a WU SEND event from the binary trace data.

        Returns a WuSendEvent for the described event.
        """
        (partial_timestamp, faddr, addl_count) = self.parse_header(hdr)

        if addl_count != 4:
            raise ValueError('parse_send_event: expected addl_count == 4, but got %d' % addl_count)

        # The final three short H values are padding
        result = struct.unpack('>QQLLHHHH', addl_words)
        arg0 = result[0]
        arg1 = result[1]
        wuid = result[2] & 0xffff
        dest = result[3]
        flags = result[4] & 0xffff

        try:
            dest_faddr = event.FabricAddress.from_faddr(dest)
        except ValueError as e:
            sys.stderr.write('Problems parsing send event: bad faddr: %s' % e)
            return None

        timestamp = self.full_timestamp(faddr, partial_timestamp)
        return event.WuSendEvent(timestamp, faddr, arg0, arg1, wuid,
                                 self.wu_name(wuid),
                                 dest_faddr, flags)

    def parse_end_event(self, hdr, addl_words):
        """Parses a WU END event from the binary trace data.

        Returns a WuEndEvent for the described event.
        """
        (partial_timestamp, faddr, addl_count) = self.parse_header(hdr)

        if addl_count != 0:
            raise ValueError('parse_end_event: expected addl_count == 0, but got %d' % addl_count)

        timestamp = self.full_timestamp(faddr, partial_timestamp)
        return event.WuEndEvent(timestamp, faddr)

    def parse_timer_start_event(self, hdr, addl_words):
        """Parses a TIMER START event from the binary trace data.

        Returns a TimerStartEventt for the described event, or None in case of error.
        """
        (partial_timestamp, faddr, addl_count) = self.parse_header(hdr)

        if addl_count != 3:
            raise ValueError('parse_timer_start_event: expected addl_count == 3, but got %d' % addl_count)

        # Last uint32_t is padding.
        result = struct.unpack('>LLQLL', addl_words)

        timer_id = result[0]
        wuid = result[1] & 0xffff
        wu_name = self.wu_name(wuid)
        arg0 = result[2]
        dest = result[3]

        try:
            dest_faddr = event.FabricAddress.from_faddr(dest)
        except ValueError as e:
            sys.stderr.write('Problems parsing timer start event: bad faddr: %s' % e)
            return None

        timestamp = self.full_timestamp(faddr, partial_timestamp)
        return event.TimerStartEvent(timestamp, faddr, timer_id, wuid, wu_name, dest_faddr, arg0)

    def parse_annotate_event(self, hdr, addl_words):
        (partial_timestamp, faddr, addl_count) = self.parse_header(hdr)
        clean_msg = clean_string(addl_words)

        timestamp = self.full_timestamp(faddr, partial_timestamp)
        return event.TransactionAnnotateEvent(timestamp, faddr, clean_msg)

    def parse_time_sync_event(self, hdr, addl_words):
        """Parses a TIME SYNC event from the binary trace data.

        Updates the parser's idea of the full timestamp.

        Returns a TimeSyncEvent for the described event.
        """
        (partial_timestamp, faddr, addl_count) = self.parse_header(hdr)

        if addl_count != 1:
            raise ValueError('Additional word count value')

        result = struct.unpack('>Q', addl_words)
        full_timestamp = result[0]
        self.last_full_timestamp[faddr] = full_timestamp

        return event.TimeSyncEvent(partial_timestamp, faddr,
                                   full_timestamp)

    def _partial_timestamp(self, full_timestamp):
        """Returns a bit-reduced timestamp.

        For testing only.  Behavior should match FunOS.
        """
        return (full_timestamp >> self.LOST_TIME_BITS) & 0xffffffff

    def full_timestamp(self, faddr, partial_timestamp):
        """ Converts a partial timestamp to a full timestamp.

        faddr is the processor where the event with the partial time
        was generated.
        partial_timestamp is the timestamp recorded in the event.

        Returns an absolute timestamp based on the TIME SYNC events seen
        recently.
        """
        if faddr not in self.last_full_timestamp:
            raise ValueError('No recent full timestamp to fix partial.')

        full_timestamp = self.last_full_timestamp[faddr]
        base32 = (full_timestamp >> self.LOST_TIME_BITS) & 0xffffffff

        # If the time is less than the base, it means we've wrapped.
        if partial_timestamp < base32:
            partial_timestamp += 0x100000000

        high_bitmask = ~0x3fffffffff
        timestamp = ((full_timestamp & high_bitmask)
                     + (partial_timestamp << self.LOST_TIME_BITS))
        return timestamp

    def parse(self, fh, output_file=None):
        """ Does the parsing of the raw trace file in binary format.

        fh is a file handle for reading the byte stream.

        Returns a list of event dicts which are the data model for the
        next step in trace processing.
        """
        events = []
        count = 0
        offset = 0
        wfh = None
        if output_file:
            wfh = open(output_file, 'w')
        # strip initial cluster byte
        fh.read(1)

        while True:
            hdr = fh.read(HDR_LEN)
            count += 1
            offset += HDR_LEN

            # EOF
            if not hdr:
                break

            hdr_words = struct.unpack(HDR_DEF, hdr)
            evt_id = (hdr_words[1] >> 26) & 0x3f
            addl_count = (hdr_words[1] & 0xf000) >> 12
            partial_timestamp = hdr_words[0]
            # Read the additional words
            content = None
            if addl_count > 0:
                content = fh.read(addl_count * 8)
                offset += addl_count * 8
                if not content:
                    # We have a problem: the file contents are too short
                    raise ValueError('Truncated file')

            if evt_id == event.WU_START_EVENT:
                new_event = self.parse_start_event(hdr, content)
            elif evt_id == event.WU_SEND_EVENT:
                new_event = self.parse_send_event(hdr, content)
            elif evt_id == event.WU_END_EVENT:
                new_event = self.parse_end_event(hdr, content)
            elif evt_id == event.TIMER_START_EVENT:
                new_event = self.parse_timer_start_event(hdr, content)
            elif evt_id == event.TRANSACTION_ANNOT_EVENT:
                new_event = self.parse_annotate_event(hdr, content)
            # TODO(bowdidge): Handle timer events.
            elif evt_id == event.TIME_SYNC_EVENT:
                # This is guaranteed to be seen before any partial
                # timestamps from the same source.
                new_event = self.parse_time_sync_event(hdr, content)
            elif evt_id == 0:
                continue
            else:
                print("Skip event %d for %d bytes" % (evt_id, evt_id))
                # raise ValueError('Unhandled event id %d' % evt_id)

            if not new_event:
                # Parse error.
                continue

            if wfh:
                wfh.write('%d time 0x%08x offset 0x%08x %s\n' % (new_event.timestamp, partial_timestamp, offset, new_event))
            events.append(new_event)
        # Sort the events by timestamp
        events.sort(key=lambda et: et.timestamp)
        if wfh:
            wfh.close()
        return events

class WuListExtractor(object):
    """ Extracts WU lists from a FunOS binary.

    Index in the list corresponds to WU id, value corresponds to the WU name

    TODO: figure out a common place to share this with perf
    """

    def __init__(self, image_path):
        self.funos_image_path = image_path

    def generate_wu_list(self):
        """Generates WU list from FunOS image file."""

        print("Generating WU List")
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
                       '--eval-command', 'set max-value-size 262144',
                       '--eval-command', 'p *wu_handlers_default@16384',
                       self.funos_image_path]

        gdb_command_string = ' '.join(gdb_command).replace(' -', ' \\\n-')
        print("Executing GDB as:")
        print("  ", gdb_command_string.replace('\n', '\n    '))
        print

        try:
            gdb_output = subprocess.check_output(gdb_command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            print("GDB failed with return code %d\n" % error.returncode)
            print("GDB output:\n%s\n" % error.output)
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

def parse_int(str):
    """Returns int, or throws an exception."""
    try:
        value = int(str)
        return value
    except ValueError as e:
        if not str.startswith('0x'):
            raise e
        value = int(str, 16)
        return value

class TraceLogParser(object):
    """Turns TRACE log messages from console into sequence of Event objects."""
    EXPECTED_KEYWORDS = {
        ('WU', 'START'): {'faddr', 'wuid', 'name', 'arg0', 'arg1', 'origin'},
        ('WU', 'END'): {'faddr'},
        ('WU', 'SEND'): {'faddr', 'wuid', 'name', 'arg0', 'arg1', 'dest',
                         'flags'},
        ('TIMER', 'START'): {'faddr', 'timer', 'wuid', 'name', 'dest', 'arg0'},
        ('TRANSACTION', 'START'): {'faddr'},
        ('TRANSACTION', 'ANNOT'): {'faddr'},
        ('HU', 'SQL_DBL'): {'sqid'},
        }

    def __init__(self):
        self.wu_list = []

    def wu_name(self, wu_id):
        """Returns name of WU associated with the wuid."""
        # TODO(bowdidge): be more forgiving of unknown WUs.
        return self.wu_list[wu_id]

    def parse_line(self, line, filename='unknown', line_number=0):
        """Turns an log line for a trace event into a keyword dictionary.

        Returns (dictionary of keywords, error_string)
        """
        line = line.strip()
        values = {}
        match = re.match('\s*([0-9]+).([0-9]+) TRACE ([A-Z_]+) ([A-Z_]+)',
                         line)
        if not match:
            # Not a log line, but not an error either.
            return (None, None)

        time_nsec = int(match.group(1)) * 1000000000 + int(match.group(2))

        values = {'filename': filename,
                  'line_number': line_number,
                  'timestamp': time_nsec,
                  'verb': match.group(3),
                  'noun': match.group(4)
                  }
        remaining_string = line[len(match.group(0)):].lstrip()

        if len(remaining_string) == 0:
            return (values, None)

        # Annotation is special - we need to find the faddr at the
        # beginning, but the rest counts as the message.
        if values['verb'] == 'TRANSACTION' and values['noun'] == 'ANNOT':
            annot_match = re.match(
                'faddr (FA[0-9]+:[0-9]+:[0-9]+\[VP\]) msg (.*)',
                remaining_string)
            if not annot_match:
                error = '%s:%d: malformed transaction annotation: "%s"\n' % (
                    filename, line_number, line)
                return (None, error)

            try:
                faddr_str = annot_match.group(1)
                faddr = event.FabricAddress.from_string(faddr_str)
            except ValueError as e:
                error = '%s:%d: malformed fabric address in trace for key %s: %s' % (
                    filename, line_number, 'faddr', e)
                return (None, error)
            values['faddr'] = faddr
            values['msg'] = annot_match.group(2)
            return (values, None)

        # Anything other than TRANSACTION ANNOT.
        token_iter = iter(remaining_string.split(' '))
        try:
            pairs = [(a, next(token_iter)) for a in token_iter]
        except StopIteration as e:
            error = '%s:%d: malformed log line: "%s"\n' % (
                filename, line_number, line)
            return (None, error)

        for (key, value) in pairs:
            values[key] = value

        expect_keywords = self.EXPECTED_KEYWORDS.get((values['verb'],
                                                      values['noun']))
        if not expect_keywords:
            error = '%s:%d: unknown verb or noun: %s %s\n' % (filename,
                                                              line_number,
                                                              values['verb'],
                                                              values['noun'])
            return (None, error)

        for expected_keyword in expect_keywords:
            if expected_keyword not in values:
                error = '%s:%d: missing key "%s" in command %s %s\n' % (
                    filename, line_number, expected_keyword,
                    values['verb'], values['noun'])
                return (None, error)

        int_keywords = ['wuid', 'arg0', 'arg1', 'sqid', 'flags']
        vp_keywords = ['dest', 'origin', 'faddr']

        for keyword in int_keywords:
            if keyword in values:
                try:
                    values[keyword] = parse_int(values[keyword])
                except ValueError as e:
                    error = '%s:%d: malformed hex value in trace for key %s: %s' % (
                        filename, line_number, keyword, e)
                    return (None, error)

        for keyword in vp_keywords:
            if keyword in values:
                try:
                    values[keyword] = event.FabricAddress.from_string(values[keyword])
                except ValueError as e:
                    error = '%s:%d: malformed fabric address in trace for key %s: %s' % (
                        filename, line_number, keyword, e)
                    return (None, error)

        if 'wuid' in values:
            if 'name' in values:
                wuid = values['wuid']
                wu_list_len = len(self.wu_list)

                if wu_list_len <= wuid:
                    self.wu_list += ['unknown'] * (wuid - wu_list_len + 1)
                if self.wu_list[wuid] != 'unknown':
                    if self.wu_list[wuid] != values['name']:
                        raise ValueError('Bad WU name: %s vs %s' % (
                                self.wu_list[wuid], values['name']))
                self.wu_list[wuid] = values['name']



        return (values, None)

    def create_start_event(self, keywords):
        wuid = keywords['wuid'] & 0xffff
        return event.WuStartEvent(keywords['timestamp'],
                                  keywords['faddr'],
                                  keywords['arg0'],
                                  keywords['arg1'],
                                  wuid,
                                  self.wu_name(wuid),
                                  keywords['origin'])

    def create_send_event(self, keywords):
        wuid = keywords['wuid'] & 0xffff
        return event.WuSendEvent(keywords['timestamp'],
                                 keywords['faddr'],
                                 keywords['arg0'],
                                 keywords['arg1'],
                                 wuid,
                                 self.wu_name(wuid),
                                 keywords['dest'],
                                 keywords['flags'])

    def create_end_event(self, keywords):
        return event.WuEndEvent(keywords['timestamp'], keywords['faddr'])


    def create_annotate_event(self, keywords):
        clean_msg = clean_string(keywords['msg'])
        return event.TransactionAnnotateEvent(keywords['timestamp'],
                                              keywords['faddr'],
                                              clean_msg)

    def create_transaction_start_event(self, keywords):
        return event.TransactionStartEvent(keywords['timestamp'],
                                           keywords['faddr'])

    def create_timer_start_event(self, keywords):
        wuid = keywords['wuid'] & 0xffff
        return event.TimerStartEvent(keywords['timestamp'],
                                     keywords['faddr'],
                                     keywords['timer'],
                                     wuid,
                                     self.wu_name(wuid),
                                     keywords['dest'],
                                     keywords['arg0'])

    def create_time_sync_event(self, keywords):
        raise ValueError('not handled')

    def create_event(self, keywords, filename, line_number):
        """Turns a log line into a Trace event.

        keywords is a dictionary of keywords from the log line.
        filename is name of file where logs were gathered.  For error report.
        line_number is the line for the log line generating keywords.
        """
        if keywords['verb'] == 'WU' and keywords['noun'] == 'START':
            return self.create_start_event(keywords)
        elif keywords['verb'] == 'WU' and keywords['noun'] == 'SEND':
            return self.create_send_event(keywords)
        elif keywords['verb'] == 'WU' and keywords['noun'] == 'END':
            return self.create_end_event(keywords)
        elif keywords['verb'] == 'TRANSACTION' and keywords['noun'] == 'ANNOT':
            return self.create_annotate_event(keywords)
        elif keywords['verb'] == 'TRANSACTION' and keywords['noun'] == 'START':
            return self.create_transaction_start_event(keywords)
        elif keywords['verb'] == 'TIMER' and keywords['noun'] == 'START':
            return self.create_timer_start_event(keywords)
        elif keywords['verb'] == 'TIME' and keywords['noun'] == 'SYNC':
            return self.create_time_sync_event(keywords)
        elif keywords['verb'] == 'FLUSH' and keywords['noun'] == 'FLUSH':
            return None
        else:
            print("Do not know how to handle %s/%s" % (keywords['verb'],
                                                       keywords['noun']))
        return None

    def parse(self, fh, filename='unknown'):
        """Parse all lines of an input trace log file.

        fh is a file handle that will supply all lines of the file.

        filename is the name of the file being read for error reporting.

        Returns array of all events in sorted order.
        """
        events = []
        line_number = 0
        while True:
            line = fh.readline()
            if not line:
                break

            line_number += 1
            (log_keywords, error) = self.parse_line(line, filename,
                                                    line_number)
            if error:
                sys.stderr.write(error)
            if not log_keywords:
                continue
            event = self.create_event(log_keywords, filename=filename,
                                      line_number=line_number)
            if event:
                events.append(event)

        events.sort(key=lambda et: et.timestamp)
        return events
