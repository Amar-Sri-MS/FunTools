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
        self.assertEqual(1, render.TruncatedSecs(1000000000))
        self.assertEqual(99, render.TruncatedSecs(99999999999))
        self.assertEqual(1, render.TruncatedSecs(101222222000))

    def testTruncatedUsecs(self):
        self.assertEqual(0, render.TruncatedUsecs(0))
        self.assertEqual(2, render.TruncatedUsecs(1000002000))
        self.assertEqual(222222, render.TruncatedUsecs(101222222000))
    
    def testTimeString(self):
        self.assertEqual('01.000002', render.TimeString(1000002000))
        self.assertEqual('02.345678', render.TimeString(102345678000))

    def testRangeString(self):
        self.assertEqual('01.000100 - 01.000256',
                         render.RangeString(1000100000, 1000256000))

    def testDurationString(self):
        self.assertEqual('0 usec', render.DurationString(0))
        self.assertEqual('0 usec', render.DurationString(500))
        self.assertEqual('1 usec', render.DurationString(1000))
        self.assertEqual('100 usec', render.DurationString(100000))
        self.assertEqual('1.001 msec', render.DurationString(1001000))
        self.assertEqual('100.101 msec', render.DurationString(100101000))
        self.assertEqual('23.435678 sec', render.DurationString(23435678000))

class TestPercentile(unittest.TestCase):
    def testEdgeCases(self):
        self.assertEqual(None, render.PercentileIndex(1, 0))
        self.assertEqual(None, render.PercentileIndex(90, 0))
        self.assertEqual(None, render.PercentileIndex(99, 0))

        self.assertEqual(0, render.PercentileIndex(1, 1))
        self.assertEqual(0, render.PercentileIndex(90, 1))
        self.assertEqual(0, render.PercentileIndex(99, 1))

        self.assertEqual(0, render.PercentileIndex(1, 2))
        self.assertEqual(1, render.PercentileIndex(90, 2))
        self.assertEqual(1, render.PercentileIndex(99, 2))

        self.assertEqual(0, render.PercentileIndex(30, 3))
        self.assertEqual(1, render.PercentileIndex(50, 3))
        self.assertEqual(2, render.PercentileIndex(90, 3))
        self.assertEqual(2, render.PercentileIndex(99, 3))

    def testTen(self):
        self.assertEqual(0, render.PercentileIndex(1, 10))
        self.assertEqual(2, render.PercentileIndex(25, 10))
        self.assertEqual(4, render.PercentileIndex(50, 10))
        self.assertEqual(7, render.PercentileIndex(75, 10))
        self.assertEqual(8, render.PercentileIndex(90, 10))
        self.assertEqual(9, render.PercentileIndex(99, 10))

if __name__ == '__main__':
  unittest.main()

