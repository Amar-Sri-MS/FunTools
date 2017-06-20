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
# WUs, VERB un can be START, END, SEND, or CALL.  For timers, VERB can
# be START or TRIGGER.  Remaining arguments are always of the form
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
  values = {}
  match = re.match('([0-9]+).([0-9]+) faddr (VP[0-9]+.[0-9]+.[0-9]+) ([A-Z_]+) ([A-Z_]+)', line)
  if not match:
    # Not a log line, but not an error either.
    return (None, None)

  values = {'timestamp': int(match.group(1)) * 1000000 + int(match.group(2)),
            'vp': match.group(3),
            'verb': match.group(4),
            'noun': match.group(5)
            }
  remaining_string = line[len(match.group(0)):].lstrip()

  if len(remaining_string) == 0:
    return (values, None)

  if values['verb'] == 'TRANSACTION' and values['noun'] == 'ANNOT':
    values['msg'] = remaining_string
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
    expect_keywords = ['src', 'dest', 'id', 'name', 'arg0', 'arg1']

  elif event_type == ('WU', 'END'):
    # should define id, name, arg0, arg1.
    expect_keywords = ['id', 'name', 'arg0', 'arg1']

  elif event_type == ('WU', 'CALL'):
    # should define id, name, arg0, arg1.
    expect_keywords = ['id', 'name', 'arg0', 'arg1']

  elif event_type == ('WU', 'SEND'):
    # Should define src, dest, id, name, arg0, arg1.
    expect_keywords = ['src', 'dest', 'id', 'name', 'arg0', 'arg1']

  elif event_type == ('TIMER', 'TRIGGER'):
    # Should define timer and arg0.
    expect_keywords = ['timer', 'arg0']

  elif event_type == ('TIMER', 'START'):
    # Should define timer, value, and arg0.
    expect_keywords = ['timer', 'value', 'arg0']

  elif event_type == ('TRANSACTION', 'START'):
    expect_keywords = []

  elif event_type == ('TRANSACTION', 'ANNOT'):
    # Annotate uses rest of line as message.
    expect_keywords = [ ]

  elif event_type == ('HU', 'SQ_DBL'):
    expect_keywords = ['sqid']

  else:
    error = '%s:%d: unknown verb or noun: %s %s\n' % (file, line_number, values['verb'], values['noun'])
    return (None, error)

  for expected_keyword in expect_keywords:
    if expected_keyword not in values:
      error = '%s:%d: missing key "%s"\n' % (file, line_number, expected_keyword)
      return (None, error)

  int_keywords = ['id', 'arg0', 'arg1', 'sqid']
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
    # Map from (arg0, arg1) from a WU send to the event that triggered the send.
    self.frame_to_caller = {}

    # Map from timer id to the event setting the timer.
    self.timer_to_caller = {}

    # Map from timer id to the time the timer was set.  For setting start_time for event.
    self.timer_to_start_time = {}

    # Map from VP to the currently running WU on that VP.
    self.vp_to_event = {}

    # String name of the file which is being read.
    self.input_filename = input_filename

    boot_event =  event.TraceEvent(0, 0, 'boot', None)
    self.boot_transaction = event.Transaction(boot_event)
    self.transactions = [self.boot_transaction]

  def HandleLogLine(self, log_keywords, line_number):
    """Reads in each logging event, and creates or updates any log events."""
    timestamp = log_keywords['timestamp']
    vp = log_keywords['vp']

    event_type = (log_keywords['verb'], log_keywords['noun'])
    if event_type == ('WU', 'START'):
      arg0 = log_keywords['arg0']
      arg1 = log_keywords['arg1']

      current_event = event.TraceEvent(timestamp, timestamp, log_keywords['name'], vp)
      self.vp_to_event[vp] = current_event

      if (arg0, arg1) in self.frame_to_caller:
        # Regular send.  Connect to caller.
        predecessor = self.frame_to_caller[(arg0, arg1)]
        current_event.transaction = predecessor.transaction
        predecessor.successors.append(current_event)
        del self.frame_to_caller[(arg0, arg1)]

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
      arg0 = log_keywords['arg0']
      arg1 = log_keywords['arg1']

      curr = None
      if vp in self.vp_to_event:
        curr = self.vp_to_event[vp]
        self.frame_to_caller[(arg0, arg1)] = curr

    elif event_type == ('WU', 'CALL'):
      # Ignore.  Calls don't say anything about control flow; knowing whether something is
      # a continuation is a better signal for part of transaction vs. sub-part.
      pass

    elif event_type == ('HU', 'SQ_DBL'):
      label = 'HU doorbell: sqid=%d' % log_keywords['sqid']
      current_event = event.TraceEvent(timestamp, timestamp,
                                       "HU doorbell: sqid=%d" % log_keywords['sqid'],
                                       vp)
      transaction = event.Transaction(current_event)
      self.transactions.append(transaction)
      current_event.transaction = transaction

    elif event_type == ('TIMER', 'START'):
      arg0 = log_keywords['arg0']
      timer = log_keywords['timer']
      if vp not in self.vp_to_event:
        sys.stderr.write('%s:%d: unknown vp in send\n' % (self.input_filename, line_number))
        return

      current_event = self.vp_to_event[vp]
      if current_event is None:
        sys.stderr.write('%s:%d: unsure what WU started timer.\n' % (self.input_filename, line_number))
        return
      self.timer_to_caller[timer] = current_event
      self.timer_to_start_time[timer] = timestamp

    elif event_type == ('TIMER', 'TRIGGER'):
      arg0 = log_keywords['arg0']
      timer = log_keywords['timer']

      if timer not in self.timer_to_caller:
        sys.stderr.write('%s:%d: unknown timer id %s\n' % (
            self.input_filename, line_number, timer))
        return

      prev = self.timer_to_caller[timer]
      current_event = event.TraceEvent(timestamp, timestamp, 'timer_trigger', vp)
      current_event.is_timer = True
      current_event.transaction = prev.transaction
      current_event.timer_start = int(self.timer_to_start_time[timer])
      prev.successors.append(current_event)
      # TODO(bowdidge): True?
      self.vp_to_event[vp] = current_event

      self.frame_to_caller[(arg0, 0)] = current_event
      del self.timer_to_caller[timer]

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
                                      vp)
       current_event.successors.append(annot_event)
       
    else:
      sys.stderr.write('%s:%d: Invalid verb/noun %s %s\n' % (input_filename, line_number,
                                                           log_keywords['verb'], log_keywords['noun']))
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
  transactions[0].root_event.start_time = min({e.start_time for e in boot_events if e.start_time != 0})
  transactions[0].root_event.end_time = min({e.end_time for e in boot_events if e.end_time != 0})

  if args.format == 'text':
    for tr in transactions:
      render.Dump(out_file, tr, 0)
      print('\n')
  elif args.format == 'graphviz':
    render.RenderGraphviz(out_file, transactions)
  elif args.format is None or args.format == 'html':
    render.RenderHTML(out_file, transactions)
  out_file.close()


if __name__ == '__main__':
    main(sys.argv[1:])
