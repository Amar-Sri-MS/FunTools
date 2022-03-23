#
# Tests for parse_funos_log.py
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import json
import io
import unittest

import parse_funos_log
from parse_funos_log import LogParser


def decode_json(json_str):
    return json.loads(json_str)


class TestLogParser(unittest.TestCase):

    def setUp(self):
        self.parser = LogParser()

    def test_parse_empty_line(self):
        self.parser.parse_line('');
        self.assertIsNone(self.parser.json_str())

    def test_parse_nonmatching_line(self):
        self.parser.parse_line('[0.140573 8.0.0] INFO fun_malloc '
                               '"Malloc agent (coherent) for log_size 6 will '
                               'run on FA6:14:0[VP]"')
        self.assertIsNone(self.parser.json_str())

    def test_parse_matching_line(self):
        self.parser.parse_line('[2.457574 8.0.0] INFO nucleus '
                               '"data  FA6:26:0[VP] sent 21012, '
                               'recv 20883 WUs 3.1800000%	'
                               '[wu 169/irq 0/unk 0]"')
        result = self._get_parser_result()
        self.assertEqual(1, len(result), 'list length')
        self.check_faddr(0, 6, 26, result)
        self.check_metrics(0, 21012, 20883, 3.18, result)

    def _get_parser_result(self):
        res_str = self.parser.json_str()
        return decode_json(res_str)

    def test_parse_multiple_matching_lines(self):
        self.parser.parse_line('[2.458104 8.0.0] INFO nucleus '
                               '"ctrl  FA7:17:0[VP] sent 39, '
                               'recv 41 WUs 0.32000000%	'
                               '[wu 0/irq 0/unk 0]"')
        self.parser.parse_line('[2.458151 8.0.0] INFO nucleus '
                               '"ctrl  FA8:20:0[VP] sent 45, '
                               'recv 0 WUs 0.31000000%	'
                               '[wu 0/irq 0/unk 0]"')
        result = self._get_parser_result()
        self.assertEqual(2, len(result), 'list length')
        self.check_faddr(0, 7, 17, result)
        self.check_faddr(1, 8, 20, result)
        self.check_metrics(0, 39, 41, 0.32, result)
        self.check_metrics(1, 45, 0, 0.31, result)

    def test_parse_is_insensitive_to_more_whitespace(self):
        self.parser.parse_line('[2.458104   8.0.0]   INFO    nucleus   '
                               '"  ctrl    FA7:17:0  [VP]   sent   39  ,   '
                               '  recv   41   WUs    0.32000000%	   '
                               '  [wu   0/  irq    0/    unk   0]   "')
        result = self._get_parser_result()
        self.check_metrics(0, 39, 41, 0.32, result)

    def test_parse_handles_percentage_without_decimal_place(self):
        """ FunOS may print 21% and not 21.000% """
        self.parser.parse_line('[2.458104 8.0.0] INFO nucleus '
                               '"ctrl  FA7:17:0[VP] sent 39, '
                               'recv 41 WUs 5%	'
                               '[wu 0/irq 0/unk 0]"')
        result = self._get_parser_result()
        self.check_metrics(0, 39, 41, 5, result)

    def test_parse_excludes_unfinished_line(self):
        """
        One possible mode of failure is that the log terminates
        unexpectedly.
        """
        self.parser.parse_line('[2.458104   8.0.0]   INFO    nucleus   '
                               '"  ctrl    FA7:17:0  [VP]   sent   39  ,   '
                               '  recv   	   "')
        self.assertIsNone(self.parser.json_str())

    def check_faddr(self, entry_index, gid, lid, obj):
        entry = obj[entry_index]
        self.assertEqual(gid, entry['faddr']['gid'], 'gid')
        self.assertEqual(lid, entry['faddr']['lid'], 'lid')

    def check_metrics(self, entry_index, sent, recvd, pct, obj):
        entry = obj[entry_index]
        self.assertEqual(sent, entry['wus_sent'], 'wus_sent')
        self.assertEqual(recvd, entry['wus_recvd'], 'wus_recvd')
        self.assertAlmostEqual(pct, entry['util_pct'], 'util_pct')


class TestParseLogFileFunction(unittest.TestCase):
    """
    Tests the parse_log_file function, which covers most
    of the logic except for the opening and closing of
    files.
    """

    def test_partial_log(self):
        log = io.StringIO(
            '[0.000518 8.0.0] [32mINFO nucleus[0m "data              '
            '0xa800000000905900 0xa800000000fdded0 ~7009 KB" \n'
            
            '[0.140346 8.0.0] INFO nucleus "shutdown request from '
            'bootstrap with timeout(fun_time) 3900000000"\n'
            
            '[2.457089 8.0.0] INFO nucleus "data  FA6:16:0[VP] sent 3476, '
            'recv 2689 WUs 0.8%	[wu 135/irq 0/unk 0]\n"'
            
            '[2.457774 8.0.0] INFO nucleus "data  FA6:30:0[VP] sent 11342, '
            'recv 11312 WUs 10.689999%	[wu 446/irq 0/unk 0]\n"'
        )

        result = io.StringIO()
        parse_funos_log.parse_log_file(log, result)
        result.seek(0)
        obj = decode_json(result.read())
        self.assertEqual(2, len(obj), 'number of stat entries')
