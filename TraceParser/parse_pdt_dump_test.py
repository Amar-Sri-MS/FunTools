#!/usr/bin/env python3

#
# Unit tests for pdtrace raw data parser.
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import unittest

from io import BytesIO

import parse_pdt_dump


class TestDequeuerOutputFormat(unittest.TestCase):

    def test_frame_index_is_prepended(self):
        m = b'DEADBEEFCAFEBABE12345678FFFFFFFF00000000111111112222222233333333'
        data = BytesIO(m)

        result = parse_pdt_dump.generate_dqr_contents(data)

        frame_index0 = result[0:4]
        self.assertEqual(b'\x00\x00\x00\x00', frame_index0, 'index 0')
        frame_index1 = result[36:40]
        self.assertEqual(b'\x00\x00\x00\x01', frame_index1, 'index 1')

    def test_frame_contents_are_reversed_8_byte_chunks(self):
        m = b'00000000AAAAAAAACCCCCCCCFFFFFFFF'
        data = BytesIO(m)

        result = parse_pdt_dump.generate_dqr_contents(data)
        self.assertEqual(b'FFFFFFFF', result[4:12], 'first 8 bytes')
        self.assertEqual(b'CCCCCCCC', result[12:20], 'second 8 bytes')
        self.assertEqual(b'AAAAAAAA', result[20:28], 'third 8 bytes')
        self.assertEqual(b'00000000', result[28:36], 'final 8 bytes')

