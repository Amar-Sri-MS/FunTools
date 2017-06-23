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

class TestReadableList(unittest.TestCase):
  def testSimple(self):
    self.assertEqual("", utils.ReadableList(None))

    self.assertEqual("", utils.ReadableList([]))
    self.assertEqual("", utils.ReadableList([]))
    self.assertEqual("a", utils.ReadableList(["a"]))
    self.assertEqual("a and b", utils.ReadableList(["a", "b"]))
    self.assertEqual("a, c, and d", utils.ReadableList(["a", "c", "d"]))


class TestParseInt(unittest.TestCase):
  def testSimple(self):
      self.assertEqual(32, utils.ParseInt("32"))
      self.assertEqual(-32, utils.ParseInt("-32"))
      self.assertEqual(32, utils.ParseInt("0x20"))
      self.assertEqual(1, utils.ParseInt("0x0000001"))

      self.assertEqual(8, utils.ParseInt("0b01000"))
      self.assertEqual(15, utils.ParseInt("0b1111"))

  def testInvalid(self):
    self.assertIsNone(utils.ParseInt("foo"))
    self.assertIsNone(utils.ParseInt("0xlose"))
    self.assertIsNone(utils.ParseInt("0xlose"))
    self.assertIsNone(utils.ParseInt("0x0x"))


class TestStripComment(unittest.TestCase):
  def testSimple(self):
     self.assertEqual("Foo", utils.StripComment("// Foo"))
     self.assertEqual("Foo", utils.StripComment("/* Foo */"))
     self.assertEqual("", utils.StripComment("//"))
     self.assertEqual("", utils.StripComment("/* */"))
                    
if __name__ == '__main__':
    unittest.main()
