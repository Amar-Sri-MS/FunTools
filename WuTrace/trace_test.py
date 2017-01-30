#
# Unit tests for wu trace parsing.
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.
#

import sys
import unittest

import render
import wu_trace

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
    root_event = wu_trace.ParseFile(log, "foo.trace")

    self.assertIsNotNone(root_event)
    self.assertEqual(1, len(root_event.subevents))
    self.assertEqual(0, len(root_event.next_wus))

    event = root_event.subevents[0]
    self.assertEqual(100, event.Duration())
    self.assertEqual(1000100, event.start_time)
    self.assertEqual("my_wu", event.label)
    self.assertEqual(0, len(event.subevents))

  def testSendGroupsWithEvent(self):
    log = ["1.000100 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0x1 name my_wu arg0 1 arg1 2",
           "1.000050 faddr VP0.0.0 WU SEND src VP0.0.0 dest VP0.0.0 id 0x2 name sent_wu arg0 1 arg1 1",
           "1.000200 faddr VP0.0.0 WU END id 0x1 name my_wu arg0 1 arg1 2",
           "1.000300 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0x2 name sent_wu arg0 1 arg1 1",
           "1.004000 faddr VP0.0.0 WU END id 0x2 name sent_wu arg0 1 arg1 2"]
    root_event = wu_trace.ParseFile(log, "foo.trace")
    wu_trace.Dump(sys.stdout, root_event, 0)
    self.assertIsNotNone(root_event)

    self.assertEqual(1, len(root_event.subevents))
    my_wu = root_event.subevents[0]
    self.assertEqual(1, len(my_wu.next_wus))


  def testTriggerTimer(self):
    log = ["1.000100 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0x1 name my_wu arg0 1 arg1 2",
           "1.000050 faddr VP0.0.0 TIMER START timer 0x1 value 0x1 arg0 0x1",
           "1.000200 faddr VP0.0.0 WU END id 0x1 name my_wu arg0 1 arg1 2",
           "1.000250 faddr VP0.0.0 TIMER TRIGGER timer 0x1 arg0 0x2",
           "1.000300 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 0x2 name sent_wu arg0 0x2 arg1 0",
           "1.004000 faddr VP0.0.0 WU END id 0x2 name sent_wu arg0 1 arg1 2"]
    root_event = wu_trace.ParseFile(log, "foo.trace")

    self.assertIsNotNone(root_event)
    self.assertEqual(1, len(root_event.subevents))
    event = root_event.subevents[0]
    self.assertEqual(1, len(event.subevents))

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
    root_event = wu_trace.ParseFile(log, "foo.trace")
    wu_trace.Dump(sys.stdout, root_event, 0)

    self.assertIsNotNone(root_event)
    # TODO(bowdidge): Should separate next vs. subevent.
    self.assertEqual(1, len(root_event.subevents))
    event = root_event.subevents[0]
    self.assertEqual(1, len(event.subevents))

  def testTopLevelTransaction(self):
    log = ["1.00100 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 1 name fun_a arg0 1 arg1 2",
           "1.00200 faddr VP0.0.0 TRANSACTION START",
           "1.00300 faddr VP0.0.0 WU END id 1 name fun_a arg0 1 arg1 2"
           ]
    root_event = wu_trace.ParseFile(log, "foo.trace")
    wu_trace.Dump(sys.stdout, root_event, 0)
    self.assertIsNotNone(root_event)
    self.assertEqual(1, len(root_event.subevents))

  def testRecursionToIteration(self):
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
0.000015 faddr VP0.0.0 WU END id 0 name foo arg0 0x3 arg1 0
"""
      events = wu_trace.ParseFile(trace.split('\n'), "foo.trace")
      wu_trace.Dump(sys.stdout, events, 0)
      self.assertEqual(4, len(events.subevents))


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
    root_event = wu_trace.ParseFile(log, "foo.trace")
    # First, make sure we can run the graphviz code.
    outputFile = FakeFile()
    render.RenderGraphviz(outputFile, root_event)

    expected_output = ['strict digraph foo {\n',
                       'start -> fun_a;\n',
                       'label="\\nbold: wu send\\nsolid: wu call\\ndot: timer"\n',                       '}\n']

    self.assertEqual(expected_output, outputFile.lines)

  def testMinimalSend(self):
    log = ['1.00100 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 1 name fun_a arg0 1 arg1 2',
           '1.00200 faddr VP0.0.0 TRANSACTION START',
           '1.00300 faddr VP0.0.0 WU SEND src VP0.0.0 dest VP0.0.0 id 2 name bar arg0 2 arg1 3',
           '1.00300 faddr VP0.0.0 WU END id 1 name fun_a arg0 1 arg1 2',
           '1.00400 faddr VP0.0.0 WU START src VP0.0.0 dest VP0.0.0 id 2 name bar arg0 2 arg1 3',
           '1.00500 faddr VP0.0.0 WU END id 2 name bar arg0 2 arg1 3'
           ]
    root_event = wu_trace.ParseFile(log, "foo.trace")
    # First, make sure we can run the graphviz code.
    outputFile = FakeFile()
    render.RenderGraphviz(outputFile, root_event)

    expected_output = ['strict digraph foo {\n',
                       'start -> fun_a;\n',
                       'fun_a -> bar [style=bold];\n',
                       'label="\\nbold: wu send\\nsolid: wu call\\ndot: timer"\n',
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
    root_event = wu_trace.ParseFile(log, "foo.trace")
    output_file = FakeFile()

    render.RenderGraphviz(output_file, root_event)

    # TODO(bowdidge): Check more than just length of output.
    self.assertIn('strict digraph foo {\n', output_file.lines)
    self.assertIn('start -> foo;\n', output_file.lines)
    self.assertIn('foo -> foo_to_timer_to_foo -> foo [style=dotted]; \n', output_file.lines)
    self.assertIn('}\n', output_file.lines)

if __name__ == '__main__':
  unittest.main()
