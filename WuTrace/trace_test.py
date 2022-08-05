#
# Unit tests for wu trace parsing.
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.
#

import json
import sys
import unittest

import render
from io import StringIO
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
        line = '123123123.567890000 TRACE WU START faddr FA8:12:0[CCV8.1.0] wuid 0x1 name foo arg0 1 arg1 2 origin FA8:12:0[CCV8.1.0]'
        (line_args, error) = self.file_parser.parse_line(line)

        self.assertIsNone(error)
        self.assertEqual(123123123567890000, line_args['timestamp'])
        self.assertEqual('FA8:12:0[VP]', line_args['faddr'].as_faddr_str())
        self.assertEqual('WU', line_args['verb'])
        self.assertEqual('START', line_args['noun'])
        self.assertEqual(1, line_args['arg0'])
        self.assertEqual(2, line_args['arg1'])


    def testParseTransactionStart(self):
        line = '1.000001000 TRACE TRANSACTION START faddr FA8:12:0[CCV8.1.0]'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNotNone(line_args)
        self.assertIsNone(error)

        line = '0.000006000 TRACE TRANSACTION START faddr FA8:12:0[CCV8.1.0]\n'
        line_args = self.file_parser.parse_line(line)
        self.assertIsNotNone(line_args)
        self.assertIsNone(error)

    def testParseAnnotation(self):
        line = '0.024206656 TRACE TRANSACTION ANNOT faddr FA0:16:0[CCV0.2.0] msg Start unit test timer_test_microseconds'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNotNone(line_args)
        self.assertIsNone(error)

    def testParseAnnotation(self):
        line = '0.024206656 TRACE TRANSACTION ANNOT faddr FA1:31:0[CCV1.5.3] msg Start unit test timer_test_microseconds'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNotNone(line_args)
        self.assertIsNone(error)

    def testBadVerb(self):
        # Colon after send is invalid.
        line = '485375410.764454000 TRACE WU SEND: faddr FA1:31:0[CCV1.5.3] wuid 0x60 name wuh_mp_notify arg0 0x0 arg1 0x0 dest FA1:31:0[CCV1.5.3]'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNone(line_args)
        self.assertIn('malformed log line', error)

    def testUnknownVerb(self):
        # Comma after VP is unexpected.
        line = '485375410.764454000 TRACE FOO BAR faddr FA8:12:0[CCV8.1.0] dest FA8:12:0[CCV8.1.0], wuid 0x60 name wuh_mp_notify arg0 0x0 arg1 0x0'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNone(line_args)
        self.assertIn('unknown verb or noun', error)

    def testMissingKey(self):
        # Remove src.
        line = '485375410.764454000 TRACE WU START faddr FA8:12:0[CCV8.1.0] wuid 0x60 name wuh_mp_notify arg1 0x0 origin FA8:12:0[CCV8.1.0]'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNone(line_args)
        self.assertIn('missing key "arg0"', error)

    # def testMalformedNumber(self):
        # gg is not valid hex.
        line = '485375410.764454000 TRACE WU SEND faddr FA8:12:0[CCV8.1.0] wuid 0xgg name wuh_mp_notify arg0 0x0 arg1 0x0 dest FA8:12:0[CCV8.1.0] flags 0'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNone(line_args)
        self.assertIn('invalid literal for int() with base 16', error)

    def testMalformedHexNumber(self):
        # 1A is not valid decimal value.
        line = '485375410.764454000 TRACE WU SEND faddr FA0:17:0[CCV0.2.1] wuid 1A name wuh_mp_notify arg0 0x0 arg1 0x0 flags 0 dest FA0:17:0[CCV0.2.1]'
        (line_args, error) = self.file_parser.parse_line(line)
        self.assertIsNone(line_args)
        self.assertIn('invalid literal for int() with base 10', error)

    # TODO(bowdidge): Remove.  Sorting now.
    def disableTestTimeGoesBackwards(self):
        """Test that we correctly remember the last timestamp seen."""
        line1 = '123123123.567890000 TRACE WU START faddr FA0:17:0[CCV0.2.1] wuid 0x1 name foo arg0 1 arg1 2'

        line2 = '123123123.467890000 TRACE WU START faddr FA0:17:0[CCV0.2.1] wuid 0x1 name foo arg0 1 arg1 2'

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
        fake_input = StringIO('\n'.join(lines))
        file_parser = read_trace.TraceLogParser()
        events = []
        events = file_parser.parse(fake_input, filename=filename)
        trace_processor = wu_trace.TraceProcessor(filename)
        for idx, e in enumerate(events):
            trace_processor.handle_log_line(e, idx)
        return trace_processor.transactions


    def testStartEnd(self):
        log = ['1.000100000 TRACE WU START faddr FA0:17:0[CCV0.2.1] wuid 0x1 name my_wu arg0 1 arg1 2 origin FA0:17:0[CCV0.2.1]',
               '1.000200000 TRACE WU END faddr FA0:17:0[CCV0.2.1]']
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
1.000100000 TRACE WU START faddr FA7:30:0[CCV7.5.2] wuid 0x1 name my_wu arg0 1 arg1 2 origin FA7:30:0[CCV7.5.2]
1.000150000 TRACE WU SEND faddr FA7:30:0[CCV7.5.2] wuid 0x2 name sent_wu arg0 1 arg1 1 flags 0 dest FA6:29:0[CCV6.5.1]
1.000200000 TRACE WU END faddr FA7:30:0[CCV7.5.2] wuid 0x1 name my_wu arg0 1 arg1 2
1.000300000 TRACE WU START faddr FA6:29:0[CCV6.5.1] wuid 0x2 name sent_wu arg0 1 arg1 1 origin FA6:29:0[CCV6.5.1]
1.0004000000 TRACE WU END faddr FA6:29:0[CCV6.5.1]
""".split('\n')
        transactions = self.process_transactions(log)
        tr = first_transaction(transactions)
        render.dump_transactions(sys.stdout, transactions)
        self.assertIsNotNone(tr)

        self.assertEqual(1, len(tr.root_event.successors))


    def testTriggerTimer(self):
        log = """
1.000100000 TRACE WU START faddr FA8:12:0[CCV8.1.0] wuid 0x1 name my_wu arg0 1 arg1 2 origin FA8:12:0[CCV8.1.0]
1.000150000 TRACE TIMER START faddr FA8:12:0[CCV8.1.0] timer 0x1 wuid 0x2 name sent_wu dest FA8:12:0[CCV8.1.0] arg0 0x2
1.000200000 TRACE WU END faddr FA8:12:0[CCV8.1.0]
1.000300000 TRACE WU START faddr FA8:12:0[CCV8.1.0] wuid 0x2 name sent_wu arg0 0x2 arg1 0 origin FA8:12:0[CCV8.1.0]
1.0004000 faddr000 TRACE WU END FA8:12:0[CCV8.1.0]
""".split('\n')
        transactions = self.process_transactions(log)
        print(transactions)
        self.assertIsNotNone(transactions)

        self.assertEqual(2, len(transactions))
        tr = first_transaction(transactions)

        self.assertEqual(1, len(tr.root_event.successors))

    def testTopLevelTransaction(self):
        log = """
1.00100000 TRACE WU START faddr FA8:12:0[CCV8.1.0] wuid 1 name fun_a arg0 1 arg1 2 origin FA8:12:0[CCV8.1.0]
1.00200000 TRACE TRANSACTION START faddr FA8:12:0[CCV8.1.0]
1.00300000 TRACE WU END faddr FA8:12:0[CCV8.1.0] wuid 1 name fun_a arg0 1 arg1 2
""".split('\n')
        transactions = self.process_transactions(log)

        # One transaction for boot, one for the created transaction.
        self.assertEqual(2, len(transactions))

        tr = transactions[1]
        self.assertIsNotNone(tr.root_event)
        self.assertEqual(0, len(tr.root_event.successors))

    def testChainOfTransactions(self):
        log = """
0.000001000 TRACE WU START faddr FA8:12:0[CCV8.1.0] wuid 0 name foo arg0 0 arg1 0 origin FA8:12:0[CCV8.1.0]
0.000002000 TRACE TIMER START faddr FA8:12:0[CCV8.1.0] timer 0x1 wuid 0x9 name bar arg0 0x1 dest FA8:12:0[CCV8.1.0]
0.000003000 TRACE WU END faddr FA8:12:0[CCV8.1.0]
0.000006000 TRACE WU START faddr FA8:12:0[CCV8.1.0] wuid 0x9 name bar arg0 0x1 arg1 0 origin FA8:12:0[CCV8.1.0]
0.000006000 TRACE TRANSACTION START faddr FA8:12:0[CCV8.1.0]
0.000007000 TRACE TIMER START faddr FA8:12:0[CCV8.1.0] timer 0x1 wuid 17 name baz arg0 0x2 dest FA8:12:0[CCV8.1.0]
0.000008000 TRACE WU END faddr FA8:12:0[CCV8.1.0]
0.000011000 TRACE WU START faddr FA8:12:0[CCV8.1.0] origin FA8:12:0[CCV8.1.0] wuid 17 name baz arg0 0x2 arg1 0 origin FA8:12:0[CCV8.1.0]
0.000011000 TRACE TRANSACTION START faddr FA8:12:0[CCV8.1.0]
0.000012000 TRACE TIMER START faddr FA8:12:0[CCV8.1.0] timer 0x1 wuid 19 name boof arg0 0x3 dest FA8:12:0[CCV8.1.0]
0.000013000 TRACE WU END faddr FA8:12:0[CCV8.1.0]
0.000014000 TRACE WU START faddr FA8:12:0[CCV8.1.0] origin FA8:12:0[CCV8.1.0] wuid 19 name boof arg0 0x3 arg1 0 origin FA8:12:0[CCV8.1.0]
0.000015000 TRACE TRANSACTION START faddr FA8:12:0[CCV8.1.0]
0.000016000 TRACE WU END faddr FA8:12:0[CCV8.1.0]
""".split('\n')

        transactions = self.process_transactions(log)
        output_file = FakeFile()
        render.dump_transactions(output_file, transactions)

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

    def testHighPriorityQueue(self):
        """Test that a high priority WU SEND is connected to the correct VP."""
        log = """
0.000001000 TRACE WU START faddr FA8:12:0[CCV8.1.0] wuid 0 name foo arg0 0 arg1 0 origin FA8:12:0[CCV8.1.0]
0.000002000 TRACE WU SEND faddr FA8:12:0[CCV8.1.0] dest FA8:12:0[CCV8.1.0] wuid 2 name bar arg0 2 arg1 3 flags 0
0.000003000 TRACE WU END faddr FA8:12:0[CCV8.1.0]
0.000004000 TRACE WU START faddr FA8:12:0[CCV8.1.0] wuid 2 name bar arg0 2 arg1 3 origin FA8:12:0[CCV8.1.0]
0.000005000 TRACE WU END faddr FA8:12:0[CCV8.1.0]
""".split('\n')
        transactions = self.process_transactions(log)
        output_file = FakeFile()
        render.dump_transactions(output_file, transactions)
        expected = [
            '00.000000 - 00.000000 (0 nsec): transaction "boot"\n',
            '+ 00.000000 - 00.000000 (0 nsec): boot\n',
            '00.000001 - 00.000005 (4.0 usec): transaction "foo"\n',
            '+ 00.000001 - 00.000003 (2.0 usec): foo\n',
            '+ 00.000004 - 00.000005 (1.0 usec): bar\n']

        self.assertEqual(expected, output_file.lines)


class FakeFile:
    def __init__(self):
        self.lines = []

    def write(self, line):
        self.lines.append(line)

class EndToEndTest(unittest.TestCase):
    def process_transactions(self, lines):
        filename = 'fake_file'
        fake_input = StringIO('\n'.join(lines))
        file_parser = read_trace.TraceLogParser()
        events = []
        events = file_parser.parse(fake_input, filename=filename)
        trace_processor = wu_trace.TraceProcessor(filename)
        for idx, e in enumerate(events):
            trace_processor.handle_log_line(e, idx)
        return trace_processor.transactions

    def testMinimalGraphviz(self):
        log = """
1.001000000 TRACE WU START faddr FA8:12:0[CCV8.1.0] origin FA8:12:0[CCV8.1.0] dest FA8:12:0[CCV8.1.0] wuid 1 name fun_a arg0 1 arg1 2
1.00200000  TRACE TRANSACTION START faddr FA8:12:0[CCV8.1.0]
1.00300000 TRACE WU END faddr FA8:12:0[CCV8.1.0] wuid 1 name fun_a arg0 1 arg1 2
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
1.00100 TRACE WU START faddr FA8:12:0[CCV8.1.0] origin FA8:12:0[CCV8.1.0] dest FA8:12:0[CCV8.1.0] wuid 1 name fun_a arg0 1 arg1 2
1.00200 TRACE TRANSACTION START faddr FA8:12:0[CCV8.1.0]
1.00300 TRACE WU SEND faddr FA8:12:0[CCV8.1.0] origin FA8:12:0[CCV8.1.0] dest FA8:12:0[CCV8.1.0] wuid 2 name bar arg0 2 arg1 3 flags 0 dest FA8:12:0[CCV8.1.0]
1.00300 TRACE WU END faddr FA8:12:0[CCV8.1.0] wuid 1 name fun_a arg0 1 arg1 2
1.00400 TRACE WU START faddr FA8:12:0[CCV8.1.0] origin FA8:12:0[CCV8.1.0] dest FA8:12:0[CCV8.1.0] wuid 2 name bar arg0 2 arg1 3
1.00500 TRACE WU END faddr FA8:12:0[CCV8.1.0] wuid 2 name bar arg0 2 arg1 3
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
0.000001000 TRACE WU START faddr FA8:12:0[CCV8.1.0] origin FA8:12:0[CCV8.1.0] dest FA8:12:0[CCV8.1.0] wuid 0 name wu_foo arg0 0 arg1 0
0.000002000 TRACE TRANSACTION ANNOT faddr FA8:12:0[CCV8.1.0] msg Request to /movies/Star Wars
0.000003000 TRACE WU END faddr FA8:12:0[CCV8.1.0]
    """.split('\n')

        transactions = self.process_transactions(log)

        self.assertEqual(2, len(transactions))

        out_file = StringIO()

        render.dump(out_file, transactions[1])

        contents = out_file.getvalue();
        self.assertIn('00.000002 (0 nsec): Request to /movies/Star Wars',
                      out_file.getvalue())

    def testMinimalTimer(self):
        # Run foo multiple times, triggered by a timer.
        log = """
0.000001000 TRACE WU START faddr FA8:12:0[CCV8.1.0] origin FA8:12:0[CCV8.1.0] dest FA8:12:0[CCV8.1.0] wuid 0 name foo arg0 0 arg1 0 origin FA8:12:0[CCV8.1.0]
0.000002000 TRACE TIMER START faddr FA8:12:0[CCV8.1.0] timer 0x1 wuid 0x5 name timer_handler dest FA8:12:0[CCV8.1.0] arg0 1 wuid 0 name foo
0.000003000 TRACE WU END faddr FA8:12:0[CCV8.1.0] wuid 0 name foo arg0 0 arg1 0
0.000006000 TRACE WU START faddr FA8:12:0[CCV8.1.0] origin FA8:12:0[CCV8.1.0] dest FA8:12:0[CCV8.1.0] wuid 0 name foo arg0 0x1 arg1 0 origin FA8:12:0[CCV8.1.0]
0.000007000 TRACE TIMER START faddr FA8:12:0[CCV8.1.0] timer 0x1 value 0x1 arg0 0x2 wuid 0 dest FA8:12:0[CCV8.1.0] arg0 0x2 name foo
0.000008000 TRACE WU END faddr FA8:12:0[CCV8.1.0] wuid 0 name foo arg0 0x1 arg1 0
0.000011000 TRACE WU START faddr FA8:12:0[CCV8.1.0] origin FA8:12:0[CCV8.1.0] wuid 0 name foo arg0 0x2 arg1 0 origin FA8:12:0[CCV8.1.0]
0.000012000 TRACE TIMER START faddr FA8:12:0[CCV8.1.0] timer 0x1 value 0x1 arg0 0x3 dest FA8:12:0[CCV8.1.0] wuid 0 arg0 0x3 name foo
0.000013000 TRACE WU END faddr FA8:12:0[CCV8.1.0] wuid 0 name foo arg0 0x2 arg1 0
0.000014000 TRACE WU START faddr FA8:12:0[CCV8.1.0] origin FA8:12:0[CCV8.1.0] dest FA8:12:0[CCV8.1.0] wuid 0 name foo arg0 0x3 arg1 0
0.000015000 TRACE WU END faddr FA8:12:0[CCV8.1.0] wuid 0 name foo arg0 0x3 arg1 0

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

    def testTransactionMerging(self):
        log = """88.515109248 TRACE WU START faddr FA0:16:0[CCV0.2.0] wuid 0x12ea name hw_le_null origin FA0:16:0[CCV0.2.0] arg0 0xc000000013c76406 arg1 0xc000800125b85f00
88.515112768 TRACE WU SEND faddr FA0:16:0[CCV0.2.0] wuid 0 name wuh_idle arg0 0x10012ed00000000 arg1 0xc000000013c76478 flags 1 dest FA7:5:0[LE]
88.515113152 TRACE WU END faddr FA0:16:0[CCV0.2.0]
88.515113792 TRACE WU START faddr FA0:16:0[CCV0.2.0] wuid 0x140 name group__LE_BASIC_TEST_GROUP0 origin FA7:5:0[LE] arg0 0 arg1 0
88.515115520 TRACE WU END faddr FA0:16:0[CCV0.2.0]"""

        f1 = open("test_file.txt", 'w') # creating a file for the test
        f1.write(log)
        f1.close()
        with open("test_file.txt", "r") as f1:
            trace_parser = read_trace.TraceLogParser()
            events = trace_parser.parse(f1, filename="test_file.txt")

        trace_parser = wu_trace.TraceProcessor("test_file.txt")
        for idx, e in enumerate(events):
            trace_parser.handle_log_line(e, idx)
        transactions = trace_parser.transactions
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[1].root_event.label, "hw_le_null")
        worklist = [transactions[1].root_event]
        self.assertEqual(len(worklist[0].successors), 1)
        self.assertEqual(worklist[0].successors[0].label, "HW-LE: wuh_idle")
        self.assertEqual(len(worklist[0].successors[0].successors), 1)
        self.assertEqual(worklist[0].successors[0].successors[0].label, "group__LE_BASIC_TEST_GROUP0")
        os.remove("test_file.txt") # removing the file now

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
