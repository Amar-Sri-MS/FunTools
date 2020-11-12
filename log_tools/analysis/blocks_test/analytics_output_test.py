#!/usr/bin/env python3

#
# Unit tests for the analytics output block
#

import hashlib
import unittest

from blocks.analytics_output import AnalyticsOutput
from blocks_test.common import lines_to_iterable


class AnalyticsOutputTest(unittest.TestCase):
    """ Unit tests for the Analytics Output block """

    def setUp(self):
        self.block = AnalyticsOutput()

    def test_check_for_duplicates(self):
        """ check if duplicate log entries are found """
        lines = ['[8.3.0] "opcode": "VOL_ADMIN_OPCODE_STATUS",',
                 '[physical_resources.go:1771] PDT m=+606846.835741524 eror c8:2c:2b:00:0a:28',
                 '[8.3.0] "opcode": "VOL_ADMIN_OPCODE_STATUS",']
        hashval = hashlib.md5(lines[0].encode('utf-8')).digest()
        expected_count = 2

        self.block.check_for_duplicate_entry(lines_to_iterable(lines))

        duplicated_entry_count = self.block.duplicate_entries[hashval]['count']
        self.assertEqual(expected_count, duplicated_entry_count)

    def test_most_duplicated_entries(self):
        """ check if the most duplicates entries are sorted """
        lines = ['[8.3.0] "opcode": "VOL_ADMIN_OPCODE_STATUS",',
                 '[physical_resources.go:1771] PDT m=+606846.835741524 eror c8:2c:2b:00:0a:28',
                 '[8.3.0] "opcode": "VOL_ADMIN_OPCODE_STATUS",']

        # Checking for duplicates
        self.block.check_for_duplicate_entry(lines_to_iterable(lines))
        # Sorting the duplicates and getting the most duplicated entries
        most_duplicated_entries = self.block.get_most_duplicated_entries()

        expected = ['[8.3.0] "opcode": "VOL_ADMIN_OPCODE_STATUS",',
                    '[physical_resources.go:1771] PDT m=+606846.835741524 eror c8:2c:2b:00:0a:28']
        most_duplicated_lines = [entry['msg']['line'] for entry in most_duplicated_entries]

        self.assertListEqual(expected, most_duplicated_lines)