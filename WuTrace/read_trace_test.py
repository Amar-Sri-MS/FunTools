#!/usr/bin/env python3
#
# read_trace_test.py: unit tests for parsing binary trace events.
#

import struct
import unittest

import event
import read_trace

class TraceFileParserTest(unittest.TestCase):

    def testPartialTime(self):
        trace_parser = read_trace.TraceFileParser([])
        reserved = 0
        timestamp = 0x12345678
        src_id = 15
        addl_words = 1
        word0 = timestamp
        word1 = (reserved | (src_id << 16) | (addl_words << 12))
        header = struct.pack('>LL', word0, word1)
        (partial_timestamp, src_faddr,
         word_count) = trace_parser.parse_header(header)
        self.assertEqual(partial_timestamp, timestamp)
        self.assertEqual('VP0.3.3', str(src_faddr))
        self.assertEqual(1, word_count)

        full_timestamp = 0x123456789abcdef
        second_word = struct.pack('>Q', full_timestamp)
        trace_parser.parse_time_sync_event(header, second_word)

        self.assertEqual(full_timestamp,
                         trace_parser.last_full_timestamp[src_faddr])


def FUN_TIME_FROM_SECS(secs):
    """Returns the nominal nanoseconds for the number of seconds.

    Used for creating timestamps.
    """
    # TODO(bowdidge) FunOS clock is actually cycle-based.
    ns_per_sec = 1000 * 1000 * 1000
    return secs * ns_per_sec


class TestPartialTimestamp(unittest.TestCase):

    def testFullTimestampHasNoEffect(self):
        """Check when full timestamp is 0."""
        file_parser = read_trace.TraceFileParser([])
        my_faddr = event.FabricAddress.from_ordinal(5)

        file_parser.last_full_timestamp[my_faddr] = 0

        self.assertEqual(0, file_parser.full_timestamp(my_faddr, 0))
        self.assertEqual(0x80000000 << file_parser.LOST_TIME_BITS,
                         file_parser.full_timestamp(my_faddr, 0x80000000))
        self.assertEqual(0xffffffff << file_parser.LOST_TIME_BITS,
                         file_parser.full_timestamp(my_faddr, 0xffffffff))

    def testWrappingTimestamp(self):
        """Test high bits from timestamp brought over correctly."""
        file_parser = read_trace.TraceFileParser([])
        my_faddr = event.FabricAddress.from_ordinal(5)

        # full timestamp has no bits set in region where partial gets added.
        last_timestamp = FUN_TIME_FROM_SECS(30)
        file_parser.last_full_timestamp[my_faddr] = last_timestamp

        # 60 seconds should set high bits but not roll the clock.
        check_time = last_timestamp  + FUN_TIME_FROM_SECS(40)
        partial_check_time = file_parser._partial_timestamp(check_time)
        self.assertEqual(check_time,
                         file_parser.full_timestamp(my_faddr,
                                                    partial_check_time))

        check_time = last_timestamp + FUN_TIME_FROM_SECS(250)
        partial_check_time = file_parser._partial_timestamp(check_time)
        self.assertEqual(check_time,
                         file_parser.full_timestamp(my_faddr,
                                                    partial_check_time))

        check_time = last_timestamp + FUN_TIME_FROM_SECS(550)
        partial_check_time = file_parser._partial_timestamp(check_time)
        # Too far out of range.
        self.assertNotEqual(check_time,
                            file_parser.full_timestamp(my_faddr,
                                                       partial_check_time))

        # If we update the last full timestamp, it's ok.
        check_time = last_timestamp + FUN_TIME_FROM_SECS(550)
        file_parser.last_full_timestamp[my_faddr] = FUN_TIME_FROM_SECS(450)
        partial_check_time = file_parser._partial_timestamp(check_time)
        self.assertEqual(check_time,
                         file_parser.full_timestamp(my_faddr,
                                                    partial_check_time))

if __name__ == '__main__':
  unittest.main()
