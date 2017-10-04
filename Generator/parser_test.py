# Unit tests for generator.py
#
# Robert Bowdidge, August 8, 2016.
# Copyright Fungible Inc. 2016.

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

  def testBaseName(self):
    self.assertEqual("uint32_t", 
                     parser.TypeForName("uint32_t").BaseName())
    self.assertEqual("uint32_t",
                     parser.ArrayTypeForName("uint32_t", 4).BaseName())

  def testCompare(self):
    self.assertEqual(parser.TypeForName("uint32_t"),
                     parser.TypeForName("uint32_t"))
    self.assertEqual(parser.TypeForName("uint8_t"),
                     parser.TypeForName("uint8_t"))

    self.assertNotEqual(parser.TypeForName("uint8_t"),
                        parser.TypeForName("char"))

    self.assertEqual(parser.ArrayTypeForName("uint8_t", 4),
                     parser.ArrayTypeForName("uint8_t", 4))

    self.assertNotEqual(parser.ArrayTypeForName("char", 4),
                        parser.ArrayTypeForName("uint16_t", 4))
    self.assertNotEqual(parser.ArrayTypeForName("char", 4),
                        parser.ArrayTypeForName("char", 8))


class PrintingTest(unittest.TestCase):
  def testSimpleType(self):
    self.assertEqual('char', parser.TypeForName('char').DeclarationType())
    self.assertEqual('char[6]',
                     parser.ArrayTypeForName('char', 6).DeclarationType())


  def testStructType(self):
    s = parser.Struct('Bar', False)
    struct_array_type = parser.RecordArrayTypeForStruct(s, 4)
    self.assertEqual('Bar[4]', struct_array_type.DeclarationType())

  def testZeroLengthStructArrayType(self):
    s = parser.Struct('Bar', False)
    struct_array_type = parser.RecordArrayTypeForStruct(s, 0)
    self.assertEqual('Bar[0]', struct_array_type.DeclarationType())


class PackedNameTest(unittest.TestCase):

  def testPackedNameSimple(self):
    fields = [parser.Field('a', None, 0, 0),
              parser.Field('b', None, 0, 0)]
    self.assertEqual('a_to_b', generator.ChoosePackedFieldName(fields))

  def testPackedNameMultipleFields(self):
    fields = [parser.Field('a', None, 0, 0),
              parser.Field('c1', None, 0, 0),
              parser.Field('c2', None, 0, 0),
              parser.Field('c3', None, 0, 0),
              parser.Field('c4', None, 0, 0),
              parser.Field('b', None, 0, 0)]
    self.assertEqual('a_to_b', generator.ChoosePackedFieldName(fields))

  def testPackedNameFirstFieldReserved(self):
    fields = [parser.Field('rsvd_bitfield', None, 0, 0),
              parser.Field('b', None, 0, 0)]
    self.assertEqual('b_pack', generator.ChoosePackedFieldName(fields))

  def testPackedNameLastFieldReservedSingleField(self):
    fields = [parser.Field('a', None, 0, 0),
              parser.Field('reserved', None, 0, 0)]
    self.assertEqual('a_pack', generator.ChoosePackedFieldName(fields))

  def testPackedNameLastFieldReserved(self):
    fields = [parser.Field('a', None, 0, 0),
              parser.Field('b', None, 0, 0),
              parser.Field('reserved', None, 0, 0)]
    self.assertEqual('a_to_b', generator.ChoosePackedFieldName(fields))

  def testPackedNameReservedInMiddle(self):
    fields = [parser.Field('a', None, 0, 0),
              parser.Field('reserved_foo', None, 0, 0),
              parser.Field('b', None, 0, 0)]
    self.assertEqual('a_to_b', generator.ChoosePackedFieldName(fields))

  def testPackedNameMatchingPrefix(self):
    fields = [parser.Field('prefix_a', None, 0, 0),
              parser.Field('prefix_b', None, 0, 0),
              parser.Field('prefix_c', None, 0, 0)]
    self.assertEqual('prefix_pack', generator.ChoosePackedFieldName(fields))

  def testPackedNameMatchingPrefixFirstTermOnly(self):
    fields = [parser.Field('pre_fix_a', None, 0, 0),
              parser.Field('pre_fix_b', None, 0, 0),
              parser.Field('pre_fix_c', None, 0, 0)]
    self.assertEqual('pre_pack', generator.ChoosePackedFieldName(fields))

  def testPackedNameMatchingPrefixSimilarNames(self):
    fields = [parser.Field('prefix_a', None, 0, 0),
              parser.Field('pre_b', None, 0, 0),
              parser.Field('pre_c', None, 0, 0)]
    self.assertEqual('prefix_a_to_pre_c',
                     generator.ChoosePackedFieldName(fields))

  def testPackedNameMatchingPrefixReservedFieldAtStart(self):
    fields = [parser.Field('reserved', None, 0, 0),
              parser.Field('pre_b', None, 0, 0),
              parser.Field('pre_c', None, 0, 0)]
    self.assertEqual('pre_pack',
                     generator.ChoosePackedFieldName(fields))

  def testPackedNameMatchingPrefixReservedFieldAtEnd(self):
    fields = [parser.Field('pre_a', None, 0, 0),
              parser.Field('pre_b', None, 0, 0),
              parser.Field('reserved', None, 0, 0)]
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

if __name__ == '__main__':
    unittest.main()
