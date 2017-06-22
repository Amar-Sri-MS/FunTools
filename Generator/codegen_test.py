import unittest

import codegen
import generator

class CodeGeneratorTest(unittest.TestCase):
  def setUp(self):
    self.printer = generator.CodeGenerator(None)

  def testPrintStructNoVar(self):
    builder = generator.DocBuilder()  
    builder.parseStructStart('STRUCT Foo')
    builder.parseLine('0 63:0 uint64_t packet')
    builder.parseEnd('END')
    doc = builder.current_document

    code = self.printer.visitDocument(doc)

    self.assertIn('struct Foo {', code)
    # Should automatically create a field name for the struct.
    self.assertIn('};', code)

  def testPrintStructWithVar(self):
    builder = generator.DocBuilder()  
    builder.parseStructStart('STRUCT Foo foo_cmd')
    builder.parseLine('0 63:0 uint64_t packet')
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

  def testPrintArray(self):
    field = generator.Field("foo", generator.Type("char", 8), 0, 64, 0)
    code = self.printer.visitField(field)
  
    self.assertEquals('char foo[8];\n', code)


  def testPrintUnion(self):
    union = generator.Union("Foo", None)
    
    code = self.printer.visitUnion(union)

    self.assertEquals('union Foo {\n};\n', code)

  def testPrintUnionWithVar(self):
    union = generator.Union("Foo", 'xxx')
    
    code = self.printer.visitUnion(union)

    self.assertEquals('union Foo {\n} xxx;\n', code)

  def testPrintField(self):
    field = generator.Field("foo", generator.Type("uint8_t"), 0, 3, 0)
    code = self.printer.visitField(field)
    self.assertEqual("uint8_t foo:4;\n", code)

  def testPrintFieldNotBitfield(self):
    field = generator.Field("foo", generator.Type("uint8_t"), 0, 7, 0)
    code = self.printer.visitField(field)
    self.assertEqual("uint8_t foo;\n", code)

  def testPrintFieldWithComment(self):
    field = generator.Field("foo", generator.Type("uint8_t"), 0, 7, 0)
    field.key_comment = 'A'
    field.body_comment = 'B'
    code = self.printer.visitField(field)
    self.assertEqual("/* B */\nuint8_t foo; // A\n", code)

  def testPrintFieldWithLongComment(self):
    field = generator.Field("foo", generator.Type("uint8_t"), 0, 7, 0)
    long_comment = "long long long long long long long long long long comment"
    field.body_comment = long_comment
    print("long comment is %d" %len(long_comment))
    field.bodyuser_comment = long_comment
    code = self.printer.visitField(field)
    self.assertEqual('/* %s */\nuint8_t foo;\n' % long_comment, code)

  def testPrintEnum(self):
    enum = generator.Enum("MyEnum")
    var = generator.EnumVariable("MY_COMMAND", 1)
    enum.variables.append(var)

    code = self.printer.visitEnum(enum)
    self.assertEqual('enum MyEnum {\n\tMY_COMMAND = 1,\n};\n', code)


class TestIndentString(unittest.TestCase):
  def testSimple(self):
    # Tests only properties that hold true regardless of the formatting style.
    generator = codegen.CodeGenerator(None)
    generator.indent = 1
    self.assertTrue(len(generator.indentString()) > 0)

  def testTwoIndentDoublesOneIndent(self):
    generator = codegen.CodeGenerator(None)
    generator.indent = 1
    oneIndent = generator.indentString()
    generator.indent = 2
    twoIndent = generator.indentString()    
    self.assertEqual(twoIndent, oneIndent + oneIndent)



if __name__ == '__main__':
    unittest.main()
