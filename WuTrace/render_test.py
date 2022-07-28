#
# Test routines for render.py.
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.
#

import unittest

import render
import event

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

    def testOutlierString(self):
        e1 = event.TraceEvent(1220007424, 1220007424, 'WU1', 'FA0:16:00[VP]')
        e2 = event.TraceEvent(1, 11, 'WU2', 'FA0:16:00[VP]')
        e3 = event.TraceEvent(1209000, 1209080, 'WU3', 'FA0:16:00[VP]')
        e4 = event.TraceEvent(28374832, 28374833, 'WU4', 'FA0:16:00[VP]')
        e5 = event.TraceEvent(0, 0, 'WU5', 'FA0:16:00[VP]')

        outlier_lis1 = [e1, e2, e3, e4, e5]
        outlier_lis2 = [e1]
        outlier_lis3 = []

        result_1 = 'WU1: %s: %s\nWU2: %s: %s\nWU3: %s: %s\nWU4: %s: %s\nWU5: %s: %s'
        result_1 = result_1 % (render.range_string(1220007424, 1220007424),
                    render.duration_string(0),
                    render.range_string(1, 11), render.duration_string(10),
                    render.range_string(1209000, 1209080),
                    render.duration_string(80),
                    render.range_string(28374832, 28374833),
                    render.duration_string(1),
                    render.range_string(0, 0), render.duration_string(0))
        result_2 = 'WU1: %s: %s' % (render.range_string(1220007424, 1220007424),
                    render.duration_string(0))
        result_3 = 'There are 0 outliers for this sequence.'

        self.assertEqual(result_1, (render.outlier_string(outlier_lis1)))
        self.assertEqual(result_2, (render.outlier_string(outlier_lis2)))
        self.assertEqual(result_3, (render.outlier_string(outlier_lis3)))

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
