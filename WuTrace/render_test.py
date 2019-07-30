#
# Test routines for render.py.
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.
#

import unittest

import render

class TestDisplay(unittest.TestCase):
    def testTruncatedSecs(self):
        self.assertEqual(0, render.truncated_secs(0))
        self.assertEqual(1, render.truncated_secs(1000000000))
        self.assertEqual(99, render.truncated_secs(99999999999))
        self.assertEqual(1, render.truncated_secs(101222222000))

    def testTruncatedUsecs(self):
        self.assertEqual(0, render.truncated_usecs(0))
        self.assertEqual(2, render.truncated_usecs(1000002000))
        self.assertEqual(222222, render.truncated_usecs(101222222000))

    def testTimeString(self):
        self.assertEqual('01.000002', render.time_string(1000002000))
        self.assertEqual('02.345678', render.time_string(102345678000))

    def testRangeString(self):
        self.assertEqual('01.000100 - 01.000256',
                         render.range_string(1000100000, 1000256000))

    def testDurationString(self):
        self.assertEqual('0 nsec', render.duration_string(0))
        self.assertEqual('500 nsec', render.duration_string(500))
        self.assertEqual('1.0 usec', render.duration_string(1000))
        self.assertEqual('100 usec', render.duration_string(100000))
        self.assertEqual('1.001 msec', render.duration_string(1001000))
        self.assertEqual('100.101 msec', render.duration_string(100101000))
        self.assertEqual('23.435678 sec', render.duration_string(23435678000))

class TestPercentile(unittest.TestCase):
    def testEdgeCases(self):
        self.assertEqual(None, render.percentile_index(1, 0))
        self.assertEqual(None, render.percentile_index(90, 0))
        self.assertEqual(None, render.percentile_index(99, 0))

        self.assertEqual(0, render.percentile_index(1, 1))
        self.assertEqual(0, render.percentile_index(90, 1))
        self.assertEqual(0, render.percentile_index(99, 1))

        self.assertEqual(0, render.percentile_index(1, 2))
        self.assertEqual(1, render.percentile_index(90, 2))
        self.assertEqual(1, render.percentile_index(99, 2))

        self.assertEqual(0, render.percentile_index(30, 3))
        self.assertEqual(1, render.percentile_index(50, 3))
        self.assertEqual(2, render.percentile_index(90, 3))
        self.assertEqual(2, render.percentile_index(99, 3))

    def testTen(self):
        self.assertEqual(0, render.percentile_index(1, 10))
        self.assertEqual(2, render.percentile_index(25, 10))
        self.assertEqual(4, render.percentile_index(50, 10))
        self.assertEqual(7, render.percentile_index(75, 10))
        self.assertEqual(8, render.percentile_index(90, 10))
        self.assertEqual(9, render.percentile_index(99, 10))

if __name__ == '__main__':
  unittest.main()
