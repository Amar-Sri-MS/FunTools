# event.py
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.

class TraceEvent:
  def __init__(self, start_time, end_time, label, vp):
      # Attributes of event.
      self.start_time = start_time
      self.end_time = end_time
      self.label = label
      self.vp = vp

      # Hierarchy.
      # All WUs explicitly sent from this WU.
      self.next_wus = []
      # All call and timer sequences sent from this WU.
      self.subevents = []
      self.parent = None
      # Whether this TraceEvent is the root of all traces.
      self.is_root = False
      
      self.is_timer = False
      # For timers, the timestamp for when the timer was scheduled.
      self.timerStart = None

  def Range(self):
      """Returns start and end time for this event alone."""
      return (self.start_time, self.end_time)

  def Duration(self):
      """Returns time spent only in this event."""
      return self.end_time - self.start_time

  def Span(self):
      """Returns overall time spent in this event and subevents."""
      (start, end) = self.Interval()
      return end - start

  def Interval(self):
      """Returns time range spent in this event and subevents."""
      last_end_time = self.end_time
      first_start_time = self.start_time
      for subevent in self.subevents + self.next_wus:
        (start, end) = subevent.Interval()
        if end > last_end_time:
            last_end_time = end
        if start < first_start_time:
            first_start_time = start
      return (first_start_time, last_end_time)

  def AddSubevent(self, event):
    self.subevents.append(event)
    event.parent = self

  def AddNext(self, event):
    self.next_wus.append(event)
    event.parent = self.parent

  def RemoveChild(self, event):
    """Removes an event which is either a successor or a child of this event."""
    if event in self.subevents:
      self.subevents.remove(event)
    elif event in self.next_wus:
      self.next_wus.remove(event)
    else:
      wus = self.next_wus
      while len(wus) > 0:
        wu = wus[0]
        if event in wu.next_wus:
          wu.next_wus.remove(event)
          return
        wus.remove(wu)

  def __cmp__(self, other):
      return self.start_time.__cmp__(other.start_time)

  
  def __str__(self):
    subeventMsg =  ''
    if self.subevents is not None:
      subeventMsg = '%d subevents' % len(self.subevents)
    
    str = '<TraceEvent: %s - %s %s, %s>' % (self.start_time, self.end_time,
                                           self.label, 
                                           subeventMsg)
    return str

  def __repl__(self):
    subeventMsg =  ''
    if self.subevents is not None:
      subeventMsg = '%d subevents' % len(self.subevents)
    
    str = '<TraceEvent: %s - %s %s, %s>' % (self.start_time, self.end_time,
                                           self.label, 
                                           subeventMsg)
    return str


