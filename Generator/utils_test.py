#!/usr/bin/python

import unittest

import utils

class CheckIncludeGuardName(unittest.TestCase):

  def testNames(self):
    self.assertEqual('AXI_H', utils.AsGuardName("axi.h"))
    self.assertEqual('A_XI_H', utils.AsGuardName("aXi.h"))
    self.assertEqual('AXI_H', utils.AsGuardName("Axi.h"))

    self.assertEqual('AXI_FOO_H', utils.AsGuardName("axiFoo.h"))
    self.assertEqual('AXI_FOO_BAR_H', utils.AsGuardName("axiFooBar.h"))

if __name__ == '__main__':
    unittest.main()
