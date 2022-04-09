#!/usr/bin/env python3
# Unit tests for generator.py
#
# Robert Bowdidge, August 8, 2016.
# Copyright Fungible Inc. 2016.

import tempfile
import unittest 

import generator
import parser

class TestTypes(unittest.TestCase):
  def testBitWidth(self):
    self.assertEqual(32, parser.TypeForName("uint32_t").BitWidth())
    self.assertEqual(32, parser.TypeForName("unsigned").BitWidth())
    self.assertEqual(8, parser.TypeForName("char").BitWidth())
    self.assertEqual(64, parser.TypeForName("double").BitWidth())
    self.assertEqual(8, parser.TypeForName("uint8_t").BitWidth())

    self.assertEqual(128, parser.ArrayTypeForName("uint8_t", 16).BitWidth())
    self.assertEqual(128, parser.ArrayTypeForName("uint64_t", 2).BitWidth())

  def testIsArray(self):
    self.assertTrue(parser.ArrayTypeForName("uint32_t", 4).IsArray())
    self.assertTrue(parser.ArrayTypeForName("char", 16).IsArray())

    self.assertFalse(parser.TypeForName("double").IsArray())
    self.assertFalse(parser.TypeForName("int").IsArray())

  def testHasEndianness(self):
      self.assertTrue(parser.TypeForName("__be32", linux_type=True).IsNoSwap())
      self.assertFalse(parser.TypeForName("uint32_t",
                                          linux_type=True).IsNoSwap())
      self.assertTrue(parser.TypeForName("__le16", linux_type=True).IsNoSwap())
      self.assertFalse(parser.TypeForName("uint8_t",
                                          linux_type=True).IsNoSwap())

      self.assertTrue(parser.ArrayTypeForName("__be32", 10,
                                              linux_type=True).IsNoSwap())
      self.assertFalse(parser.ArrayTypeForName("uint64_t", 10,
                                               linux_type=True).IsNoSwap())

  def testBaseName(self):
    self.assertEqual("uint32_t", 
                     parser.TypeForName("uint32_t").BaseName())
    self.assertEqual("uint32_t",
                     parser.ArrayTypeForName("uint32_t", 4).BaseName())

  def testCompare(self):
    self.assertTrue(parser.TypeForName("uint32_t").IsSameType(
        parser.TypeForName("uint32_t")))

    self.assertTrue(parser.TypeForName("uint8_t").IsSameType(
        parser.TypeForName("uint8_t")))

    self.assertFalse(parser.TypeForName("uint8_t").IsSameType(
                        parser.TypeForName("char")))

    self.assertTrue(parser.ArrayTypeForName("uint8_t", 4).IsSameType(
        parser.ArrayTypeForName("uint8_t", 4)))

    self.assertFalse(parser.ArrayTypeForName("char", 4).IsSameType(
        parser.ArrayTypeForName("uint16_t", 4)))
    self.assertFalse(parser.ArrayTypeForName("char", 4).IsSameType(
        parser.ArrayTypeForName("char", 8)))


class PrintingTest(unittest.TestCase):
  def testSimpleType(self):
    self.assertEqual('char', parser.TypeForName('char').ParameterTypeName())
    self.assertEqual('char[6]',
                     parser.ArrayTypeForName('char', 6).ParameterTypeName())


  def testStructType(self):
    s = parser.Struct('Bar', False)
    struct_array_type = parser.RecordArrayTypeForStruct(s, 4)
    self.assertEqual('struct Bar[4]', struct_array_type.ParameterTypeName())

  def testZeroLengthStructArrayType(self):
    s = parser.Struct('Bar', False)
    struct_array_type = parser.RecordArrayTypeForStruct(s, 0)
    self.assertEqual('struct Bar[0]', struct_array_type.ParameterTypeName())

  def testZeroLengthStructArrayType(self):
    s = parser.Struct('Bar', False)
    struct_array_type = parser.RecordArrayTypeForStruct(s, 0)
    self.assertEqual('struct Bar[]',
                     struct_array_type.ParameterTypeName(linux_type=True))



class PackedNameTest(unittest.TestCase):
  # Simple type to use for all fields - Field constructor does
  # need a type to look at.
  CHAR_TYPE = parser.TypeForName("char")

  def testPackedNameSimple(self):
    fields = [parser.Field('a', self.CHAR_TYPE, 0, 0),
              parser.Field('b', self.CHAR_TYPE, 0, 0)]
    self.assertEqual('a_to_b', generator.ChoosePackedFieldName(fields))

  def testPackedNameMultipleFields(self):
    fields = [parser.Field('a', self.CHAR_TYPE, 0, 0),
              parser.Field('c1', self.CHAR_TYPE, 0, 0),
              parser.Field('c2', self.CHAR_TYPE, 0, 0),
              parser.Field('c3', self.CHAR_TYPE, 0, 0),
              parser.Field('c4', self.CHAR_TYPE, 0, 0),
              parser.Field('b', self.CHAR_TYPE, 0, 0)]
    self.assertEqual('a_to_b', generator.ChoosePackedFieldName(fields))

  def testPackedNameFirstFieldReserved(self):
    fields = [parser.Field('rsvd_bitfield', self.CHAR_TYPE, 0, 0),
              parser.Field('b', self.CHAR_TYPE, 0, 0)]
    self.assertEqual('b_pack', generator.ChoosePackedFieldName(fields))

  def testPackedNameLastFieldReservedSingleField(self):
    fields = [parser.Field('a', self.CHAR_TYPE, 0, 0),
              parser.Field('reserved', self.CHAR_TYPE, 0, 0)]
    self.assertEqual('a_pack', generator.ChoosePackedFieldName(fields))

  def testPackedNameLastFieldReserved(self):
    fields = [parser.Field('a', self.CHAR_TYPE, 0, 0),
              parser.Field('b', self.CHAR_TYPE, 0, 0),
              parser.Field('reserved', self.CHAR_TYPE, 0, 0)]
    self.assertEqual('a_to_b', generator.ChoosePackedFieldName(fields))

  def testPackedNameReservedInMiddle(self):
    fields = [parser.Field('a', self.CHAR_TYPE, 0, 0),
              parser.Field('reserved_foo', self.CHAR_TYPE, 0, 0),
              parser.Field('b', self.CHAR_TYPE, 0, 0)]
    self.assertEqual('a_to_b', generator.ChoosePackedFieldName(fields))

  def testPackedNameMatchingPrefix(self):
    fields = [parser.Field('prefix_a', self.CHAR_TYPE, 0, 0),
              parser.Field('prefix_b', self.CHAR_TYPE, 0, 0),
              parser.Field('prefix_c', self.CHAR_TYPE, 0, 0)]
    self.assertEqual('prefix_pack', generator.ChoosePackedFieldName(fields))

  def testPackedNameMatchingPrefixFirstTermOnly(self):
    fields = [parser.Field('pre_fix_a', self.CHAR_TYPE, 0, 0),
              parser.Field('pre_fix_b', self.CHAR_TYPE, 0, 0),
              parser.Field('pre_fix_c', self.CHAR_TYPE, 0, 0)]
    self.assertEqual('pre_pack', generator.ChoosePackedFieldName(fields))

  def testPackedNameMatchingPrefixSimilarNames(self):
    fields = [parser.Field('prefix_a', self.CHAR_TYPE, 0, 0),
              parser.Field('pre_b', self.CHAR_TYPE, 0, 0),
              parser.Field('pre_c', self.CHAR_TYPE, 0, 0)]
    self.assertEqual('prefix_a_to_pre_c',
                     generator.ChoosePackedFieldName(fields))

  def testPackedNameMatchingPrefixReservedFieldAtStart(self):
    fields = [parser.Field('reserved', self.CHAR_TYPE, 0, 0),
              parser.Field('pre_b', self.CHAR_TYPE, 0, 0),
              parser.Field('pre_c', self.CHAR_TYPE, 0, 0)]
    self.assertEqual('pre_pack',
                     generator.ChoosePackedFieldName(fields))

  def testPackedNameMatchingPrefixReservedFieldAtEnd(self):
    fields = [parser.Field('pre_a', self.CHAR_TYPE, 0, 0),
              parser.Field('pre_b', self.CHAR_TYPE, 0, 0),
              parser.Field('reserved', self.CHAR_TYPE, 0, 0)]
    self.assertEqual('pre_pack',
                     generator.ChoosePackedFieldName(fields))


class StringTest(unittest.TestCase):
  def testDeclarationString(self):
    inner = parser.Struct('container', False)

    struct = parser.Struct('my_struct', False)
    field1 = parser.Field('simple', parser.TypeForName('uint32_t'), 0, 32)
    field2 = parser.Field('array', parser.ArrayTypeForName('uint8_t', 4),
                          32, 32)
    field3 = parser.Field('c', parser.RecordTypeForStruct(inner),
                          64, 64)
    struct.AddField(field1)
    struct.AddField(field2)
    struct.AddField(field3)

    self.assertEqual('struct my_struct {\n'
                     '  uint32_t simple;\n'
                     '  uint8_t array[4];\n'
                     '\n'  # Blank line between flits.
                     '  struct container c;\n'
                     '}', struct.DefinitionString())
    self.assertEqual('struct my_struct', struct.DeclarationString())

    self.assertEqual('uint32_t simple;\n', field1.DefinitionString())
    self.assertEqual('uint32_t simple', field1.DeclarationString())

    self.assertEqual('uint8_t array[4];\n', field2.DefinitionString())
    self.assertEqual('uint8_t array[4]', field2.DeclarationString())

    self.assertEqual('struct container c;\n', field3.DefinitionString())
    self.assertEqual('struct container c', field3.DeclarationString())

    container_type = parser.RecordTypeForStruct(inner)
    self.assertEqual('(struct container)', container_type.CastString())
    uint8_type = parser.TypeForName('uint8_t')
    self.assertEqual('(uint8_t)', uint8_type.CastString())

class DefaultTypeTest(unittest.TestCase):

  def testSimple(self):
    self.assertEqual('uint8_t',
                     parser.DefaultTypeForWidth(8, 8).ParameterTypeName())

    self.assertEqual('uint16_t',
                     parser.DefaultTypeForWidth(8, 3).ParameterTypeName())

    self.assertEqual('uint16_t',
                     parser.DefaultTypeForWidth(8, 6).ParameterTypeName())

    self.assertEqual('uint32_t',
                     parser.DefaultTypeForWidth(8, 14).ParameterTypeName())

    self.assertEqual('uint64_t',
                     parser.DefaultTypeForWidth(8, 31).ParameterTypeName())

    self.assertEqual('uint32_t',
                     parser.DefaultTypeForWidth(12, 8).ParameterTypeName())

    self.assertEqual('uint32_t',
                     parser.DefaultTypeForWidth(16, 10).ParameterTypeName())

    self.assertEqual('uint32_t',
                     parser.DefaultTypeForWidth(16, 4).ParameterTypeName())


if __name__ == '__main__':
    unittest.main()
