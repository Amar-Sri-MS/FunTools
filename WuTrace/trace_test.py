#
# Unit tests for wu trace parsing.
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.
#

import sys
import unittest

import render
import wu_trace

def firstTransaction(transactions):
  """Returns the first transaction parsed, or None if no transaction was parsed.
  The transactions list reserves the 0th transaction for the bootstrap code, so
  transactions[1] would be the first transaction.
  """
  if len(transactions) < 2:
    return None
  return transactions[1]

class TestParser(unittest.TestCase):

  def testNotALogLine(self):
    self.assertEqual((None, None), wu_trace.ParseLogLine("foo", "filename", 1))
    self.assertEqual((None, None),
                      wu_trace.ParseLogLine("1000.001000", "filename", 1))

  def testSimpleParse(self):
    line = "123123123.567890 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0x1 name foo arg0 1 arg1 2"
    (line_args, error) = wu_trace.ParseLogLine(line, "filename", 1)

    self.assertIsNone(error)

    self.assertEqual(123123123567890, line_args["timestamp"])
    self.assertEqual("VP0.0.0", line_args["vp"])
    self.assertEqual("WU", line_args["verb"])
    self.assertEqual("START", line_args["noun"])
    self.assertEqual("VP0.0.0", line_args["src"])
    self.assertEqual(1, line_args["arg0"])
    self.assertEqual(2, line_args["arg1"])


  def testParseTransactionStart(self):
    line = '1.000001 faddr VP0.0.0 TRANSACTION START'
    (line_args, error) = wu_trace.ParseLogLine(line, 'filename', 1)
    self.assertIsNotNone(line_args)
    self.assertIsNone(error)

    line = '0.000006 faddr VP0.0.0 TRANSACTION START\n'
    line_args = wu_trace.ParseLogLine(line, 'filename', 1)
    self.assertIsNotNone(line_args)
    self.assertIsNone(error)

  def testBadVerb(self):
    # Colon after send is invalid.
    line = '485375410.764454 faddr VP0.2.0 WU SEND: src VP0.2.0 dest VP0.0.0 id 0x60 name wuh_mp_notify arg0 0x0 arg1 0x0'
    (line_args, error) = wu_trace.ParseLogLine(line, 'filename', 1)
    self.assertIsNone(line_args)
    self.assertIn('malformed log line', error)

  def testUnknownVerb(self):
    # Comma after VP is unexpected.
    line = '485375410.764454 faddr VP0.2.0 FOO BAR src VP0.2.0, dest VP0.0.0, id 0x60 name wuh_mp_notify arg0 0x0 arg1 0x0'
    (line_args, error) = wu_trace.ParseLogLine(line, 'filename', 1)
    self.assertIsNone(line_args)
    self.assertIn('unknown verb or noun', error)

  def testMissingKey(self):
    # Remove src.
    line = '485375410.764454 faddr VP0.2.0 WU SEND dest VP0.0.0, id 0x60 name wuh_mp_notify arg0 0x0 arg1 0x0'
    (line_args, error) = wu_trace.ParseLogLine(line, 'filename', 1)
    self.assertIsNone(line_args)
    self.assertIn('missing key "src"', error)

  def testMalformedNumber(self):
    # gg is not valid hex.
    line = '485375410.764454 faddr VP0.2.0 WU SEND src VP0.0.0 dest VP0.0.0, id 0xgg name wuh_mp_notify arg0 0x0 arg1 0x0'
    (line_args, error) = wu_trace.ParseLogLine(line, 'filename', 1)
    self.assertIsNone(line_args)
    self.assertIn('malformed hex value "0xgg"', error)

  def testMalformedNumber(self):
    # 1A is not valid decimal value.
    line = '485375410.764454 faddr VP0.2.0 WU SEND src VP0.0.0 dest VP0.0.0, id 1A name wuh_mp_notify arg0 0x0 arg1 0x0'
    (line_args, error) = wu_trace.ParseLogLine(line, 'filename', 1)
    self.assertIsNone(line_args)
    self.assertIn('malformed integer "1A"', error)

  def testStartEnd(self):
    log = ["1.000100 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0x1 name my_wu arg0 1 arg1 2",
           "1.000200 faddr VP0.0.0 WU END id 0x1 name my_wu arg0 1 arg1 2"]
    transactions = wu_trace.ParseFile(log, "foo.trace")

    self.assertIsNotNone(transactions)
    tr = firstTransaction(transactions)
    self.assertIsNotNone(tr)
    self.assertEqual(1, len(tr.Flatten()))

    self.assertEqual(100, tr.root_event.Duration())
    self.assertEqual(1000100, tr.root_event.start_time)
    self.assertEqual("my_wu", tr.root_event.label)
    self.assertEqual(0, len(tr.root_event.successors))

  def testSendGroupsWithEvent(self):
    log = ["1.000100 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0x1 name my_wu arg0 1 arg1 2",
           "1.000050 faddr VP0.0.0 WU SEND src VP0.0.0 dest VP0.0.0 id 0x2 name sent_wu arg0 1 arg1 1",
           "1.000200 faddr VP0.0.0 WU END id 0x1 name my_wu arg0 1 arg1 2",
           "1.000300 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0x2 name sent_wu arg0 1 arg1 1",
           "1.004000 faddr VP0.0.0 WU END id 0x2 name sent_wu arg0 1 arg1 2"]
    transactions = wu_trace.ParseFile(log, "foo.trace")
    tr = firstTransaction(transactions)
    render.DumpTransactions(sys.stdout, transactions)
    self.assertIsNotNone(tr)

    self.assertEqual(1, len(tr.root_event.successors))


  def testTriggerTimer(self):
    log = ["1.000100 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0x1 name my_wu arg0 1 arg1 2",
           "1.000050 faddr VP0.0.0 TIMER START timer 0x1 value 0x1 arg0 0x1",
           "1.000200 faddr VP0.0.0 WU END id 0x1 name my_wu arg0 1 arg1 2",
           "1.000250 faddr VP0.0.0 TIMER TRIGGER timer 0x1 arg0 0x2",
           "1.000300 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0x2 name sent_wu arg0 0x2 arg1 0",
           "1.004000 faddr VP0.0.0 WU END id 0x2 name sent_wu arg0 1 arg1 2"]
    transactions = wu_trace.ParseFile(log, "foo.trace")

    self.assertIsNotNone(transactions)
    self.assertEqual(2, len(transactions))
    tr = firstTransaction(transactions)

    self.assertEqual(1, len(tr.root_event.successors))

  def testCall(self):
    log = ["1.000100 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0x1 name fun_a arg0 1 arg1 2",
           "1.000060 faddr VP0.0.0 WU SEND src VP0.0.0 dest VP0.0.0 id 0x2 name fun_a_a arg0 10 arg1 11",
           "1.000070 faddr VP0.0.0 WU CALL id 0x2 name fun_a_a arg0 10 arg1 11",
           "1.000200 faddr VP0.0.0 WU END id 0x1 name fun_arg0 arg0 1 arg1 2",
           "1.000300 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0x2 name fun_a_a arg0 10 arg1 11",
           "1.000350 faddr VP0.0.0 WU SEND src VP0.0.0 dest VP0.0.0 id 0x3 name fun_a_b arg0 12 arg1 13",
           "1.004000 faddr VP0.0.0 WU END id 0x2 name fun_a_a arg0 1 arg1 2",
           "1.000300 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0x3 name fun_a_b arg0 12 arg1 13",
           "1.004000 faddr VP0.0.0 WU END id 0x3 name fun_a_b arg0 1 arg1 2"]
    transactions = wu_trace.ParseFile(log, "foo.trace")

    tr = firstTransaction(transactions)
    self.assertIsNotNone(tr)
    self.assertEqual(1, len(tr.root_event.successors))

  def testTopLevelTransaction(self):
    log = ["1.00100 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 1 name fun_a arg0 1 arg1 2",
           "1.00200 faddr VP0.0.0 TRANSACTION START",
           "1.00300 faddr VP0.0.0 WU END id 1 name fun_a arg0 1 arg1 2"
           ]
    transactions = wu_trace.ParseFile(log, "foo.trace")
    self.assertEqual(3, len(transactions))

    tr = transactions[2]
    self.assertIsNotNone(tr.root_event)
    self.assertEqual(0, len(tr.root_event.successors))

  def testChainOfTransactions(self):
      trace = """
0.000001 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0 name foo arg0 0 arg1 0
0.000002 faddr VP0.0.0 TIMER START timer 0x1 value 0x1 arg0 0x1
0.000003 faddr VP0.0.0 WU END id 0 name foo arg0 0 arg1 0
0.000004 faddr VP0.0.0 TIMER TRIGGER timer 0x1 arg0 0x1
0.000005 faddr VP0.0.0 WU SEND src VP0.0.0 dest VP0.0.0 id 0x0 name foo arg0 1 arg1 0
0.000006 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0 name foo arg0 0x1 arg1 0
0.000006 faddr VP0.0.0 TRANSACTION START
0.000007 faddr VP0.0.0 TIMER START timer 0x1 value 0x1 arg0 0x2
0.000008 faddr VP0.0.0 WU END id 0 name foo arg0 0x1 arg1 0
0.000009 faddr VP0.0.0 TIMER TRIGGER timer 0x1 arg0 0x2
0.000010 faddr VP0.0.0 WU SEND src VP0.0.0 dest VP0.0.0 id 0x0 name foo arg0 2 arg1 0
0.000011 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0 name foo arg0 0x2 arg1 0
0.000011 faddr VP0.0.0 TRANSACTION START
0.000012 faddr VP0.0.0 TIMER START timer 0x1 value 0x1 arg0 0x3
0.000013 faddr VP0.0.0 WU END id 0 name foo arg0 0x2 arg1 0
0.000014 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0 name foo arg0 0x3 arg1 0
0.000015 faddr VP0.0.0 TRANSACTION START
0.000016 faddr VP0.0.0 WU END id 0 name foo arg0 0x3 arg1 0
"""
      
      transactions = wu_trace.ParseFile(trace.split('\n'), "foo.trace")
      output_file = FakeFile()
      render.DumpTransactions(output_file, transactions)
      print(output_file.lines)
      expected = ['00.000000 - 00.000000 (0 usec): transaction "boot"\n',
                  '+ 00.000000 - 00.000000 (0 usec): boot\n',
                  '00.000001 - 00.000004 (3 usec): transaction "foo"\n',
                  '+ 00.000001 - 00.000003 (2 usec): foo\n',
                  '+ 00.000004 - 00.000004 (0 usec): timer_trigger\n',
                  '00.000006 - 00.000009 (3 usec): transaction "foo"\n',
                  '+ 00.000006 - 00.000008 (2 usec): foo\n',
                  '+ 00.000009 - 00.000009 (0 usec): timer_trigger\n',
                  '00.000011 - 00.000013 (2 usec): transaction "foo"\n',
                  '+ 00.000011 - 00.000013 (2 usec): foo\n',
                  '00.000000 - 00.000000 (0 usec): transaction "foo"\n',
                  '00.000014 - 00.000016 (2 usec): transaction "foo"\n',
                  '+ 00.000014 - 00.000016 (2 usec): foo\n']

      self.assertEqual(expected, output_file.lines)


class FakeFile:
  def __init__(self):
    self.lines = []

  def write(self, line):
    self.lines.append(line)

class EndToEndTest(unittest.TestCase):

  def testMinimalGraphviz(self):
    log = ['1.00100 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 1 name fun_a arg0 1 arg1 2',
           '1.00200 faddr VP0.0.0 TRANSACTION START',
           '1.00300 faddr VP0.0.0 WU END id 1 name fun_a arg0 1 arg1 2'
           ]
    transactions = wu_trace.ParseFile(log, "foo.trace")
    # First, make sure we can run the graphviz code.
    outputFile = FakeFile()
    render.RenderGraphviz(outputFile, transactions)

    expected_output = ['strict digraph foo {\n',
                       'label="\\nbold: wu send\\ndot: timer"\n',                       '}\n']

    self.assertEqual(expected_output, outputFile.lines)

  def testMinimalSend(self):
    log = ['1.00100 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 1 name fun_a arg0 1 arg1 2',
           '1.00200 faddr VP0.0.0 TRANSACTION START',
           '1.00300 faddr VP0.0.0 WU SEND src VP0.0.0 dest VP0.0.0 id 2 name bar arg0 2 arg1 3',
           '1.00300 faddr VP0.0.0 WU END id 1 name fun_a arg0 1 arg1 2',
           '1.00400 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 2 name bar arg0 2 arg1 3',
           '1.00500 faddr VP0.0.0 WU END id 2 name bar arg0 2 arg1 3'
           ]
    transactions = wu_trace.ParseFile(log, "foo.trace")
    # First, make sure we can run the graphviz code.
    outputFile = FakeFile()
    render.RenderGraphviz(outputFile, transactions)

    expected_output = ['strict digraph foo {\n',
                       'fun_a -> bar [style=bold];\n',
                       'label="\\nbold: wu send\\ndot: timer"\n',
                       '}\n']
    
    self.assertEqual(expected_output, outputFile.lines)

  def testMinimalTimer(self):
    # Run foo multiple times, triggered by a timer.
    log = """
0.000001 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0 name foo arg0 0 arg1 0
0.000002 faddr VP0.0.0 TIMER START timer 0x1 value 0x1 arg0 0x1
0.000003 faddr VP0.0.0 WU END id 0 name foo arg0 0 arg1 0
0.000004 faddr VP0.0.0 TIMER TRIGGER timer 0x1 arg0 0x1
0.000005 faddr VP0.0.0 WU SEND src VP0.0.0 dest VP0.0.0 id 0x0 name foo arg0 1 arg1 0
0.000006 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0 name foo arg0 0x1 arg1 0
0.000007 faddr VP0.0.0 TIMER START timer 0x1 value 0x1 arg0 0x2
0.000008 faddr VP0.0.0 WU END id 0 name foo arg0 0x1 arg1 0
0.000009 faddr VP0.0.0 TIMER TRIGGER timer 0x1 arg0 0x2
0.000010 faddr VP0.0.0 WU SEND src VP0.0.0 dest VP0.0.0 id 0x0 name foo arg0 2 arg1 0
0.000011 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0 name foo arg0 0x2 arg1 0
0.000012 faddr VP0.0.0 TIMER START timer 0x1 value 0x1 arg0 0x3
0.000013 faddr VP0.0.0 WU END id 0 name foo arg0 0x2 arg1 0
0.000014 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0 name foo arg0 0x3 arg1 0
0.000015 faddr VP0.0.0 WU END id 0 name foo arg0 0x3 arg1 0

    """.split('\n')
    transactions = wu_trace.ParseFile(log, "foo.trace")
    output_file = FakeFile()

    render.RenderGraphviz(output_file, transactions)

    # TODO(bowdidge): Check more than just length of output.
    self.assertIn('strict digraph foo {\n', output_file.lines)
    self.assertIn('foo -> {timer_trigger_foo [label="timer_trigger" '
                  + 'style=dotted]};\n', output_file.lines)
    self.assertIn('}\n', output_file.lines)

if __name__ == '__main__':
  unittest.main()
