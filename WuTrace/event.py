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

  def Label(self):
    """Returns human-readable label describing event."""
    return self.label

  def StartTime(self):
    """Time in microseconds since epoch when the first WU started."""
    # TODO(bowdidge): Stop recalculating this each time.
    if not self.root_event:
      return 0
    start = self.root_event.start_time
    for e in self.Flatten():
      if start > e.start_time:
        start = e.start_time
    return start

  def EndTime(self):
    """Time in microseconds since epoch when the last WU finished."""
    if not self.root_event:
      return 0
    end = self.root_event.end_time
    for e in self.Flatten():
      if end < e.end_time:
        end = e.end_time
    return end

  def Duration(self):
    """Number of microseconds elapsed during transaction."""
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
  def __init__(self, start_time, end_time, label, vp):
    # When the event started.
    self.start_time = start_time

    # When the event ended.
    self.end_time = end_time

    # Text label to display when showing this event.
    self.label = label

    # Virtual processor where this event ran.
    # String of form VP.[0-9]+.[0-9]+.[0-9]+
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

  def Label(self):
    """Returns a human-readable string describing this event."""
    return self.label

  def Range(self):
    """Returns start and end time for this event alone."""
    return (self.start_time, self.end_time)

  def Duration(self):
    """Returns time spent only in this event."""
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


