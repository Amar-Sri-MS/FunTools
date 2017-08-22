import unittest

import generator
import htmlgen

class HTMLGeneratorTest(unittest.TestCase):
    def testEnumVariablePrinting(self):
        input = ['// Body comment for ENUM A',
                 'ENUM A // Key comment for ENUM A',
                 '// Body comment for ENUM A1',
                 'A1 = 1 // key comment for A1',
                 '// Tail comment for A',
                 'END']

        out = generator.GenerateFile(True, generator.OutputStyleHTML, None,
                                     input, 'foo.gen', False)
        self.assertIsNotNone(out)
        self.assertIn('<h3>enum A</h3>\n'
                      '<p>Key comment for ENUM A</p>\n'
                      '<p>Body comment for ENUM A</p>', out)
        self.assertIn('<dt><code>A1 = 1</code></dt>\n', out)
        self.assertIn('<dd>\nkey comment for A1\n<br>\n', out)
        self.assertIn('Body comment for ENUM A1\n</dd>', out)

    def testFieldPrinting(self):
        input = ['// Body comment for struct A.',
                 'STRUCT A // Key comment for struct A.',
                 '// Body comment for a1.',
                 '0 63:0 uint64_t a1 // Key comment for a1.',
                 '// Tail comment for A.',
                 'END']

        out = generator.GenerateFile(True, generator.OutputStyleHTML, None,
                                     input, 'foo.gen', False)
        self.assertIsNotNone(out)
        self.assertIn('<h3>struct A:</h3>\n'
                      '<p>Key comment for struct A.</p>\n'
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

        out = generator.GenerateFile(True, generator.OutputStyleHTML, None,
                                     input, 'foo.gen', False)
        self.assertIsNotNone(out)
        self.assertIn('<h3>struct A:</h3>\n'
                      '<p>Key comment for struct A.</p>\n'
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

        out = generator.GenerateFile(True, generator.OutputStyleHTML, None,
                                     input, 'foo.gen', False)
        self.assertIsNotNone(out)
        self.assertIn('<h3>struct A:</h3>\n'
                      '<p>Key comment for struct A.</p>\n'
                      '<p>Body comment for struct A.</p>', out)
        self.assertIn('Body comment for a1.', out)
        self.assertIn('Key comment for array.', out)
        self.assertIn('Body comment for array.', out)
        self.assertIn('Tail comment for A', out)

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
        out = generator.GenerateFile(True, generator.OutputStyleHTML, None,
                                     input, 'foo.gen', False)
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
        out = generator.GenerateFile(True, generator.OutputStyleHTML, None,
                                     input, 'foo.gen', False)
        self.assertIsNotNone(out)
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
      out = generator.GenerateFile(True, generator.OutputStyleHTML, None,
                                   contents, 'foo.gen', False)

      self.assertIn('<h3>Flags: Foo</h3>', out)
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
      out = generator.GenerateFile(True, generator.OutputStyleHTML, None,
                                   contents, 'foo.gen', False)

      self.assertIn('<td>BC</td><td>0x00000006</td><td>0 1 1 0</td></tr>', out)


if __name__ == '__main__':
    unittest.main()
