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
    self.assertIn('};', header)

  def testPrintStructWithComments(self):
    struct = generator.Struct('Foo', False)
    struct.key_comment = 'Key comment'
    struct.body_comment = 'body comment\nbody comment'

    header = self.printer.VisitStruct(struct)
    self.assertIn('/* Key comment */', header)
    self.assertIn('/*\n'
                  ' * body comment\n'
                  ' * body comment\n'
                  ' */', header)
    self.assertIn('struct Foo {', header)
    self.assertIn('};', header)

  def testPrintArray(self):
    field = generator.Field('foo', generator.ArrayTypeForName('char', 8), 0, 64)
    code = self.printer.VisitField(field)
  
    self.assertIn('char foo[8];\n', code)

  def testPrintUnionWithVar(self):
    union = generator.Struct('Foo', True)
    hdr = self.printer.VisitStruct(union)

    self.assertIn('union Foo {', hdr)
    self.assertIn('};', hdr)

  def testPrintField(self):
    field = generator.Field('foo', generator.TypeForName('uint8_t'), 0, 4)
    code = self.printer.VisitField(field)
    self.assertEqual('uint8_t foo:4;\n', code)

  def testPrintFieldNotBitfield(self):
    field = generator.Field('foo', generator.TypeForName('uint8_t'), 0, 8)
    code = self.printer.VisitField(field)
    self.assertEqual('uint8_t foo;\n', code)

  def testPrintFieldWithComment(self):
    field = generator.Field('foo', generator.TypeForName('uint8_t'), 0, 8)
    field.key_comment = 'A'
    field.body_comment = 'B'
    code = self.printer.VisitField(field)
    self.assertEqual('/* B */\nuint8_t foo; /* A */\n', code)

  def testPrintFieldWithLongComment(self):
    field = generator.Field('foo', generator.TypeForName('uint8_t'), 0, 8)
    long_comment = 'long long long long long long long long long long comment'
    field.body_comment = long_comment
    field.bodyuser_comment = long_comment
    code = self.printer.VisitField(field)
    self.assertEqual('/* %s */\nuint8_t foo;\n' % long_comment, code)

  def testPrintEnum(self):
    enum = generator.Enum('MyEnum')
    var = generator.EnumVariable('MY_COMMAND', 1)
    enum.variables.append(var)

    (hdr, src) = self.printer.VisitEnum(enum)
    self.assertIn('enum MyEnum {', hdr)
    self.assertIn('MY_COMMAND = 0x1,\n', hdr)
    self.assertIn('extern const char *myenum_names', hdr)
    self.assertIn('const char *myenum_names', src)
    self.assertIn('"MY_COMMAND"', src)

  def testPrintLargeEnum(self):
    enum = generator.Enum('MyEnum')
    var = generator.EnumVariable('MY_COMMAND', 31)
    enum.variables.append(var)

    (hdr, src) = self.printer.VisitEnum(enum)
    self.assertIn('enum MyEnum {', hdr)
    self.assertIn('MY_COMMAND = 0x1f,\n', hdr)
    self.assertIn('extern const char *myenum_names', hdr)
    self.assertIn('const char *myenum_names', src)
    self.assertIn('"MY_COMMAND",  /* 0x1f */', src)

class HelperGeneratorTest(unittest.TestCase):
  def testInitializeSimpleField(self):
    gen = codegen.HelperGenerator()
    s = generator.Struct('Foo', False)
    f = generator.Field('a1', generator.TypeForName('char'), 0, 8)

    statement = gen.GenerateInitializer(s, f, 'pointer.')
  
    self.assertEqual('\ts->pointer.a1 = a1;', statement)

  def testInitializeBitfield(self):
    gen = codegen.HelperGenerator()
    s = generator.Struct('Foo', False)
    f = generator.Field('a1', generator.TypeForName('char'), 0, 2)

    statement = gen.GenerateInitializer(s, f, '')
  
    self.assertEqual('\ts->a1 = a1;', statement)

  def testInitializePackedField(self):
    gen = codegen.HelperGenerator()
    s = generator.Struct('Foo', False)
    f = generator.Field('a', generator.TypeForName('char'), 0, 8)
    f1 = generator.Field('a1', generator.TypeForName('char'), 8, 4)
    f2 = generator.Field('a2', generator.TypeForName('char'), 12, 4)
    f.packed_fields = [f1, f2]

    statement = gen.GenerateInitializer(s, f, '')
  
    self.assertEqual('\ts->a = FUN_FOO_A1_P(a1) | FUN_FOO_A2_P(a2);', statement)

  def testInitializePackedFieldWithAllCapStructureName(self):
    gen = codegen.HelperGenerator()
    s = generator.Struct('ffe_access_command', False)
    f = generator.Field('a', generator.TypeForName('char'), 0, 8)
    f1 = generator.Field('a1', generator.TypeForName('char'), 0, 4)
    f2 = generator.Field('a2', generator.TypeForName('char'), 4, 4)
    f.packed_fields = [f1, f2]

    statement = gen.GenerateInitializer(s, f, '')
  
    self.assertEqual('\ts->a = FUN_FFE_ACCESS_COMMAND_A1_P(a1) | '
                     'FUN_FFE_ACCESS_COMMAND_A2_P(a2);', statement)


  def testCreateSimpleInitializer(self):
    gen = codegen.HelperGenerator()
    s = generator.Struct('Foo', False)
    f = generator.Field('a1', generator.TypeForName('char'), 0, 8)
    s.fields = [f]

    (declaration, definition) = gen.GenerateInitRoutine("init", "MyStruct",
                                                        "foo.", s)
  
    self.assertEqual('extern void init(struct MyStruct* s, char a1);\n',
                     declaration)
    self.assertIn('void init(struct MyStruct* s, char a1) {', definition)
    self.assertIn('\ts->foo.a1 = a1;\n', definition)

  def testNoCreateArrayInitializer(self):
    gen = codegen.HelperGenerator()
    s = generator.Struct('Foo', False)
    f = generator.Field('a1', generator.ArrayTypeForName('char', 8), 0, 64)
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
    self.assertIn('uint8_t a; /* comment about a */', out)
    # Did bitfield get packed?
    self.assertIn('uint8_t b_to_c;', out)
    # Did array get included?
    self.assertIn('char d[6];', out)
    # Did constructor get created?
    self.assertIn('void Foo_init(struct Foo* s, uint8_t a, uint8_t b, '
                  'uint8_t c);', out)
    # Did accessor macro get created?
    self.assertIn('#define FUN_FOO_B_P(x)', out)

    # Check macros weren't created for reserved fields.
    self.assertNotIn('#define FUN_FOO_RESERVED', out)

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
    # TODO(bowdidge): Structures with unions should get union-specific
    # constructors.
    self.assertIn('void A_init(struct A* s, uint64_t a)', out)
    self.assertIn('void B_B1_init(struct B* s, uint8_t b11, uint8_t b12)', out)
    self.assertIn('void B_B2_init(struct B* s, uint8_t b21, uint8_t b22)', out)

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

  def testNoBitfieldForAlignedVariables(self):
    doc_builder = generator.DocBuilder()
    input = [
      'STRUCT s',
      '0 63:56 uint8_t a',
      '0 55:54 uint8_t b',
      '0 53:48 uint8_t c',
      '0 47:40 uint8_t d',
      'END'
      ]
    
    out = generator.GenerateFile(False, generator.OutputStyleHeader, None,
                                 input, 'foo.gen')

    self.assertIsNotNone(out)
    self.assertIn('uint8_t a;', out)
    self.assertIn('uint8_t b:2;', out)
    self.assertIn('uint8_t c:6;', out)
    self.assertIn('uint8_t d;', out)

class TestComments(unittest.TestCase):

  def testStructComments(self):
    doc_builder = generator.DocBuilder()
    # ... allows a field to overflow into later flits.
    input = [
      '// Body comment.',
      'STRUCT fun_admin_cmd_common',
      '// Field comment.',
      '0 63:00 uint64_t common_opcode // Key comment',
      '// Tail comment.',
      'END'
      ]

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 input, 'foo.gen')

    self.assertIn('/* Body comment. */', out)
    self.assertIn('struct fun_admin_cmd_common {', out)
    self.assertIn('/* Field comment. */', out)
    self.assertIn('uint64_t common_opcode; /* Key comment */', out)
    self.assertIn('/* Tail comment. */', out)

  def testUnionComments(self):
    doc_builder = generator.DocBuilder()
    
    input = [
      '// Struct comment.',
      'STRUCT large ',
      '// Union body comment.',
      'UNION union_name u',
      '// A comment',
      'STRUCT a a',
      '0 63:00 uint64_t a1',
      'END',
      '// B comment.',
      'STRUCT b b',
      '0 63:32 uint32_t b1',
      'END',
      'END',
      'END']

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 input, 'foo.gen')

    self.assertIn('/* Struct comment. */', out)
    self.assertIn('/* Union body comment. */', out)
    self.assertIn('/* A comment */', out)
    self.assertIn('/* B comment. */', out)

  def testEnumComments(self):
    doc_builder = generator.DocBuilder()
    
    input = [
      '// Enum comment.',
      'ENUM values',
      '// Enum body comment',
      'A = 1 // Enum key comment 1',
      'B = 2 // Enum key comment 2',
      '// Tail comment',
      'END']

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 input, 'foo.gen')
    self.assertIn('enum values {', out)
    self.assertIn('A = 0x1,' ,out)
    self.assertIn('/* Enum key comment 1 */', out)
    self.assertIn('B = 0x2,', out)
    self.assertIn('/* Enum key comment 2 */', out)
    self.assertIn('/* Tail comment */', out)

  def testArrayOfStructs(self):
    contents = ['STRUCT Foo',
                '0 63:32 uint64_t a',
                'END',
                'STRUCT BAR',
                '0 63:0 Foo f[2]',
                'END']

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 contents, 'foo.gen')
    self.assertIn('struct Foo f[2];', out)

  def disableTestUnknownArrayOfStructs(self):
    contents = ['STRUCT Foo',
                '0 63:32 uint64_t a',
                'END',
                'STRUCT BAR',
                '0 0:0 Foo f[0]',
                'END']

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 contents, 'foo.gen')
    self.assertIn('struct Foo f[2];', out)

  def testNameListCorrectlyHandlesEnumVariablesWithGaps(self):
    contents = ['ENUM A',
                'A = 1',
                'C = 3',
                'D = 4',
                'E = 5',
                'F = 7',
                'G = 10'
                ]
    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 contents, 'foo.gen')

    self.assertIn('"undefined",  /* 0x0 */', out)
    self.assertIn('"A",  /* 0x1 */', out)
    self.assertIn('"undefined",  /* 0x2 */', out)
    self.assertIn('"C",  /* 0x3 */', out)
    self.assertIn('"E",  /* 0x5 */', out)
    self.assertIn('"undefined",  /* 0x6 */', out)
    self.assertIn('"G",  /* 0xa */', out)

  def testVariableLengthArray(self):
    doc_builder = generator.DocBuilder()
    contents = [
      'STRUCT foo',
      '0 63:56 char initial',
      '_ _:_ char array[0]',
      'END'
      ]

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 contents, 'foo.gen')

    self.assertIn('char array[0];\n};', out)


class TestIndentString(unittest.TestCase):
  def testSimple(self):
    # Tests only properties that hold true regardless of the formatting style.
    generator = codegen.CodeGenerator(None)
    generator.indent = 1
    self.assertTrue(len(generator.Indent()) > 0)

  def testTwoIndentDoublesOneIndent(self):
    generator = codegen.CodeGenerator(None)
    generator.indent = 1
    oneIndent = generator.Indent()
    generator.indent = 2
    twoIndent = generator.Indent()    
    self.assertEqual(twoIndent, oneIndent + oneIndent)



if __name__ == '__main__':
    unittest.main()
