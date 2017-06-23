# Unit tests for generator.py
#
# Robert Bowdidge, August 8, 2016.
# Copyright Fungible Inc. 2016.

import unittest 

import generator


class TestTypes(unittest.TestCase):
  def testBitWidth(self):
    self.assertEqual(32, generator.Type("uint32_t").BitWidth())
    self.assertEqual(32, generator.Type("unsigned").BitWidth())
    self.assertEqual(8, generator.Type("char").BitWidth())
    self.assertEqual(64, generator.Type("double").BitWidth())
    self.assertEqual(8, generator.Type("uint8_t").BitWidth())

    self.assertEqual(128, generator.Type("uint8_t", 16).BitWidth())
    self.assertEqual(128, generator.Type("uint64_t", 2).BitWidth())

  def testIsArray(self):
    self.assertTrue(generator.Type("uint32_t", 4).IsArray())
    self.assertTrue(generator.Type("char", 16).IsArray())

    self.assertFalse(generator.Type("double").IsArray())
    self.assertFalse(generator.Type("int").IsArray())

  def testBaseName(self):
    self.assertEqual("uint32_t", generator.Type("uint32_t").BaseName())
    self.assertEqual("uint32_t", generator.Type("uint32_t", 4).BaseName())

  def testCompare(self):
    self.assertEqual(generator.Type("uint32_t"), generator.Type("uint32_t"))
    self.assertEqual(generator.Type("uint8_t"), generator.Type("uint8_t"))

    self.assertNotEqual(generator.Type("uint8_t"), generator.Type("char"))

    self.assertEqual(generator.Type("uint8_t", 4), generator.Type("uint8_t", 4))

    self.assertNotEqual(generator.Type("char", 4), generator.Type("uint16_t", 4))
    self.assertNotEqual(generator.Type("char", 4), generator.Type("char", 8))


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
    self.assertEqual(0, firstField.flit)
    self.assertEqual(63, firstField.start_bit)
    self.assertEqual(0, firstField.end_bit)
    self.assertEqual('packet', firstField.name)

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

  def testValidFile(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 63:0 uint64_t packet', 'END']
    
    errors = doc_builder.Parse(contents)
  
    self.assertIsNone(errors)

  def testTooBigFlit(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 64:0 uint64_t packet', 'END']
    
    errors = doc_builder.Parse(contents)

    self.assertEqual(1, len(errors))
    self.assertIn('has start bit "64" too large', errors[0])

  def testArray(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 63:0 uint8_t chars[8]', 'END']

    errors = doc_builder.Parse(contents)

    self.assertIsNone(errors)

    doc = doc_builder.current_document
    self.assertEqual(1, len(doc.structs))

    my_struct = doc.structs[0]
    self.assertEqual(1, len(my_struct.fields))
    my_field = my_struct.fields[0]

    self.assertEqual('chars', my_field.name)
    self.assertEqual(generator.Type('uint8_t', 8), my_field.type)
    self.assertEqual(True, my_field.type.IsArray())
    self.assertEqual(8, my_field.type.ArraySize())
    self.assertEqual(0, my_field.flit)
    self.assertEqual(64, my_field.Size())
    self.assertEqual(0, my_field.flit)


  def testArraySizedTooSmall(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 63:0 uint8_t chars[2]', 'END']

    errors = doc_builder.Parse(contents)
    self.assertEqual(1, len(errors))
    self.assertIn('needed 16 bytes', errors[0])

  def testArraySizedTooLarge(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 63:0 uint8_t chars[16]', 'END']

    errors = doc_builder.Parse(contents)
    self.assertEqual(1, len(errors))
    self.assertIn('needed 128 bytes', errors[0])
                     

  def testEnum(self):
    doc_builder = generator.DocBuilder()
    contents = ['ENUM Commands', 'A = 1', 'BBBBBB=0x02', 'END']
    
    errors = doc_builder.Parse(contents)
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

    self.assertIsNone(doc_builder.ParseFieldLine(line))
  
    self.assertEqual(1, len(doc_builder.errors))
    self.assertIn('Invalid flit', doc_builder.errors[0])

  def testInvalidStart(self):
    # Test generator rejects field with a non-numeric start_bit.
    doc_builder = generator.DocBuilder()
    line = '2 foo:15 uint64_t packet'
    
    self.assertIsNone(doc_builder.ParseFieldLine(line))
  
    self.assertEqual(1, len(doc_builder.errors))
    self.assertIn('Invalid start bit', doc_builder.errors[0])

  def testInvalidEnd(self):
    # Test generator rejects field with non-numeric end bit.
    doc_builder = generator.DocBuilder()
    line = '2 15:bar uint64_t packet'
    
    self.assertIsNone(doc_builder.ParseFieldLine(line))
  
    self.assertEqual(1, len(doc_builder.errors))
    self.assertIn('Invalid end bit', doc_builder.errors[0])

  def testWrongOrder(self):
    # Test generator rejects field with high bit below low.
    doc_builder = generator.DocBuilder()
    line = '2 3:10 uint64_t packet'
    
    self.assertIsNotNone(doc_builder.ParseFieldLine(line))
  
    self.assertEqual(1, len(doc_builder.errors))
    self.assertIn('greater than end bit', doc_builder.errors[0])

  def testTypeTooSmall(self):
    # Test generator rejects field with a non-numeric flit number.
    doc_builder = generator.DocBuilder()
    line = '2 40:0 uint8_t packet'
    
    self.assertIsNone(doc_builder.ParseFieldLine(line))
  
    self.assertEqual(1, len(doc_builder.errors))
    self.assertIn('too small to hold', doc_builder.errors[0])

  def testSingleBit(self):
    # Test generator rejects field with a single-digit field number.
    # TODO(bowdidge): Consider supporting.
    doc_builder = generator.DocBuilder()
    line = '2 38 uint8_t packet'
    
    field = doc_builder.ParseFieldLine(line)
    self.assertIsNotNone(field)
    self.assertEqual(0, len(doc_builder.errors))

    self.assertEqual(2, field.flit)
    self.assertEqual(38, field.start_bit)
    self.assertEqual(38, field.end_bit)


  def testMissingCommentIsNone(self):
    # Test that code correctly handles a packet with a non-numeric flit number.
    doc_builder = generator.DocBuilder()
    line = '2 15:12 int64_t packet'
    
    field = doc_builder.ParseFieldLine(line)
  
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
    builder.ParseEnd('END')
    builder.ParseUnionStart('UNION Baz u')
    builder.ParseLine('0 63:0 uint64_t packet')
    builder.ParseEnd('END')
    builder.ParseEnd('END')

    doc = builder.current_document
    self.assertEqual(1, len(doc.structs))

    firstStruct = doc.structs[0]
    self.assertEqual(0, len(firstStruct.fields))
    self.assertEqual(2, len(firstStruct.unions))

    firstUnion = firstStruct.unions[0]
    firstField = firstUnion.fields[0]
    self.assertEqual(0, firstField.flit)
    self.assertEqual(63, firstField.start_bit)
    self.assertEqual(0, firstField.end_bit)
    self.assertEqual('packet', firstField.name)

  def testParseCommentInField(self):
    doc_builder = generator.DocBuilder()

    field = doc_builder.ParseFieldLine(
      '0 47:0 uint64_t packet /* 6 byte packet to send out */')

    self.assertEqual(0, len(doc_builder.errors))

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
    builder.Parse(the_file)
    
    self.assertEqual(0, len(builder.errors))
    self.assertIsNotNone(builder.current_document)
    self.assertEqual(1, len(builder.current_document.structs))

    the_struct = builder.current_document.structs[0]
    self.assertIsNone(the_struct.key_comment)
    self.assertEqual('Body comment\n', the_struct.body_comment)
    self.assertEqual('Tail comment\n', the_struct.tail_comment)

    self.assertEqual(1, len(the_struct.fields))
    the_field = the_struct.fields[0]
    self.assertEqual('Packet key comment', the_field.key_comment)
    self.assertEqual('Packet body comment\n', the_field.body_comment)
    self.assertIsNone(the_field.tail_comment)


class PackerTest(unittest.TestCase):
  def testDontPackArgumentsFittingOwnType(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 63:32 unsigned packet',
                '0 31:0 unsigned other','END']
    errors = doc_builder.Parse(contents)
    self.assertIsNone(errors)

    doc = doc_builder.current_document
    p = generator.Packer()
    p.VisitDocument(doc)

    self.assertEqual(2, len(doc.structs[0].fields))
    self.assertEqual("packet", doc.structs[0].fields[0].name)

  def testNoPackSingleField(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 31:0 unsigned packet', 'END']
    errors = doc_builder.Parse(contents)
    self.assertIsNone(errors)

    doc = doc_builder.current_document
    p = generator.Packer()
    p.VisitDocument(doc)
    
    self.assertEqual(1, len(doc.structs[0].fields))
    field = doc.structs[0].fields[0]
    # Packer doesn't change name.
    self.assertEqual('packet', field.name)
    self.assertEqual(31, field.start_bit)
    self.assertEqual(0, field.end_bit)

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
    errors = doc_builder.Parse(contents)
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
    errors = doc_builder.Parse(contents)
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
    errors = doc_builder.Parse(contents)
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

  def testNoPackArrayAndRegularType(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', 
                '0 63:8 uint8_t chars[7]',
                '0 7:0 uint8_t opcode',
                'END']

    errors = doc_builder.Parse(contents)

    self.assertIsNone(errors)

    doc = doc_builder.current_document
    self.assertEqual(1, len(doc.structs))

    p = generator.Packer()
    p.VisitDocument(doc)

    self.assertEqual(2, len(doc.structs[0].fields))

  def testNoPackArray(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo', 
                '0 63:32 uint8_t chars[4]',
                '0 31:0 uint8_t opcode[4]',
                'END']

    errors = doc_builder.Parse(contents)

    self.assertIsNone(errors)

    doc = doc_builder.current_document
    self.assertEqual(1, len(doc.structs))

    p = generator.Packer()
    p.VisitDocument(doc)

    self.assertEqual(2, len(doc.structs[0].fields))


class CheckerTest(unittest.TestCase):

  def testCheckerAdjacentTypesEqual(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 3:2 uint8_t b',
                '0 1:0 uint8_t a',
                'END']
    errors = doc_builder.Parse(contents)
    self.assertIsNone(errors)

    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(0, len(checker.warnings))

  def testCheckerAdjacentTypesDifferent(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 3:2 uint16_t b',
                '0 1:0 uint8_t a',
                'END']
    errors = doc_builder.Parse(contents)
    self.assertIsNone(errors)

    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    print(checker.warnings)
    self.assertEqual(1, len(checker.warnings))
    self.assertIn('allow alignment', checker.warnings[0])

  def testFlagOutOfOrder(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 7:0 uint8_t b',
                '0 15:8 uint8_t a',
                'END']
    errors = doc_builder.Parse(contents)
    self.assertIsNone(errors)

    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(1, len(checker.warnings))
    self.assertIn('field "b" and "a" not in bit order', checker.warnings[0])

  def testFlagOverlappingFields(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 15:8 uint8_t b',
                '0 15:0 uint16_t a',
                'END']
    errors = doc_builder.Parse(contents)
    self.assertIsNone(errors)
    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(1, len(checker.warnings))
    self.assertIn('field "b" and "a" not in bit order', checker.warnings[0])

  def testFlagOverlappingFieldsEqualAtBottom(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 15:8 uint8_t b',
                '0 12:8 uint8_t a',
                'END']
    errors = doc_builder.Parse(contents)
    self.assertIsNone(errors)
    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(1, len(checker.warnings))
    self.assertIn('field "b" and "a" not in bit order', checker.warnings[0])

  def testFlagOverlappingFieldsBottom(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 15:8 uint8_t b',
                '0 9:7 uint8_t a',
                'END']
    errors = doc_builder.Parse(contents)
    self.assertIsNone(errors)
    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(1, len(checker.warnings))
    self.assertIn('field "b" overlaps field "a"', checker.warnings[0])

  def testFlagExtraSpace(self):
    doc_builder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 15:8 uint8_t b',
                '0 3:0 uint8_t a',
                'END']
    errors = doc_builder.Parse(contents)
    self.assertIsNone(errors)
    checker = generator.Checker()
    checker.VisitDocument(doc_builder.current_document)

    self.assertEqual(1, len(checker.warnings))
    self.assertIn('unexpected space between field "b" and "a"',
                  checker.warnings[0])

if __name__ == '__main__':
    unittest.main()
