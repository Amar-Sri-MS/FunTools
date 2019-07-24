#
# Unit tests for wu trace parsing.
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.
#

import json
import sys
import unittest

import render
import StringIO
import read_trace
import wu_trace

def first_transaction(transactions):
    """Return first transaction parsed, or None if no transaction was parsed.

    The transactions list reserves the 0th transaction for the
    bootstrap code, so transactions[1] would be the first transaction.
    """
    if len(transactions) < 2:
        return None
    return transactions[1]

class TestParseLine(unittest.TestCase):
    def setUp(self):
        self.file_parser = read_trace.TraceLogParser()

    def testNotALogLine(self):
        self.assertEqual((None, None), self.file_parser.parse_line('foo'))
        self.assertEqual((None, None),
                         self.file_parser.parse_line('1000.001000000'))

    def testSimpleParse(self):
        line = '123123123.567890000 TRACE WU START faddr FA0:8:0[VP] wuid 0x1 name foo arg0 1 arg1 2 origin FA0:8:0[VP]'
        (line_args, error) = self.file_parser.parse_line(line)

        self.assertIsNone(error)

        self.assertEqual(123123123567890000, line_args['timestamp'])
        self.assertEqual('FA0:8:0[VP]', line_args['faddr'].as_faddr_str())
        self.assertEqual('WU', line_args['verb'])
        self.assertEqual('START', line_args['noun'])
        self.assertEqual(1, line_args['arg0'])
        self.assertEqual(2, line_args['arg1'])


    def testParseTransactionStart(self):
        line = '1.000001000 TRACE TRANSACTION START faddr FA0:8:0[VP]'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNotNone(line_args)
        self.assertIsNone(error)

        line = '0.000006000 TRACE TRANSACTION START faddr FA0:8:0[VP]\n'
        line_args = self.file_parser.parse_line(line)
        self.assertIsNotNone(line_args)
        self.assertIsNone(error)

    def testParseAnnotation(self):
        line = '0.024206656 TRACE TRANSACTION ANNOT faddr FA0:19:0[VP] msg Start unit test timer_test_microseconds'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNotNone(line_args)
        self.assertIsNone(error)

    def testParseAnnotation(self):
        line = '0.024206656 TRACE TRANSACTION ANNOT faddr FA0:19:0[VP] msg Start unit test timer_test_microseconds'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNotNone(line_args)
        self.assertIsNone(error)

    def testBadVerb(self):
        # Colon after send is invalid.
        line = '485375410.764454000 TRACE WU SEND: faddr FA0:12:0[VP] wuid 0x60 name wuh_mp_notify arg0 0x0 arg1 0x0 dest FA0:12:0[VP]'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNone(line_args)
        self.assertIn('malformed log line', error)

    def testUnknownVerb(self):
        # Comma after VP is unexpected.
        line = '485375410.764454000 TRACE FOO BAR faddr FA0:12:0[VP] dest FA0:8:0[VP], wuid 0x60 name wuh_mp_notify arg0 0x0 arg1 0x0'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNone(line_args)
        self.assertIn('unknown verb or noun', error)

    def testMissingKey(self):
        # Remove src.
        line = '485375410.764454000 TRACE WU START faddr FA0:12:0[VP] wuid 0x60 name wuh_mp_notify arg1 0x0 origin FA0:12:0[VP]'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNone(line_args)
        self.assertIn('missing key "arg0"', error)

    def testMalformedNumber(self):
        # gg is not valid hex.
        line = '485375410.764454000 TRACE WU SEND faddr FA0:12:0[VP] wuid 0xgg name wuh_mp_notify arg0 0x0 arg1 0x0 dest FA0:12:0[VP] flags 0'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNone(line_args)
        self.assertIn('invalid literal for int() with base 16', error)

    def testMalformedHexNumber(self):
        # 1A is not valid decimal value.
        line = '485375410.764454000 TRACE WU SEND faddr FA0:12:0[VP] wuid 1A name wuh_mp_notify arg0 0x0 arg1 0x0 flags 0 dest FA0:12:0[VP]'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNone(line_args)
        self.assertIn('invalid literal for int() with base 10', error)

    # TODO(bowdidge): Remove.  Sorting now.
    def disableTestTimeGoesBackwards(self):
        """Test that we correctly remember the last timestamp seen."""
        line1 = '123123123.567890000 TRACE WU START faddr FA0:8:0[VP] wuid 0x1 name foo arg0 1 arg1 2'

        line2 = '123123123.467890000 TRACE WU START faddr FA1:8:0[VP] wuid 0x1 name foo arg0 1 arg1 2'

        (line_args, error) = self.file_parser.parse_line(line1)
        self.assertIsNotNone(line_args)
        self.assertIsNone(error)

        (line_args, error) = self.file_parser.parse_line(line2)
        self.assertIsNone(line_args)
        self.assertIsNotNone(error)
        self.assertIn('timestamp going backwards', error)


class TestProcessFile(unittest.TestCase):
    def process_transactions(self, lines):
        filename = 'fake_file'
        fake_input = StringIO.StringIO('\n'.join(lines))
        file_parser = read_trace.TraceLogParser()
        events = []
        events = file_parser.parse(fake_input, filename=filename)
        trace_processor = wu_trace.TraceProcessor(filename)
        for idx, e in enumerate(events):
            trace_processor.handle_log_line(e, idx)
        return trace_processor.transactions


    def testStartEnd(self):
        log = ['1.000100000 TRACE WU START faddr FA0:8:0[VP] wuid 0x1 name my_wu arg0 1 arg1 2 origin FA0:8:0[VP]',
               '1.000200000 TRACE WU END faddr FA0:8:0[VP]']
        transactions = self.process_transactions(log)

        self.assertIsNotNone(transactions)
        tr = first_transaction(transactions)
        self.assertIsNotNone(tr)
        self.assertEqual(1, len(tr.flatten()))

        self.assertEqual(100000, tr.root_event.duration())
        self.assertEqual(1000100000, tr.root_event.start_time)
        self.assertEqual('my_wu', tr.root_event.label)
        self.assertEqual(0, len(tr.root_event.successors))

    def testSendGroupsWithEvent(self):
        log = """
1.000100000 TRACE WU START faddr FA0:8:0[VP] wuid 0x1 name my_wu arg0 1 arg1 2 origin FA0:8:0[VP]
1.000150000 TRACE WU SEND faddr FA0:8:0[VP] wuid 0x2 name sent_wu arg0 1 arg1 1 flags 0 dest FA0:12:0[VP]
1.000200000 TRACE WU END faddr FA0:8:0[VP] wuid 0x1 name my_wu arg0 1 arg1 2
1.000300000 TRACE WU START faddr FA0:12:0[VP] wuid 0x2 name sent_wu arg0 1 arg1 1 origin FA0:8:0[VP]
1.0004000000 TRACE WU END faddr FA0:12:0[VP]
""".split('\n')
        transactions = self.process_transactions(log)
        tr = first_transaction(transactions)
        render.dump_transactions(sys.stdout, transactions)
        self.assertIsNotNone(tr)

        self.assertEqual(1, len(tr.root_event.successors))


    def testTriggerTimer(self):
        log = """
1.000100000 TRACE WU START faddr FA0:8:0[VP] wuid 0x1 name my_wu arg0 1 arg1 2 origin FA0:8:0[VP]
1.000150000 TRACE TIMER START faddr FA0:8:0[VP] timer 0x1 wuid 0x2 name sent_wu dest FA0:8:0[VP] arg0 0x2
1.000200000 TRACE WU END faddr FA0:8:0[VP]
1.000300000 TRACE WU START faddr FA0:8:0[VP] wuid 0x2 name sent_wu arg0 0x2 arg1 0 origin FA0:8:0[VP]
1.0004000 faddr000 TRACE WU END FA0:8:0[VP]
""".split('\n')
        transactions = self.process_transactions(log)
        print transactions
        self.assertIsNotNone(transactions)

        self.assertEqual(2, len(transactions))
        tr = first_transaction(transactions)

        self.assertEqual(1, len(tr.root_event.successors))

    def testTopLevelTransaction(self):
        log = """
1.00100000 TRACE WU START faddr FA0:8:0[VP] wuid 1 name fun_a arg0 1 arg1 2 origin FA0:0:0[VP]
1.00200000 TRACE TRANSACTION START faddr FA0:8:0[VP]
1.00300000 TRACE WU END faddr FA0:8:0[VP] wuid 1 name fun_a arg0 1 arg1 2
""".split('\n')
        transactions = self.process_transactions(log)

        # One transaction for boot, one for the created transaction.
        self.assertEqual(2, len(transactions))

        tr = transactions[1]
        self.assertIsNotNone(tr.root_event)
        self.assertEqual(0, len(tr.root_event.successors))

    def testChainOfTransactions(self):
        log = """
0.000001000 TRACE WU START faddr FA0:8:0[VP] wuid 0 name foo arg0 0 arg1 0 origin FA0:8:0[VP]
0.000002000 TRACE TIMER START faddr FA0:8:0[VP] timer 0x1 wuid 0x9 name bar arg0 0x1 dest FA0:8:0[VP]
0.000003000 TRACE WU END faddr FA0:8:0[VP]
0.000006000 TRACE WU START faddr FA0:8:0[VP] wuid 0x9 name bar arg0 0x1 arg1 0 origin FA0:8:0[VP]
0.000006000 TRACE TRANSACTION START faddr FA0:8:0[VP]
0.000007000 TRACE TIMER START faddr FA0:8:0[VP] timer 0x1 wuid 17 name baz arg0 0x2 dest FA0:8:0[VP]
0.000008000 TRACE WU END faddr FA0:8:0[VP]
0.000011000 TRACE WU START faddr FA0:8:0[VP] origin FA0:8:0[VP] wuid 17 name baz arg0 0x2 arg1 0 origin FA0:8:0[VP]
0.000011000 TRACE TRANSACTION START faddr FA0:8:0[VP]
0.000012000 TRACE TIMER START faddr FA0:8:0[VP] timer 0x1 wuid 19 name boof arg0 0x3 dest FA0:8:0[VP]
0.000013000 TRACE WU END faddr FA0:8:0[VP]
0.000014000 TRACE WU START faddr FA0:8:0[VP] origin FA0:8:0[VP] wuid 19 name boof arg0 0x3 arg1 0 origin FA0:8:0[VP]
0.000015000 TRACE TRANSACTION START faddr FA0:8:0[VP]
0.000016000 TRACE WU END faddr FA0:8:0[VP]
""".split('\n')

        transactions = self.process_transactions(log)
        output_file = FakeFile()
        render.dump_transactions(output_file, transactions)

        for l in output_file.lines:
            print(l)
            expected = ['00.000000 - 00.000000 (0 nsec): transaction "boot"\n',
                        '+ 00.000000 - 00.000000 (0 nsec): boot\n',
                        '00.000001 - 00.000003 (2.0 usec): transaction "foo"\n',
                        '+ 00.000001 - 00.000003 (2.0 usec): foo\n',
                        '+ 00.000002 - 00.000006 (4.0 usec): timer\n',
                        '00.000006 - 00.000008 (2.0 usec): transaction "bar"\n',
                        '+ 00.000006 - 00.000008 (2.0 usec): bar\n',
                        '+ 00.000007 - 00.000011 (4.0 usec): timer\n',
                        '00.000011 - 00.000013 (2.0 usec): transaction "baz"\n',
                        '+ 00.000011 - 00.000013 (2.0 usec): baz\n',
                        '+ 00.000012 - 00.000014 (2.0 usec): timer\n',
                        '00.000014 - 00.000016 (2.0 usec): transaction "boof"\n',
                        '+ 00.000014 - 00.000016 (2.0 usec): boof\n']

            self.assertEqual(expected, output_file.lines)

class FakeFile:
    def __init__(self):
        self.lines = []

    def write(self, line):
        self.lines.append(line)

class EndToEndTest(unittest.TestCase):
    def process_transactions(self, lines):
        filename = 'fake_file'
        fake_input = StringIO.StringIO('\n'.join(lines))
        file_parser = read_trace.TraceLogParser()
        events = []
        events = file_parser.parse(fake_input, filename=filename)
        trace_processor = wu_trace.TraceProcessor(filename)
        for idx, e in enumerate(events):
            trace_processor.handle_log_line(e, idx)
        return trace_processor.transactions

    def testMinimalGraphviz(self):
        log = """
1.001000000 TRACE WU START faddr FA0:8:0[VP] origin FA0:8:0[VP] dest FA0:8:0[VP] wuid 1 name fun_a arg0 1 arg1 2
1.00200000  TRACE TRANSACTION START faddr FA0:8:0[VP]
1.00300000 TRACE WU END faddr FA0:8:0[VP] wuid 1 name fun_a arg0 1 arg1 2
""".split('\n')
        transactions = self.process_transactions(log)

        # First, make sure we can run the graphviz code.
        outputFile = FakeFile()
        render.render_graphviz(outputFile, transactions)

        expected_output = ['strict digraph foo {\n',
                           'label="\\nbold: wu send\\ndot: timer"\n',
                           '}\n']

        self.assertEqual(expected_output, outputFile.lines)

    def testMinimalSend(self):
        log = """
1.00100 TRACE WU START faddr FA0:8:0[VP] origin FA0:8:0[VP] dest FA0:8:0[VP] wuid 1 name fun_a arg0 1 arg1 2
1.00200 TRACE TRANSACTION START faddr FA0:8:0[VP]
1.00300 TRACE WU SEND faddr FA0:8:0[VP] origin FA0:8:0[VP] dest FA0:8:0[VP] wuid 2 name bar arg0 2 arg1 3 flags 0 dest FA0:8:0[VP]
1.00300 TRACE WU END faddr FA0:8:0[VP] wuid 1 name fun_a arg0 1 arg1 2
1.00400 TRACE WU START faddr FA0:8:0[VP] origin FA0:8:0[VP] dest FA0:8:0[VP] wuid 2 name bar arg0 2 arg1 3
1.00500 TRACE WU END faddr FA0:8:0[VP] wuid 2 name bar arg0 2 arg1 3
""".split('\n')

        transactions = self.process_transactions(log)

        # First, make sure we can run the graphviz code.
        outputFile = FakeFile()
        render.render_graphviz(outputFile, transactions)

        expected_output = ['strict digraph foo {\n',
                           'fun_a -> bar [style=bold];\n',
                           'label="\\nbold: wu send\\ndot: timer"\n',
                           '}\n']

        self.assertEqual(expected_output, outputFile.lines)

    def testAnnotate(self):
        log = """
0.000001000 TRACE WU START faddr FA0:8:0[VP] origin FA0:8:0[VP] dest FA0:8:0[VP] wuid 0 name wu_foo arg0 0 arg1 0
0.000002000 TRACE TRANSACTION ANNOT faddr FA0:8:0[VP] msg Request to /movies/Star Wars
0.000003000 TRACE WU END faddr FA0:8:0[VP]
    """.split('\n')

        transactions = self.process_transactions(log)

        self.assertEqual(2, len(transactions))

        out_file = StringIO.StringIO()

        render.dump(out_file, transactions[1])

        contents = out_file.getvalue();
        self.assertIn('00.000002 (0 nsec): Request to /movies/Star Wars',
                      out_file.getvalue())

    def testMinimalTimer(self):
        # Run foo multiple times, triggered by a timer.
        log = """
0.000001000 TRACE WU START faddr FA0:8:0[VP] origin FA0:8:0[VP] dest FA0:8:0[VP] wuid 0 name foo arg0 0 arg1 0 origin FA:0:8:0[VP]
0.000002000 TRACE TIMER START faddr FA0:8:0[VP] timer 0x1 wuid 0x5 name timer_handler dest FA0:8:0[VP] arg0 1 wuid 0 name foo
0.000003000 TRACE WU END faddr FA0:8:0[VP] wuid 0 name foo arg0 0 arg1 0
0.000006000 TRACE WU START faddr FA0:8:0[VP] origin FA0:8:0[VP] dest FA0:8:0[VP] wuid 0 name foo arg0 0x1 arg1 0 origin FA0:8:0[VP]
0.000007000 TRACE TIMER START faddr FA0:8:0[VP] timer 0x1 value 0x1 arg0 0x2 wuid 0 dest FA0:8:0[VP] arg0 0x2 name foo
0.000008000 TRACE WU END faddr FA0:8:0[VP] wuid 0 name foo arg0 0x1 arg1 0
0.000011000 TRACE WU START faddr FA0:8:0[VP] origin FA0:8:0[VP] wuid 0 name foo arg0 0x2 arg1 0 origin FA0:8:0[VP]
0.000012000 TRACE TIMER START faddr FA0:8:0[VP] timer 0x1 value 0x1 arg0 0x3 dest FA0:8:0[VP] wuid 0 arg0 0x3 name foo
0.000013000 TRACE WU END faddr FA0:8:0[VP] wuid 0 name foo arg0 0x2 arg1 0
0.000014000 TRACE WU START faddr FA0:8:0[VP] origin FA0:8:0[VP] dest FA0:8:0[VP] wuid 0 name foo arg0 0x3 arg1 0
0.000015000 TRACE WU END faddr FA0:8:0[VP] wuid 0 name foo arg0 0x3 arg1 0

        """.split('\n')

        transactions = self.process_transactions(log)

        output_file = FakeFile()

        render.render_graphviz(output_file, transactions)

        # TODO(bowdidge): Check more than just length of output.
        self.assertIn('strict digraph foo {\n', output_file.lines)
        self.assertIn('foo -> {timer_foo [label="timer" style=dotted]};\n',
                      output_file.lines)
        self.assertIn('{timer_foo [label="timer"]} -> foo [style=bold];\n',
                      output_file.lines)
        self.assertIn('}\n', output_file.lines)


class TestRenderJSON(unittest.TestCase):
    def testIdsAreUnique(self):
        filename = 'testdata/lsv.trace'

        file_parser = read_trace.TraceLogParser()
        with open(filename, 'r') as fh:
            events = file_parser.parse(fh)
        trace_processor = wu_trace.TraceProcessor(filename)
        for idx, e in enumerate(events):
            trace_processor.handle_log_line(e, idx)
        transactions = trace_processor.transactions

        json_string = render.render_json(transactions)

        json_dict = json.loads(json_string)
        dict = {}

        for group in json_dict['groups']:
            self.assertTrue(group['id'] not in dict)
            dict[group['id']] = group

        # Transactions are in the same numbering space as groups.
        for transaction in group['transactions']:
            self.assertTrue(transaction['id'] not in dict)
            dict[group['id']] = transaction

if __name__ == '__main__':
  unittest.main()
