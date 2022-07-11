#!/usr/bin/env python3

#
# Unit tests for coverage processing.
#
# Copyright (c) 2019 Fungible Inc. All rights reserved.
#

import json
import io
import struct
import unittest

import process_cov_samples


class TestGCDAConverter(unittest.TestCase):
    """
    Sanity checks for the GCDA converter.
    """

    def setUp(self):
        with open('testdata/test.json') as fh:
            cov_json = json.load(fh)

        self.assertIsNotNone(cov_json)
        self.converter = process_cov_samples.GCDAConverter(cov_json)

    def test_correct_filename(self):
        filename, _ = self.converter.generate_file_contents()
        self.assertEqual('testoutput/services/malloc/fun_maheap.gcda',
                         filename)

    def test_file_contents(self):
        _, contents = self.converter.generate_file_contents()
        buf = io.StringIO(contents)

        # These checks read the buffer, and therefore modify its state (the
        # buffer is a file-like object)
        self._check_magic(buf)
        self._check_version(buf)
        self._check_timestamp(buf, 2927061476)
        self._check_first_function(buf)

    def _check_magic(self, buf):
        magic = self._read_unsigned(buf)
        self.assertEqual(process_cov_samples.GCOV_DATA_MAGIC, magic)

    def _check_version(self, buf):
        version = self._read_unsigned(buf)
        self.assertEqual(process_cov_samples.GCOV_VERSION, version)

    def _check_timestamp(self, buf, expected_timestamp):
        val = self._read_unsigned(buf)
        self.assertEqual(expected_timestamp, val)

    def _read_unsigned(self, buf):
        s = buf.read(4)
        val = struct.unpack('I', s)[0]
        return val

    def _check_first_function(self, buf):
        tag = self._read_unsigned(buf)
        length = self._read_unsigned(buf)

        self.assertEqual(process_cov_samples.GCOV_TAG_FUNCTION, tag)
        self.assertEqual(process_cov_samples.GCOV_FUNCTION_LEN, length)

        # skip testing the ident and checksums in the belief we cannot mess
        # those up
        self._read_unsigned(buf)
        self._read_unsigned(buf)
        self._read_unsigned(buf)

        self._check_first_counter_group(buf)

    def _check_first_counter_group(self, buf):
        tag = self._read_unsigned(buf)
        length = self._read_unsigned(buf)

        self.assertEqual(0x01a10000, tag)
        self.assertEqual(60, length)
