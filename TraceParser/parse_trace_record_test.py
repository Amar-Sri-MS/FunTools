#!/usr/bin/env python3

#
# Various tests for the trace record parsing.
#
# Copyright (c) 2021 Fungible Inc.  All rights reserved.
#

import io
import struct
import unittest

import parse_trace_record


class TestTraceRecordGeneration(unittest.TestCase):
    """ Checks various aspects of trace record decoding """

    def test_header_num_records_decoding(self):
        """ Ensure the number of records is decoded correctly """
        vpnum = 34
        num_records = [3, 5, 13]

        pages = bytes()
        for num in num_records:
            pages += self.make_fake_trace_page(vpnum, num)
        fh = io.BytesIO(pages)
        record_iter = parse_trace_record.generate_trace_record(fh)

        count = 0
        for record in record_iter:
            count += 1
        self.assertEqual(sum(num_records), count)

    def make_fake_trace_page(self, vpnum, num_records):
        """ Concocts a fake trace page (a bytes-like object) """
        page = struct.pack('>H4xH56x', num_records, vpnum)

        record = b'deadbeef' * 8
        page += (record * 255)
        self.assertEqual(parse_trace_record.TRACE_PAGE_LEN, len(page))
        return page

    def test_header_vpnum_decoding(self):
        """ Ensure the vpnum is decoded correctly """
        vpnum = 46

        page = self.make_fake_trace_page(vpnum, 2)
        fh = io.BytesIO(page)
        record_iter = parse_trace_record.generate_trace_record(fh)

        for record_vp, record in record_iter:
            self.assertEqual(vpnum, record_vp)
