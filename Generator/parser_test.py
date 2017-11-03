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

class DefaultTypeTest(unittest.TestCase):

  def testSimple(self):
    self.assertEqual('uint8_t',
                     parser.DefaultTypeForWidth(8, 8).DeclarationType())

    self.assertEqual('uint16_t',
                     parser.DefaultTypeForWidth(8, 3).DeclarationType())

    self.assertEqual('uint16_t',
                     parser.DefaultTypeForWidth(8, 6).DeclarationType())

    self.assertEqual('uint32_t',
                     parser.DefaultTypeForWidth(8, 14).DeclarationType())

    self.assertEqual('uint64_t',
                     parser.DefaultTypeForWidth(8, 31).DeclarationType())

    self.assertEqual('uint32_t',
                     parser.DefaultTypeForWidth(12, 8).DeclarationType())

    self.assertEqual('uint32_t',
                     parser.DefaultTypeForWidth(16, 10).DeclarationType())

    self.assertEqual('uint32_t',
                     parser.DefaultTypeForWidth(16, 4).DeclarationType())


class YAMLParserTest(unittest.TestCase):
  def testEnum(self):
    input = """
---
DESCRIPTION: ' Enums used in NU'
ENUMLIST:
  - DESCRIPTION: Ingress Stream Type Definition
    ENUMS:
      - DESCRIPTION: SF
        NAME: SF
        VALUE: 0
      - DESCRIPTION: CX
        NAME: CX
        VALUE: 1
      - DESCRIPTION: SX or DX
        NAME: SX_DX
        VALUE: 2
      - DESCRIPTION: Reserved
        NAME: RESV
        VALUE: 3
    NAME: nu_ig_stream_type_t
    WIDTH: 2
  - DESCRIPTION: Switch Type Definition
    ENUMS:
      - DESCRIPTION: SF
        NAME: SF
        VALUE: 0
      - DESCRIPTION: SX
        NAME: SX
        VALUE: 1
      - DESCRIPTION: DX
        NAME: DX
        VALUE: 2
      - DESCRIPTION: DF
        NAME: DF
        VALUE: 3
    NAME: nu_switch_type_t
"""
    temp_input = tempfile.NamedTemporaryFile()
    temp_input.write(input)
    temp_input.flush()
    name = temp_input.name

    yaml_parser = parser.YAMLParser()
    yaml_parser.Parse(name)

    document = yaml_parser.current_document

    self.assertEqual(2, len(document.Enums()))
    self.assertEqual(0, len(document.Structs()))

    enum_a = document.Enums()[0]
    self.assertEqual('nu_ig_stream_type_t', enum_a.name)
    self.assertEqual(4, len(enum_a.variables))
    self.assertEqual('SF', enum_a.variables[0].name)
    self.assertEqual('RESV', enum_a.variables[3].name)
    self.assertEqual(3, enum_a.last_value)

    enum_b = document.Enums()[1]
    self.assertEqual('nu_switch_type_t', enum_b.name)
    self.assertEqual(4, len(enum_b.variables))
    self.assertEqual('SX', enum_b.variables[1].name)
    self.assertEqual('DX', enum_b.variables[2].name)
    self.assertEqual(3, enum_b.last_value)

    temp_input.close()

  def testStruct(self):
    input = """
---
IS_STRUCT: 1
LIST:
  - DESCRIPTION: Foo
    NAME: my_struct
    SIGLIST:
      - DESCRIPTION: field a
        NAME: a
        WIDTH: 8

      - DESCRIPTION: field b
        NAME: b
        WIDTH: 32

      - DESCRIPTION: field c
        NAME: c
        WIDTH: 24
"""
    temp_input = tempfile.NamedTemporaryFile()
    temp_input.write(input)
    temp_input.flush()
    name = temp_input.name

    yaml_parser = parser.YAMLParser()
    yaml_parser.Parse(name)
    
    document = yaml_parser.current_document
    
    self.assertEqual(0, len(document.Enums()))
    self.assertEqual(1, len(document.Structs()))
    
    struct_a = document.Structs()[0]
    self.assertEqual('my_struct', struct_a.name)
    self.assertEqual(3, len(struct_a.fields))
    self.assertEqual(64, struct_a.BitWidth())

    field_a = struct_a.fields[0]
    self.assertEqual('a', field_a.name)
    self.assertEqual(8, field_a.BitWidth())

    field_b = struct_a.fields[1]
    self.assertEqual('b', field_b.name)
    self.assertEqual(32, field_b.BitWidth())

    field_c = struct_a.fields[2]
    self.assertEqual('c', field_c.name)
    self.assertEqual(24, field_c.BitWidth())


if __name__ == '__main__':
    unittest.main()
