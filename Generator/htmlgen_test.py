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
                                     input, 'foo.gen')
        self.assertIsNotNone(out)
        self.assertIn('<h3>enum A</h3>\n'
                      '<p>Key comment for ENUM A</p>\n'
                      '<p>Body comment for ENUM A</p>', out)
        self.assertIn('<dt>A1 = 1</dt>\n'
                      '<dd>\n'
                      'key comment for A1<br>Body comment for ENUM A1</dd>', out)

    def testFieldPrinting(self):
        input = ['// Body comment for struct A.',
                 'STRUCT A // Key comment for struct A.',
                 '// Body comment for a1.',
                 '0 63:0 uint64_t a1 // Key comment for a1.',
                 '// Tail comment for A.',
                 'END']

        out = generator.GenerateFile(True, generator.OutputStyleHTML, None,
                                     input, 'foo.gen')
        self.assertIsNotNone(out)
        self.assertIn('<h3>struct A:</h3>\n'
                      '<p>Key comment for struct A.</p>\n'
                      '<p>Body comment for struct A.</p>', out)
        self.assertIn('Body comment for a1.', out)
        self.assertIn('Key comment for a1.', out)
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
                                     input, 'foo.gen')
        print out
        self.assertIsNotNone(out)



if __name__ == '__main__':
    unittest.main()
