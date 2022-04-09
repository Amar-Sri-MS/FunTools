#!/usr/bin/env python3
# Unit tests for generator.py
#
# Robert Bowdidge, August 8, 2016.
# Copyright Fungible Inc. 2016.

import unittest 

import generator
import parser

class DocBuilderTest(unittest.TestCase):
  # Test that we correctly parse valid and invalid structure definitions.
  def testEmptyDoc(self):
    gen_parser = parser.GenParser()
    self.assertIsNotNone(gen_parser.current_document)

  def testParseSimpleStructLine(self):
    gen_parser = parser.GenParser()  
    doc = gen_parser.current_document
    self.assertEqual(0, len(doc.Structs()))

    gen_parser.ParseStructStart('STRUCT Foo')
    gen_parser.ParseLine('0 63:0 uint64_t packet')
    gen_parser.ParseEnd('END')

    doc = gen_parser.current_document
    self.assertEqual(0, len(gen_parser.errors))

    print("testParseSimpleStruct %s" % doc)
    self.assertEqual(1, len(doc.Structs()))

    firstStruct = doc.Structs()[0]
    self.assertEqual(1, len(firstStruct.fields))

    firstField = firstStruct.fields[0]
    self.assertEqual(0, firstField.StartFlit())
    self.assertEqual(0, firstField.EndFlit())
    self.assertEqual(63, firstField.StartBit())
    self.assertEqual(0, firstField.EndBit())
    self.assertEqual('packet', firstField.name)

    self.assertEqual(1, firstStruct.Flits())

  def testStructSize(self): 
    gen_parser = parser.GenParser()
    doc = gen_parser.current_document

    gen_parser.ParseStructStart('STRUCT Foo')
    gen_parser.ParseLine('0 63:0 uint64_t packet')
    gen_parser.ParseEnd('END')

    self.assertEqual(1, len(doc.Structs()))

    struct = doc.Structs()[0]
    self.assertEqual(8, struct.Bytes())

  def testNotPackedStructSize(self): 
    gen_parser = parser.GenParser()
    doc = gen_parser.current_document

    gen_parser.ParseStructStart('STRUCT Foo')
    gen_parser.ParseLine('0 63:0 uint64_t packet')
    gen_parser.ParseLine('1 63:56 uint64_t bar')
    gen_parser.ParseEnd('END')

    self.assertEqual(1, len(doc.Structs()))
                     
    struct = doc.Structs()[0]
    # TODO(bowdidge): Should be 9 bytes?
    self.assertEqual(16, struct.Bytes())
    self.assertEqual(2, struct.Flits())

  def testValidFile(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo', '0 63:0 uint64_t packet', 'END']
    
    errors = gen_parser.Parse('filename', contents)
  
    self.assertIsNone(errors)

  def testTooBigFlit(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo', '0 64:49 uint16_t packet', 'END']
    errors = gen_parser.Parse('filename', contents)

    self.assertEqual(1, len(errors))
    self.assertIn('has start bit "64" too large', errors[0])

  def testSimpleStructBitWidth(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo', '0 63:0 uint64_t packet', 'END']
    
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
    doc = gen_parser.current_document

    self.assertEqual(1, len(doc.Structs()))

    s = doc.Structs()[0]
    self.assertEqual(64, s.BitWidth())
  
  def testPartialFlitBitWidth(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo', '0 63:16 uint64_t packet', 'END']
    
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
    doc = gen_parser.current_document

    self.assertEqual(1, len(doc.Structs()))

    s = doc.Structs()[0]
    self.assertEqual(48, s.BitWidth())

  def testPartialFlitBitWidth(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:32 uint32_t a', 
                '0 31:0 uint32_t b', 
                '1 63:32 uint32_t c', 
                'END']
    
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
    doc = gen_parser.current_document

    self.assertEqual(1, len(doc.Structs()))

    s = doc.Structs()[0]
    self.assertEqual(96, s.BitWidth())

  def testArray(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo', '0 63:0 uint8_t chars[8]', 'END']

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
    doc = gen_parser.current_document

    self.assertEqual(1, len(doc.Structs()))

    my_struct = doc.Structs()[0]
    self.assertEqual(1, len(my_struct.fields))
    my_field = my_struct.fields[0]

    self.assertEqual('chars', my_field.name)
    uint8_t = parser.ArrayTypeForName('uint8_t', 8)
    self.assertTrue(uint8_t.IsSameType(my_field.type))
    self.assertTrue(my_field.type.IsArray())
    self.assertEqual(8, my_field.type.ArraySize())
    self.assertEqual(0, my_field.StartFlit())
    self.assertEqual(0, my_field.EndFlit())
    self.assertEqual(64, my_field.BitWidth())


  def testArraySizedTooSmall(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo', 
                '0 63:0 uint8_t chars[2]', 
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('is 64 bits, type "uint8_t[2]" is 16', errors[0])

  def testMultiFlitNotNeeded(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:0 uint8_t chars[8]',
                '1 63:0 ...',
                'END']

    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('Multi-line flit continuation seen without', errors[0])

  def testMultiFlitTooLarge(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:0 uint8_t chars[18]',
                '1 63:0 ...',
                '2 63:0 uint64_t value',
                'END']

    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('Field spec for "chars" too short: expected 144 bits, got 128',
                  errors[0])

  def testContinuationNotAllowedAcrossFlitForBasicTypes(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:8 uint64_t fifty_six_bits',
                # It's illegal to have a scalar straddling a flit because
                # there's no way to tell its length.
                '0 7:0 uint64_t sixteen_bits',
                '1 63:56 ...',
                'END']

    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('Multi-line flit continuation seen without pending field.',
                  errors[0])

  # TODO(bowdidge): Can we even turn this into a C structure?
  def testContinuationAcrossFlitOkIfInStructure(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Tiny',
                '0 63:48 uint16_t foo',
                'END',
                'STRUCT Foo',
                '0 63:8 uint64_t fifty_six_bits',
                '0 7:0 Tiny sixteen_bits',
                '1 63:56 ...',
                'END']

    errors = gen_parser.Parse('filename', contents)
    self.assertFalse(errors)
    
    foo = gen_parser.current_document.Structs()[1]
    self.assertEqual("Foo", foo.name)
    self.assertEqual(72, foo.BitWidth())

  def testArraySizedTooLarge(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo', '0 63:0 uint8_t chars[16]', 'END']

    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('expected 128 bits, got 64', errors[0])
                     

  def testEnum(self):
    gen_parser = parser.GenParser()
    contents = ['ENUM Commands', 'A = 1', 'BBBBBB=0x02', 'END']
    
    errors = gen_parser.Parse('filename', contents)
    doc = gen_parser.current_document
  
    self.assertEqual(1, len(doc.Enums()))
    my_enum = doc.Enums()[0]
    self.assertEqual(2, len(my_enum.variables))
    var_a = my_enum.variables[0]
    var_b = my_enum.variables[1]
    self.assertEqual('A', var_a.name)
    self.assertEqual(1, var_a.value)
                    
    self.assertEqual('BBBBBB', var_b.name)
    self.assertEqual(2, var_b.value)

  def testConst(self):
    gen_parser = parser.GenParser()
    contents = ['CONST buffer_sizes', 'A = 0x1000', 'BBBBBB=99999', 'END']
    
    errors = gen_parser.Parse('filename', contents)
    doc = gen_parser.current_document
  
    self.assertEqual(1, len(doc.Consts()))
    my_const = doc.Consts()[0]
    self.assertEqual(2, len(my_const.variables))
    var_a = my_const.variables[0]
    var_b = my_const.variables[1]
    self.assertEqual('A', var_a.name)
    self.assertEqual(0x1000, var_a.value)
                    
    self.assertEqual('BBBBBB', var_b.name)
    self.assertEqual(99999, var_b.value)

  def disableTestEnumReference(self):
    # TODO(bowdidge): Should allow enum (and flag) declarations to be used as type names.
    gen_parser = parser.GenParser()
    contents = ['ENUM Commands',
                'A = 1',
                'BBBBBB=0x02',
                'END',
                'STRUCT Foo',
                '0 63:56 Commands a',
                'END'
                ]
    
    errors = gen_parser.Parse('filename', contents)
    doc = gen_parser.current_document
    
    self.assertEqual(1, len(doc.Structs()))
    foo = doc.Structs()[0]

    self.assertEqual(1, len(foo.fields))
    self.assertEqual(8, foo.BitWidth())

  def testLargeEnum(self):
    gen_parser = parser.GenParser()
    contents = ['ENUM Commands', 'A = 31', 'BBBBBB=0x3f', 'END']
    
    errors = gen_parser.Parse('filename', contents)
    doc = gen_parser.current_document
  
    self.assertEqual(1, len(doc.Enums()))
    my_enum = doc.Enums()[0]
    self.assertEqual(2, len(my_enum.variables))
    var_a = my_enum.variables[0]
    var_b = my_enum.variables[1]
    self.assertEqual('A', var_a.name)
    self.assertEqual(31, var_a.value)
                    
    self.assertEqual('BBBBBB', var_b.name)
    self.assertEqual(63, var_b.value)

  def testBadEnumFields(self):
    gen_parser = parser.GenParser()
    self.assertIsNone(gen_parser.ParseEnumLine("A"))
    self.assertIsNone(gen_parser.ParseEnumLine("3"))
    self.assertIsNone(gen_parser.ParseEnumLine("A=A"))
    self.assertIsNone(gen_parser.ParseEnumLine("A,A"))

  def testGoodEnumFields(self):
    gen_parser = parser.GenParser()
    field = gen_parser.ParseEnumLine('A=1')
    self.assertEqual('A', field.name)
    self.assertEqual(1, field.value)
    self.assertIsNone(field.key_comment)
    self.assertIsNone(field.body_comment)

    field = gen_parser.ParseEnumLine('bb1 = 3 /* Foobar */')
    self.assertEqual('bb1', field.name)
    self.assertEqual(3, field.value)
    self.assertEqual("Foobar", field.key_comment)

  def testInvalidFlit(self):
    # Test generator rejects a field with a non-numeric flit number.
    gen_parser = parser.GenParser()
    line = 'flit 63:0 uint64_t packet'

    gen_parser.ParseFieldLine(line, parser.Struct("fakeStruct", False))
  
    self.assertEqual(1, len(gen_parser.errors))
    self.assertIn('Invalid bit pattern', gen_parser.errors[0])

  def testInvalidTypeName(self):
    gen_parser = parser.GenParser()
    line = '0 63:0 NotAValidType field_name'

    gen_parser.ParseFieldLine(line, parser.Struct("fakeStruct", False))

    self.assertEqual(1, len(gen_parser.errors))
    self.assertIn('Unknown type name', gen_parser.errors[0])

  def testInvalidStart(self):
    # Test generator rejects field with a non-numeric start_bit.
    gen_parser = parser.GenParser()
    line = '2 foo:15 uint64_t packet'
    
    gen_parser.ParseFieldLine(line, parser.Struct("fakeStruct", False))
  
    self.assertEqual(1, len(gen_parser.errors))
    self.assertIn('Invalid bit pattern', gen_parser.errors[0])

  def testInvalidEnd(self):
    # Test generator rejects field with non-numeric end bit.
    gen_parser = parser.GenParser()
    line = '2 15:bar uint64_t packet'
    
    gen_parser.ParseFieldLine(line, parser.Struct("fakeStruct", False))
  
    self.assertEqual(1, len(gen_parser.errors))
    self.assertIn('Invalid bit pattern', gen_parser.errors[0])

  def testWrongOrder(self):
    # Test generator rejects field with high bit below low.
    gen_parser = parser.GenParser()
    line = '2 3:10 uint64_t packet'
    
    gen_parser.ParseFieldLine(line, parser.Struct("fakeStruct", False))
  
    self.assertEqual(1, len(gen_parser.errors))
    self.assertIn('greater than end bit', gen_parser.errors[0])

  def testSingleBit(self):
    # Test generator accepts field with a single-digit field number.
    gen_parser = parser.GenParser()
    line = '2 38 uint8_t packet'
    
    struct = parser.Struct("fakeStruct", False)
    self.assertTrue(gen_parser.ParseFieldLine(line, struct))

    self.assertEqual(1, len(struct.fields))
    field = struct.fields[0]

    self.assertIsNotNone(field)
    self.assertEqual(0, len(gen_parser.errors))

    self.assertEqual(2, field.StartFlit())
    self.assertEqual(2, field.EndFlit())
    self.assertEqual(38, field.StartBit())
    self.assertEqual(38, field.EndBit())

  def testMissingCommentIsNone(self):
    gen_parser = parser.GenParser()
    line = '2 15:12 int64_t packet'
    
    struct = parser.Struct("fakeStruct", False)
    self.assertTrue(gen_parser.ParseFieldLine(line, struct))

    self.assertEqual(1, len(struct.fields))
    field = struct.fields[0]
    
    self.assertIsNone(field.key_comment)
    self.assertIsNone(field.body_comment)
    self.assertIsNone(field.generator_comment)

  def testSimpleUnion(self): 
    gen_parser = parser.GenParser()  
    doc = gen_parser.current_document

    self.assertEqual(0, len(doc.Structs()))

    contents = ['STRUCT Foo',
                'UNION Bar u',
                'STRUCT A a',
                '0 63:0 uint64_t packet',
                'END',
                'STRUCT B b',
                '0 63:0 uint64_t buf',
                'END',
                'END',
                'END']

    errors = gen_parser.Parse('filename', contents)
    self.assertFalse(errors)

    doc = gen_parser.current_document
    self.assertEqual(4, len(doc.Structs()))

    first_struct = doc.Structs()[0]

    self.assertEqual('Foo', first_struct.Name())
    self.assertEqual(1, len(first_struct.fields))
    self.assertEqual('u', first_struct.fields[0].name)

    union = gen_parser.current_document.Structs()[1]
    self.assertEqual('Bar', union.Name())

    first_field = union.fields[0]
    self.assertEqual(0, first_field.StartFlit())
    self.assertEqual(0, first_field.EndFlit())
    self.assertEqual(63, first_field.StartBit())
    self.assertEqual(0, first_field.EndBit())
    self.assertEqual('a', first_field.name)

    struct_a = doc.Structs()[2]
    self.assertEqual('A', struct_a.Name())
    self.assertEqual(1, len(struct_a.fields))
    self.assertEqual('packet', struct_a.fields[0].Name())

    struct_b = doc.Structs()[3]
    self.assertEqual('B', struct_b.Name())
    self.assertEqual(1, len(struct_b.fields))
    self.assertEqual('buf', struct_b.fields[0].Name())

  def testParseCommentInField(self):
    gen_parser = parser.GenParser()

    struct = parser.Struct("fakeStruct", False)
    self.assertTrue(gen_parser.ParseFieldLine(
      '0 47:0 uint64_t packet /* 6 byte packet to send out */',
      struct))

    self.assertEqual(0, len(gen_parser.errors))

    self.assertEqual(1, len(struct.fields))
    field = struct.fields[0]
                     
    self.assertEqual("packet", field.name)
    self.assertEqual("6 byte packet to send out", field.key_comment)

  def testParseTailComment(self):
    gen_parser = parser.GenParser()
    the_file = ['// Body comment\n',
                'STRUCT Foo\n',
                '// Packet body comment\n',
                '0 63:0 uint64_t packet // Packet key comment\n',
                '// Tail comment\n',
                'END\n']
    gen_parser.Parse('filename', the_file)
    
    self.assertEqual(0, len(gen_parser.errors))
    self.assertIsNotNone(gen_parser.current_document)
    self.assertEqual(1, len(gen_parser.current_document.Structs()))

    the_struct = gen_parser.current_document.Structs()[0]
    self.assertEqual(None, the_struct.key_comment)
    self.assertEqual('Body comment\n', the_struct.body_comment)
    self.assertEqual('Tail comment\n', the_struct.tail_comment)

    self.assertEqual(1, len(the_struct.fields))
    the_field = the_struct.fields[0]
    self.assertEqual('Packet key comment', the_field.key_comment)
    self.assertEqual('Packet body comment\n', the_field.body_comment)
    self.assertIsNone(the_field.tail_comment)

  def testParseMultiFlitDots(self):
    gen_parser = parser.GenParser()
    # ... allows a field to overflow into later flits.
    contents = [
      'STRUCT Foo',
      '0 63:56 uint8_t command',
      '0 55:0 uint8_t buf[23]',
      '1 63:0 ...',
      '2 63:0 ...',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = gen_parser.current_document

    self.assertEqual(1, len(doc.Structs()))

    struct = doc.Structs()[0]
    self.assertEqual(3, struct.Flits())

    self.assertEqual(2, len(struct.fields))
    long_field = struct.fields[1]

    self.assertTrue(long_field.crosses_flit)
    self.assertEqual(55, long_field.StartBit())
    self.assertEqual(0, long_field.EndBit())
    self.assertEqual(0, long_field.StartFlit())
    self.assertEqual(2, long_field.EndFlit())

  def disableTestDuplicateBitfield(self):
    """Test that we flag an error if the flit for a ... is incorrect."""
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:0 uint8_t chars[16]',
                '0 63:0 ...',
                'END']

    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('reuse', errors[0])


  def testNestedStruct(self):
    gen_parser = parser.GenParser()
    # ... allows a field to overflow into later flits.
    contents = [
      'STRUCT Foo',
      '0 63:56 uint8_t command',
      '0 55:48 uint8_t arg',
      'END',
      'STRUCT Bar',
      '0 63:48 Foo header',
      '0 47:0 uint8_t buf[6]',
      'END',
      'STRUCT Baz',
      '0 63:48 Foo header',
      '0 47:0 uint64_t arg2',
      '1 63:32 uint32_t arg3',
      '1 31:0 uint32_t arg4',
      '2 63:0 Bar b',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = gen_parser.current_document

    self.assertEqual(3, len(doc.Structs()))
    
    foo = doc.Structs()[0]
    bar = doc.Structs()[1]
    baz = doc.Structs()[2]
    
    self.assertEqual(16, foo.BitWidth())
    self.assertEqual(64, bar.BitWidth())
    self.assertEqual(192, baz.BitWidth())

    self.assertEqual(0, baz.fields[0].StartOffset())
    self.assertEqual(16, baz.fields[1].StartOffset())
    self.assertEqual(64, baz.fields[2].StartOffset())
    self.assertEqual(96, baz.fields[3].StartOffset())
    self.assertEqual(128, baz.fields[4].StartOffset())

    b = baz.fields[4]
    self.assertEqual(2, b.StartFlit())
    self.assertEqual(2, b.EndFlit())
    self.assertEqual(63, b.StartBit())
    self.assertEqual(0, b.EndBit())

  def testNestedUnion(self):
    gen_parser = parser.GenParser()
    # ... allows a field to overflow into later flits.
    contents = [
      'STRUCT Foo',
      '0 63:0 uint64_t command',
      'UNION foo u',
      'STRUCT A1 a1',
      '0 63:0 uint64_t a1_value',
      'END',
      'STRUCT A2 a2',
      '0 63:0 uint64_t a2_value',
      'END',
      'STRUCT A3 a3',
      '0 63:0 uint64_t a3_value',
      'END',
      'END',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = gen_parser.current_document

    self.assertEqual(5, len(doc.Structs()))
    
    foo = doc.Structs()[0]
    
    self.assertEqual(128, foo.BitWidth())

    self.assertEqual(2, len(foo.fields))

    union = foo.fields[1]
    self.assertEqual(64, union.StartOffset())
    self.assertEqual(127, union.EndOffset())

    self.assertEqual(3, len(union.subfields))

    a1 = union.subfields[0]
    self.assertEqual(64, a1.StartOffset())
    self.assertEqual(127, a1.EndOffset())

    a2 = union.subfields[0]
    self.assertEqual(64, a2.StartOffset())
    self.assertEqual(127, a2.EndOffset())

    a3 = union.subfields[0]
    self.assertEqual(64, a3.StartOffset())
    self.assertEqual(127, a3.EndOffset())
    
  def testOffsetForInlineStruct(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT A',
      '0 63:32 uint32_t a',
      'STRUCT B',
      '0 31:0 uint32_t b',
      'END',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    struct_b = gen_parser.current_document.StructWithName('B')
    self.assertEqual(32, struct_b.StartOffset())

    self.assertEqual(1, len(struct_b.fields))

    field_b = struct_b.fields[0]
    self.assertEqual(32, field_b.StartOffset())                   


  def testOffsetForStructWithZeroDimArray(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT A',
      '0 63:32 uint32_t a',
      '_ _:_ uint32_t rest[0]',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    struct_b = gen_parser.current_document.StructWithName('A')
    self.assertEqual(0, struct_b.StartOffset())
    self.assertEqual(31, struct_b.EndOffset())


  def testOffsetForStructWithContinuation(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT A',
      '0 63:0 uint64_t a[2]',
      '1 63:0 ...',
      'END',
      'STRUCT B',
      '0 63:0 A b',
      '1 63:0 ...',
      '2 63:0 uint64_t c',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
    
    struct_b = gen_parser.current_document.StructWithName('B')

    self.assertEqual(2, len(struct_b.fields))

    field_b = struct_b.fields[0]
    self.assertEqual(0, field_b.StartOffset())
    self.assertEqual(127, field_b.EndOffset())

    self.assertEqual(0, struct_b.StartOffset())
    self.assertEqual(191, struct_b.EndOffset())


  def testCatchMissingEnd(self):
    """Tests that error generated if not all objects closed."""
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT A',
      '0 63:00 uint64_t a'
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('END missing at end of file', errors[0])

  def testMultiFlitNestedStruct(self):
    gen_parser = parser.GenParser()
    # ... allows a field to overflow into later flits.
    contents = [
      'STRUCT fun_admin_cmd_common',
      '0 63:00 uint64_t common_opcode',
      '1 63:00 uint64_t arg',
      'END',
      'STRUCT fun_admin_epsq_cmd',
      '0 63:00 fun_admin_cmd_common c',
      '1 63:00 ...',
      '2 63:0 uint64_t arg2',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = gen_parser.current_document

    self.assertEqual(2, len(doc.Structs()))
    
    common = doc.Structs()[0]
    cmd = doc.Structs()[1]
    
    self.assertEqual(128, common.BitWidth())
    self.assertEqual(192, cmd.BitWidth())

  def testVariableLengthArray(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT foo',
      '0 63:56 char initial',
      '_ _:_ char array[0]',
      'END'
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = gen_parser.current_document

    self.assertEqual(1, len(doc.Structs()))
    foo = doc.Structs()[0]
    self.assertEqual(2, len(foo.fields))
    array = foo.fields[1]
    self.assertEqual('<Type: char[0]>', str(array.Type()))
    
    self.assertEqual(8, foo.BitWidth())
    self.assertEqual(0, array.BitWidth())

  def testVariableLengthStructArray(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT element',
      '0 63:56 char item',
      'END',
      'STRUCT foo',
      '0 63:56 char initial',
      '_ _:_ element array[0]',
      'END'
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = gen_parser.current_document

    self.assertEqual(2, len(doc.Structs()))
    foo = doc.Structs()[1]
    self.assertEqual(2, len(foo.fields))
    array = foo.fields[1]
    self.assertEqual('<Type: element[0]>', str(array.Type()))
    
    self.assertEqual(8, foo.BitWidth())
    self.assertEqual(0, array.BitWidth())

  def testSimpleFlags(self):
    gen_parser = parser.GenParser()
    contents = [
      'FLAGS Foo',
      'A = 1',
      'B = 2',
      'C = 4',
      'D = 8',
      'E = 16',
      'F = 0x20',
      'END',
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = gen_parser.current_document
    self.assertEqual(1,len(doc.Flagsets()))
    foo = doc.Flagsets()[0]
    
    self.assertEqual(6, len(foo.variables))
    
  def testValidStructName(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT 1',
                'END']
    errors = gen_parser.Parse('filename', contents)

    self.assertEqual(1, len(errors))
    self.assertIn('"1" is not a valid', errors[0])

  def testValidUnionName(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT A',
                'UNION 1_1 a',
                'END',
                'END']
    errors = gen_parser.Parse('filename', contents)
    print(errors)
    self.assertEqual(1, len(errors))
    self.assertIn('"1_1" is not a valid', errors[0])

  def testValidUnionVariable(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT A',
                'UNION A1 1_a',
                'END',
                'END']
    errors = gen_parser.Parse('filename', contents)
    print(errors)
    self.assertEqual(1, len(errors))
    self.assertIn('"1_a" is not a valid', errors[0])

  def testValidFieldName(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT A',
                '0 63:0 uint64_t 1dh',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('field name "1dh" is not a valid identifier', errors[0])


  def testValidEnumName(self):
    gen_parser = parser.GenParser()
    contents = ['ENUM 1AA', 'END']
    errors = gen_parser.Parse('filename', contents)

    self.assertEqual(1, len(errors))
    self.assertIn('"1AA" is not a valid identifier', errors[0])

  def testValidEnumVarName(self):
    gen_parser = parser.GenParser()
    contents = ['ENUM A',
                '1 = 3',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('"1" is not a valid identifier', errors[0])

  def testValidEnumVarValue(self):
    gen_parser = parser.GenParser()
    contents = ['ENUM A',
                'v = 999999999999',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('is larger than the 2^32', errors[0])

  def testValidEnumVarValueInHex(self):
    gen_parser = parser.GenParser()
    contents = ['ENUM A',
                'v = 0x10000000011',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('is larger than the 2^32', errors[0])

  def testValidFlagName(self):
    gen_parser = parser.GenParser()
    contents = ['FLAGS 1AA', 'END']
    errors = gen_parser.Parse('filename', contents)

    self.assertEqual(1, len(errors))
    self.assertIn('"1AA" is not a valid identifier', errors[0])

  def testValidFlagVarName(self):
    gen_parser = parser.GenParser()
    contents = ['FLAGS A',
                '1 = 3',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('"1" is not a valid identifier', errors[0])

  def testValidFlagVarValue(self):
    gen_parser = parser.GenParser()
    contents = ['FLAGS A',
                'v = 999999999999',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('is larger than the 2^32', errors[0])

  def testValidFlagVarValueInHex(self):
    gen_parser = parser.GenParser()
    contents = ['FLAGS A',
                'v = 0x10000000011',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('is larger than the 2^32', errors[0])

  def testBitSizeOfUnion(self):
    gen_parser = parser.GenParser()

    input = ['STRUCT B',
             '0 63:56 uint8_t a',
             'UNION Cmd u1',
             'STRUCT B1 b1',
             '0 55:48 uint8_t b11',
             'END',
             'END',
             'END'
             ]

    errors = gen_parser.Parse('filename', input)

    self.assertFalse(errors)
    struct_a = gen_parser.current_document.StructWithName('B')

    self.assertIsNotNone(struct_a)

    union_cmd = gen_parser.current_document.StructWithName('Cmd')
    self.assertIsNotNone(union_cmd)

    b1_field = union_cmd.fields[0]
    b1_struct = gen_parser.current_document.StructWithName('B1')

    self.assertEqual('b1', b1_field.Name())

    self.assertEqual(8, b1_struct.StartOffset())
    self.assertEqual(15, b1_struct.EndOffset())

    self.assertEqual(8, b1_struct.BitWidth())
    self.assertEqual(8, b1_field.BitWidth())
    self.assertEqual(8, union_cmd.BitWidth())

  def testFieldNotAllowedInUnion(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT Foo',
      'UNION A u',
      '0 63:56 uint8_t cmd',
      '0 63:56 uint8_t other',
      'END',
      'END',
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(2, len(errors))
    self.assertIn('fields cannot occur directly in a union', errors[0])
    self.assertIn('Field "other" not allowed', errors[1])

  def testCatchDuplicateFields(self):
    gen_parser = parser.GenParser()
    input = ['STRUCT B',
             '0 63:56 uint8_t a',
             '0 55:48 uint8_t a',
             'END']

    errors = gen_parser.Parse('filename', input)
    self.assertEqual(1, len(errors))
    self.assertIn('Field with name "a" already exists in struct', errors[0])

  def testCatchDuplicateStructureField(self):
    gen_parser = parser.GenParser()
    input = ['STRUCT B',
             '0 63:56 uint8_t a',
             'STRUCT A a',
             'END']

    errors = gen_parser.Parse('filename', input)
    self.assertEqual(1, len(errors))
    self.assertIn('Field with name "a" already exists in struct "B"', errors[0])

  def testCatchDuplicateUnionField(self):
    gen_parser = parser.GenParser()
    input = ['STRUCT B',
             '0 63:56 uint8_t a',
             'UNION A a',
             'END']

    errors = gen_parser.Parse('filename', input)
    self.assertEqual(1, len(errors))
    self.assertIn('Field with name "a" already exists in struct', errors[0])


class StripCommentTest(unittest.TestCase):
  def testSimple(self):
    gen_parser = parser.GenParser()
    self.assertEqual("Foo", gen_parser.StripKeyComment("// Foo"))
    self.assertEqual("Foo", gen_parser.StripKeyComment("/* Foo */"))
    self.assertEqual("", gen_parser.StripKeyComment("//"))
    self.assertEqual("", gen_parser.StripKeyComment("/* */"))

  def testNotTerminated(self):
    gen_parser = parser.GenParser()
    gen_parser.current_line = 15

    self.assertEqual(None, gen_parser.StripKeyComment('/* foo bar'))
    self.assertEqual(1, len(gen_parser.errors))
    self.assertIn('15: Badly formatted comment',
                  gen_parser.errors[0])

  def testNotStarted(self):
    gen_parser = parser.GenParser()
    self.assertEqual(None, gen_parser.StripKeyComment('foo bar */'))
    self.assertEqual(1, len(gen_parser.errors))
    self.assertIn('0: Unexpected stuff where comment should be',
                     gen_parser.errors[0])
                                         

  def testStructureAndUnion(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT foo',
      '0 63:0 uint64_t a',
      '1 63:0 uint64_t b',
      'END',
      'STRUCT bar',
      '0 63:0 foo f',
      '1 63:0 ...',
      'UNION baz u',
      'STRUCT container',
      '2 63:56 char c',
      'END',
      'END',
      'END'
      ]

    errors = gen_parser.Parse('filename', contents)

    self.assertIsNone(errors)
    doc = gen_parser.current_document
    self.assertEqual(4, len(doc.Structs()))

    bar = doc.Structs()[1]
    self.assertEqual("bar", bar.Name())
    self.assertEqual(2, len(bar.fields))

    f = bar.fields[0]
    u = bar.fields[1]
    self.assertEqual(128, f.BitWidth())
    self.assertEqual(128, u.StartOffset())
    

class PackerTest(unittest.TestCase):
  def testDontPackArgumentsFittingOwnType(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo', '0 63:32 unsigned packet',
                '0 31:0 unsigned other','END']
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = gen_parser.current_document
    p = generator.Packer()
    p.VisitDocument(doc)

    self.assertEqual(2, len(doc.Structs()[0].fields))
    self.assertEqual("packet", doc.Structs()[0].fields[0].name)

  def testNoPackSingleField(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo', '0 31:0 unsigned packet', 'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = gen_parser.current_document
    p = generator.Packer()
    p.VisitDocument(doc)
    
    self.assertEqual(1, len(doc.Structs()[0].fields))
    field = doc.Structs()[0].fields[0]
    # Packer doesn't change name.
    self.assertEqual('packet', field.name)
    self.assertEqual(31, field.StartBit())
    self.assertEqual(0, field.EndBit())

  def testPackBitfields(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT Foo',
      '0 63:56 uint8_t favorite_char',
      '0 55 uint8_t is_valid_char',
      '0 54:53 uint8_t foo',
      '0 52:48 uint8_t reserved',
      '0 47:40 uint8_t another_char',
      '0 39:32 uint8_t third_char',
      '0 31:0 uint32_t value',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = gen_parser.current_document
    p = generator.Packer()
    p.VisitDocument(doc)
    self.assertEqual(5, len(doc.Structs()[0].fields))
    self.assertEqual('favorite_char', doc.Structs()[0].fields[0].name)
    self.assertEqual('is_valid_char_to_foo',
                     doc.Structs()[0].fields[1].name)
    self.assertEqual('another_char', doc.Structs()[0].fields[2].name)
    self.assertEqual('third_char', doc.Structs()[0].fields[3].name)
    self.assertEqual('value', doc.Structs()[0].fields[4].name)

    # Make sure the comment describing the packed layout appears.
    self.assertIn('6:5: foo', doc.Structs()[0].fields[1].body_comment)

  def testTypeChanges(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT Foo',
      '0 63:56 uint8_t favorite_char',
      '0 55 uint8_t is_valid_char',
      '0 54:53 char foo',
      '0 52:48 char bar',
      '0 47:40 uint8_t another_char',
      '0 39:32 uint8_t third_char',
      '0 31:0 uint32_t value',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = gen_parser.current_document
    p = generator.Packer()
    p.VisitDocument(doc)
    print ([x.name for x in doc.Structs()[0].fields])

    self.assertEqual(6, len(doc.Structs()[0].fields))
    self.assertEqual('favorite_char', doc.Structs()[0].fields[0].name)
    self.assertEqual('is_valid_char', doc.Structs()[0].fields[1].name)
    self.assertEqual('foo_to_bar', doc.Structs()[0].fields[2].name)
    self.assertEqual('another_char', doc.Structs()[0].fields[3].name)
    self.assertEqual('third_char', doc.Structs()[0].fields[4].name)
    self.assertEqual('value', doc.Structs()[0].fields[5].name)

  def testPackOnlyContiguous(self):
    """Tests that two sets of packed fields separated by a non-packed
    variable are not merged.
    """
    
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT Foo',
      '0 63:60 uint8_t a',
      '0 59:56 uint8_t b',
      '0 55:48 uint8_t c',
      '0 47:44 uint8_t d',
      '0 43:40 uint8_t e',
      '0 39:0 uint64_t reserved',
      'END'
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = gen_parser.current_document
    p = generator.Packer()
    p.VisitDocument(doc)

    # a, b, d, and e should not be packed.
    self.assertEqual(4, len(doc.Structs()[0].fields))
    self.assertEqual('a_to_b', doc.Structs()[0].fields[0].name)
    self.assertEqual('c', doc.Structs()[0].fields[1].name)
    self.assertEqual('d_to_e', doc.Structs()[0].fields[2].name)
    self.assertEqual('reserved', doc.Structs()[0].fields[3].name)

  def testPackSplitCorrectly(self):
    """Tests that two sets of packed fields separated by a non-packed
    variable are not merged.
    """
    
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT Foo',
      '0 63:32 uint32_t rsvd0',
      '0 31:22 uint16_t rsvd1',
      '0 21:16 uint16_t ucode_ix',
      '0 15:10 uint16_t rsvd2',
      '0 9:0 uint16_t dmem_ix',
      'END'
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = gen_parser.current_document
    p = generator.Packer()
    p.VisitDocument(doc)

    self.assertEqual(0, len(p.errors))

    # a, b, d, and e should not be packed.
    self.assertEqual(3, len(doc.Structs()[0].fields))
    self.assertEqual('rsvd0', doc.Structs()[0].fields[0].name)
    self.assertEqual('ucode_ix_pack', doc.Structs()[0].fields[1].name)
    self.assertEqual('dmem_ix_pack', doc.Structs()[0].fields[2].name)

  def testWarningOnPackLargerThanBaseType(self):
    """Tests that two sets of packed fields separated by a non-packed
    variable are not merged.
    """
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT Foo',
      '0 63:58 uint8_t a',
      '0 57:54 uint8_t b',
      '0 54:50 uint8_t c',
      '0 50:48 uint8_t d',
      '0 47:0 uint64_t reserved',
      'END'
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = gen_parser.current_document
    p = generator.Packer()
    errors = p.VisitDocument(doc)
    
    self.assertTrue(1, len(errors))
    self.assertIn('Width of packed bit-field containing a and b (10 bits) exceeds width of its type (8 bits).', errors[0])

  def testReservedFieldIgnoredWhenPacking(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT Foo',
      '0 63:56 uint8_t favorite_char',
      '0 55 uint8_t is_valid_char',
      '0 54:53 char foo',
      '0 52:51 char bar',
      '0 50:48 char reserved',
      '0 47:40 uint8_t another_char',
      '0 39:32 uint8_t third_char',
      '0 31:0 uint32_t value',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = gen_parser.current_document
    p = generator.Packer()
    errors = p.VisitDocument(doc)
    self.assertEqual(0, len(errors))

    self.assertEqual(6, len(doc.Structs()[0].fields))
    self.assertEqual('favorite_char', doc.Structs()[0].fields[0].name)
    self.assertEqual('is_valid_char', doc.Structs()[0].fields[1].name)
    self.assertEqual('foo_to_bar', doc.Structs()[0].fields[2].name)
    self.assertEqual('another_char', doc.Structs()[0].fields[3].name)
    self.assertEqual('third_char', doc.Structs()[0].fields[4].name)
    self.assertEqual('value', doc.Structs()[0].fields[5].name)

  def testNoPackArrayAndRegularType(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo', 
                '0 63:8 uint8_t chars[7]',
                '0 7:0 uint8_t opcode',
                'END']

    errors = gen_parser.Parse('filename', contents)

    self.assertIsNone(errors)

    doc = gen_parser.current_document
    self.assertEqual(1, len(doc.Structs()))

    p = generator.Packer()
    errors = p.VisitDocument(doc)
    self.assertEqual(0, len(errors))
    

    self.assertEqual(2, len(doc.Structs()[0].fields))

  def testNoPackArray(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo', 
                '0 63:32 uint8_t chars[4]',
                '0 31:0 uint8_t opcode[4]',
                'END']

    errors = gen_parser.Parse('filename', contents)

    self.assertIsNone(errors)

    doc = gen_parser.current_document
    self.assertEqual(1, len(doc.Structs()))

    p = generator.Packer()
    p.VisitDocument(doc)

    self.assertEqual(2, len(doc.Structs()[0].fields))

  def testTooManyEnds(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:0 uint64_t cmd',
                'STRUCT Bar',
                '1 63:0 uint64_t cmd',
                'END',
                'END',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('without matching', errors[0])
                
  def testParseVariableLengthArrayInSubStructure(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT outer',
      '0 63:56 char initial_outer',
      'STRUCT inner',
      '0 63:56 char initial_inner',
      '_ _:_ char array[0]',
      'END',
      'END'
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = gen_parser.current_document
    self.assertEqual(2, len(doc.Structs()))
    outer = doc.Structs()[0]
    inner = doc.Structs()[1]
    self.assertEqual("inner", inner.name)
    self.assertEqual(2, len(inner.fields))
    var_length_array = inner.fields[1]
    self.assertEqual("array", var_length_array.name)
    self.assertTrue(var_length_array.no_offset)

  def testParseVariableLengthArrayInUnion(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT outer',
      '0 63:56 char initial_outer',
      'UNION theUnion u',
      'STRUCT first s1',
      '0 55:0 uint64_t value',
      '_ _:_ char chars[0]',
      'END',
      'STRUCT second s2',
      '0 55:0 uint64_t value',
      'END',
      'END',
      'END'
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = gen_parser.current_document
    self.assertEqual(4, len(doc.Structs()))
    outer = doc.Structs()[0]
    union = doc.Structs()[1]
    s1 = doc.Structs()[2]
    s2 = doc.Structs()[3]
    self.assertEqual("outer", outer.name)
    self.assertEqual("theUnion", union.name)
    self.assertEqual("first", s1.name)
    self.assertEqual("second", s2.name)

    self.assertEqual(2, len(s1.fields))
    var_length_array = s1.fields[1]
    self.assertEqual("chars", var_length_array.name)
    self.assertTrue(var_length_array.no_offset)

  def testParseVariableLengthStructArrayInUnion(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT inside_union',
      '0 63:00 uint64_t value',
      'END',
      'STRUCT outer',
      '0 63:56 char initial_outer',
      'UNION theUnion u',
      'STRUCT first s1',
      '0 63:32 uint32_t value',
      '_ _:_ inside_union inside[0]',
      'END',
      'END',
      'END'
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
    doc = gen_parser.current_document

    self.assertEqual(4, len(doc.Structs()))

    inside_union = doc.Structs()[0]
    outer = doc.Structs()[1]
    the_union = doc.Structs()[2]
    first = doc.Structs()[3]
    self.assertEqual("inside_union", inside_union.name)
    self.assertEqual("outer", outer.name)
    self.assertEqual("theUnion", the_union.name)
    self.assertEqual("first", first.name)

    self.assertEqual(64, inside_union.BitWidth())
    # TODO(bowdidge) - 32 bit struct can't be aligned right up against
    # the char.
    self.assertEqual(40, outer.BitWidth())
    self.assertEqual(32, the_union.BitWidth())
    self.assertEqual(32, first.BitWidth())


class CheckerTest(unittest.TestCase):

  def testCheckerAdjacentTypesEqual(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 3:2 uint8_t b',
                '0 1:0 uint8_t a',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)
    self.assertEqual(0, len(checker.errors))

  def disableTestCheckerAdjacentTypesDifferent(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 3:2 uint16_t b',
                '0 1:0 uint8_t a',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    print(checker.errors)
    self.assertEqual(1, len(checker.errors))
    self.assertIn('allow alignment', checker.errors[0])

  def testStructTooSmall(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:32 uint64_t a',
                'END',
                'STRUCT BAR',
                '0 63:48 Foo f',
                '0 47:32 uint16_t b',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('Field smaller than type', errors[0])

  def testStructTooLarge(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:32 uint64_t a',
                'END',
                'STRUCT BAR',
                '0 63:0 Foo f',
                '1 63:32 uint32_t b',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('Field larger than type', errors[0])

  def testArrayOfStructs(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:32 uint64_t a',
                'END',
                'STRUCT BAR',
                '0 63:0 Foo f[2]',
                'END']

    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(None, errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)
    self.assertEqual(0, len(checker.errors))

    self.assertEqual(2, len(gen_parser.current_document.Structs()))
    bar = gen_parser.current_document.Structs()[1]

    self.assertEqual(1, len(bar.fields))

    f = bar.fields[0]
    self.assertTrue(f.type.IsRecord())
    self.assertTrue(f.type.IsArray())

  def testFlagOutOfOrder(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 7:0 uint8_t b',
                '0 15:8 uint8_t a',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('field "b" and "a" not in bit order', checker.errors[0])

  def testFlagOverlappingFields(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 15:8 uint8_t a',
                '0 15:0 uint16_t b',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('field "a" overlaps field "b"', checker.errors[0])

  def testFlagOverlappingFieldsEqualAtBottom(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 15:8 uint8_t a',
                '0 12:8 uint8_t b',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('field "a" overlaps field "b"', checker.errors[0])

  def testFlagOverlappingFieldsBottom(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 15:8 uint8_t a',
                '0 9:7 uint8_t b',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('field "a" overlaps field "b"', checker.errors[0])

  def testFlagExtraSpace(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 15:8 uint8_t a',
                '0 3:0 uint8_t b',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('unexpected space between field "a" and "b"',
                  checker.errors[0])

  def testExtraFlit(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:0 uint64_t a',
                '2 63:0 uint64_t b',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('unexpected space between field "a" and "b"',
                  checker.errors[0])

  def testMultiFlitFieldHandledOk(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:56 uint8_t cmd',
                '0 55:0 uint8_t buf[15]',
                '1 63:0 ...',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(0, len(checker.errors))

  def testMultiFlitFieldOverlapGeneratesWarning(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:56 uint8_t cmd',
                '0 55:0 uint8_t buf[15]',
                '1 63:0 ...',
                '1 63:0 uint64_t c',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)
    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('field "buf" overlaps field "c"',
                  checker.errors[0])

  def testUnionNoOverlap(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:0 uint64_t cmd',
                'UNION Bar u',
                'STRUCT B b',
                '1 63:0 uint64_t data',
                'END',
                'END',
                'END']
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(0, len(checker.errors))

  def testUnionOverlap(self):
    gen_parser = parser.GenParser()
    contents = ['STRUCT Foo',
                '0 63:0 uint64_t cmd',
                'UNION Bar u',
                '0 31:0 uint32_t data',
                'END',
                'END']
    # TODO(bowdidge): Finish.

  def testVariableLengthArray(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT foo',
      '0 63:56 char initial',
      '_ _:_ char array[0]',
      'END'
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = gen_parser.current_document
    self.assertIsNone(errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)
    self.assertEqual(0, len(checker.errors))

  def testVariableLengthStructureArray(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT element',
      '0 63:56 char value',
      'END',
      'STRUCT foo',
      '0 63:56 char initial',
      '_ _:_ element array[0]',
      'END'
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = gen_parser.current_document
    self.assertIsNone(errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)
    self.assertEqual(0, len(checker.errors))

  def testErrorIfVariableLengthArrayNotAtEnd(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT foo',
      '0 63:56 char initial',
      '_ _:_ char array[0]',
      '0 55:48 char end',
      'END'
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('is not the last field', checker.errors[0])

  def testErrorIfFailToCloseEnum(self):
    gen_parser = parser.GenParser()
    contents = [
      'ENUM x',
      'A = 1',
      'STRUCT Foo',
      '0 63:0 uint64_t value',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertEqual(2, len(errors))
    self.assertEqual('filename:3: Struct starting in inappropriate context',
                     errors[0])
    self.assertEqual('filename:4: ' +
                     'Invalid enum line: "0 63:0 uint64_t value"',
                     errors[1])

  def disableTestErrorIfVariableLengthArrayNotAtEndOfContainer(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT outer',
      '0 63:56 char initial_outer',
      'STRUCT inner',
      '0 63:56 char initial_inner',
      '_ _:_ char array[0]',
      'END',
      'END'
      ]

    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('is not the last field', checker.errors[0])

  def testCheckOkPositionAfterUnion(self):
    """Test that the positions of fields in structs in a union are
    ignored, and the next field only cares about the size.
    """
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT A',
      '0 63:00 uint64_t a',
      'UNION crypto_params crypto',
      'STRUCT A1 a1',
      '1 63:00 uint64_t b',
      'END',
      'STRUCT A2 a2',
      # TODO(bowdidge): Checker should flag wrong flit here.
      '2 63:00 uint64_t c',
      'END',
      'END',
      # Checker doesn't complain because total size of the union
      # is still one flit.
      '2 63:00 uint64_t d',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)

    self.assertIsNone(errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(0, len(checker.errors))

  def testBadPositionAfterUnion(self):
    """Test that a hole after the union is noticed."""
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT A',
      '0 63:00 uint64_t a',
      'UNION crypto_params crypto',
      'STRUCT A1 a1',
      '1 63:00 uint64_t b',
      'END',
      'STRUCT A2 a2',
      '1 63:00 uint64_t c',
      'END',
      'END',
      # Hole between unions and d.
      # We should get an error.
      '4 63:00 uint64_t d',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)

    self.assertIsNone(errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertIsNotNone(checker.errors)
    self.assertEqual(1, len(checker.errors))
    self.assertIn('unexpected space between field "crypto" and "d".',
                  checker.errors[0])

  def testHoleInStructure(self):
    """Tests that a gap between regular fields is noticed."""
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT A',
      '0 63:00 uint64_t a',
      # error: Nothing in flit 1.
      '2 63:0 uint64_t b',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertIsNone(errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('unexpected space between field "a" and "b"',
                  checker.errors[0])

  def disableTestErrorIfStructsInUnionHaveDifferentStarts(self):
    """Test that a union with structs that start at different bits
    are treated as an error.
    """
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT A',
      '0 63:00 uint64_t a',
      'UNION crypto_params crypto',
      'STRUCT A1 a1',
      '1 63:00 uint64_t b',
      'END',
      'STRUCT A2 a2',
      '2 63:00 uint64_t c',
      'END',
      'END',
      ]
    errors = gen_parser.Parse('filename', contents)

    self.assertIsNone(errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('field "a2" in union does not match start bit of previous.',
                  checker.errors[1])

  def testIncorrectStructLength(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT A',
      '0 63:00 uint64_t value',
      'END',
      'STRUCT B',
      '0 63:00 A header',
      '1 63:00 ...',
      '2 63:48 uint16_t end',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)

    self.assertEqual(1, len(errors))
    self.assertIn('Multi-line flit continuation seen without pending field.',
                  errors[0])

  def testIncorrectSmallStructLength(self):
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT A',
      '0 63:32 uint32_t value',
      'END',
      'STRUCT B',
      '0 63:16 A header',
      '0 15:0 uint16_t value',
      'END'
      ]
    errors = gen_parser.Parse('filename', contents)

    self.assertEqual(1, len(errors))
    self.assertIn('Field larger than type: field "header" is 48 bits, '
                  'type "A" is 32.', errors[0])

  def testOkForSmallIntIfDifferentType(self):
    """Tests that it's ok for the 16 bit value to be in a 32 bit
    type because we'll assume it'll have to be packed.
    """
    gen_parser = parser.GenParser()
    contents = [
      'STRUCT A',
      '0 63:56 uint8_t a',
      '0 55:40 uint32_t b',
      'END',
      ]
    errors = gen_parser.Parse('filename', contents)
    self.assertFalse(errors)

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)

    self.assertFalse(checker.errors)

class CodegenArgsTest(unittest.TestCase):

  def testSimple(self):
    codegen_args = ['pack', 'nojson']
    
    self.assertFalse(generator.SetFromArgs('missing', codegen_args, False))
    self.assertTrue(generator.SetFromArgs('missing', codegen_args, True))

    self.assertFalse(generator.SetFromArgs('json', codegen_args, False))
    self.assertFalse(generator.SetFromArgs('json', codegen_args, True))

    self.assertTrue(generator.SetFromArgs('pack', codegen_args, False))
    self.assertTrue(generator.SetFromArgs('pack', codegen_args, True))
      

  def testCPacked(self):
    """Tests that cpacked argument adds correct __attribute__ in code."""
    codegen_args = ['cpacked']
  
    input = ['STRUCT A',
             '0 63:0 uint64_t foo',
             'END']
    (out, errs) = generator.GenerateFile(generator.OutputStyleHeader, None, 
                                         input, 'input.gen',
                                         ['cpacked'])
    
    self.assertEqual([], errs)
    self.assertIn('} __attribute__((packed))', out)

class HashTest(unittest.TestCase):
  def testSimple(self):
    generator.GENERATOR_VERSION = 0
    # If the example files change, these values will (correctly) change.
    self.assertEqual(14530946, generator.FileHash('examples/rdma.gen'))
    self.assertEqual(148504078, generator.FileHash('examples/packed.gen'))
    self.assertEqual(0, generator.FileHash('no/such/file.gen'))

  def testDifferentVersion(self):
    """Tests that the FileHash will return different values for the same
    file if the generator version changes.
    """
    generator.GENERATOR_VERSION = 1
    # These values should be different from values in testSimple.
    self.assertEqual(14530947, generator.FileHash('examples/rdma.gen'))
    self.assertEqual(148504079, generator.FileHash('examples/packed.gen'))
    self.assertEqual(1, generator.FileHash('no/such/file.gen'))

class AlignmentCheckerTest(unittest.TestCase):
  def Parse(self, contents):
    """Parses and checks the gen file for sanity.
    Returns the parsed document, or None if errors.
    """
    gen_parser = parser.GenParser()
    errors = gen_parser.Parse('filename', contents)
    if errors:
      print(errors)
      return None

    checker = parser.Checker()
    checker.VisitDocument(gen_parser.current_document)
    if len(checker.errors) > 0:
      print(checker.errors)
      return None

    return gen_parser.current_document

  def testSimpleAlignment(self):
    contents = [
      'STRUCT A',
      '0 63:0 uint64_t a',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(True)
    aligner.VisitDocument(doc)
    self.assertEqual(0, len(aligner.errors))

  def testBadAlignment(self):
    contents = [
      'STRUCT A',
      '0 63:56 uint8_t a',
      '0 55:24 uint32_t b',  # Must be 32 bit aligned.
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(False)
    aligner.VisitDocument(doc)
    self.assertEqual(1, len(aligner.errors))
    self.assertIn('Expected alignment: 32 bits', aligner.errors[0])

  def testAlignmentOkIfPacked(self):
    contents = [
      'STRUCT A',
      '0 63:56 uint8_t a',
      '0 55:24 uint32_t b',  # OK for 8 bit alignment if packed.
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(True)
    aligner.VisitDocument(doc)
    print(aligner.errors)
    self.assertEqual(0, len(aligner.errors))

  def testBitfieldAlignmentOk(self):
    contents = [
      'STRUCT A',
      '0 63:61 uint8_t a',
      '0 60:56 uint8_t b',
      'END'
      ]
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(False)
    aligner.VisitDocument(doc)
    self.assertEqual(0, len(aligner.errors))


  def testBitfieldDeservesNewWord(self):
    contents = [
      'STRUCT A',
      '0 63:56 uint8_t a',
      '0 55:53 uint8_t b',
      '0 52:48 uint8_t c',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(False)
    aligner.VisitDocument(doc)
    self.assertEqual(1, len(aligner.errors))
    self.assertIn('because of switch from non-bitfield', aligner.errors[0])

  def testNonBitfieldDeservesNewWord(self):
    contents = [
      'STRUCT A',
      '0 63:61 uint8_t a',
      '0 60:53 uint8_t b',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(False)
    aligner.VisitDocument(doc)
    self.assertEqual(1, len(aligner.errors))
    self.assertIn('because of switch from bitfield', aligner.errors[0])

  def testBitfieldOkOnWordBoundary(self):
    contents = [
      'STRUCT A',
      '0 63:32 uint32_t a',
      '0 31:30 uint8_t b',
      '0 29:24 uint8_t c',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(False)
    aligner.VisitDocument(doc)
    self.assertEqual(0, len(aligner.errors))

  def testNonBitfieldOkOnWordBoundary(self):
    contents = [
      'STRUCT A',
      '0 63:42 uint32_t a',
      '0 41:32 uint32_t b',
      '0 31:0 uint32_t c',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)
    aligner = generator.AlignmentChecker(False)
    aligner.VisitDocument(doc)
    self.assertEqual(0, len(aligner.errors))

  def testBitfieldDeservesNewWordIfPacked(self):
    contents = [
      'STRUCT A',
      '0 63:56 uint8_t a',
      '0 55:53 uint8_t b',
      '0 52:48 uint8_t c',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(True)
    aligner.VisitDocument(doc)
    self.assertEqual(1, len(aligner.errors))
    self.assertIn('because of switch from non-bitfield', aligner.errors[0])

  def testNonBitfieldDeservesNewWordIfPacked(self):
    contents = [
      'STRUCT A',
      '0 63:61 uint8_t a',
      '0 60:53 uint8_t b',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(True)
    aligner.VisitDocument(doc)
    self.assertEqual(1, len(aligner.errors))
    self.assertIn('because of switch from bitfield', aligner.errors[0])

  def testBitfieldOkOnWordBoundaryIfPacked(self):
    contents = [
      'STRUCT A',
      '0 63:32 uint32_t a',
      '0 31:30 uint8_t b',
      '0 29:24 uint8_t c',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(True)
    aligner.VisitDocument(doc)
    self.assertEqual(0, len(aligner.errors))

  def testFlagErrorIfMisalignFullType(self):
    gen_parser = parser.GenParser()
    # Even with the packed attribute, llvm still treats uint8_t with
    # the same number of bits as the type as something to align.
    # We can misalign uint8_t only with a bitfield, and only if the
    # bitfield is smaller than the type.
    contents = [
      'STRUCT s',
      '0 63:60 uint8_t a',
      '0 59:52 uint8_t b',
      '0 51:44 uint8_t c',
      '0 43:36 uint8_t d',
      'END'
      ]

    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(False)
    aligner.VisitDocument(doc)

    self.assertEqual(3, len(aligner.errors))
    print(aligner.errors)
    self.assertIn('"b" cannot be placed', aligner.errors[0])
    self.assertIn('"c" cannot be placed', aligner.errors[1])
    self.assertIn('"d" cannot be placed', aligner.errors[2])

  def testIncorrectSmallIntPosition(self):
    contents = [
      'STRUCT A',
      '0 63:56 uint8_t a',
      '0 55:40 uint16_t b',
      'END',
      ]

    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(False)
    aligner.VisitDocument(doc)
    self.assertEqual(1, len(aligner.errors))
    self.assertIn('Field "b" cannot be placed', aligner.errors[0])

  def testAlignmentOnPackedField(self):
    contents = [
      'STRUCT A',
      '0 63:51 uint32_t a',
      '0 50:43 uint32_t b',
      '0 42:32 uint32_t c',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    packer = generator.Packer()
    packer.VisitDocument(doc)
    self.assertEqual(0, len(packer.errors))

    aligner = generator.AlignmentChecker(True)
    aligner.VisitDocument(doc)
    self.assertEqual(0, len(aligner.errors))

  def testOkAlignmentOnPackedFieldPackedStruct(self):
    contents = [
      'STRUCT A',
      '0 63:56 uint8_t start',
      # Ok to put a_to_c on 8 bit boundary because structure is packed.
      '0 55:51 uint32_t a',
      '0 50:43 uint32_t b',
      '0 42:24 uint32_t c',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    packer = generator.Packer()
    packer.VisitDocument(doc)
    self.assertEqual(0, len(packer.errors))

    aligner = generator.AlignmentChecker(True)
    aligner.VisitDocument(doc)
    self.assertEqual(0, len(aligner.errors))

  def testBadAlignmentOnPackedFieldNonPackedStruct(self):
    contents = [
      'STRUCT A',
      '0 63:56 uint8_t start',
      # Not ok to put a_to_c on 8 bit boundary if structure isn't packed.
      '0 55:51 uint32_t a',
      '0 50:43 uint32_t b',
      '0 42:24 uint32_t c',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    packer = generator.Packer()
    packer.VisitDocument(doc)
    self.assertEqual(0, len(packer.errors))

    aligner = generator.AlignmentChecker(False)
    aligner.VisitDocument(doc)

    self.assertEqual(1, len(aligner.errors))
    self.assertIn('Field "a_to_c" cannot be placed', aligner.errors[0])

  def testZeroLengthArrayAlignmentCharArray(self):
    contents = [
      'STRUCT A',
      '0 63:56 uint8_t a',
      # Ok because aligned to 8 bits.
      '_ _:_ uint8_t rest[0]',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(False)
    aligner.VisitDocument(doc)
    self.assertEqual(0, len(aligner.errors))

  def testZeroLengthArrayAlignmentCharArrayPackedStructure(self):
    contents = [
      'STRUCT A',
      '0 63:56 uint8_t a',
      # Ok because aligned to 8 bits.
      '_ _:_ uint8_t rest[0]',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(True)
    aligner.VisitDocument(doc)
    self.assertEqual(0, len(aligner.errors))

  def testZeroLengthArrayAlignmentWordArray(self):
    contents = [
      'STRUCT A',
      '0 63:56 uint8_t a',
      # Not ok because array wants to be on 32 bit alignment.
      '_ _:_ uint32_t rest[0]',
      'END']
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(False)
    aligner.VisitDocument(doc)
    self.assertEqual(1, len(aligner.errors))
    self.assertIn('Field "rest" cannot be placed at location',
                  aligner.errors[0])

  def testBitfieldNotAllowedEvenIfSameType(self):
    contents = [
      'STRUCT s',
      '0 63:56 uint8_t a',
      '0 55:54 uint8_t b',
      '0 53:48 uint8_t c',
      '0 47:40 uint8_t d',
      'END'
      ]
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(False)
    aligner.VisitDocument(doc)
    self.assertEqual(2, len(aligner.errors))
    self.assertIn('Field "b" cannot be placed at location', aligner.errors[0])
    self.assertIn('Field "d" cannot be placed at location', aligner.errors[1])

  def testBitfieldNotAllowedEvenIfSameTypePackedStruct(self):
    contents = [
      'STRUCT A',
      # Even if we're using packed attribute on A, bitfields will
      # be in different word.
      '0 63:56 uint8_t a',
      '0 55:54 uint8_t b',
      '0 53:48 uint8_t c',
      '0 47:40 uint8_t d',
      'END'
      ]
    doc = self.Parse(contents)
    self.assertIsNotNone(doc)

    aligner = generator.AlignmentChecker(True)
    aligner.VisitDocument(doc)
    self.assertEqual(2, len(aligner.errors))
    self.assertIn('Field "b" cannot be placed at location', aligner.errors[0])
    self.assertIn('Field "d" cannot be placed at location', aligner.errors[1])

if __name__ == '__main__':
    unittest.main()
