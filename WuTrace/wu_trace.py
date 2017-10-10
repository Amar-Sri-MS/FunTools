#!/usr/bin/python
#
# Converts output from funos-posix's --wulog option into a graphical
# form to show the order and timing of work units.
#
# Usage:
# wutrace.py inputfile [-o outputfile]
#
# Input can be a mix of arbitrary log messages and the wulog messages.
#
# All wu event messages are expected to start with:
#
# 9999999.999999 faddr VP9.9.9 VERB NOUN ...
#
# where the initial number is the number of seconds and microseconds
# since epoch, and the VP... is the fabric address of the unit sending
# the log message.  Verb, for now, is either WU, TIMER, or HU.  For
# WUs, VERB un can be START, END, or SEND.  For timers, VERB must
# be START.  Remaining arguments are always of the form
# 'name value', and should have no separators other than spaces.
#
# Log messages get combined into sequences of WUs, representing all the
# work done on behalf of an incoming request.  Sometimes, a single item
# in the sequence can trigger some sub-tasks, such as timers triggering
# a separate sequence of requests.
#
# TODO(bowdidge): Consider when a WU send represents a call or suboperation,
# and when it represents the next operation.
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.
#


import argparse
import re
import sys

import event
import render

DEBUG = False

def ParseLogLine(line, file, line_number):
  """Parses a single log line from --wulog.
  Returns a tuple of (dictionary of key-value pairs, error) where
  error is None if parsing was successful, and the dictionary is not None
  if the line represented a WU log entry.
  """
  line = line.lstrip().rstrip()
  values = {}
  match = re.match('([0-9]+).([0-9]+) TRACE ([A-Z_]+) ([A-Z_]+)', line)
  if not match:
    # Not a log line, but not an error either.
    return (None, None)

  time_nsec = int(match.group(1)) * 1000000000 + int(match.group(2))
  values = {'timestamp': time_nsec / 1000,
            'verb': match.group(3),
            'noun': match.group(4)
            }
  remaining_string = line[len(match.group(0)):].lstrip()

  if len(remaining_string) == 0:
    return (values, None)

  # Annotation is special - we need to find the faddr at the
  # beginning, but the rest counts as the message.
  if values['verb'] == 'TRANSACTION' and values['noun'] == 'ANNOT':
    annot_match = re.match('faddr (VP[0-9]+.[0-9]+.[0-9]+) (.*)',
                           remaining_string)
    if not annot_match:
      error = '%s:%d: malformed transaction annotation: "%s"\n' % (
        file, line_number, line)
      return (None, error)

    values['faddr'] = annot_match.group(1)
    values['msg'] = annot_match.group(2)
  else:
    token_iter = iter(remaining_string.split(' '))

    try:
      pairs = [(a, next(token_iter)) for a in token_iter]
    except StopIteration as e:
      error = '%s:%d: malformed log line: "%s"\n' % (
        file, line_number, line)
      return (None, error)

    for (key, value) in pairs:
      values[key] = value

  expect_keywords = []

  event_type = (values['verb'], values['noun'])
  
  if event_type == ('WU', 'START'):
    # Should define src, dest, id, name, arg0, arg1.
    expect_keywords = ['faddr', 'wuid', 'name', 'arg0', 'arg1']

  elif event_type == ('WU', 'END'):
    # should define id, name, arg0, arg1.
    expect_keywords = ['faddr']

  elif event_type == ('WU', 'SEND'):
    # Should define src, dest, id, name, arg0, arg1.
    expect_keywords = ['faddr', 'wuid', 'name', 'arg0', 'arg1', 'dest']

  elif event_type == ('TIMER', 'TRIGGER'):
    # Should define timer and arg0.
    expect_keywords = ['faddr', 'timer', 'arg0']

  elif event_type == ('TIMER', 'START'):
    expect_keywords = ['faddr', 'timer', 'wuid', 'name', 'dest', 'arg0']

  elif event_type == ('TRANSACTION', 'START'):
    expect_keywords = ['faddr']

  elif event_type == ('TRANSACTION', 'ANNOT'):
    # Annotate uses rest of line as message.
    expect_keywords = ['faddr']

  elif event_type == ('HU', 'SQ_DBL'):
    expect_keywords = ['sqid']

  else:
    error = '%s:%d: unknown verb or noun: %s %s\n' % (file, line_number, values['verb'], values['noun'])
    return (None, error)

  for expected_keyword in expect_keywords:
    if expected_keyword not in values:
      error = '%s:%d: missing key "%s" in command %s %s\n' % (
        file, line_number, expected_keyword,
        values['verb'], values['noun'])
      return (None, error)

  int_keywords = ['wuid', 'arg0', 'arg1', 'sqid']
  for keyword in int_keywords:
    if keyword in values:
      string_value = values[keyword]
      if string_value.startswith('0x'):
        try:
          values[keyword] = int(string_value, 16)
        except ValueError as e:
          error = '%s:%d: malformed hex value "%s" for key %s\n' % (
          file, line_number, string_value, keyword)
          return (None, error)

      else:
        try:
          values[keyword] = int(string_value)
        except ValueError as e:
          error = '%s:%d: malformed integer "%s" for key %s\n' % (
            file, line_number, string_value, keyword)
          return (None, error)


  return (values, None)


class TraceParser:
  """Converts event start/stop messages into sequences of events grouped by transaction."""

  def __init__(self, input_filename):
    # Map of VPs to sent WUs that have not yet started.
    # Mapped items are tuples of (sender event, called wu, called arg0,
    # called arg1).
    self.caller_queues = {}

    # Map from timer id to the event setting the timer.
    self.timer_to_caller = {}


    # Map from timer id to the time the timer was set.  For setting start_time for event.
    self.timer_to_start_time = {}

    # Map from VP to the currently running WU on that VP.
    self.vp_to_event = {}

    # String name of the file which is being read.
    self.input_filename = input_filename

    boot_event =  event.TraceEvent(0, 0, 'boot', None, [])
    self.boot_transaction = event.Transaction(boot_event)
    self.transactions = [self.boot_transaction]

  def RememberSend(self, event, wu_id, arg0, arg1, dest, is_timer):
    """Records the WU send event for later matching with a start."""
    if dest not in self.caller_queues:
      self.caller_queues[dest] = []
    self.caller_queues[dest].append((event, wu_id, arg0, arg1, is_timer))

  def FindPreviousSend(self, wu_id, arg0, arg1, dest):
    """Returns the WU send that would have started a WU with the arguments,
    """
    if dest not in self.caller_queues:
      return (None, False)
    if len(self.caller_queues[dest]) == 0:
      return (None, False)
    for entry in self.caller_queues[dest]:
      (sender, sent_wu_id, sent_arg0, sent_arg1, is_timer) = entry
      if (sent_wu_id == wu_id and sent_arg0 == arg0 and
          sent_arg1 == arg1):
        self.caller_queues[dest].remove(entry)
        return (sender, is_timer)
    return (None, False)

  def HandleLogLine(self, log_keywords, line_number):
    """Reads in each logging event, and creates or updates any log events."""
    event_type = (log_keywords['verb'], log_keywords['noun'])

    if event_type == ('FLUSH', 'FLUSH'):
      return

    timestamp = log_keywords['timestamp']

    vp = log_keywords['faddr']

    if event_type == ('WU', 'START'):
      arg0 = log_keywords['arg0']
      arg1 = log_keywords['arg1']

      current_event = event.TraceEvent(timestamp, timestamp,
                                       log_keywords['name'], vp, log_keywords)
      self.vp_to_event[vp] = current_event

      (predecessor, is_timer) = self.FindPreviousSend(log_keywords['wuid'],
                                                      arg0, arg1, vp)
      if predecessor:
        current_event.transaction = predecessor.transaction
        current_event.is_timer = is_timer
        predecessor.successors.append(current_event)

      elif log_keywords['name'] == 'wuh_mp_notify':
        # Bootstrap process. Connect to fake event.
        current_event.transaction = self.boot_transaction
        self.boot_transaction.root_event.successors.append(current_event)
        if self.boot_transaction.root_event.start_time is None:
          self.boot_transaction.root_event.start_time = timestamp
          self.boot_transaction.root_event.end_time = timestamp

      else:
        # New event not initiated by a previous WU.
        transaction = event.Transaction(current_event)
        self.transactions.append(transaction)
        current_event.transaction = transaction

    elif event_type == ('WU', 'END'):
      # Identify the matching start event, and set the end time.
      if vp not in self.vp_to_event:
        sys.stderr.write('%s:%d: unexpected end\n' % (self.input_filename, line_number))
        return

      current_event = self.vp_to_event[vp]
      del self.vp_to_event[vp]

      if current_event is None:
        sys.stderr.write('Line %d: unknown end\n' % line_number)
        return
      current_event.end_time = timestamp
    elif event_type == ('WU', 'SEND'):
      # Use arg0, the flow pointer, to match up the send with the WU when it starts.
      wu_id = log_keywords['wuid']
      arg0 = log_keywords['arg0']
      arg1 = log_keywords['arg1']

      curr = None
      if vp in self.vp_to_event:
        curr = self.vp_to_event[vp]
        self.RememberSend(curr, wu_id, arg0, arg1, log_keywords['dest'],
                          False)

    elif event_type == ('HU', 'SQ_DBL'):
      label = 'HU doorbell: sqid=%d' % log_keywords['sqid']
      current_event = event.TraceEvent(timestamp, timestamp,
                                       "HU doorbell: sqid=%d" % log_keywords['sqid'],
                                       vp,
                                       log_keywords)

      transaction = event.Transaction(current_event)
      self.transactions.append(transaction)
      current_event.transaction = transaction

    elif event_type == ('TIMER', 'START'):
      wuid = log_keywords['wuid']
      timer = log_keywords['timer']
      arg0 = log_keywords['arg0']
      if vp not in self.vp_to_event:
        sys.stderr.write('%s:%d: unknown vp in TIMER START\n' % (self.input_filename, line_number))
        return

      current_event = self.vp_to_event[vp]
      if current_event is None:
        sys.stderr.write('%s:%d: unsure what WU started timer.\n' % (self.input_filename, line_number))

      self.RememberSend(current_event, wuid, arg0, 0, log_keywords['dest'],
                        True)

    elif event_type == ('TRANSACTION', 'START'):
       if vp not in self.vp_to_event:
         sys.stderr.write('%s:%d: TRANSACTION START does not match running WU on %s' % (
             self.input_filename, line_number, vp))
         return
       current_event = self.vp_to_event[vp]

       if current_event.transaction:
         current_event.transaction.Remove(current_event)
       new_transaction = event.Transaction(current_event)
       current_event.transaction = new_transaction
       self.transactions.append(new_transaction)

    elif event_type == ('TRANSACTION', 'ANNOT'):
       if vp not in self.vp_to_event:
         sys.stderr.write('%s:%d: TRANSACTION START does not match running WU on %s' % (
             self.input_filename, line_number, vp))
         return
       current_event = self.vp_to_event[vp]
       annot_event = event.TraceEvent(timestamp, timestamp,
                                      log_keywords['msg'],
                                      vp, log_keywords)
       annot_event.is_annotation = True
       current_event.successors.append(annot_event)
       
    else:
      sys.stderr.write('%s:%d: Invalid verb/noun %s %s\n' % (
          self.input_filename, line_number, log_keywords['verb'],
          log_keywords['noun']))
      return


def ParseFile(lines, input_filename):
  trace_parser = TraceParser(input_filename)

  line_number = 0
  for line in lines:
    line_number += 1
    if DEBUG:
      sys.stderr.write('line %d\n' % line_number)
    (log_keywords, error) = ParseLogLine(line, input_filename, line_number)
    if error:
      sys.stderr.write(error)
    if not log_keywords:
      continue
    trace_parser.HandleLogLine(log_keywords, line_number)

  return trace_parser.transactions

def main(argv):
  global DEBUG
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument('inputs', metavar='file', type=str, nargs='+',
                      help='log files to read')
  arg_parser.add_argument(
    '--format', type=str,
    help='output style: html (default), text, or graphviz.', default=None)
  arg_parser.add_argument('--output', nargs=1, help='file name to write to')
  arg_parser.add_argument('--debug', action='store_const', const=True,
                          help='add debugging output')
  args = arg_parser.parse_args()

  input_filename = args.inputs[0]
  if args.debug:
    DEBUG = True

  if args.format is not None:
    if args.format not in ['text', 'html', 'graphviz']:
      sys.stderr.write(
        'Unknown option %s to --format.  Must be text, html, graphviz.\n')
      exit(1)

  transactions = ParseFile(open(input_filename), input_filename)

  out_file = sys.stdout
  if args.output is not None:
    out_file = open(args.output[0], 'w')

  # Hack: Update start and end time on fake event on boot.
  boot_events = transactions[0].Flatten()

  # transactions[0].root_event.start_time = min({e.start_time for e in boot_events if e.start_time != 0})
  # transactions[0].root_event.end_time = min({e.end_time for e in boot_events if e.end_time != 0})

  if args.format == 'text':
    for tr in transactions:
      render.Dump(out_file, tr)
      print('\n')
  elif args.format == 'graphviz':
    render.RenderGraphviz(out_file, transactions)
  elif args.format is None or args.format == 'html':
    render.RenderHTML(out_file, transactions)
  out_file.close()


if __name__ == '__main__':
    main(sys.argv[1:])
