# event.py
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.

class TraceEvent:
  def __init__(self, start_time, end_time, label, vp):
      self.start_time = start_time
      self.end_time = end_time
      self.label = label
      self.vp = vp
      self.subevents = []
      self.parent = None
      # For timers, the timestamp for when the timer was scheduled.
      self.timerStart = None

  def Color(self):
      if self.label is None:
        return '#ffa0a0'
      if self.label == 'wuh_process_doorbell':
          return 'yellow'
      elif 'start' in self.label:
          return 'red'
      elif 'init' in self.label:
          return 'red'
      return '#ff8080'

  def Range(self):
      return (self.start_time, self.end_time)

  def Duration(self):
      return self.end_time - self.start_time

  def Span(self):
      """Returns overall time spent in this event and subevents."""
      (start, end) = self.Interval()
      return end - start

  def Interval(self):
      """Returns time range spent in this event and subevents."""
      last_end_time = self.end_time
      first_start_time = self.start_time
      for subevent in self.subevents:
          (start, end) = subevent.Interval()
          if end > last_end_time:
              last_end_time = end
          if start < first_start_time:
              first_start_time = start
      return (first_start_time, last_end_time)

  def Add(self, event):
    self.subevents.append(event)
    event.parent = self
    if event.label != 'timer trigger':
      self.end_time = event.end_time

  def LastEvent(self, event):
    if len(self.subevents) == 0:
      return None
    return self.subevents[len(self.subevents) - 1]

  def MoveUp(self, event):
      if self.parent.parent:
          self.subevents.remove(event)
          self.parent.parent.Add(event)
      else:
          self.subevents.remove(event)
          self.parent.Add(event)

  def __cmp__(self, other):
      return self.start_time.__cmp__(other.start_time)

  
  def __str__(self):
    subeventMsg =  ""
    if self.subevents is not None:
      subeventMsg = "%d subevents" % len(self.subevents)
    
    str = '<TraceEvent: %s - %s %s, %s>' % (self.start_time, self.end_time,
                                           self.label, 
                                           subeventMsg)
    return str

  def __repl__(self):
    subeventMsg =  ""
    if self.subevents is not None:
      subeventMsg = "%d subevents" % len(self.subevents)
    
    str = '<TraceEvent: %s - %s %s, %s>' % (self.start_time, self.end_time,
                                           self.label, 
                                           subeventMsg)
    return str


