#
# Test routines for render.py.
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.
#

import unittest

import render

class TestDisplay(unittest.TestCase):
    def testTruncatedSecs(self):
        self.assertEqual(0, render.TruncatedSecs(0))
        self.assertEqual(1, render.TruncatedSecs(1000000))
        self.assertEqual(99, render.TruncatedSecs(99999999))
        self.assertEqual(1, render.TruncatedSecs(101222222))

    def testTruncatedUsecs(self):
        self.assertEqual(0, render.TruncatedUsecs(0))
        self.assertEqual(2, render.TruncatedUsecs(1000002))
        self.assertEqual(222222, render.TruncatedUsecs(101222222))
    
    def testTimeString(self):
        self.assertEqual('01.000002', render.TimeString(1000002))
        self.assertEqual('02.345678', render.TimeString(102345678))

    def testRangeString(self):
        self.assertEqual('01.000100 - 01.000256', render.RangeString(1000100, 1000256))

    def testDurationString(self):
        self.assertEqual('0 usec', render.DurationString(0))
        self.assertEqual('1 usec', render.DurationString(1))
        self.assertEqual('100 usec', render.DurationString(100))
        self.assertEqual('1.001 msec', render.DurationString(1001))
        self.assertEqual('100.101 msec', render.DurationString(100101))
        self.assertEqual('23.435678 sec', render.DurationString(23435678))

if __name__ == '__main__':
  unittest.main()

