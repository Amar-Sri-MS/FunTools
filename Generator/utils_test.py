#!/usr/bin/python3

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


class TestParseBitSpec(unittest.TestCase):
  def testSimple(self):
    self.assertEqual((1, 63, 50), utils.ParseBitSpec('1 63:50'))
    self.assertEqual((1, 63, 63), utils.ParseBitSpec('1 63'))
    self.assertEqual((1, 63, 63), utils.ParseBitSpec('1 63:63'))
    self.assertEqual((1, 21, 21), utils.ParseBitSpec('1 0x15:0x15'))

  def testBadStrings(self):
    self.assertEqual(None, utils.ParseBitSpec('A 0:0'))
    self.assertEqual(None, utils.ParseBitSpec('1 -1'))
    self.assertEqual(None, utils.ParseBitSpec('-1 1'))
    self.assertEqual(None, utils.ParseBitSpec('0 1,2'))

class TestCleanComment(unittest.TestCase):
  def testEmpty(self):
    self.assertEqual('', utils.AsComment('  '))
  def testSingleLine(self):
    self.assertEqual('/* a */', utils.AsComment('a'))

  def testMultiLine(self):
    self.assertEqual('/*\n * a\n * b\n */', utils.AsComment('a\nb\n'))


class TestBitPatternString(unittest.TestCase):
  def testSimple(self):

    self.assertEqual('0', utils.BitPatternString(0, 1))
    self.assertEqual('00', utils.BitPatternString(0, 2))
    self.assertEqual('0000', utils.BitPatternString(0, 4))
    self.assertEqual('1001', utils.BitPatternString(9, 4))
    self.assertEqual('1101', utils.BitPatternString(13, 4))
    self.assertEqual('0001', utils.BitPatternString(1, 4))


class TestValidIdentifier(unittest.TestCase):
  def testSimple(self):
    self.assertTrue(utils.IsValidCIdentifier('a'))
    self.assertTrue(utils.IsValidCIdentifier('_'))
    self.assertTrue(utils.IsValidCIdentifier('_ab123_'))
    self.assertTrue(utils.IsValidCIdentifier('_1'))

    self.assertFalse(utils.IsValidCIdentifier('^'))
    self.assertFalse(utils.IsValidCIdentifier('1a'))
    self.assertFalse(utils.IsValidCIdentifier(''))
    self.assertFalse(utils.IsValidCIdentifier('0'))
    self.assertFalse(utils.IsValidCIdentifier('-'))

    self.assertFalse(utils.IsValidCIdentifier('default'))
    self.assertFalse(utils.IsValidCIdentifier('private'))

class TestAsLine(unittest.TestCase):
  def testSimple(self):
    self.assertEqual('a b c', utils.AsLine('a\nb\nc'))
    self.assertEqual('', utils.AsLine(''))

class TestAsLower(unittest.TestCase):
  def testSimple(self):
    self.assertEqual('abcd', utils.AsLower('Abcd'))
    self.assertEqual('aaaa bbbb ccc', utils.AsLower('AAAA BbBb cCc'))

class TestIndent(unittest.TestCase):
  def testSimple(self):
    self.assertEqual('  foo\n', utils.Indent('foo', 2))
    self.assertEqual('    a\n    b\n', utils.Indent('a\nb', 4))
    self.assertEqual('  a\n  b\n', utils.Indent('a\nb\n', 2))
    self.assertEqual('    a\n    b\n    c\n', utils.Indent('a\nb\nc', 4))


if __name__ == '__main__':
    unittest.main()
