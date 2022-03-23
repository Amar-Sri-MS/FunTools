#!/usr/bin/env python3

#
# Unit tests for the log scanner.
#

import io
import unittest

from log_scanner import DecisionGraph
from log_scanner import Edge
from log_scanner import LogScanner


class LogScannerTest(unittest.TestCase):
    """ Testcases for the log scanner """

    def setUp(self):
        self.log = io.StringIO()
        self.test_messages = ['taxman',
                              'eleanor rigby',
                              'im only sleeping',
                              'love you to',
                              'here there and everywhere']

        for msg in self.test_messages:
            self.log.write(msg + '\n')
        self.log.seek(0)

        self.scanner = LogScanner()

    def test_scan_for_single_message(self):
        """ Look for a single message in the log """
        msg = 'found song'

        g = DecisionGraph(0)
        g.add_edge('start',
                   Edge('end', [self.test_messages[0]]))
        g.add_report('end', msg)

        self.scanner.add_graph(g)

        reports = self.scanner.scan(self.log)
        self.assertEqual(1, len(reports))
        self.assertEqual(msg, reports[0][1])

    def test_scan_for_subsequence(self):
        """ Look for two messages in sequence """
        msg = 'found songs'

        g = DecisionGraph(0)
        g.add_edge('start',
                   Edge('t1', [self.test_messages[0]]))
        g.add_edge('t1',
                   Edge('end', [self.test_messages[3]]))
        g.add_report('end', msg)

        self.scanner.add_graph(g)

        reports = self.scanner.scan(self.log)
        self.assertEqual(1, len(reports))
        self.assertEqual(msg, reports[0][1])

    def test_scan_missing_sequence(self):
        """ Look for a sequence that does not exist """
        msg = 'should not be found'

        g = DecisionGraph(0)
        g.add_edge('start', Edge('t1', self.test_messages[0]))
        g.add_edge('t1', Edge('end', ['nowhere man']))
        g.add_report('end', msg)

        self.scanner.add_graph(g)

        reports = self.scanner.scan(self.log)
        self.assertEqual(0, len(reports))
