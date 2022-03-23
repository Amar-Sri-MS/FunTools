#!/usr/bin/env python3
#
# Unit tests for the Samurai trace parser HTML generation.
#
# Robert Bowdidge, February 2018
#
# Copyright Fungible Inc. 2018

import unittest

import html_gen

class StandardDeviationTest(unittest.TestCase):
    def testSimple(self):
        self.assertEqual(0, html_gen.standard_deviation([]))
        self.assertEqual(0, html_gen.standard_deviation([1]))

        # If all values are equal, standard deviation is zero.
        self.assertEqual(0, html_gen.standard_deviation([1, 1]))

        self.assertAlmostEqual(1.414213562,
                               html_gen.standard_deviation([-1, 1]))

if __name__ == '__main__':
    unittest.main()
                       
                        
