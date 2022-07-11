#!/usr/bin/env python3
#
# Unit tests for Generator's code generation.
#
# Copyright Fungible Inc. 2017.

import unittest

import re

import codegen
import generator
import parser

# Common lists of codegen options.
OPTIONS_GENERATE_JSON = ['json']
OPTIONS_PACK = ['pack']
OPTIONS_NONE = []

def RemoveWhitespace(str):
  """Converts all whitespace to single spaces for consistent compares."""
  return re.sub('\s+', ' ', str)

class CodegenEndToEnd(unittest.TestCase):
  def testSimpleEndToEnd(self):
    input = ['STRUCT Foo',
             '0 63:56 uint8_t a /* comment about a */',
             '0 55:54 uint8_t b',
             '0 53:52 uint8_t c',
             '0 51:48 uint8_t reserved',
             '0 47:0 char d[6]',
             'END']

    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           input, 'foo.gen', ['pack', 'json'])
    self.assertEqual(0, len(errors))
    self.assertIsNotNone(out)

    out = RemoveWhitespace(out)

    # Did structure get generated?
    self.assertIn('struct Foo {', out)
    # Did field a get rendered?
    self.assertIn('uint8_t a; /* comment about a */', out)
    # Did bitfield get packed?
    self.assertIn('uint8_t b_to_c;', out)
    # Did array get included?
    self.assertIn('char d[6];', out)
    # Did constructor get created?
    self.assertIn('void Foo_init(struct Foo *s, ', out)
    # Did accessor macro get created?
    self.assertIn('#define FOO_B_P(x)', out)

    # Check macros weren't created for reserved fields.
    self.assertNotIn('#define FOO_RESERVED', out)

    # Did bitfield get initialized?'
    self.assertIn('s->b_to_c = FOO_B_P(b) | FOO_C_P(c)', out)

  def testZeroDimensionArray(self):
    input = ['STRUCT Foo',
             '0 63:56 uint8_t a',
             '_ _:_ uint8_t chars[0]',
             'END']
    out, errors = generator.GenerateFile(generator.OutputStyleLinux, None,
                                         input, 'foo.gen',
                                         ['pack', 'json', 'swap'])
    print(errors)
    self.assertEqual(0, len(errors))
    self.assertIsNotNone(out)

    out = RemoveWhitespace(out)

    # Check for C99 style of flex arrays, not gcc style.
    self.assertIn('[]', out)
    self.assertNotIn('[0]', out)


  def testLinuxBadTypeNames(self):
    """Linux mode limits type names to only uint8, uint16_t, uint32_t, and
    uint64_t.
    """
    input = ['STRUCT Foo',
             '0 63:48 int16_t a',
             'END']
    (out, errors) = generator.GenerateFile(generator.OutputStyleLinux, None,
                                           input, 'foo.gen', [])
    self.assertEquals(1, len(errors))
    self.assertIn('Unknown type name "int16_t', errors[0])

  def testLinuxEndToEnd(self):
    input = ['STRUCT Foo',
             '0 63:56 uint8_t a /* comment about a */',
             '0 55:54 uint8_t b',
             '0 53:52 uint8_t c',
             '0 51:48 uint8_t reserved',
             '0 47:0 uint8_t d[6]',
             '1 63:32 uint32_t e',
             'END']

    (out, errors) = generator.GenerateFile(generator.OutputStyleLinux, None,
                                           input, 'foo.gen',
                                           ['pack', 'json', 'swap'])
    self.assertEqual(0, len(errors))
    self.assertIsNotNone(out)

    out = RemoveWhitespace(out)

    # Did structure get generated?
    self.assertIn('struct Foo {', out)
    # Did field a get rendered?
    self.assertIn('__u8 a; /* comment about a */', out)
    # Did bitfield get packed?
    self.assertIn('__u8 b_to_c;', out)
    # Did array get included?
    self.assertIn('__u8 d[6];', out)
    self.assertIn('__dpu32 e;', out)
    # Did constructor get created?
    # Test individually because of odd whitespace around the commas.
    self.assertIn('void Foo_init(struct Foo *s, __u8 a', out)
    self.assertIn('__u8 b', out)
    self.assertIn('__u8 c', out)

    # Did accessor macro get created?
    self.assertIn('#define FOO_B_P(x)', out)

    # Check macros weren't created for reserved fields.
    self.assertNotIn('#define FOO_RESERVED', out)

    # Did bitfield get initialized?'
    self.assertIn('s->b_to_c = ( FOO_B_P_NOSWAP(b) | FOO_C_P_NOSWAP(c) );',
                  out)
    # Did full field get initialized?
    self.assertIn('s->e = cpu_to_dpu32(e)', out)

  # Test disabled because checker complains that the
  # union is misaligned.
  def disableTestInitFunctionsCreated(self):
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

    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           input, 'foo.gen', OPTIONS_PACK)
    self.assertEqual(0, len(errors))
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
    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           input, 'foo.gen', OPTIONS_PACK)
    print(out)
    self.assertEqual(0, len(errors))
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
    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           input, 'foo.gen', OPTIONS_PACK)

    self.assertEqual(0, len(errors))
    self.assertIsNotNone(out)
    self.assertIn('#define AX1_A_S 4', out)

  # Disabled until issues with union layout resolved.
  def disableTestInitFunctionsCreated(self):
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

    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           input, 'foo.gen', OPTIONS_PACK)
    self.assertEqual(0, len(errors))
    self.assertIsNotNone(out)

    out = RemoveWhitespace(out)

    # Did structure get generated?
    # TODO(bowdidge): Structures with unions should get union-specific
    # constructors.
    self.assertIn('void A_init(struct A *s, uint64_t a', out)
    self.assertIn('void B1_init(struct B *s, uint8_t a, uint64_t c, '
                  'uint8_t b11, uint8_t b12', out)
    self.assertIn('void B2_init(struct B *s, uint8_t a, uint64_t c, '
                  'uint8_t b21, uint8_t b22', out)

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

    out = generator.GenerateFile(generator.OutputStyleHeader, None,
                                 input, 'foo.gen', OPTIONS_PACK)
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

    out = generator.GenerateFile(generator.OutputStyleHeader, None,
                                 input, 'foo.gen', OPTIONS_PACK)
    self.assertIsNotNone(out)

  def testMultiFlitNestedStruct(self):
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

    (out, errors)  = generator.GenerateFile(generator.OutputStyleHeader, None,
                                            input, 'foo.gen', OPTIONS_PACK)
    print(errors)
    self.assertEqual(0, len(errors))
    self.assertIsNotNone(out)
    self.assertIn('struct fun_admin_cmd_common c;', out)

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

    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           contents, 'foo.gen', OPTIONS_PACK)

    self.assertEqual(0, len(errors))

    out = RemoveWhitespace(out)

    self.assertEqual(1, out.count('void BA_init'))
    self.assertEqual(1, out.count('void BB_init'))

  def testSimpleFlags(self):
    contents = [
      'FLAGS foo',
      'A = 1',
      'B = 2',
      'C = 4',
      'D = 8',
      'E = 16',
      'F = 0x20 /* Comment */',
      'G = 0xFFFFFFFF',
      'END',
      ]

    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           contents, 'foo.gen', OPTIONS_PACK)

    self.assertEqual(0, len(errors))
    out = RemoveWhitespace(out)

    self.assertIn('static const unsigned int A = 0x1;', out)
    self.assertIn('static const unsigned int D = 0x8;', out)
    self.assertIn('static const unsigned int F = 0x20; /* Comment */', out)
    self.assertIn('static const unsigned int G = 0xffffffff;', out)
    self.assertIn('extern const char *foo_names', out)
    self.assertIn('const char *foo_names[] = {', out)

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

    (out, errors)= generator.GenerateFile(generator.OutputStyleHeader, None,
                                          contents, 'foo.gen', OPTIONS_PACK)
    self.assertEqual(0, len(errors))
    out = RemoveWhitespace(out)

    self.assertIn('const unsigned int A = 0x1;', out)
    self.assertIn('const unsigned int AB = 0x3;', out)
    self.assertIn('const unsigned int D = 0x10;', out)
    self.assertIn('"A", /* 0x1 */', out)
    self.assertIn('"C", /* 0x4 */', out)
    self.assertIn('"D", /* 0x10 */', out)
    self.assertIn('"undefined", /* 0x8 */', out)
    self.assertNotIn('"AB", /* 0x3 */', out)
    self.assertIn('extern const char *foo_names', out)
    self.assertIn('const char *foo_names[] = {', out)


class TestComments(unittest.TestCase):

  def testStructComments(self):
    # ... allows a field to overflow into later flits.
    input = [
      '// Body comment.',
      'STRUCT fun_admin_cmd_common',
      '// Field comment.',
      '0 63:00 uint64_t common_opcode // Key comment',
      '// Tail comment.',
      'END'
      ]

    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           input, 'foo.gen', OPTIONS_PACK)
    self.assertEqual(0, len(errors))

    out = RemoveWhitespace(out)

    self.assertIn('/* Body comment. */', out)
    self.assertIn('struct fun_admin_cmd_common {', out)
    self.assertIn('/* Field comment. */', out)
    self.assertIn('uint64_t common_opcode; /* Key comment */', out)
    self.assertIn('/* Tail comment. */', out)

  def testUnionComments(self):
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

    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           input, 'foo.gen', OPTIONS_PACK)
    self.assertEqual(0, len(errors))

    self.assertIn('/* Struct comment. */', out)
    self.assertIn('/* Union body comment. */', out)
    self.assertIn('/* A comment */', out)
    self.assertIn('/* B comment. */', out)

  def testEnumComments(self):
    input = [
      '// Enum comment.',
      'ENUM values',
      '// Enum body comment',
      'A = 1 // Enum key comment 1',
      'B = 2 // Enum key comment 2',
      '// Tail comment',
      'END']

    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           input, 'foo.gen', OPTIONS_PACK)
    self.assertEqual(0, len(errors))

    out = RemoveWhitespace(out)

    self.assertIn('enum values {', out)
    self.assertIn('A = 0x1,' ,out)
    self.assertIn('/* Enum key comment 1 */', out)
    self.assertIn('B = 0x2,', out)
    self.assertIn('/* Enum key comment 2 */', out)
    self.assertIn('/* Tail comment */', out)

  def testConstComments(self):
    input = [
      '// Maximum buffer lengths.',
      'CONST max_buffer_len',
      '// Enum body comment',
      'MAX_BUF = 4000 // Enum key comment 1',
      'MAX_BIG_BUF = 0x999999 // Enum key comment 2',
      '// Tail comment',
      'END']

    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           input, 'foo.gen', OPTIONS_PACK)
    self.assertEqual(0, len(errors))

    out = RemoveWhitespace(out)
    print(out)
    # TODO(bowdidge): Check comments.
    self.assertIn('enum max_buffer_len', out)
    self.assertIn('MAX_BUF = 0xfa0,' ,out)
    self.assertIn('MAX_BIG_BUF = 0x999999,' ,out)


  def testArrayOfStructs(self):
    contents = ['STRUCT Foo',
                '0 63:32 uint64_t a',
                'END',
                'STRUCT BAR',
                '0 63:0 Foo f[2]',
                'END']

    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           contents, 'foo.gen', OPTIONS_PACK)

    self.assertEqual(0, len(errors))

    out = RemoveWhitespace(out)

    self.assertIn('struct Foo f[2];', out)

  def disableTestUnknownArrayOfStructs(self):
    contents = ['STRUCT Foo',
                '0 63:32 uint64_t a',
                'END',
                'STRUCT BAR',
                '0 0:0 Foo f[0]',
                'END']

    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           contents, 'foo.gen', OPTIONS_PACK)
    self.assertEqual(0, len(errors))

    self.assertIn('struct Foo f[2];', out)

  def testNameListCorrectlyHandlesEnumVariablesWithGaps(self):
    contents = ['ENUM A',
                'A = 1',
                'C = 3',
                'D = 4',
                'E = 5',
                'F = 7',
                'G = 10',
                'END'
                ]
    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           contents, 'foo.gen', OPTIONS_PACK)
    self.assertEqual(0, len(errors))

    out = RemoveWhitespace(out)

    self.assertIn('"undefined", /* 0x0 */', out)
    self.assertIn('"A", /* 0x1 */', out)
    self.assertIn('"undefined", /* 0x2 */', out)
    self.assertIn('"C", /* 0x3 */', out)
    self.assertIn('"E", /* 0x5 */', out)
    self.assertIn('"undefined", /* 0x6 */', out)
    self.assertIn('"G", /* 0xa */', out)

  def testVariableLengthArray(self):
    contents = [
      'STRUCT foo',
      '0 63:56 char initial',
      '_ _:_ char array[0]',
      'END'
      ]

    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           contents, 'foo.gen', OPTIONS_PACK)
    self.assertEqual(0, len(errors))

    out = RemoveWhitespace(out);

    self.assertIn('char array[0]; };', out)

  def testLinuxVariableLengthArray(self):
    contents = [
      'STRUCT foo',
      '0 63:56 uint8_t initial',
      '_ _:_ uint8_t array[0]',
      'END'
      ]

    (out, errors) = generator.GenerateFile(generator.OutputStyleLinux, None,
                                           contents, 'foo.gen', OPTIONS_PACK)
    print(errors)
    self.assertEqual(0, len(errors))

    out = RemoveWhitespace(out);

    # Linux uses C99 style variable args, not gcc style.
    self.assertIn('__u8 array[]; };', out)

  # Disable until we can run the generator without errors on funhci.
  def disable_testPackedError(self):
    contents = [
	'STRUCT foo',
	'0 63:60 uint8_t foo',
        '0 59:55 uint8_t bar',
        '0 54:50 uint8_t baz',
	'0 49:48 uint8_t boof',
	'END'
	]
    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           contents, 'foo.gen', OPTIONS_PACK)
    self.assertEqual(1, len(errors))
    self.assertIn("Width of packed bit-field containing foo and bar (9 bits)",
                  errors[0])

  def testJSON(self):
    contents = [
	'STRUCT foo',
	'0 63:48 uint16_t foo',
        '0 47:32 uint16_t bar',
        '0 31:0 uint32_t baz',
	'END'
	]
    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           contents, 'foo.gen', ['pack', 'json'])
    self.assertEqual(0, len(errors))

    out = RemoveWhitespace(out)

    self.assertIn('bool foo_json_init(struct fun_json *j,', out)
    self.assertIn('struct foo *s)', out)

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

    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader, None,
                                           contents, 'foo.gen', ['pack', 'json'])
    self.assertEqual(0, len(errors))
    self.assertIn('struct fun_json *outer_struct_json_init', out)
    # Need JSON for inner structure.
    self.assertIn('struct fun_json *inner_struct_json_init', out)
    # Should see call to outer and inner init.
    self.assertIn('outer_struct_init(s, ', out)
    self.assertIn('inner_struct_init(&inner_var, ', out)

  def testEndiannessWhenGeneratingLittleEndian(self):
    contents = [
        'STRUCT foo',
        '0 63:48 uint16_t foo',
        '0 47:32 __le16 bar',
        '0 31:16 __be16 baz',
        '0 15:0 uint16_t beep',
        'END']
    (out, errors) = generator.GenerateFile(generator.OutputStyleLinux,
                                           None, contents, 'foo.gen',
                                           ['pack', 'swap', 'le'])
    self.assertEqual(0, len(errors))
    self.assertIsNotNone(out)

    out = RemoveWhitespace(out)

    # Native types get swapped.
    self.assertIn('cpu_to_le16(foo)', out)
    self.assertIn('cpu_to_le16(beep)', out)

    # types with endianness don't get swapped.
    self.assertIn('s->bar = (bar)', out)
    self.assertIn('s->baz = (baz)', out)

  def testEndiannessWhenGeneratingBigEndian(self):
    contents = [
        'STRUCT foo',
        '0 63:48 uint16_t foo',
        '0 47:32 __le16 bar',
        '0 31:16 __be16 baz',
        '0 15:0 uint16_t beep',
        'END']
    (out, errors) = generator.GenerateFile(generator.OutputStyleLinux,
                                           None, contents, 'foo.gen',
                                           ['pack', 'swap', 'be'])
    self.assertEqual(0, len(errors))
    self.assertIsNotNone(out)

    out = RemoveWhitespace(out)

    # Native types get swapped.
    self.assertIn('cpu_to_be16(foo)', out)
    self.assertIn('cpu_to_be16(beep)', out)

    # types with endianness don't get swapped.
    self.assertIn('s->bar = (bar)', out)
    self.assertIn('s->baz = (baz)', out)

  def testEndianFieldsInPackedMode(self):
    contents = [
        'STRUCT foo',
        '0 63:52 uint16_t foo',
        '0 51:40 __le16 bar',
        '0 39:28 __be16 baz',
        '0 27:16 uint16_t beep',
        'END']
    (out, errors) = generator.GenerateFile(generator.OutputStyleHeader,
                                           None, contents, 'foo.gen',
                                           ['pack', 'swap', 'le'])
    self.assertEqual(2, len(errors))
    self.assertIn('field with endian-specific type __le16 cannot '
                     'be a bitfield', errors[0])
    self.assertIn('field with endian-specific type __be16 cannot '
                     'be a bitfield', errors[1])

  def testEndianFieldsInPackedModeLinux(self):
    contents = [
        'STRUCT foo',
        '0 63:52 __be32 foo',
        '0 51:40 __be32 bar',
        '0 39:32 __be32 baz',
        '0 31:27 uint32_t beep',
        '0 26:19 uint32_t bop',
        '0 18:0 uint32_t beet',
        'END']
    (out, errors) = generator.GenerateFile(generator.OutputStyleLinux,
                                           None, contents, 'foo.gen',
                                           ['pack', 'swap', 'le'])
    self.assertEqual(3, len(errors))

    self.assertIn('field with endian-specific type __be32 cannot '
                     'be a bitfield', errors[0])
    self.assertIn('field with endian-specific type __be32 cannot '
                     'be a bitfield', errors[1])
    self.assertIn('field with endian-specific type __be32 cannot '
                     'be a bitfield', errors[2])

  def testEndiannessInSoloPackedFields(self):
    contents = [
        'STRUCT foo',
        '0 63:61 __le16 foo',
        'END']
    (out, errors) = generator.GenerateFile(generator.OutputStyleLinux,
                                           None, contents, 'foo.gen',
                                           ['pack', 'swap', 'le'])

    self.assertEqual(1, len(errors))
    self.assertIn('field with endian-specific type __le16 cannot '
                  'be a bitfield', errors[0])

  def testEndiannessIfPulledIntoPackedField(self):
    contents = [
        'STRUCT foo',
        # foo requires a bitfield.
        '0 63:48 uint64_t foo',
        # We shouldn't pack the fields - different types.
        '0 47:32 __le64 bar',
        'END']
    (out, errors) = generator.GenerateFile(generator.OutputStyleLinux,
                                           None, contents, 'foo.gen',
                                           ['pack', 'swap', 'le'])
    print(errors)
    self.assertEqual(1, len(errors))
    self.assertIn('field with endian-specific type __le64 cannot '
                  'be a bitfield', errors[0])

if __name__ == '__main__':
    unittest.main(verbosity=2)
