# Unit tests for generator.py
#
# Robert Bowdidge, August 8, 2016.
# Copyright Fungible Inc. 2016.

import unittest 

import generator


class TestTypes(unittest.TestCase):
  def testBitWidth(self):
    self.assertEqual(32, generator.TypeForName("uint32_t").BitWidth())
    self.assertEqual(32, generator.TypeForName("unsigned").BitWidth())
    self.assertEqual(8, generator.TypeForName("char").BitWidth())
    self.assertEqual(64, generator.TypeForName("double").BitWidth())
    self.assertEqual(8, generator.TypeForName("uint8_t").BitWidth())

    self.assertEqual(128, generator.ArrayTypeForName("uint8_t", 16).BitWidth())
    self.assertEqual(128, generator.ArrayTypeForName("uint64_t", 2).BitWidth())

  def testIsArray(self):
    self.assertTrue(generator.ArrayTypeForName("uint32_t", 4).IsArray())
    self.assertTrue(generator.ArrayTypeForName("char", 16).IsArray())

    self.assertFalse(generator.TypeForName("double").IsArray())
    self.assertFalse(generator.TypeForName("int").IsArray())

  def testBaseName(self):
    self.assertEqual("uint32_t", 
                     generator.TypeForName("uint32_t").BaseName())
    self.assertEqual("uint32_t",
                     generator.ArrayTypeForName("uint32_t", 4).BaseName())

  def testCompare(self):
    self.assertEqual(generator.TypeForName("uint32_t"),
                     generator.TypeForName("uint32_t"))
    self.assertEqual(generator.TypeForName("uint8_t"),
                     generator.TypeForName("uint8_t"))

    self.assertNotEqual(generator.TypeForName("uint8_t"),
                        generator.TypeForName("char"))

    self.assertEqual(generator.ArrayTypeForName("uint8_t", 4),
                     generator.ArrayTypeForName("uint8_t", 4))

    self.assertNotEqual(generator.ArrayTypeForName("char", 4),
                        generator.ArrayTypeForName("uint16_t", 4))
    self.assertNotEqual(generator.ArrayTypeForName("char", 4),
                        generator.ArrayTypeForName("char", 8))


class TestDocBuilder(unittest.TestCase):
  # Test that we correctly parse valid and invalid structure definitions.
  def testEmptyDoc(self):
    doc = generator.DocBuilder()
    self.assertIsNotNone(doc.current_document)

  def testParseSimpleStructLine(self):
    builder = generator.DocBuilder()  
    doc = builder.current_document
    self.assertEqual(0, len(doc.structs))

    builder.ParseStructStart('STRUCT Foo')
    builder.ParseLine('0 63:0 uint64_t packet')
    builder.ParseEnd('END')

    doc = builder.current_document
    self.assertEqual(0, len(builder.errors))

    print("testParseSimpleStruct %s" % doc)
    self.assertEqual(1, len(doc.structs))

    firstStruct = doc.structs[0]
    self.assertEqual(1, len(firstStruct.fields))

    firstField = firstStruct.fields[0]
    self.assertEqual(0, firstField.StartFlit())
    self.assertEqual(0, firstField.EndFlit())
    self.assertEqual(63, firstField.StartBit())
    self.assertEqual(0, firstField.EndBit())
    self.assertEqual('packet', firstField.name)

    self.assertEqual(1, firstStruct.Flits())

  def testStructSize(self): 
    builder = generator.DocBuilder()
    doc = builder.current_document

    builder.ParseStructStart('STRUCT Foo')
    builder.ParseLine('0 63:0 uint64_t packet')
    builder.ParseEnd('END')

    self.assertEqual(1, len(doc.structs))

    struct = doc.structs[0]
    self.assertEqual(8, struct.Bytes())

  def testNotPackedStructSize(self): 
    builder = generator.DocBuilder()
    doc = builder.current_document

    builder.ParseStructStart('STRUCT Foo')
    builder.ParseLine('0 63:0 uint64_t packet')
    builder.ParseLine('1 63:56 uint64_t bar')
    builder.ParseEnd('END')

    self.assertEqual(1, len(doc.structs))
                     
    struct = doc.structs[0]
    # TODO(bowdidge): Should be 9 bytes?
    self.assertEqual(16, struct.Bytes())
    self.assertEqual(2, struct.Flits())

  def testValidFile(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 63:0 uint64_t packet', 'END']
    
    errors = doc_builder.Parse('filename', contents)
  
    self.assertIsNone(errors)

  def testTooBigFlit(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 64:0 uint64_t packet', 'END']
    errors = doc_builder.Parse('filename', contents)

    self.assertEqual(1, len(errors))
    self.assertIn('has start bit "64" too large', errors[0])

  def testSimpleStructBitWidth(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 63:0 uint64_t packet', 'END']
    
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
    doc = doc_builder.current_document

    self.assertEquals(1, len(doc.structs))

    s = doc.structs[0]
    self.assertEquals(64, s.BitWidth())
  
  def testPartialFlitBitWidth(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 63:16 uint64_t packet', 'END']
    
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
    doc = doc_builder.current_document

    self.assertEquals(1, len(doc.structs))

    s = doc.structs[0]
    self.assertEquals(48, s.BitWidth())

  def testPartialFlitBitWidth(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 63:32 uint32_t a', 
                '0 31:0 uint32_t b', 
                '1 63:32 uint32_t c', 
                'END']
    
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
    doc = doc_builder.current_document

    self.assertEquals(1, len(doc.structs))

    s = doc.structs[0]
    self.assertEquals(96, s.BitWidth())

  def testArray(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 63:0 uint8_t chars[8]', 'END']

    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
    doc = doc_builder.current_document

    self.assertEqual(1, len(doc.structs))

    my_struct = doc.structs[0]
    self.assertEqual(1, len(my_struct.fields))
    my_field = my_struct.fields[0]

    self.assertEqual('chars', my_field.name)
    self.assertEqual(generator.ArrayTypeForName('uint8_t', 8),
                     my_field.type)
    self.assertEqual(True, my_field.type.IsArray())
    self.assertEqual(8, my_field.type.ArraySize())
    self.assertEqual(0, my_field.StartFlit())
    self.assertEqual(0, my_field.EndFlit())
    self.assertEqual(64, my_field.BitWidth())


  def testArraySizedTooSmall(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', 
                '0 63:0 uint8_t chars[2]', 
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('is 64 bits, type "uint8_t[2]" is 16', errors[0])

  def testMultiFlitTooSmall(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 63:0 uint8_t chars[10]',
                '1 63:0 ...',
                'END']

    errors = doc_builder.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('expected 80 bits, got 128', errors[0])

  def testMultiFlitNotNeeded(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 63:0 uint8_t chars[8]',
                '1 63:0 ...',
                'END']

    errors = doc_builder.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('Multi-line flit continuation seen without', errors[0])

  def testMultiFlitTooLarge(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 63:0 uint8_t chars[18]',
                '1 63:0 ...',
                '2 63:0 uint64_t value',
                'END']

    errors = doc_builder.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('Field spec for "chars" too short: expected 144 bits, got 128',
                  errors[0])

  def testArraySizedTooLarge(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 63:0 uint8_t chars[16]', 'END']

    errors = doc_builder.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('expected 128 bits, got 64', errors[0])
                     

  def testEnum(self):
    doc_builder = generator.DocBuilder()
    contents = ['ENUM Commands', 'A = 1', 'BBBBBB=0x02', 'END']
    
    errors = doc_builder.Parse('filename', contents)
    doc = doc_builder.current_document
  
    self.assertEqual(1, len(doc.enums))
    my_enum = doc.enums[0]
    self.assertEqual(2, len(my_enum.variables))
    var_a = my_enum.variables[0]
    var_b = my_enum.variables[1]
    self.assertEqual('A', var_a.name)
    self.assertEqual(1, var_a.value)
                    
    self.assertEqual('BBBBBB', var_b.name)
    self.assertEqual(2, var_b.value)

  def testLargeEnum(self):
    doc_builder = generator.DocBuilder()
    contents = ['ENUM Commands', 'A = 31', 'BBBBBB=0x3f', 'END']
    
    errors = doc_builder.Parse('filename', contents)
    doc = doc_builder.current_document
  
    self.assertEqual(1, len(doc.enums))
    my_enum = doc.enums[0]
    self.assertEqual(2, len(my_enum.variables))
    var_a = my_enum.variables[0]
    var_b = my_enum.variables[1]
    self.assertEqual('A', var_a.name)
    self.assertEqual(31, var_a.value)
                    
    self.assertEqual('BBBBBB', var_b.name)
    self.assertEqual(63, var_b.value)

  def testBadEnumFields(self):
    doc_builder = generator.DocBuilder()
    self.assertIsNone(doc_builder.ParseEnumLine("A"))
    self.assertIsNone(doc_builder.ParseEnumLine("3"))
    self.assertIsNone(doc_builder.ParseEnumLine("A=A"))
    self.assertIsNone(doc_builder.ParseEnumLine("A,A"))

  def testGoodEnumFields(self):
    doc_builder = generator.DocBuilder()
    field = doc_builder.ParseEnumLine('A=1')
    self.assertEqual('A', field.name)
    self.assertEqual(1, field.value)
    self.assertIsNone(field.key_comment)
    self.assertIsNone(field.body_comment)

    field = doc_builder.ParseEnumLine('bb1 = 3 /* Foobar */')
    self.assertEqual('bb1', field.name)
    self.assertEqual(3, field.value)
    self.assertEqual("Foobar", field.key_comment)

  def testInvalidFlit(self):
    # Test generator rejects a field with a non-numeric flit number.
    doc_builder = generator.DocBuilder()
    line = 'flit 63:0 uint64_t packet'

    doc_builder.ParseFieldLine(line, generator.Struct("fakeStruct", False))
  
    self.assertEqual(1, len(doc_builder.errors))
    self.assertIn('Invalid bit pattern', doc_builder.errors[0])

  def testInvalidTypeName(self):
    doc_builder = generator.DocBuilder()
    line = '0 63:0 NotAValidType field_name'

    doc_builder.ParseFieldLine(line, generator.Struct("fakeStruct", False))

    self.assertEqual(1, len(doc_builder.errors))
    self.assertIn('Unknown type name', doc_builder.errors[0])

  def testInvalidStart(self):
    # Test generator rejects field with a non-numeric start_bit.
    doc_builder = generator.DocBuilder()
    line = '2 foo:15 uint64_t packet'
    
    doc_builder.ParseFieldLine(line, generator.Struct("fakeStruct", False))
  
    self.assertEqual(1, len(doc_builder.errors))
    self.assertIn('Invalid bit pattern', doc_builder.errors[0])

  def testInvalidEnd(self):
    # Test generator rejects field with non-numeric end bit.
    doc_builder = generator.DocBuilder()
    line = '2 15:bar uint64_t packet'
    
    doc_builder.ParseFieldLine(line, generator.Struct("fakeStruct", False))
  
    self.assertEqual(1, len(doc_builder.errors))
    self.assertIn('Invalid bit pattern', doc_builder.errors[0])

  def testWrongOrder(self):
    # Test generator rejects field with high bit below low.
    doc_builder = generator.DocBuilder()
    line = '2 3:10 uint64_t packet'
    
    doc_builder.ParseFieldLine(line, generator.Struct("fakeStruct", False))
  
    self.assertEqual(1, len(doc_builder.errors))
    self.assertIn('greater than end bit', doc_builder.errors[0])

  def testSingleBit(self):
    # Test generator accepts field with a single-digit field number.
    doc_builder = generator.DocBuilder()
    line = '2 38 uint8_t packet'
    
    struct = generator.Struct("fakeStruct", False)
    self.assertTrue(doc_builder.ParseFieldLine(line, struct))

    self.assertEqual(1, len(struct.fields))
    field = struct.fields[0]

    self.assertIsNotNone(field)
    self.assertEqual(0, len(doc_builder.errors))

    self.assertEqual(2, field.StartFlit())
    self.assertEqual(2, field.EndFlit())
    self.assertEqual(38, field.StartBit())
    self.assertEqual(38, field.EndBit())

  def testMissingCommentIsNone(self):
    doc_builder = generator.DocBuilder()
    line = '2 15:12 int64_t packet'
    
    struct = generator.Struct("fakeStruct", False)
    self.assertTrue(doc_builder.ParseFieldLine(line, struct))

    self.assertEqual(1, len(struct.fields))
    field = struct.fields[0]
    
    self.assertIsNone(field.key_comment)
    self.assertIsNone(field.body_comment)
    self.assertIsNone(field.generator_comment)

  def testSimpleUnion(self): 
    builder = generator.DocBuilder()  
    doc = builder.current_document

    self.assertEqual(0, len(doc.structs))

    builder.ParseStructStart('STRUCT Foo')
    builder.ParseUnionStart('UNION Bar u')
    builder.ParseLine('0 63:0 uint64_t packet')
    builder.ParseLine('0 63:0 uint64_t buf')
    builder.ParseEnd('END')
    builder.ParseEnd('END')

    doc = builder.current_document
    self.assertEqual(2, len(doc.structs))

    firstStruct = doc.structs[0]

    self.assertEqual('Foo', firstStruct.Name())
    self.assertEqual(1, len(firstStruct.fields))
    self.assertEqual('u', firstStruct.fields[0].name)

    union = builder.current_document.structs[1]
    self.assertEqual('Bar', union.Name())

    firstField = union.fields[0]
    self.assertEqual(0, firstField.StartFlit())
    self.assertEqual(0, firstField.EndFlit())
    self.assertEqual(63, firstField.StartBit())
    self.assertEqual(0, firstField.EndBit())
    self.assertEqual('packet', firstField.name)

  def testParseCommentInField(self):
    doc_builder = generator.DocBuilder()

    struct = generator.Struct("fakeStruct", False)
    self.assertTrue(doc_builder.ParseFieldLine(
      '0 47:0 uint64_t packet /* 6 byte packet to send out */',
      struct))

    self.assertEqual(0, len(doc_builder.errors))

    self.assertEqual(1, len(struct.fields))
    field = struct.fields[0]
                     
    self.assertEqual("packet", field.name)
    self.assertEqual("6 byte packet to send out", field.key_comment)

  def testParseTailComment(self):
    builder = generator.DocBuilder()
    the_file = ['// Body comment\n',
                'STRUCT Foo\n',
                '// Packet body comment\n',
                '0 63:0 uint64_t packet // Packet key comment\n',
                '// Tail comment\n',
                'END\n']
    builder.Parse('filename', the_file)
    
    self.assertEqual(0, len(builder.errors))
    self.assertIsNotNone(builder.current_document)
    self.assertEqual(1, len(builder.current_document.structs))

    the_struct = builder.current_document.structs[0]
    self.assertEqual(None, the_struct.key_comment)
    self.assertEqual('Body comment\n', the_struct.body_comment)
    self.assertEqual('Tail comment\n', the_struct.tail_comment)

    self.assertEqual(1, len(the_struct.fields))
    the_field = the_struct.fields[0]
    self.assertEqual('Packet key comment', the_field.key_comment)
    self.assertEqual('Packet body comment\n', the_field.body_comment)
    self.assertIsNone(the_field.tail_comment)

  def testParseMultiFlitDots(self):
    doc_builder = generator.DocBuilder()
    # ... allows a field to overflow into later flits.
    contents = [
      'STRUCT Foo',
      '0 63:56 uint8_t command',
      '0 55:0 uint8_t buf[23]',
      '1 63:0 ...',
      '2 63:0 ...',
      'END'
      ]
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = doc_builder.current_document

    self.assertEqual(1, len(doc.structs))

    struct = doc.structs[0]
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
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 63:0 uint8_t chars[16]',
                '0 63:0 ...',
                'END']

    errors = doc_builder.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('reuse', errors[0])


  def testNestedStruct(self):
    doc_builder = generator.DocBuilder()
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
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = doc_builder.current_document

    self.assertEqual(3, len(doc.structs))
    
    foo = doc.structs[0]
    bar = doc.structs[1]
    baz = doc.structs[2]
    
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
    doc_builder = generator.DocBuilder()
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
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = doc_builder.current_document

    self.assertEqual(5, len(doc.structs))
    
    foo = doc.structs[0]
    
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
    
  def testMultiFlitNestedStruct(self):
    doc_builder = generator.DocBuilder()
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
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = doc_builder.current_document

    self.assertEqual(2, len(doc.structs))
    
    common = doc.structs[0]
    cmd = doc.structs[1]
    
    self.assertEqual(128, common.BitWidth())
    self.assertEqual(192, cmd.BitWidth())

  def testVariableLengthArray(self):
    doc_builder = generator.DocBuilder()
    contents = [
      'STRUCT foo',
      '0 63:56 char initial',
      '_ _:_ char array[0]',
      'END'
      ]

    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = doc_builder.current_document

    self.assertEqual(1, len(doc.structs))
    foo = doc.structs[0]
    self.assertEqual(2, len(foo.fields))
    array = foo.fields[1]
    self.assertEquals('<Type: char[0]>', str(array.Type()))
    
    self.assertEqual(8, foo.BitWidth())
    self.assertEqual(0, array.BitWidth())


  def testVariableLengthStructArray(self):
    doc_builder = generator.DocBuilder()
    contents = [
      'STRUCT element',
      '0 63:56 char item',
      'END',
      'STRUCT foo',
      '0 63:56 char initial',
      '_ _:_ element array[0]',
      'END'
      ]

    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = doc_builder.current_document

    self.assertEqual(2, len(doc.structs))
    foo = doc.structs[1]
    self.assertEqual(2, len(foo.fields))
    array = foo.fields[1]
    self.assertEquals('<Type: element[0]>', str(array.Type()))
    
    self.assertEqual(8, foo.BitWidth())
    self.assertEqual(0, array.BitWidth())


class TestStripComment(unittest.TestCase):
  def testSimple(self):
    doc_builder = generator.DocBuilder()
    self.assertEqual("Foo", doc_builder.StripKeyComment("// Foo"))
    self.assertEqual("Foo", doc_builder.StripKeyComment("/* Foo */"))
    self.assertEqual("", doc_builder.StripKeyComment("//"))
    self.assertEqual("", doc_builder.StripKeyComment("/* */"))

  def testNotTerminated(self):
    doc_builder = generator.DocBuilder()
    doc_builder.current_line = 15

    self.assertEqual(None, doc_builder.StripKeyComment('/* foo bar'))
    self.assertEquals(1, len(doc_builder.errors))
    self.assertIn('15: Badly formatted comment',
                  doc_builder.errors[0])

  def testNotStarted(self):
    doc_builder = generator.DocBuilder()
    self.assertEqual(None, doc_builder.StripKeyComment('foo bar */'))
    self.assertEquals(1, len(doc_builder.errors))
    self.assertIn('0: Unexpected stuff where comment should be',
                     doc_builder.errors[0])
                                         

  def testStructureAndUnion(self):
    doc_builder = generator.DocBuilder()
    contents = [
      'STRUCT foo',
      '0 63:0 uint64_t a',
      '1 63:0 uint64_t b',
      'END',
      'STRUCT bar',
      '0 63:0 foo f',
      '1 63:0 ...',
      'UNION baz u',
      '2 63:56 char c',
      'END'
      'END'
      ]

    errors = doc_builder.Parse('filename', contents)

    self.assertIsNone(errors)
    doc = doc_builder.current_document
    self.assertEqual(3, len(doc.structs))

    bar = doc.structs[1]
    self.assertEqual("bar", bar.Name())
    self.assertEqual(2, len(bar.fields))

    f = bar.fields[0]
    u = bar.fields[1]
    self.assertEqual(128, f.BitWidth())
    self.assertEqual(128, u.StartOffset())
    

class PackerTest(unittest.TestCase):
  def testDontPackArgumentsFittingOwnType(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 63:32 unsigned packet',
                '0 31:0 unsigned other','END']
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = doc_builder.current_document
    p = generator.Packer()
    p.VisitDocument(doc)

    self.assertEqual(2, len(doc.structs[0].fields))
    self.assertEqual("packet", doc.structs[0].fields[0].name)

  def testNoPackSingleField(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 31:0 unsigned packet', 'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = doc_builder.current_document
    p = generator.Packer()
    p.VisitDocument(doc)
    
    self.assertEqual(1, len(doc.structs[0].fields))
    field = doc.structs[0].fields[0]
    # Packer doesn't change name.
    self.assertEqual('packet', field.name)
    self.assertEqual(31, field.StartBit())
    self.assertEqual(0, field.EndBit())

  def testPackBitfields(self):
    doc_builder = generator.DocBuilder()
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
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = doc_builder.current_document
    p = generator.Packer()
    p.VisitDocument(doc)
    self.assertEqual(5, len(doc.structs[0].fields))
    self.assertEqual('favorite_char', doc.structs[0].fields[0].name)
    self.assertEqual('is_valid_char_to_foo',
                     doc.structs[0].fields[1].name)
    self.assertEqual('another_char', doc.structs[0].fields[2].name)
    self.assertEqual('third_char', doc.structs[0].fields[3].name)
    self.assertEqual('value', doc.structs[0].fields[4].name)

    # Make sure the comment describing the packed layout appears.
    self.assertIn('6:5: foo', doc.structs[0].fields[1].body_comment)

  def testTypeChanges(self):
    doc_builder = generator.DocBuilder()
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
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = doc_builder.current_document
    p = generator.Packer()
    p.VisitDocument(doc)
    self.assertEqual(6, len(doc.structs[0].fields))
    self.assertEqual('favorite_char', doc.structs[0].fields[0].name)
    self.assertEqual('is_valid_char', doc.structs[0].fields[1].name)
    self.assertEqual('foo_to_bar', doc.structs[0].fields[2].name)
    self.assertEqual('another_char', doc.structs[0].fields[3].name)
    self.assertEqual('third_char', doc.structs[0].fields[4].name)
    self.assertEqual('value', doc.structs[0].fields[5].name)

  def testPackOnlyContiguous(self):
    """Tests that two sets of packed fields separated by a non-packed
    variable are not merged.
    """
    
    doc_builder = generator.DocBuilder()
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

    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = doc_builder.current_document
    p = generator.Packer()
    p.VisitDocument(doc)

    # a, b, d, and e should not be packed.
    self.assertEqual(4, len(doc.structs[0].fields))
    self.assertEqual('a_to_b', doc.structs[0].fields[0].name)
    self.assertEqual('c', doc.structs[0].fields[1].name)
    self.assertEqual('d_to_e', doc.structs[0].fields[2].name)
    self.assertEqual('reserved', doc.structs[0].fields[3].name)

  def testWarningOnPackLargerThanBaseType(self):
    """Tests that two sets of packed fields separated by a non-packed
    variable are not merged.
    """
    doc_builder = generator.DocBuilder()
    contents = [
      'STRUCT Foo',
      '0 63:58 uint8_t a',
      '0 57:54 uint8_t b',
      '0 54:50 uint8_t c',
      '0 50:48 uint8_t d',
      '0 47:0 uint64_t reserved',
      'END'
      ]

    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = doc_builder.current_document
    p = generator.Packer()
    errors = p.VisitDocument(doc)
    
    self.assertTrue(1, len(errors))
    self.assertIn('Fields are 18 bits, type is 8 bits.', errors[0])

  def testReservedFieldIgnoredWhenPacking(self):
    doc_builder = generator.DocBuilder()
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
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
  
    doc = doc_builder.current_document
    p = generator.Packer()
    errors = p.VisitDocument(doc)
    self.assertEqual(0, len(errors))

    self.assertEqual(6, len(doc.structs[0].fields))
    self.assertEqual('favorite_char', doc.structs[0].fields[0].name)
    self.assertEqual('is_valid_char', doc.structs[0].fields[1].name)
    self.assertEqual('foo_to_bar', doc.structs[0].fields[2].name)
    self.assertEqual('another_char', doc.structs[0].fields[3].name)
    self.assertEqual('third_char', doc.structs[0].fields[4].name)
    self.assertEqual('value', doc.structs[0].fields[5].name)

  def testNoPackArrayAndRegularType(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', 
                '0 63:8 uint8_t chars[7]',
                '0 7:0 uint8_t opcode',
                'END']

    errors = doc_builder.Parse('filename', contents)

    self.assertIsNone(errors)

    doc = doc_builder.current_document
    self.assertEqual(1, len(doc.structs))

    p = generator.Packer()
    errors = p.VisitDocument(doc)
    self.assertEqual(0, len(errors))
    

    self.assertEqual(2, len(doc.structs[0].fields))

  def testNoPackArray(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', 
                '0 63:32 uint8_t chars[4]',
                '0 31:0 uint8_t opcode[4]',
                'END']

    errors = doc_builder.Parse('filename', contents)

    self.assertIsNone(errors)

    doc = doc_builder.current_document
    self.assertEqual(1, len(doc.structs))

    p = generator.Packer()
    p.VisitDocument(doc)

    self.assertEqual(2, len(doc.structs[0].fields))

  def testTooManyEnds(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 63:0 uint64_t cmd',
                'STRUCT Bar',
                '1 63:0 uint64_t cmd',
                'END',
                'END',
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('without matching', errors[0])
                

class CheckerTest(unittest.TestCase):

  def testCheckerAdjacentTypesEqual(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 3:2 uint8_t b',
                '0 1:0 uint8_t a',
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)

    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)
    self.assertEqual(0, len(checker.errors))

  def disableTestCheckerAdjacentTypesDifferent(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 3:2 uint16_t b',
                '0 1:0 uint8_t a',
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)

    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    print(checker.errors)
    self.assertEqual(1, len(checker.errors))
    self.assertIn('allow alignment', checker.errors[0])


  def testFlagErrorIfMisalignFullType(self):
    doc_builder = generator.DocBuilder()
    # Even with the packed attribute, llvm still treats uint8_t with
    # the same number of bits as the type as something to align.
    # We can misalign uint8_t only with a bitfield, and only if the
    # bitfield is smaller than the type.
    input = [
      'STRUCT s',
      '0 63:60 uint8_t a',
      '0 59:52 uint8_t b',
      '0 51:44 uint8_t c',
      '0 43:36 uint8_t d',
      'END'
      ]

    doc_builder = generator.DocBuilder()
    errors = doc_builder.Parse('filename', input)
    self.assertIsNone(errors)
  
    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)
    self.assertEqual(3, len(checker.errors))
    self.assertIn('"b" cannot be placed', checker.errors[0])
    self.assertIn('"c" cannot be placed', checker.errors[1])
    self.assertIn('"d" cannot be placed', checker.errors[2])
    
  def testStructTooSmall(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 63:32 uint64_t a',
                'END',
                'STRUCT BAR',
                '0 63:48 Foo f',
                '0 47:32 uint16_t b',
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('Field smaller than type', errors[0])

  def testStructTooLarge(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 63:32 uint64_t a',
                'END',
                'STRUCT BAR',
                '0 63:0 Foo f',
                '1 63:32 uint32_t b',
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertEqual(1, len(errors))
    self.assertIn('Field larger than type', errors[0])

  def testArrayOfStructs(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 63:32 uint64_t a',
                'END',
                'STRUCT BAR',
                '0 63:0 Foo f[2]',
                'END']

    errors = doc_builder.Parse('filename', contents)
    self.assertEqual(None, errors)

    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)
    self.assertEqual(0, len(checker.errors))

    self.assertEqual(2, len(doc_builder.current_document.structs))
    bar = doc_builder.current_document.structs[1]

    self.assertEqual(1, len(bar.fields))

    f = bar.fields[0]
    self.assertTrue(f.type.IsRecord())
    self.assertTrue(f.type.IsArray())

  def testFlagOutOfOrder(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 7:0 uint8_t b',
                '0 15:8 uint8_t a',
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)

    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('field "b" and "a" not in bit order', checker.errors[0])

  def testFlagOverlappingFields(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 15:8 uint8_t a',
                '0 15:0 uint16_t b',
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('field "a" overlaps field "b"', checker.errors[0])

  def testFlagOverlappingFieldsEqualAtBottom(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 15:8 uint8_t a',
                '0 12:8 uint8_t b',
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('field "a" overlaps field "b"', checker.errors[0])

  def testFlagOverlappingFieldsBottom(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 15:8 uint8_t a',
                '0 9:7 uint8_t b',
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('field "a" overlaps field "b"', checker.errors[0])

  def testFlagExtraSpace(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 15:8 uint8_t a',
                '0 3:0 uint8_t b',
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('unexpected space between field "a" and "b"',
                  checker.errors[0])

  def testMultiFlitFieldHandledOk(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 63:56 uint8_t cmd',
                '0 55:0 uint8_t buf[15]',
                '1 63:0 ...',
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(0, len(checker.errors))

  def testMultiFlitFieldOverlapGeneratesWarning(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 63:56 uint8_t cmd',
                '0 55:0 uint8_t buf[15]',
                '1 63:0 ...',
                '1 63:0 uint64_t c',
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)
    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('field "buf" overlaps field "c"',
                  checker.errors[0])

  def testUnionNoOverlap(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 63:0 uint64_t cmd',
                'UNION Bar u',
                '1 63:0 uint64_t data',
                'END',
                'END']
    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)

    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(0, len(checker.errors))

  def testUnionOverlap(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 63:0 uint64_t cmd',
                'UNION Bar u',
                '0 31:0 uint32_t data',
                'END',
                'END']

  def testVariableLengthArray(self):
    doc_builder = generator.DocBuilder()
    contents = [
      'STRUCT foo',
      '0 63:56 char initial',
      '_ _:_ char array[0]',
      'END'
      ]

    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = doc_builder.current_document
    self.assertIsNone(errors)

    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)
    self.assertEqual(0, len(checker.errors))

  def testVariableLengthStructureArray(self):
    doc_builder = generator.DocBuilder()
    contents = [
      'STRUCT element',
      '0 63:56 char value',
      'END',
      'STRUCT foo',
      '0 63:56 char initial',
      '_ _:_ element array[0]',
      'END'
      ]

    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)

    doc = doc_builder.current_document
    self.assertIsNone(errors)

    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)
    self.assertEqual(0, len(checker.errors))

  def testErrorIfVariableLengthArrayNotAtEnd(self):
    doc_builder = generator.DocBuilder()
    contents = [
      'STRUCT foo',
      '0 63:56 char initial',
      '_ _:_ char array[0]',
      '0 55:48 char end',
      'END'
      ]

    errors = doc_builder.Parse('filename', contents)
    self.assertIsNone(errors)

    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(1, len(checker.errors))
    self.assertIn('is not the last field', checker.errors[0])

if __name__ == '__main__':
    unittest.main()
