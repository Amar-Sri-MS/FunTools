#!/usr/bin/python

import unittest

import utils

class CheckIncludeGuardName(unittest.TestCase):

  def testNames(self):
    self.assertEqual('__AXI_H__', utils.AsGuardName("axi.h"))
    self.assertEqual('__A_XI_H__', utils.AsGuardName("aXi.h"))
    self.assertEqual('__AXI_H__', utils.AsGuardName("Axi.h"))

    self.assertEqual('__AXI_FOO_H__', utils.AsGuardName("axiFoo.h"))
    self.assertEqual('__AXI_FOO_BAR_H__', utils.AsGuardName("axiFooBar.h"))

if __name__ == '__main__':
    unittest.main()
