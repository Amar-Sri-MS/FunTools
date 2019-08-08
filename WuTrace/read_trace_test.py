#!/usr/bin/env python2.7
#
# read_trace_test.py: unit tests for parsing binary trace events.
#

import struct
import unittest

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


if __name__ == '__main__':
  unittest.main()
