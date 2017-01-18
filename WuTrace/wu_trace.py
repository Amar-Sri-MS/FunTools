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
# "name value", and should have no separators other than spaces.
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

def Dump(output_file, group, indent):
  """Returns a text dump for a set of trace events."""
  indentSpaces = " " * indent
  output_file.write("%s + %s (%s) (%s): %s\n" % (indentSpaces,
                                                 render.RangeString(group.start_time, group.end_time),
                                                 render.DurationString(group.Duration()),
                                                 render.DurationString(group.Span()),group.label))

  for subevent in sorted(group.subevents):
    Dump(output_file, subevent, indent + 2)
        
def ParseLogLine(line, file, line_number):
  """Parses a single log line from --wulog, or returns None if not a log line or if invalid."""
  values = {}
  match = re.match('([0-9]+).([0-9]+) faddr (VP[0-9].[0-9].[0-9]) ([A-Z]+) ([A-Z]+) ', line)
  if not match:
    return None

  values = {"timestamp": int(match.group(1)) * 1000000 + int(match.group(2)),
            "vp": match.group(3),
            "verb": match.group(4),
            "noun": match.group(5)
            }
  remaining_string = line[len(match.group(0)):]

  token_iter = iter(remaining_string.split(' '))

  pairs = [(a, next(token_iter)) for a in token_iter]

  for (key, value) in pairs:
    values[key] = value

  expect_keywords = []

  if values["verb"] == "WU" and values["noun"] == "START":
    # Should define src, dest, id, name, arg0, arg1.
    expect_keywords = ['src', 'dest', 'id', 'name', 'arg0', 'arg1']

  elif values["verb"] == "WU" and values["noun"] == "END":
    # should define id, name, arg0, arg1.
    expect_keywords = ['id', 'name', 'arg0', 'arg1']

  elif values["verb"] == "WU" and values["noun"] == "CALL":
    # should define id, name, arg0, arg1.
    expect_keywords = ['id', 'name', 'arg0', 'arg1']

  elif values["verb"] == "WU" and values["noun"] == "SEND":
    # Should define src, dest, id, name, arg0, arg1.
    expect_keywords = ['src', 'dest', 'id', 'name', 'arg0', 'arg1']

  elif values["verb"] == "TIMER" and values["noun"] == "TRIGGER":
    # Should define timer and arg0.
    expect_keywords = ['timer', 'arg0']

  elif values["verb"] == "TIMER" and values["noun"] == "START":
    # Should define timer, value, and arg0.
    expect_keywords = ['timer', 'value', 'arg0']
    pass
  else:
    sys.stderr.write('%s:%d: unknown verb or noun: %s %s', (file, line_number, values["verb"], values["noun"]))
    return None

  for expected_keyword in expect_keywords:
    if expected_keyword not in values:
      sys.stderr.write('%s:%d: missing key %s', (file, line_number, expected_keyword))
      return None

  int_keywords = ["id", "arg0", "arg1"]
  for keyword in int_keywords:
    if keyword in values:
      string_value = values[keyword]
      if string_value.startswith('0x'):
        values[keyword] = int(string_value, 16)
      else:
        try:
          values[keyword] = int(string_value)
        except ValueError as e:
          sys.stderr.write('%s:%d: malformed integer %s for key %s\n' % (file, line_number, string_value, keyword))
    
      
  return values


class TraceParser:
  def __init__(self, input_file):
    # Map from frame pointer to the containing group of events.
    self.frame_to_group = {}
    # Map from timer id to group
    self.timer_to_group = {}
    self.timer_to_start_time = {}
    # Maps VP to the currently running WU on that VP.
    self.vp_to_event = {}
    self.input_file = input_file
    
    self.root_event = event.TraceEvent(999999999999999999, 0, "top", "-")

  def HandleLogLine(self, log_keywords, line_number):
    """Reads in each logging event, and creates or updates any log events."""
    timestamp = log_keywords['timestamp']
    vp = log_keywords['vp']

    if self.root_event.start_time > timestamp:
      self.root_event.start_time = timestamp

    if self.root_event.end_time < timestamp:
      self.root_event.end_time = timestamp


    if log_keywords['verb'] == 'WU' and log_keywords['noun'] == 'START':
      # Identify the request (or timer action) that this WU is part of.
      
      arg0 = log_keywords['arg0']
      arg1 = log_keywords['arg1']
      if arg0 in self.frame_to_group:
        group = self.frame_to_group[arg0]
        del self.frame_to_group[arg0]
      elif arg1 in self.frame_to_group:
        group = self.frame_to_group[arg1]
        del self.frame_to_group[arg1]
      else:
        group = self.root_event
          
      current_event = event.TraceEvent(timestamp, timestamp, log_keywords['name'], vp)
      self.vp_to_event[vp] = current_event

      group.Add(current_event)
        
    elif log_keywords['verb'] == 'WU' and log_keywords['noun'] == 'END':
      # Identify the matching start event, and set the end time.
      if vp not in self.vp_to_event:
        print("%s:%d: unexpected end" % (input_file, line_number))
        return

      current_event = self.vp_to_event[vp]
      del self.vp_to_event[vp]

      if current_event is None:
        print("Line %d: unknown end" % line_number)
        return

      current_event.end_time = timestamp
      if current_event.parent.end_time < timestamp:
        current_event.parent.end_time = timestamp

    elif log_keywords['verb'] == 'WU' and log_keywords['noun'] == 'SEND':
      # Use arg0, the flow pointer, to match up the send with the WU when it starts.

      arg0 = log_keywords['arg0']

      current_event = None

      if vp in self.vp_to_event:
        current_event = self.vp_to_event[vp]
      elif arg0 in self.frame_to_group:
        # Send from timer_trigger.
        current_event = self.frame_to_group[arg0]
      else:
        sys.stderr.write('%s:%d: Send from unknown WU.\n' % (self.input_file, line_number))
        return

      if current_event.label == 'wuh_bootstrap' or current_event.label == 'timer trigger':
        # WUs triggered by wuh_bootstrap count as sub-objects of wuh_bootstrap.
        self.frame_to_group[arg0] = current_event
      else:
        self.frame_to_group[arg0] = current_event.parent
      
      currentGroup = self.frame_to_group[arg0]

      # Recognize iteration via a recursive timer, and flatten out.
      if current_event.parent.label == log_keywords['name'] and current_event.label == 'timer trigger':
        current_event.parent.MoveUp(current_event)
        self.frame_to_group[arg0] = current_event

    elif log_keywords['verb'] == 'WU' and log_keywords['noun'] == 'CALL':
      # Use arg1, the flow pointer, to match up the CALL with the WU that runs.
      arg1 = log_keywords['arg1']

      if vp not in self.vp_to_event:
        sys.stderr.write("%s:%s: unknown vp in send\n" % (self.input_file, line_number, line_number))
        return

      current_event = self.vp_to_event[vp]
      if current_event is None:
        sys.stderr.write("%s:%d: unsure what WU triggered send.\n" % (self.input_file, line_number))
        return

      self.frame_to_group[arg1] = current_event.parent

    elif log_keywords['verb'] == 'HU' and log_keywords['noun'] == 'SQ_DBL':
      # Create new standalone event.
      arg0 = log_keywords['arg0']

      current_event = event.TraceEvent(timestamp, timestamp, "Doorbell", "-")
      # TODO(bowdidge): Fix.
      currentGroup.Add(current_event)

    elif log_keywords['verb'] == 'TIMER' and log_keywords['noun'] == 'START':
      # Use arg0 to remember which WU starts as a result of this timer.
      arg0 = log_keywords['arg0']
      timer = log_keywords['timer']

      if vp not in self.vp_to_event:
        sys.stderr.write("%s:%d: unknown vp in send\n" % (self.input_file, line_number))
        return

      current_event = self.vp_to_event[vp]
      if current_event is None:
        sys.stderr.write("%s:%d: unsure what WU started timer." % (self.input_file, line_number))
        return
      self.timer_to_group[timer] = current_event
      self.timer_to_start_time[timer] = timestamp
  
    elif log_keywords['verb'] == 'TIMER' and log_keywords['noun'] == 'TRIGGER':
      arg0 = log_keywords['arg0']
      timer = log_keywords['timer']

      group = self.timer_to_group[timer]
      current_event = event.TraceEvent(timestamp, timestamp, "timer trigger", vp)
      current_event.timerStart = int(self.timer_to_start_time[timer])
      group.Add(current_event)

      self.frame_to_group[arg0] = current_event
      del self.timer_to_group[timer]

    else:
      sys.stderr.write('%s:%d: Invalid verb/noun %s %s' % (input_file, line_number,
                                                           log_keywords['verb'], log_keywords['noun']))
      return


def ParseFile(lines, input_filename):
  trace_parser = TraceParser(input_filename)
  line_number = 0
  for line in lines:
    line_number += 1
    if DEBUG:
      sys.stderr.write('line %d\n' % line_number)
    log_keywords = ParseLogLine(line, input_filename, line_number)
    if not log_keywords:
      continue
    trace_parser.HandleLogLine(log_keywords, line_number)
    
  return trace_parser.root_event

def main(argv):
  global DEBUG
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument('inputs', metavar='file', type=str, nargs='+',
                      help='log files to read')
  arg_parser.add_argument('--output_text', action='store_const', const=True, help="output events rather than HTML")
  arg_parser.add_argument('--output', nargs=1, help="file name to write to")
  arg_parser.add_argument('--debug', action='store_const', const=True, help="add debugging output")
  args = arg_parser.parse_args()

  input_filename = args.inputs[0]
  if args.debug:
    DEBUG = True

  traceEvents = ParseFile(open(input_filename), input_filename)

  if args.output_text:
    Dump(sys.stdout, traceEvents, 0)
  else:
    render.RenderHTML(sys.stdout, traceEvents)

if __name__ == '__main__':
    main(sys.argv[1:])
