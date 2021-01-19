#!/usr/bin/env python3

#
# Unit tests for the analytics output block
#

import hashlib
import unittest

from blocks.analytics_output import AnalyticsOutput
from blocks_test.common import lines_to_iterable, msg_tuple_to_dict


class AnalyticsOutputTest(unittest.TestCase):
    """ Unit tests for the Analytics Output block """

    def setUp(self):
        self.block = AnalyticsOutput()
        cfg = {
            'env': {
                'build_id': 'analytics_output_test'
            },
            'dir': 'view/analytics/log_${build_id}',
            'anchor_files': [
                'config/anchors.json'
            ],
            'anchor_keys': None
        }
        self.block.set_config(cfg)

    def test_check_for_duplicates(self):
        """ check if duplicate log entries are found """
        lines = ['[8.3.0] "opcode": "VOL_ADMIN_OPCODE_STATUS",',
                 '[physical_resources.go:1771] PDT m=+606846.835741524 eror c8:2c:2b:00:0a:28',
                 '[8.3.0] "opcode": "VOL_ADMIN_OPCODE_STATUS",']
        hashval = hashlib.md5(lines[0].encode('utf-8')).digest()
        expected_count = 2

        for it in lines_to_iterable(lines):
            msg_block = msg_tuple_to_dict(it)
            self.block.check_for_duplicate_entry(msg_block)

        duplicated_entry_count = self.block.duplicate_entries[hashval]['count']
        self.assertEqual(expected_count, duplicated_entry_count)

    def test_most_duplicated_entries(self):
        """ check if the most duplicates entries are sorted """
        lines = ['[8.3.0] "opcode": "VOL_ADMIN_OPCODE_STATUS",',
                 '[physical_resources.go:1771] PDT m=+606846.835741524 eror c8:2c:2b:00:0a:28',
                 '[8.3.0] "opcode": "VOL_ADMIN_OPCODE_STATUS",']

        # Checking for duplicates
        for it in lines_to_iterable(lines):
            msg_block = msg_tuple_to_dict(it)
            self.block.check_for_duplicate_entry(msg_block)
        # Sorting the duplicates and getting the most duplicated entries
        most_duplicated_entries = self.block.get_most_duplicated_entries()

        expected = ['[8.3.0] "opcode": "VOL_ADMIN_OPCODE_STATUS",',
                    '[physical_resources.go:1771] PDT m=+606846.835741524 eror c8:2c:2b:00:0a:28']
        most_duplicated_lines = [entry['msg']['line'] for entry in most_duplicated_entries]

        self.assertListEqual(expected, most_duplicated_lines)

    def test_check_for_anchor_match(self):
        """ check if anchor matches are found """
        lines = [
            '[5.413910 8.0.0][kernel] Welcome to FunOS!',
            '[1596620459.958822 5.5.2] NOTICE tcp "flow[0x6/0x0/0x000:tcp:tcp_hton_f/0x2/0xa80000002ec86000@FA2:14:1[VP]]: net: aborting: TCP_FSM_STATE_ESTABLISHED, from (remote) 15.149.1.2:1125 to (local) 15.139.2.2:1099 reason 104 (rcvnxt 865474991 rcvwnd 259168 rcvadv 261920 coalesce_plen 0)"'
        ]
        expected_count = 2
        expected_descriptions = [
            'Welcome to FunOS',
            'FunTCP connection aborted State: TCP_FSM_STATE_ESTABLISHED Remote: 5.149.1.2:1125 Local 15.139.2.2:1099 Reason: 104'
        ]

        # Checking for anchor matches
        for it in lines_to_iterable(lines):
            msg_block = msg_tuple_to_dict(it)
            self.block.check_for_anchor_match(msg_block)

        anchor_descriptions = [anchor_match.short for anchor_match in self.block.anchor_matches]

        self.assertEqual(expected_count, len(self.block.anchor_matches))
        self.assertListEqual(expected_descriptions, anchor_descriptions)