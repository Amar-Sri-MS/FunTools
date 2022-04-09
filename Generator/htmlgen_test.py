#!/usr/bin/env python3
import unittest

import generator
import htmlgen
import parser

# Common lists of codegen options.
OPTIONS_GENERATE_JSON = ['json']
OPTIONS_PACK = ['pack']
OPTIONS_NONE = []

class HTMLGeneratorTest(unittest.TestCase):
    def testEnumVariablePrinting(self):
        input = ['// Body comment for ENUM A',
                 'ENUM A // Key comment for ENUM A',
                 '// Body comment for ENUM A1',
                 'A1 = 1 // key comment for A1',
                 '// Tail comment for A',
                 'END']

        (out, errors) = generator.GenerateFile(generator.OutputStyleHTML, None,
                                               input, 'foo.gen', OPTIONS_PACK)
        self.assertEqual(0, len(errors))
        self.assertIsNotNone(out)
        self.assertIn('<h3>A: enum declaration</h3>\n'
                      '<p><b>Key comment for ENUM A</b></p>\n'
                      '<p>Body comment for ENUM A</p>', out)
        self.assertIn('<dt><code>A1 = 1</code></dt>\n', out)
        self.assertIn('<dd>\nkey comment for A1\n<br>\n', out)
        self.assertIn('Body comment for ENUM A1\n</dd>', out)

    def testConstVariablePrinting(self):
        input = ['// Body comment for CONST',
                 'CONST buffer_sizes // Key comment for buffer sizes',
                 '// Body comment for constant A1',
                 'A1 = 999999 // key comment for A1',
                 '// Body comment for constant A2',
                 'A2 = 0x4000 // key comment for A2',
                 '// Tail comment for A',
                 'END']

        (out, errors) = generator.GenerateFile(generator.OutputStyleHTML, None,
                                               input, 'foo.gen', OPTIONS_PACK)
        self.assertEqual(0, len(errors))
        self.assertIsNotNone(out)
        self.assertIn('Key comment for buffer sizes', out)
        self.assertIn('<p><b>A1</b>: 0xf423f: key comment for A1</p>', out)
        self.assertIn('Body comment for constant A2', out)

    def testFieldPrinting(self):
        input = ['// Body comment for struct A.',
                 'STRUCT A // Key comment for struct A.',
                 '// Body comment for a1.',
                 '0 63:0 uint64_t a1 // Key comment for a1.',
                 '// Tail comment for A.',
                 'END']

        (out, errors) = generator.GenerateFile(generator.OutputStyleHTML, None,
                                               input, 'foo.gen', OPTIONS_PACK)
        self.assertIsNotNone(out)
        self.assertEqual(0, len(errors))
        self.assertIn('<h3>A: structure</h3>\n'
                      '<p><b>Key comment for struct A.</b></p>\n'
                      '<p>Body comment for struct A.</p>', out)
        self.assertIn('Body comment for a1.', out)
        self.assertIn('Key comment for a1.', out)
        self.assertIn('Tail comment for A', out)

    def testPrintZeroSizeArray(self):
        input = ['// Body comment for struct A.',
                 'STRUCT A // Key comment for struct A.',
                 '// Body comment for a1.',
                 '0 63:56 char value',
                 '// Body comment for array.',
                 '_ _:_ char array[0] /* Key comment for array. */',
                 '// Tail comment for A.',
                 'END']

        (out, errors) = generator.GenerateFile(generator.OutputStyleHTML, None,
                                               input, 'foo.gen', OPTIONS_PACK)
        self.assertIsNotNone(out)
        self.assertEqual(0, len(errors))
        self.assertIn('<h3>A: structure</h3>\n'
                      '<p><b>Key comment for struct A.</b></p>\n'
                      '<p>Body comment for struct A.</p>', out)
        self.assertIn('Body comment for a1.', out)
        self.assertIn('Key comment for array.', out)
        self.assertIn('Body comment for array.', out)
        self.assertIn('Tail comment for A', out)

    def testPrintZeroSizeStructArray(self):
        input = ['STRUCT element',
                 '0 63:56 char a',
                 'END',
                 '// Body comment for struct A.',
                 'STRUCT A // Key comment for struct A.',
                 '// Body comment for a1.',
                 '0 63:56 char value',
                 '// Body comment for array.',
                 '_ _:_ element array[0] /* Key comment for array. */',
                 '// Tail comment for A.',
                 'END']

        (out, errors) = generator.GenerateFile(generator.OutputStyleHTML, None,
                                               input, 'foo.gen', OPTIONS_PACK)
        self.assertIsNotNone(out)
        self.assertEqual(0, len(errors))
        self.assertIn('<h3>A: structure</h3>\n'
                      '<p><b>Key comment for struct A.</b></p>\n'
                      '<p>Body comment for struct A.</p>', out)
        self.assertIn('Body comment for a1.', out)
        self.assertIn('Key comment for array.', out)
        self.assertIn('Body comment for array.', out)
        self.assertIn('Tail comment for A', out)
        self.assertIn('element[0]', out)
        self.assertIn('<td>array</td>', out)

    def testPrintSubfields(self):
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
        (out, errors) = generator.GenerateFile(generator.OutputStyleHTML, None,
                                               input, 'foo.gen', OPTIONS_PACK)
        self.assertEqual(0, len(errors))
        self.assertIsNotNone(out)

    def testPrintNestedSubfields(self):
        input = [
            'STRUCT outer'
            '// Body comment for a.',
            '0 63:00 uint64_t a // Key comment for a.',
            'STRUCT inner',
            '// Body comment for b.',
            '0 63:00 uint64_t b // Key comment for b.',
            'END',
            'END'
            ]
        (out, errors) = generator.GenerateFile(generator.OutputStyleHTML, None,
                                               input, 'foo.gen', OPTIONS_PACK)
        self.assertIsNotNone(out)
        self.assertEqual(0, len(errors))
        self.assertIn('Key comment for a.', out)
        self.assertIn('Key comment for b.', out)
        self.assertIn('Body comment for a.', out)
        self.assertIn('Body comment for b.', out)

    def testPrintFlags(self):
      contents = [
        'FLAGS Foo',
        'A = 1',
        'B = 2',
        'C = 4',
        'D = 8',
        'E = 16',
        'F = 0x20',
        'END'
        ]
      (out, errors) = generator.GenerateFile(generator.OutputStyleHTML, None,
                                             contents, 'foo.gen', OPTIONS_PACK)

      self.assertIn('<h3>Foo: flagset</h3>', out)
      self.assertEqual(0, len(errors))
      self.assertIn('<td>A</td><td>0x00000001</td><td>0 0 0 0 0 1</td></tr>',
                    out)
      self.assertIn('<td>F</td><td>0x00000020</td><td>1 0 0 0 0 0</td></tr>',
                    out)

    def testPrintFlagsNonPowerOfTwo(self):
      contents = [
        'FLAGS Foo',
        'A = 1',
        'B = 2',
        'C = 4',
        'BC = 6',
        'D = 8',
        'END'
        ]
      (out, errors) = generator.GenerateFile(generator.OutputStyleHTML, None,
                                   contents, 'foo.gen', OPTIONS_PACK)

      self.assertEqual(0, len(errors))
      self.assertIn('<td>BC</td><td>0x00000006</td><td>0 1 1 0</td></tr>', out)

class FieldTableTest(unittest.TestCase):
    def testSimpleField(self):
        f = parser.Field('foo', parser.TypeForName('char'), 0, 8)
        f.key_comment = 'Key comment'

        gen = htmlgen.HTMLGenerator()
        out =  gen.VisitField(f, 0, {})
        self.assertIn('<td class="structBits">0</td>', out)
        self.assertIn('<td>foo</td>', out)
        self.assertIn('<td>char</td>', out)
        self.assertIn('Key comment<br>', out)

    def testSimpleArrayField(self):
        f = parser.Field('foo', parser.ArrayTypeForName('char', 8), 0, 8)
        f.key_comment = 'Key comment'

        gen = htmlgen.HTMLGenerator()
        out =  gen.VisitField(f, 0, {})
        self.assertIn('<td class="structBits">63-56</td>', out)
        self.assertIn('<td>foo</td>', out)
        self.assertIn('<td>char[8]</td>', out)
        self.assertIn('Key comment<br>', out)
        
    def testSimpleArrayField(self):
        s = parser.Struct('Bar', False)
        struct_array_type = parser.RecordArrayTypeForStruct(s, 4)
        f = parser.Field('foo', struct_array_type, 0, 8)
        f.key_comment = 'Key comment'

        gen = htmlgen.HTMLGenerator()
        out =  gen.VisitField(f, 0, {})
        self.assertIn('<td class="structBits">63-56</td>', out)
        self.assertIn('<td>foo</td>', out)
        self.assertIn('<td>struct Bar[4]</td>', out)
        self.assertIn('Key comment<br>', out)

    def testZeroLengthArrayField(self):
        s = parser.Struct('Bar', False)
        struct_array_type = parser.RecordArrayTypeForStruct(s, 0)
        f = parser.Field('foo', struct_array_type, 0, 0)
        f.key_comment = 'Key comment'

        gen = htmlgen.HTMLGenerator()
        out =  gen.VisitField(f, 0, {})
        # TODO(bowdidge): Why 63-0?
        self.assertIn('<td class="structBits">63-0</td>', out)
        self.assertIn('<td>foo</td>', out)
        self.assertIn('<td>struct Bar[0]</td>', out)
        self.assertIn('Key comment<br>', out)
        

if __name__ == '__main__':
    unittest.main()
