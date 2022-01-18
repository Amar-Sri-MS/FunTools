#!/usr/bin/env python2.7

import unittest

import missmapper


class TestFindRegion(unittest.TestCase):
    """ Unit tests for the find_region function """

    def test_within_region(self):
        regions = [(0x0, 0x2000, 'ostraya'),
                   (0x3000, 0x4000, 'britannia')]
        self.assertEqual('ostraya', missmapper.find_region(0x1000, regions))
        self.assertEqual('britannia', missmapper.find_region(0x3800, regions))

    def test_outside_region(self):
        regions = [(0x0, 0x2000, 'ostraya'),
                   (0x3000, 0x4000, 'britannia')]
        self.assertIsNone(missmapper.find_region(0x2800, regions))
