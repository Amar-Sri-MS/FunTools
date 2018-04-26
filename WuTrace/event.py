# event.py
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.

import sys

class Transaction():
  """Container for a sequence of related WU events."""
  def __init__(self, root_event, label=None):
    # List of work units and other events done as part of the transaction.
    self.root_event = root_event

    if label is not None:
      self.label = label
    else:
      self.label = root_event.label

  def __str__(self):
    return '<Transaction: %s, root event %s>' % (
      self.label, self.root_event)

  def __repr__(self):
    return '<Transaction: %s, root event %s>' % (
      self.label, self.root_event)

  def AsDict(self):
    """Returns transaction as a dictionary of explicit values.

    The dictionary defines an API of values that templates can view,
    or that can be outputted as JSON.
    """
    all_events = [e.AsDict() for e in self.Flatten()]
    min_time = min([x['start_time'] for x in all_events if not x['is_timer']])
    max_time = max([x['end_time'] for x in all_events if not x['is_timer']])
    overall_duration = max_time - min_time

    # Limit bars to 98% of container so they don't trigger a new line.
    MAX_PCT = 98

    for event in all_events:
      offset_time = event['start_time'] - min_time
      # Offset from start of tration to current event.
      if max_time - min_time == 0:
        event['offset_pct'] = 0
        event['duration_pct'] = MAX_PCT
      else:
        event['offset_pct'] = MAX_PCT * offset_time / overall_duration
        event['duration_pct'] = MAX_PCT * event['duration'] / overall_duration

    return {
      'label': self.label,
      'start_time': self.StartTime(),
      'end_time': self.EndTime(),
      'duration_nsecs': self.Duration(),
      'events': all_events
      }

  def Label(self):
    """Returns human-readable label describing event."""
    return self.label

  def StartTime(self):
    """Time in nanosecondseconds since epoch when the first WU started."""
    # TODO(bowdidge): Stop recalculating this each time.
    if not self.root_event:
      return 0
    start = self.root_event.start_time
    for e in self.Flatten():
      if start > e.start_time:
        start = e.start_time
    return start

  def EndTime(self):
    """Time in nanoseconds since epoch when the last WU finished."""
    if not self.root_event:
      return 0
    end = self.root_event.end_time
    for e in self.Flatten():
      if e.is_timer:
        continue
      if end < e.end_time:
        end = e.end_time
    return end

  def Duration(self):
    """Number of nanoseconds elapsed during transaction."""
    return self.EndTime() - self.StartTime()

  def Remove(self, event):
    """Removes a specific WU event from a transaction."""
    if event == self.root_event:
      self.root_event = None
      return

    # walk through all elements 
    for e in self.Flatten():
      if event in e.successors:
        e.successors.remove(event)
        return

  def Flatten(self):
    """Returns all events in this transaction in a single list."""
    if self.root_event == None:
      return []
    result = []
    worklist = [self.root_event]
    while (len(worklist) > 0):
      first = worklist[0]
      worklist = worklist[1:]
      if first not in result:
        result.append(first)
        worklist += first.successors
    return sorted(result, key=lambda x: x.start_time)


class TraceEvent:
  """A work unit (WU) or other action that occurred during the trace,
  Trace events can also represent timer set/trigger pairs.
  """
  def __init__(self, start_time, end_time, label, vp, keywords):
    # When the event started.
    self.start_time = start_time

    # When the event ended.
    self.end_time = end_time

    # Text label to display when showing this event.
    self.label = label

    # Virtual processor where this event ran.
    # String of form FA[0-9]+.[0-9]+.[0-9]+.*
    # Ex: FA0:8:0[VP0.0], FA1:13:0[VP1.1].
    # 
    self.vp = vp

    # Transactions holding this event.
    self.transaction = None
  
    # True if this event represents a timer set and trigger.
    # For timers, the start_time represents the time when the timer was set,
    # and the end_time represents the time when the timer was triggered.
    self.is_timer = False

    self.is_annotation = False

    # Work units or events that were instigated by this event.
    self.successors = []

    # Raw key/value pairs from trace file.
    self.keywords = keywords

  def AsDict(self):
    return {'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.Duration(),
            'label': self.label,
            'vp': self.vp,
            # No transaction because it is an object.
            'is_timer': self.is_timer,
            'is_annotation': self.is_annotation
            }

  def Label(self):
    """Returns a human-readable string describing this event."""
    return self.label

  def Range(self):
    """Returns start and end time for this event alone."""
    return (self.start_time, self.end_time)

  def Duration(self):
    """Returns time spent only in this event in nanoseconds."""
    return self.end_time - self.start_time

  def __cmp__(self, other):
    if other is None:
      return 1
    return cmp((self.label, self.start_time, self.end_time), (other.label, other.start_time, other.end_time))

  def __str__(self):
    return '<TraceEvent: %s - %s %s>' % (self.start_time, self.end_time,
                                         self.label)

  def __repr__(self):
    return '<TraceEvent: %s - %s %s>' % (self.start_time, self.end_time,
                                             self.label)


