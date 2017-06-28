import unittest

import codegen
import generator

class CodeGeneratorTest(unittest.TestCase):
  def setUp(self):
    self.printer = codegen.CodeGenerator(None)

  def testPrintStructNoVar(self):
    builder = generator.DocBuilder()  
    builder.ParseStructStart('STRUCT Foo')
    builder.ParseLine('0 63:0 uint64_t packet')
    builder.ParseEnd('END')
    doc = builder.current_document

    (header, src) = self.printer.VisitDocument(doc)

    self.assertIn('struct Foo {', header)
    # Should automatically create a field name for the struct.
    self.assertIn('};', header)

  def testPrintStructWithVar(self):
    builder = generator.DocBuilder()  
    builder.ParseStructStart('STRUCT Foo foo_cmd')
    builder.ParseLine('0 63:0 uint64_t packet')
    builder.ParseEnd('END')
    doc = builder.current_document

    (header, src) = self.printer.VisitDocument(doc)

    self.assertIn('struct Foo {', header)
    # Should automatically create a field name for the struct.
    self.assertIn('} foo_cmd;', header)

  def testPrintStructWithComments(self):
    struct = generator.Struct('Foo', 'bar')
    struct.key_comment = 'Key comment'
    struct.body_comment = 'body comment\nbody comment'

    (header, src) = self.printer.VisitStruct(struct)
    self.assertEquals('\n/* Key comment */\n'
                      '/* body comment\n'
                      'body comment */\n'
                      'struct Foo {\n'
                      '} bar;\n\n', header)

  def testPrintArray(self):
    field = generator.Field('foo', generator.ArrayTypeForName('char', 8), 0, 63, 0)
    code = self.printer.VisitField(field)
  
    self.assertEquals('char foo[8];\n', code)


  def testPrintUnion(self):
    union = generator.Union('Foo', None)
    
    code = self.printer.VisitUnion(union)

    self.assertEquals(('union Foo {\n};\n', ''), code)

  def testPrintUnionWithVar(self):
    union = generator.Union('Foo', 'xxx')
    
    code = self.printer.VisitUnion(union)

    self.assertEquals(('union Foo {\n} xxx;\n', ''), code)

  def testPrintField(self):
    field = generator.Field('foo', generator.TypeForName('uint8_t'), 0, 3, 0)
    code = self.printer.VisitField(field)
    self.assertEqual('uint8_t foo:4;\n', code)

  def testPrintFieldNotBitfield(self):
    field = generator.Field('foo', generator.TypeForName('uint8_t'), 0, 7, 0)
    code = self.printer.VisitField(field)
    self.assertEqual('uint8_t foo;\n', code)

  def testPrintFieldWithComment(self):
    field = generator.Field('foo', generator.TypeForName('uint8_t'), 0, 7, 0)
    field.key_comment = 'A'
    field.body_comment = 'B'
    code = self.printer.VisitField(field)
    self.assertEqual('/* B */\nuint8_t foo; // A\n', code)

  def testPrintFieldWithLongComment(self):
    field = generator.Field('foo', generator.TypeForName('uint8_t'), 0, 7, 0)
    long_comment = 'long long long long long long long long long long comment'
    field.body_comment = long_comment
    print('long comment is %d' %len(long_comment))
    field.bodyuser_comment = long_comment
    code = self.printer.VisitField(field)
    self.assertEqual('/* %s */\nuint8_t foo;\n' % long_comment, code)

  def testPrintEnum(self):
    enum = generator.Enum('MyEnum')
    var = generator.EnumVariable('MY_COMMAND', 1)
    enum.variables.append(var)

    code = self.printer.VisitEnum(enum)
    self.assertEqual('enum MyEnum {\n\tMY_COMMAND = 0x1,\n};\n\n', code)


class HelperGeneratorTest(unittest.TestCase):
  def testInitializeSimpleField(self):
    gen = codegen.HelperGenerator()
    s = generator.Struct('Foo', 'f1')
    f = generator.Field('a1', generator.TypeForName('char'), 0, 63, 56)

    statement = gen.GenerateInitializer(s, f, 'pointer.')
  
    self.assertEqual('  s->pointer.a1 = a1;', statement)

  def testInitializeBitfield(self):
    gen = codegen.HelperGenerator()
    s = generator.Struct('Foo', 'f1')
    f = generator.Field('a1', generator.TypeForName('char'), 0, 63, 61)

    statement = gen.GenerateInitializer(s, f, '')
  
    self.assertEqual('  s->a1 = a1;', statement)

  def testInitializePackedField(self):
    gen = codegen.HelperGenerator()
    s = generator.Struct('Foo', 'f1')
    f = generator.Field('a', generator.TypeForName('char'), 0, 63, 56)
    f1 = generator.Field('a1', generator.TypeForName('char'), 0, 63, 60)
    f2 = generator.Field('a2', generator.TypeForName('char'), 0, 59, 56)
    f.packed_fields = [f1, f2]

    statement = gen.GenerateInitializer(s, f, '')
  
    self.assertEqual('  s->a = FUN_FOO_A1_P(a1) | FUN_FOO_A2_P(a2);', statement)

  def testInitializePackedFieldWithAllCapStructureName(self):
    gen = codegen.HelperGenerator()
    s = generator.Struct('ffe_access_command', 'f1')
    f = generator.Field('a', generator.TypeForName('char'), 0, 63, 56)
    f1 = generator.Field('a1', generator.TypeForName('char'), 0, 63, 60)
    f2 = generator.Field('a2', generator.TypeForName('char'), 0, 59, 56)
    f.packed_fields = [f1, f2]

    statement = gen.GenerateInitializer(s, f, '')
  
    self.assertEqual('  s->a = FUN_FFE_ACCESS_COMMAND_A1_P(a1) | '
                     'FUN_FFE_ACCESS_COMMAND_A2_P(a2);', statement)


  def testCreateSimpleInitializer(self):
    gen = codegen.HelperGenerator()
    s = generator.Struct('Foo', 'f1')
    f = generator.Field('a1', generator.TypeForName('char'), 0, 63, 56)
    s.fields = [f]

    (declaration, definition) = gen.GenerateInitRoutine("init", "MyStruct",
                                                        "foo.", s)
  
    self.assertEqual('extern void init(struct MyStruct* s, char a1);\n',
                     declaration)
    self.assertEqual('void init(struct MyStruct* s, char a1) {\n'
                     '  s->foo.a1 = a1;\n\n'
                     '}', definition)

  def testNoCreateArrayInitializer(self):
    gen = codegen.HelperGenerator()
    s = generator.Struct('Foo', 'f1')
    f = generator.Field('a1', generator.ArrayTypeForName('char', 8),
                        0, 63, 0)
    s.fields = [f]

    (declaration, definition) = gen.GenerateInitRoutine("init", "MyStruct",
                                                        "foo.", s)
  
    self.assertEqual('', declaration)
    self.assertEqual('', definition)


class CodegenEndToEnd(unittest.TestCase):
  def testSimpleEndToEnd(self):
    input = ['STRUCT Foo',
             '0 63:56 uint8_t a /* comment about a */',
             '0 55:54 uint8_t b',
             '0 53:52 uint8_t c',
             '0 51:48 uint8_t reserved',
             '0 47:0 char d[6]',
             'END']

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 input, 'foo.gen')
    self.assertIsNotNone(out)

    # Did structure get generated?
    self.assertIn('struct Foo {', out)
    # Did field a get rendered?
    self.assertIn('uint8_t a; // comment about a', out)
    # Did bitfield get packed?
    self.assertIn('uint8_t b_to_c;', out)
    # Did array get included?
    self.assertIn('char d[6];', out)
    # Did constructor get created?
    self.assertIn('void Foo_init(struct Foo* s, uint8_t a, uint8_t b, '
                  'uint8_t c);', out)
    # Did accessor macro get created?
    self.assertIn('#define FUN_FOO_B_P(x)', out)
    # Did init function check range of bitfields?
    self.assertIn('assert(b < 0x4);', out)
    # Did bitfield get initialized?'
    self.assertIn('s->b_to_c = FUN_FOO_B_P(b) | FUN_FOO_C_P(c);', out)

  def testInitFunctionsCreated(self):
    input = ['STRUCT A',
             '0 63:0 uint64_t a',
             'END',
             'STRUCT B',
             '0 63:56 uint8_t a',
             'UNION Cmd u1',
             'STRUCT B1',
             '0 55:48 uint8_t b11',
             '0 47:40 uint8_t b12',
             'END',
             'STRUCT B2',
             '0 55:48 uint8_t b21',
             '0 47:40 uint8_t b22',
             'END',
             'END',
             '0 39:0 uint64_t c',
             'END'
             ]

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 input, 'foo.gen')
    self.assertIsNotNone(out)

    # Did structure get generated?
    self.assertIn('void A_init(struct A* s, uint64_t a)', out)
    self.assertIn('void B_init(struct B* s, uint8_t a, uint64_t c)', out)
    self.assertIn('void B1_init(struct B* s, uint8_t b11, uint8_t b12)', out)
    self.assertIn('void B2_init(struct B* s, uint8_t b21, uint8_t b22)', out)

  def testMacrosCreated(self):
    input = ['STRUCT A',
             '0 63:60 uint8_t a',
             '0 59:56 uint8_t b',
             'END']
    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 input, 'foo.gen')
    self.assertIsNotNone(out)
    self.assertIn('#define FUN_A_A_S 4', out)

  def testMacrosCreatedInUnion(self):
    input = ['STRUCT A',
             'UNION CMD u1',
             'STRUCT AX1',
             '0 63:60 uint8_t a',
             '0 59:56 uint8_t b',
             'END',
             'END',
             'END']
    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 input, 'foo.gen')
    self.assertIsNotNone(out)
    self.assertIn('#define FUN_AX1_A_S 4', out)

  def testInitFunctionsCreated(self):
    input = ['STRUCT A',
             '0 63:0 uint64_t a',
             'END',
             'STRUCT B',
             '0 63:56 uint8_t a',
             'UNION Cmd u1',
             'STRUCT B1',
             '0 55:48 uint8_t b11',
             '0 47:40 uint8_t b12',
             'END',
             'STRUCT B2',
             '0 55:48 uint8_t b21',
             '0 47:40 uint8_t b22',
             'END',
             'END',
             '0 39:0 uint64_t c',
             'END'
             ]

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 input, 'foo.gen')
    self.assertIsNotNone(out)

    # Did structure get generated?
    self.assertIn('void A_init(struct A* s, uint64_t a)', out)
    self.assertIn('void B_init(struct B* s, uint8_t a, uint64_t c)', out)
    self.assertIn('void B1_init(struct B* s, uint8_t b11, uint8_t b12)', out)
    self.assertIn('void B2_init(struct B* s, uint8_t b21, uint8_t b22)', out)

  def disableTestInitFunctionsForNestedStructures(self):
    input = ['STRUCT A',
             '0 63:56 uint8_t a',
             'STRUCT B',
             '0 55:48 uint8_t b',
             'STRUCT C',
             '0 47:40 uint8_t c',
             'END',
             'END',
             'END'
             ]

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 input, 'foo.gen')
    self.assertIsNotNone(out)

    # Did structure get generated?
    self.assertIn('void A_init(struct A* s, uint64_t a)', out)
    self.assertNotIn('void B_init(struct B* s, uint8_t b)', out)
    self.assertNotIn('void C_init(struct C* s, uint8_t c)', out)


  def testMultiFlitField(self):
    input = ['STRUCT A',
             '0 63:56 uint8_t a',
             '0 55:0 uint8_t b[19]',
             '1 63:0 ...',
             '2 63:32 ...',
             'END'
             ]

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 input, 'foo.gen')
    self.assertIsNotNone(out)
    print out

  def testMultiFlitNestedStruct(self):
    doc_builder = generator.DocBuilder()
    # ... allows a field to overflow into later flits.
    input = [
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

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 input, 'foo.gen')
    self.assertIsNotNone(out)
    self.assertIn('struct fun_admin_cmd_common c;', out)
    

class TestIndentString(unittest.TestCase):
  def testSimple(self):
    # Tests only properties that hold true regardless of the formatting style.
    generator = codegen.CodeGenerator(None)
    generator.indent = 1
    self.assertTrue(len(generator.IndentString()) > 0)

  def testTwoIndentDoublesOneIndent(self):
    generator = codegen.CodeGenerator(None)
    generator.indent = 1
    oneIndent = generator.IndentString()
    generator.indent = 2
    twoIndent = generator.IndentString()    
    self.assertEqual(twoIndent, oneIndent + oneIndent)



if __name__ == '__main__':
    unittest.main()
