# Unit tests for generator.py
#
# Robert Bowdidge, August 8, 2016.
# Copyright Fungible Inc. 2016.

import unittest 

import generator


class TestTypeWidth(unittest.TestCase):
  def testTypeWidths(self):
      self.assertEqual(32, generator.typeWidth("uint32_t"))


class TestIndentString(unittest.TestCase):
  def testSimple(self):
    # Tests only properties that hold true regardless of the formatting style.
    codeGen = generator.CodeGenerator()
    codeGen.indent = 1
    self.assertTrue(len(codeGen.indentString()) > 0)

  def testTwoIndentDoublesOneIndent(self):
    codeGen = generator.CodeGenerator()
    codeGen.indent = 1
    oneIndent = codeGen.indentString()
    codeGen.indent = 2
    twoIndent = codeGen.indentString()    
    self.assertEqual(twoIndent, oneIndent + oneIndent)


class TestParseInt(unittest.TestCase):
  def testSimple(self):
      self.assertEqual(32, generator.parseInt("32"))
      self.assertEqual(-32, generator.parseInt("-32"))
      self.assertEqual(32, generator.parseInt("0x20"))
      self.assertEqual(1, generator.parseInt("0x0000001"))

  def testInvalid(self):
    self.assertIsNone(generator.parseInt("foo"))
    self.assertIsNone(generator.parseInt("0xlose"))
    self.assertIsNone(generator.parseInt("0xlose"))
    self.assertIsNone(generator.parseInt("0x0x"))


class TestStripComment(unittest.TestCase):
  def testSimple(self):
     self.assertEqual("Foo", generator.stripComment("// Foo"))
     self.assertEqual("Foo", generator.stripComment("/* Foo */"))
     self.assertEqual("", generator.stripComment("//"))
     self.assertEqual("", generator.stripComment("/* */"))
                    

class TestDocBuilder(unittest.TestCase):
  # Test that we correctly parse valid and invalid structure definitions.
  def testEmptyDoc(self):
    doc = generator.DocBuilder()
    self.assertIsNotNone(doc.current_document)

  def testParseSimpleStructLine(self):
    builder = generator.DocBuilder()  
    doc = builder.current_document
    self.assertEqual(0, len(doc.structs))

    builder.parseStructStart('STRUCT Foo')
    builder.parseLine('0 0:63 uint64_t packet')
    builder.parseEnd('END')

    doc = builder.current_document
    self.assertEqual(0, len(builder.errors))

    print("testParseSimpleStruct %s" % doc)
    self.assertEqual(1, len(doc.structs))

    firstStruct = doc.structs[0]
    self.assertEqual(1, len(firstStruct.fields))

    firstField = firstStruct.fields[0]
    self.assertEqual(0, firstField.flit)
    self.assertEqual(0, firstField.start_bit)
    self.assertEqual(63, firstField.end_bit)
    self.assertEqual('packet', firstField.name)

  def testStructSize(self): 
    builder = generator.DocBuilder()
    doc = builder.current_document

    builder.parseStructStart('STRUCT Foo')
    builder.parseLine('0 0:63 uint64_t packet')
    builder.parseEnd('END')

    self.assertEqual(1, len(doc.structs))

    struct = doc.structs[0]
    self.assertEqual(8, struct.bytes())

  def testNotPackedStructSize(self): 
    builder = generator.DocBuilder()
    doc = builder.current_document

    builder.parseStructStart('STRUCT Foo')
    builder.parseLine('0 0:63 uint64_t packet')
    builder.parseLine('1 0:8 uint64_t bar')
    builder.parseEnd('END')

    self.assertEqual(1, len(doc.structs))

    struct = doc.structs[0]
    # TODO(bowdidge): Should be 9 bytes?
    self.assertEqual(16, struct.bytes())

  def testValidFile(self):
    docBuilder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 0:63 uint64_t packet', 'END']
    
    errors = docBuilder.parse(contents)
  
    self.assertIsNone(errors)

  def testEnum(self):
    docBuilder = generator.DocBuilder()
    contents = ['ENUM Commands', 'A = 1', 'BBBBBB=0x02', 'END']
    
    errors = docBuilder.parse(contents)
    doc = docBuilder.current_document
  
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
    docBuilder = generator.DocBuilder()
    self.assertIsNone(docBuilder.parseEnumLine("A"))
    self.assertIsNone(docBuilder.parseEnumLine("3"))
    self.assertIsNone(docBuilder.parseEnumLine("A=A"))
    self.assertIsNone(docBuilder.parseEnumLine("A,A"))

  def testGoodEnumFields(self):
    docBuilder = generator.DocBuilder()
    field = docBuilder.parseEnumLine('A=1')
    self.assertEqual('A', field.name)
    self.assertEqual(1, field.value)
    self.assertIsNone(field.key_comment)
    self.assertIsNone(field.body_comment)

    field = docBuilder.parseEnumLine('bb1 = 3 /* Foobar */')
    self.assertEqual('bb1', field.name)
    self.assertEqual(3, field.value)
    self.assertEqual("Foobar", field.key_comment)


  def testInvalidFlit(self):
    # Test that code correctly handles a packet with a non-numeric flit number.
    docBuilder = generator.DocBuilder()
    line = 'flit 0:63 uint64_t packet'

    self.assertIsNone(docBuilder.parseFieldLine(line))
  
    self.assertEqual(1, len(docBuilder.errors))
    self.assertIn('Invalid flit', docBuilder.errors[0])

  def testInvalidStart(self):
    # Test that code correctly handles a packet with a non-numeric flit number.
    docBuilder = generator.DocBuilder()
    line = '2 foo:15 uint64_t packet'
    
    self.assertIsNone(docBuilder.parseFieldLine(line))
  
    self.assertEqual(1, len(docBuilder.errors))
    self.assertIn('Invalid start bit', docBuilder.errors[0])

  def testInvalidEnd(self):
    # Test that code correctly handles a packet with a non-numeric flit number.
    docBuilder = generator.DocBuilder()
    line = '2 15:bar uint64_t packet'
    
    self.assertIsNone(docBuilder.parseFieldLine(line))
  
    self.assertEqual(1, len(docBuilder.errors))
    self.assertIn('Invalid end bit', docBuilder.errors[0])

  def testTypeTooSmall(self):
    # Test that code correctly handles a packet with a non-numeric flit number.
    docBuilder = generator.DocBuilder()
    line = '2 0:40 uint8_t packet'
    
    self.assertIsNone(docBuilder.parseFieldLine(line))
  
    self.assertEqual(1, len(docBuilder.errors))
    self.assertIn('too small to hold', docBuilder.errors[0])

  def testMissingCommentIsNone(self):
    # Test that code correctly handles a packet with a non-numeric flit number.
    docBuilder = generator.DocBuilder()
    line = '2 12:15 int64_t packet'
    
    field = docBuilder.parseFieldLine(line)
  
    self.assertIsNone(field.key_comment)
    self.assertIsNone(field.body_comment)
    self.assertIsNone(field.generator_comment)

  def testSimpleUnion(self): 
    builder = generator.DocBuilder()  
    doc = builder.current_document

    self.assertEqual(0, len(doc.structs))

    builder.parseStructStart('STRUCT Foo')
    builder.parseUnionStart('UNION Bar u')
    builder.parseLine('0 0:63 uint64_t packet')
    builder.parseEnd('END')
    builder.parseUnionStart('UNION Baz u')
    builder.parseLine('0 0:63 uint64_t packet')
    builder.parseEnd('END')
    builder.parseEnd('END')

    doc = builder.current_document
    self.assertEqual(1, len(doc.structs))

    firstStruct = doc.structs[0]
    self.assertEqual(0, len(firstStruct.fields))
    self.assertEqual(2, len(firstStruct.unions))

    firstUnion = firstStruct.unions[0]
    firstField = firstUnion.fields[0]
    self.assertEqual(0, firstField.flit)
    self.assertEqual(0, firstField.start_bit)
    self.assertEqual(63, firstField.end_bit)
    self.assertEqual('packet', firstField.name)

  def testParseCommentInField(self):
    docBuilder = generator.DocBuilder()

    field = docBuilder.parseFieldLine(
      '0 0:31 unsigned packet /* 6 byte packet to send out */')

    self.assertEqual(0, len(docBuilder.errors))

    self.assertEqual("packet", field.name)
    self.assertEqual("6 byte packet to send out", field.key_comment)

  def testParseTailComment(self):
    builder = generator.DocBuilder()
    the_file = ['// Body comment\n',
                'STRUCT Foo\n',
                '// Packet body comment\n',
                '0 0:63 uint64_t packet // Packet key comment\n',
                '// Tail comment\n',
                'END\n']
    builder.parse(the_file)
    
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


class CodeGeneratorTest(unittest.TestCase):
  def setUp(self):
    self.printer = generator.CodeGenerator()

  def testPrintStructNoVar(self):
    builder = generator.DocBuilder()  
    builder.parseStructStart('STRUCT Foo')
    builder.parseLine('0 0:63 uint64_t packet')
    builder.parseEnd('END')
    doc = builder.current_document

    code = self.printer.visitDocument(doc)

    self.assertIn('struct Foo {', code)
    # Should automatically create a field name for the struct.
    self.assertIn('};', code)

  def testPrintStructWithVar(self):
    builder = generator.DocBuilder()  
    builder.parseStructStart('STRUCT Foo foo_cmd')
    builder.parseLine('0 0:63 uint64_t packet')
    builder.parseEnd('END')
    doc = builder.current_document

    code = self.printer.visitDocument(doc)

    self.assertIn('struct Foo {', code)
    # Should automatically create a field name for the struct.
    self.assertIn('} foo_cmd;', code)

  def testPrintStructWithComments(self):
    struct = generator.Struct('Foo', 'bar')
    struct.key_comment = 'Key comment'
    struct.body_comment = 'body comment\nbody comment'

    code = self.printer.visitStruct(struct)
    self.assertEquals('\n/* Key comment */\n'
                      '/* body comment\n'
                      'body comment */\n'
                      'struct Foo {\n'
                      '} bar;\n', code)

  def testPrintUnion(self):
    union = generator.Union("Foo", None)
    
    code = self.printer.visitUnion(union)

    self.assertEquals('union Foo {\n};\n', code)

  def testPrintUnionWithVar(self):
    union = generator.Union("Foo", 'xxx')
    
    code = self.printer.visitUnion(union)

    self.assertEquals('union Foo {\n} xxx;\n', code)

  def testPrintField(self):
    field = generator.Field("foo", "uint8_t", 0, 0, 3)
    code = self.printer.visitField(field)
    self.assertEqual("uint8_t foo:4;\n", code)

  def testPrintFieldNotBitfield(self):
    field = generator.Field("foo", "uint8_t", 0, 0, 7)
    code = self.printer.visitField(field)
    self.assertEqual("uint8_t foo;\n", code)

  def testPrintFieldWithComment(self):
    field = generator.Field("foo", "uint8_t", 0, 0, 7)
    field.key_comment = 'A'
    field.body_comment = 'B'
    code = self.printer.visitField(field)
    self.assertEqual("/* B */\nuint8_t foo; // A\n", code)

  def testPrintFieldWithLongComment(self):
    field = generator.Field("foo", "uint8_t", 0, 0, 7)
    long_comment = "long long long long long long long long long long comment"
    field.body_comment = long_comment
    print("long comment is %d" %len(long_comment))
    field.bodyuser_comment = long_comment
    code = self.printer.visitField(field)
    self.assertEqual('/* %s */\nuint8_t foo;\n' % long_comment, code)
    

class PackerTest(unittest.TestCase):
  def testPackTwoFields(self):
    docBuilder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 32:63 unsigned packet', '0 0:31 unsigned other','END']
    errors = docBuilder.parse(contents)
    self.assertIsNone(errors)

    doc = docBuilder.current_document
    p = generator.Packer()
    p.visitDocument(doc)

    self.assertEqual(1, len(doc.structs[0].fields))
    field = doc.structs[0].fields[0]
    self.assertEqual("flit0", field.name)
    self.assertEqual(0, field.start_bit)
    self.assertEqual(63, field.end_bit)

  def testNoCompressSingleField(self):
    docBuilder = generator.DocBuilder()
    contents = ['STRUCT Foo', '0 0:31 unsigned packet', 'END']
    errors = docBuilder.parse(contents)
    self.assertIsNone(errors)

    doc = docBuilder.current_document
    p = generator.Packer()
    p.visitDocument(doc)
    
    self.assertEqual(1, len(doc.structs[0].fields))
    field = doc.structs[0].fields[0]
    # Packer doesn't change name.
    self.assertEqual("packet", field.name)
    self.assertEqual(0, field.start_bit)
    self.assertEqual(31, field.end_bit)


class CheckerTest(unittest.TestCase):

  def testCheckerAdjacentTypesEqual(self):
    docBuilder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 0:1 uint8_t a',
                '0 2:3 uint8_t b',
                'END']
    errors = docBuilder.parse(contents)
    self.assertIsNone(errors)

    checker = generator.Checker()
    checker.visitDocument(docBuilder.current_document)

    self.assertEqual(0, len(checker.warnings))

  def testCheckerAdjacentTypesDifferent(self):
    docBuilder = generator.DocBuilder()
    contents = ['STRUCT Foo',
                '0 0:1 uint8_t a',
                '0 2:3 uint16_t b',
                'END']
    errors = docBuilder.parse(contents)
    self.assertIsNone(errors)

    checker = generator.Checker()
    checker.visitDocument(docBuilder.current_document)

    self.assertEqual(1, len(checker.warnings))
    self.assertIn('allow alignment', checker.warnings[0])

if __name__ == '__main__':
    unittest.main()
