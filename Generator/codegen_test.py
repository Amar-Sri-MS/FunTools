import unittest

import codegen
import generator

class CodePrinterTest(unittest.TestCase):
  def setUp(self):
    self.codegen = codegen.CodeGenerator(True)
    self.printer = codegen.CodePrinter(None, True)

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

    (header, source) = self.printer.VisitStruct(struct)
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
    (hdr, src) = self.printer.VisitStruct(union)

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

    self.codegen.VisitEnum(enum)
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

    self.codegen.VisitEnum(enum)
    (hdr, src) = self.printer.VisitEnum(enum)
    self.assertIn('enum MyEnum {', hdr)
    self.assertIn('MY_COMMAND = 0x1f,\n', hdr)
    self.assertIn('extern const char *myenum_names', hdr)
    self.assertIn('const char *myenum_names', src)
    self.assertIn('"MY_COMMAND",  /* 0x1f */', src)

class CodeGeneratorTest(unittest.TestCase):
  def testInitializeSimpleField(self):
    gen = codegen.CodeGenerator(False)
    s = generator.Struct('Foo', False)
    f = generator.Field('a1', generator.TypeForName('char'), 0, 8)

    statement = gen.GenerateInitializer(s, f, 'pointer.')
  
    self.assertEqual('\ts->pointer.a1 = a1;', statement)

  def testInitializeBitfield(self):
    gen = codegen.CodeGenerator(False)
    s = generator.Struct('Foo', False)
    f = generator.Field('a1', generator.TypeForName('char'), 0, 2)

    statement = gen.GenerateInitializer(s, f, '')
  
    self.assertEqual('\ts->a1 = a1;', statement)

  def testInitializePackedField(self):
    gen = codegen.CodeGenerator(False)
    s = generator.Struct('Foo', False)
    f = generator.Field('a', generator.TypeForName('char'), 0, 8)
    f1 = generator.Field('a1', generator.TypeForName('char'), 8, 4)
    f2 = generator.Field('a2', generator.TypeForName('char'), 12, 4)
    f.packed_fields = [f1, f2]

    statement = gen.GenerateInitializer(s, f, '')
  
    self.assertEqual('\ts->a = FOO_A1_P(a1) | FOO_A2_P(a2);', statement)

  def testInitializePackedFieldWithAllCapStructureName(self):
    gen = codegen.CodeGenerator(False)
    s = generator.Struct('ffe_access_command', False)
    f = generator.Field('a', generator.TypeForName('char'), 0, 8)
    f1 = generator.Field('a1', generator.TypeForName('char'), 0, 4)
    f2 = generator.Field('a2', generator.TypeForName('char'), 4, 4)
    f.packed_fields = [f1, f2]

    statement = gen.GenerateInitializer(s, f, '')
  
    self.assertEqual('\ts->a = FFE_ACCESS_COMMAND_A1_P(a1) | '
                     'FFE_ACCESS_COMMAND_A2_P(a2);', statement)


  def testCreateSimpleInitializer(self):
    gen = codegen.CodeGenerator(False)
    # Struct foo has a single field a1.
    s = generator.Struct('Foo', False)
    f = generator.Field('a1', generator.TypeForName('char'), 0, 8)
    s.fields = [f]

    func = gen.GenerateInitRoutine(s, None)
  
    self.assertIn('extern void Foo_init(struct Foo *s, char a1)',
                     func.declaration)
    self.assertIn('void Foo_init(struct Foo *s, char a1) {', func.definition)
    self.assertIn('\ts->a1 = a1;\n', func.definition)

  def testCreateUnionInitializer(self):
    gen = codegen.CodeGenerator(False)
    # Struct Foo has field a0, and a union containing Message1 and Message2
    # which each have one field f1 and f2.
    s = generator.Struct('Foo', False)
    f = generator.Field('a0', generator.TypeForName('char'), 0, 8)
    s.fields.append(f)
    u = generator.Struct('Union', True)
    s1 = generator.Struct('Message1', False)
    s1.fields.append(generator.Field('f1', generator.TypeForName('char'), 0, 8))
    s2 = generator.Struct('Message2', False)
    s2.fields.append(generator.Field('f2', generator.TypeForName('char'), 0, 8))
    m1 = generator.Field('m1', generator.RecordTypeForStruct(s1), 0, 8)
    m2 = generator.Field('m2', generator.RecordTypeForStruct(s2), 0, 8)
    u.fields = [m1, m2]
    s.fields.append(generator.Field('u', generator.RecordTypeForStruct(u), 0, 8))
    
    func = gen.GenerateInitRoutine(s, None)
    # Foo initializer only gets a0 because it only gets non-union fielda.
    self.assertIn('Foo_init(struct Foo *s, char a0);', func.declaration)

    # Initializer for Message1 doesn't get f2 because it's in Message2.
    func = gen.GenerateInitRoutine(s, s1)
    self.assertIn('Message1_init(struct Foo *s, char a0, char f1);',
                  func.declaration)
    
    # Initializer for Message2 doesn't get f1 because it's in Message1.
    func = gen.GenerateInitRoutine(s, s2)
    self.assertIn('Message2_init(struct Foo *s, char a0, char f2);',
                  func.declaration)


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
                                 input, 'foo.gen', True)
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
    self.assertIn('void Foo_init(struct Foo *s, uint8_t a, uint8_t b, '
                  'uint8_t c);', out)
    # Did accessor macro get created?
    self.assertIn('#define FOO_B_P(x)', out)

    # Check macros weren't created for reserved fields.
    self.assertNotIn('#define FOO_RESERVED', out)

    # Did init function check range of bitfields?
    self.assertIn('assert(b < 0x4);', out)
    # Did bitfield get initialized?'
    self.assertIn('s->b_to_c = FOO_B_P(b) | FOO_C_P(c);', out)

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
                                 input, 'foo.gen', False)
    self.assertIsNotNone(out)

    # Did structure get generated?
    self.assertIn('void A_init(struct A *s, uint64_t a)', out)
    self.assertIn('void B_init(struct B *s, uint8_t a, uint64_t c)', out)
    self.assertIn('void B1_init(struct B *s, uint8_t b11, uint8_t b12)', out)
    self.assertIn('void B2_init(struct B *s, uint8_t b21, uint8_t b22)', out)

  def testMacrosCreated(self):
    input = ['STRUCT A',
             '0 63:60 uint8_t a',
             '0 59:56 uint8_t b',
             'END']
    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 input, 'foo.gen', False)
    self.assertIsNotNone(out)
    self.assertIn('#define A_A_S 4', out)

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
                                 input, 'foo.gen', False)
    self.assertIsNotNone(out)
    self.assertIn('#define AX1_A_S 4', out)

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
             '0 39:32 uint8_t reserved',
             'END',
             'STRUCT B2',
             '0 55:48 uint8_t b21',
             '0 47:40 uint8_t b22',
             'END',
             'END',
             '0 39:0 uint64_t c',
             '1 63:0 uint64_t reserved',
             'END'
             ]

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 input, 'foo.gen', False)
    self.assertIsNotNone(out)

    # Did structure get generated?
    # TODO(bowdidge): Structures with unions should get union-specific
    # constructors.
    self.assertIn('void A_init(struct A *s, uint64_t a)', out)
    self.assertIn('void B1_init(struct B *s, uint8_t a, uint64_t c, '
                  'uint8_t b11, uint8_t b12)', out)
    self.assertIn('void B2_init(struct B *s, uint8_t a, uint64_t c, '
                  'uint8_t b21, uint8_t b22)', out)

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
                                 input, 'foo.gen', False)
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
                                 input, 'foo.gen', False)
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
                                 input, 'foo.gen', False)
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
                                 input, 'foo.gen', False)

    self.assertIsNotNone(out)
    self.assertIn('uint8_t a;', out)
    self.assertIn('uint8_t b:2;', out)
    self.assertIn('uint8_t c:6;', out)
    self.assertIn('uint8_t d;', out)

  def testNoDuplicateFunctions(self):
    contents = [
      'STRUCT A',
      '0 63:0 uint64_t a',
      'UNION B u',
      'STRUCT BA b1',
      '1 63:0 uint64_t b',
      'END',
      'STRUCT BB b2',
      '1 63:0 uint64_t b',
      'END',
      'END',
      'END'
      ]

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 contents, 'foo.gen', False)
    self.assertEqual(2, out.count(' BA_init'))
    self.assertEqual(2, out.count(' BB_init'))

  def testSimpleFlags(self):
    contents = [
      'FLAGS foo',
      'A = 1',
      'B = 2',
      'C = 4',
      'D = 8',
      'E = 16',
      'F = 0x20 /* Comment */',
      'END',
      ]

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 contents, 'foo.gen', False)
    self.assertIn('static const int A = 0x1;', out)
    self.assertIn('static const int D = 0x8;', out)
    self.assertIn('static const int F = 0x20;  /* Comment */', out)
    self.assertIn('extern const char *foo_names', out)
    self.assertIn('const char *foo_names[6] = {', out)

  def testFlagsNotPowerOfTwo(self):
    contents = [
      'FLAGS Foo',
      'A = 1',
      'B = 2',
      'AB = 3',
      'C = 4',
      'D = 16',
      'END',
      ]

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 contents, 'foo.gen', False)
    self.assertIn('const int A = 0x1;', out)
    self.assertIn('const int AB = 0x3;', out)
    self.assertIn('const int D = 0x10;', out)
    self.assertIn('"A",  /* 0x1 */', out)
    self.assertIn('"C",  /* 0x4 */', out)
    self.assertIn('"D",  /* 0x10 */', out)
    self.assertIn('"0x8",  /* 0x8, not defined with flag. */', out)
    self.assertNotIn('"AB",  /* 0x3 */', out)
    self.assertIn('extern const char *Foo_names', out)
    self.assertIn('const char *Foo_names[5] = {', out)
    self.assertIn('"0x8",  /* 0x8, not defined with flag. */', out)



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
                                 input, 'foo.gen', False)

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
                                 input, 'foo.gen', False)

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
                                 input, 'foo.gen', False)
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
                                 contents, 'foo.gen', False)
    self.assertIn('struct Foo f[2];', out)

  def disableTestUnknownArrayOfStructs(self):
    contents = ['STRUCT Foo',
                '0 63:32 uint64_t a',
                'END',
                'STRUCT BAR',
                '0 0:0 Foo f[0]',
                'END']

    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 contents, 'foo.gen', False)
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
                                 contents, 'foo.gen', False)

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
                                 contents, 'foo.gen', False)

    self.assertIn('char array[0];\n};', out)

  def testPackedError(self):
    contents = [
	'STRUCT foo',
	'0 63:60 uint8_t foo',
        '0 59:55 uint8_t bar',
        '0 54:50 uint8_t baz',
	'0 49:48 uint8_t boof',
	'END'
	]
    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 contents, 'foo.gen', False)
    # TODO(bowdidge): check that errors were correctly emitted.

  def testJSON(self):
    contents = [
	'STRUCT foo',
	'0 63:48 uint16_t foo',
        '0 47:32 uint16_t bar',
        '0 31:0 uint32_t baz',
	'END'
	]
    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 contents, 'foo.gen', True)
    self.assertIn('bool foo_json_init(struct fun_json *j, struct foo *s)', out)
    self.assertIn('struct fun_json *bar_j = fun_json_lookup(j, "bar");', out)

  def disableTestNestedJSON(self):
    # TODO(bowdidge): Support initializing nested structures from JSON.
    contents = [
	'STRUCT outer_struct',
	'0 63:0 uint64_t outer_var',
        'STRUCT inner_struct',
        '1 63:0 uint64_t inner_var',
	'END',
        'END'
	]
    out = generator.GenerateFile(True, generator.OutputStyleHeader, None,
                                 contents, 'foo.gen', True)
    self.assertIn('struct fun_json *outer_struct_json_init', out)
    # Need JSON for inner structure.
    self.assertIn('struct fun_json *inner_struct_json_init', out)
    # Should see call to outer and inner init.
    self.assertIn('outer_struct_init(s, ', out)
    self.assertIn('inner_struct_init(&inner_var, ', out)
    

    

class TestIndentString(unittest.TestCase):
  def testSimple(self):
    # Tests only properties that hold true regardless of the formatting style.
    generator = codegen.CodePrinter(None, False)
    generator.indent = 1
    self.assertTrue(len(generator.Indent()) > 0)

  def testTwoIndentDoublesOneIndent(self):
    generator = codegen.CodePrinter(None, False)
    generator.indent = 1
    oneIndent = generator.Indent()
    generator.indent = 2
    twoIndent = generator.Indent()    
    self.assertEqual(twoIndent, oneIndent + oneIndent)



if __name__ == '__main__':
    unittest.main()
