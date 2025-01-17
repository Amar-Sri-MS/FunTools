# event.py
#
# Objects representing events that happened as part of a WU trace.
#
# There are two levels of events in WU tracing:
#
# * the raw events collected by FunOS: start of a WU, end of a WU, send, etc.
#   Code in read_trace.py reads various log files, and produces sequences
#   of these events.
#
# * the activities performed.  The raw events are used to identify
#   specific WUs (TraceEvent) and combination of TraceEvents for a single
#   request or action (Transaction).
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.

import re
import sys

# Defines for F1.  These all are borrowed from FunOS/nucleus/faddr.h.
# First and last GID for processing and central clusters.
GID_PC_BASE = 0
GID_PC_MAX = 8

# First and last GID for Host Units.
GID_HU_BASE = 16
GID_HU_MAX = 19

# First and last GID for Network Units.
GID_NU_BASE = 9
GID_NU_MAX = 11

GID_UNKNOWN = 31

# First LID for VPs in the cluster.  Two LIDs exist
LID_VP_BASE = 8

# Names of blocks and accelerators inside clusters.
pc_lid_table = ['CA', 'UA', 'BAM', 'DMA', 'RGX', 'LE', 'ZIP', 'WQM']
# Other valid values for block.
major_blocks = ['VP', 'HU', 'NU']
#HU block with numerical value
HU_block = 'HU[0-9]'

TOPO_MAX_VPS_PER_CORE = 4


class FabricAddress(object):
    """Representation of a F1 fabric address.

    This includes both the location and the queue.
    """
    def __init__(self):
        """Creates a new fabric address from canonical string."""
        self.raw_value = 0
        # For non-NU blocks.
        # Cluster/group.  NU is 9..11, HU is 16..19, HNU is 20..21.
        # Always 5 bits.
        self.gid = 0
        # Local id - hardware block or core/VP.  VPs start at 8.
        # For HU and NU, lid is always 0.
        # For VPs, lid is 5 bits.
        self.lid = 0
        # Queue.  For VPs, 1 = high priority queue.
        # For HU, queue is 11 bits.  For NU, queue is 14 bits.
        # For VPS, queue is 8 bits.
        self.queue = 0

    def __eq__(self, other):
        """Returns true if self and other are the same fabric address."""
        if other is None:
            return False

        return (self.gid == other.gid and self.lid == other.lid and
                self.queue == other.queue)

    def __hash__(self):
        return hash((self.gid, self.lid, self.queue))

    @classmethod
    def from_ordinal(cls, src_id):
        """Create fabric address from index of VP. """
        if src_id > ((GID_PC_MAX + 1) * 6 * 4):
            raise ValueError('Out of range src: 0%d' % src_id)

        cluster = src_id // 24
        core_vp = (src_id % 24)

        faddr = FabricAddress()
        faddr.gid = cluster
        faddr.lid = core_vp + LID_VP_BASE
        return faddr

    @classmethod
    def from_faddr(cls, faddr_int):
        """Create FabricAddress from integer value of faddr.

        Returns None if an invalid value.
        """
        if faddr_int & 0xfff00000 != 0:
            # fabric address only uses 20 bits.
            raise ValueError('FabricAddress out of range: 0x%06x, expected less than 0xfffff' % faddr_int)

        faddr = FabricAddress()
        faddr.raw_value = faddr_int

        faddr.gid = (faddr_int >> 15) & 0x1f
        if faddr.gid >= GID_HU_BASE and faddr.gid <= GID_HU_MAX:
            faddr.lid = 0
            faddr.queue = (faddr_int >> 2) & 0x7ff

        elif faddr.gid >= GID_NU_BASE and faddr.gid <= GID_NU_MAX:
            faddr.lid = 0
            faddr.queue = (faddr_int >> 1) & 0x3fff

        elif faddr.gid >= GID_PC_BASE and faddr.gid <= GID_PC_MAX:
            faddr.lid = (faddr_int >> 10) & 0x1f
            faddr.queue = (faddr_int >> 2) & 0xff

        elif faddr.gid == GID_UNKNOWN:
            # Might as well give some details.
            faddr_lid = 0
            faddr.queue = (faddr_int >> 1) & 0x3fff
        else:
            # Unknown block.
            raise ValueError('FabricAddress out of range: 0x%06x, no such gid %d\n' % (faddr_int, faddr.gid))

        return faddr

    @classmethod
    def from_string(cls, string_value):
        """Create FabricAddress from string generated by FADDR_ARGS.

        Returns None if an invalid string.
        """
        match = re.match('FA([0-9]+):([0-9]+):([0-9]+)\[(.*)\]', string_value)
        if not match:
            return None
        gid = int(match.group(1))
        lid = int(match.group(2))
        queue = int(match.group(3))
        block = match.group(4)

        if (block not in major_blocks and block not in pc_lid_table and
                re.match("CCV[0-9]\.[0-9]\.[0-9]", block) == None and
                re.match(HU_block, block) == None):
            raise ValueError('Unknown block ' + block)

        # TODO(bowdidge): Double-check block matches address.
        fa = FabricAddress()

        if gid > GID_PC_BASE:
            fa.raw_value = (gid << 15) + (queue << 2)
        else:
            fa.raw_value = (gid << 15) + (lid << 10) + (queue << 2)

        fa.gid = gid
        fa.lid = lid
        fa.queue = queue

        return fa

    def is_accelerator(self):
        """Returns True if fabric address is an accelerator block.

        Accelerator means any of the hardware blocks in a cluster.
        """
        return (self.gid >= GID_PC_BASE and self.gid <= GID_PC_MAX and
                self.lid < LID_VP_BASE)

    def is_hu(self):
        """Returns True if fabric address is a Host Unit (PCI) block."""
        return self.gid >= GID_HU_BASE and self.gid <= GID_HU_MAX

    def is_nu(self):
        """Returns True if fabric address is a Network Unit block."""
        return self.gid >= GID_NU_BASE and self.gid <= GID_NU_MAX

    def is_vp(self):
        return self.gid <= GID_PC_MAX and self.lid >= LID_VP_BASE

    def is_cluster(self):
        """Returns True if fabric address goes to a PC or CC."""
        return self.gid <= GID_PC_MAX

    def is_high_priority_queue(self):
        """True if fabric address is a high priority queue on a VP."""
        if not self.is_vp():
            return False

        return self.queue % 2 == 1

    def as_vp_hash(self):
        """Returns a VP-unique has value.

        Fabric addresses representing different WU queues on the same VP
        get the same value.

        Raises exception if not a VP.
        """
        if not self.is_cluster():
            raise ValueError('as_vp_hash: not a VP: {}'.format(
                    self.as_faddr_str()))
        return self.gid << 5 | self.lid

    def as_faddr_str(self):
        """Returns fabric address in same form as FADDR_ARGS on FunOS."""
        return 'FA{}:{}:{}[{}]'.format(self.gid, self.lid, self.queue,
                                       self.block_name())

    def block_name(self):
        if self.is_hu():
            return 'HU'
        if self.is_nu():
            return 'NU'
        if self.is_cluster():
            if self.lid < LID_VP_BASE:
                return pc_lid_table[self.lid]
            return 'VP'
        if self.gid == 31:
            return 'UNKNOWN'
        raise ValueError('Unknown block for faddr %d' % self.raw_value)

    def __str__(self):
        """Returns a human-readable string for fabric address.

        This should describe the fabric address in whatever makes sense
        for humans discussing code.
        """
        if self.is_hu():
            return 'HU{}'.format(self.gid - GID_HU_BASE)
        if self.is_nu():
            return 'NU{}'.format(self.gid - GID_NU_BASE)
        if self.lid < LID_VP_BASE:
            return '{}{}'.format(pc_lid_table[self.lid], self.gid)
        else:
            core = (self.lid - LID_VP_BASE) // TOPO_MAX_VPS_PER_CORE
            vp = (self.lid - LID_VP_BASE) % TOPO_MAX_VPS_PER_CORE
            return 'VP{}.{}.{}'.format(self.gid, core, vp)
        raise ValueError('Unknown block ' + self.block)


class Transaction(object):
    """Container for a sequence of related WU events.

    Each transaction contains a tree of TraceEvents representing WUs
    triggered by other WUs.  A transaction covers a fixed interval of
    time, and should generally represent the work for a single activity,
    request, or immutable chunk of work.
    """
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

    def as_dict(self):
        """Returns transaction as a dictionary of explicit values.

        The dictionary defines an API of values that templates can view,
        or that can be outputted as JSON.
        """
        all_events = [e.as_dict() for e in self.flatten()]
        min_time = min([x['start_time'] for x in all_events
                        if not x['is_timer']])
        max_time = max([x['end_time'] for x in all_events
                        if not x['is_timer']])
        overall_duration = max_time - min_time

        # Limit bars to 98% of container so they don't trigger a new line.
        MAX_PCT = 98

        for event in all_events:
            offset_time = event['start_time'] - min_time
            # Offset from start of tration to current event.
            event['overall_duration'] = overall_duration
            if max_time - min_time == 0:
                event['offset_pct'] = 0
                event['duration_pct'] = MAX_PCT
            else:
                event['offset_pct'] = MAX_PCT * offset_time / overall_duration
                event['duration_pct'] = (MAX_PCT * event['duration']
                                         / overall_duration)

        return {
            'label': self.label,
            'start_time': self.start_time(),
            'end_time': self.end_time(),
            'duration_nsecs': self.duration(),
            'events': all_events
            }

    def start_time(self):
        """Time in nanosecondseconds since epoch when the first WU started."""
        # TODO(bowdidge): Stop recalculating this each time.
        if not self.root_event:
            return 0
        start = self.root_event.start_time
        for e in self.flatten():
            if start > e.start_time:
                start = e.start_time
        return start

    def end_time(self):
        """Time in nanoseconds since epoch when the last WU finished."""
        if not self.root_event:
            return 0
        end = self.root_event.end_time
        for e in self.flatten():
            if e.is_timer:
                continue
            if end < e.end_time:
                end = e.end_time
        return end

    def duration(self):
        """Number of nanoseconds elapsed during transaction."""
        return self.end_time() - self.start_time()

    def remove(self, event):
        """Removes a specific WU event from a transaction."""
        if event == self.root_event:
            self.root_event = None
            return

        # walk through all elements
        for e in self.flatten():
            if event in e.successors:
                e.successors.remove(event)
                return

    def flatten(self):
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


# TODO(bowdidge): Consider merging with WuStartEvent, or
# renaming to EventInterval.
class TraceEvent(object):
    """A work unit (WU) representing either an event at a given point in
    time or an event occuring during a time interval.  Trace events usually
    represent the time a WU ran on a VP (combining the raw start and end
    events.)
    WU events can also represent timer set/trigger pairs, or simulated
    hardware events.
    """
    def __init__(self, start_time, end_time, label, vp):
        # When the event started.
        self.start_time = start_time

        # When the event ended.
        self.end_time = end_time

        # Text label to display when showing this event.
        self.label = label

        # Fabric address for virtual processor where this event ran.
        self.vp = vp

        # Transactions holding this event.
        self.transaction = None

        # True if this event represents a timer set and trigger.  For
        # timers, the start_time represents the time when the timer
        # was set, and the end_time represents the time when the timer
        # was triggered.
        self.is_timer = False

        self.is_annotation = False

        # Work units or events that were instigated by this event.
        self.successors = []

        # to recognize the WUs processed in DMA
        self.is_hw_dma = False

        #to recognize the WUs processed in LE
        self.is_hw_le = False

        # to recognize the WUs processed in compression/decompression engine
        self.is_hw_zip = False

        #to recognize the WUs processed in HU
        self.is_hw_hu = False

        # to represent the WUs processed in RGX
        self.is_hw_rgx = False

    def as_dict(self):
        return {'start_time': self.start_time,
                'end_time': self.end_time,
                'duration': self.duration(),
                'label': self.label,
                'vp': self.vp,
                # No transaction because it is an object.
                'is_timer': self.is_timer,
                'is_hw_dma': self.is_hw_dma,
                'is_hw_le': self.is_hw_le,
                'is_hw_zip': self.is_hw_zip,
                'is_hw_hu': self.is_hw_hu,
                'is_hw_rgx': self.is_hw_rgx,
                'is_annotation': self.is_annotation
                }

    def range(self):
        """Returns start and end time for this event alone."""
        return (self.start_time, self.end_time)

    def duration(self):
        """Returns time spent only in this event in nanoseconds."""
        return self.end_time - self.start_time

    def __cmp__(self, other):
        if other is None:
            return 1
        return cmp((self.label, self.start_time, self.end_time),
                   (other.label, other.start_time, other.end_time))

    def __str__(self):
        return '<TraceEvent: %s - %s %s>' % (self.start_time, self.end_time,
                                             self.label)

    def __repr__(self):
        return '<TraceEvent: %s - %s %s>' % (self.start_time, self.end_time,
                                             self.label)

# Ordinals for type of event.  Keep this equal to event types in FunOS
# to avoid confusion.
WU_START_EVENT = 1
WU_SEND_EVENT = 2
WU_END_EVENT = 3
TIMER_START_EVENT = 4
TRANSACTION_START_EVENT = 5
TRANSACTION_ANNOT_EVENT = 6
TIME_SYNC_EVENT = 7
# Not in FunOS.
HU_SQ_DBL = 8

class Event(object):
    """
    A raw event from WU tracing.

    This is the base class with common functionality across all
    event types. Subclasses perform unpacking of the additional
    words after the header.
    """

    def __init__(self, timestamp, faddr):
        # Full timestamp when event was recorded.
        self.timestamp = timestamp
        # FabricAddress where event was logged.
        self.faddr = faddr
        self.event_type = None


class WuStartEvent(Event):
    """A WU START event."""

    def __init__(self, timestamp, faddr, arg0, arg1, wuid, wu_name,
                 origin_faddr):
        super(WuStartEvent, self).__init__(timestamp, faddr)
        self.event_type = WU_START_EVENT
        # Argument 0 of arriving WU.  Often frame.
        self.arg0 = arg0
        # Argument 1 of arriving WU.
        self.arg1 = arg1
        # Ordinal value of WU being run.
        self.wuid = wuid
        # Name of WU being run.
        self.name = wu_name
        # FabricAddress of unit scheduling WU.
        self.origin_faddr = origin_faddr

    def __str__(self):
        return '<WuStartEvent timestamp %d faddr %s arg0 0x%x arg1 0x%x wuid 0x%x name %s origin_faddr %s>' % (self.timestamp, self.faddr.as_faddr_str(), self.arg0, self.arg1, self.wuid, self.name, self.origin_faddr.as_faddr_str())

class WuSendEvent(Event):
    """A WU SEND event"""
    def __init__(self, timestamp, faddr, arg0, arg1, wuid, wu_name,
                 dest_faddr, flags):
        """Creates a WU SEND event from all arguments logged."""
        super(WuSendEvent, self).__init__(timestamp, faddr)
        self.event_type = WU_SEND_EVENT
        # Argument 0 for sent WU.
        self.arg0 = arg0
        # Argument 1 for sent WU.
        self.arg1 = arg1
        # Ordinal number for the WU being sent.  Does not include prefetch
        # bits.
        self.wuid = wuid
        # Name of WU being sent.
        self.name = wu_name
        # Destination fabric address where WU should run.
        self.dest_faddr = dest_faddr
        # Additional flags describing WU.
        # bit 0 = gated WU.
        # bit 1 = Fake WU short-circuiting hardware request.
        self.flags = flags

    def __str__(self):
        return '<WuSendEvent timestamp %d faddr %s arg0 0x%x arg1 0x%x wuid 0x%x name %s dest %s flags %d>' % (self.timestamp, self.faddr.as_faddr_str(), self.arg0, self.arg1, self.wuid, self.name, self.dest_faddr.as_faddr_str(), self.flags)

class WuEndEvent(Event):
    """A WU END event."""

    def __init__(self, timestamp, faddr):
        super(WuEndEvent, self).__init__(timestamp, faddr)
        self.event_type = WU_END_EVENT

    def __str__(self):
        return '<WuEndEvent timestamp %d faddr %s>' % (self.timestamp,
                                                      self.faddr.as_faddr_str())


class TransactionAnnotateEvent(Event):
    """Event indicating an arbitrary logging message for debugging."""
    def __init__(self, timestamp, faddr, msg):
        super(TransactionAnnotateEvent, self).__init__(timestamp, faddr)
        # String provided by user as annotation.
        self.event_type = TRANSACTION_ANNOT_EVENT
        self.msg = msg

    def __str__(self):
        return '<TransactionAnnotateEvent timestamp %d faddr %s msg %s>' % (
            self.timestamp,
            self.faddr.as_faddr_str(),
            self.msg)

class TransactionStartEvent(Event):
    """Event indicating the current WU is start of a separate transaction.

    Used by trace processing to break traces up into chunks representing
    individual actions by the F1.
    """
    def __init__(self, timestamp, faddr):
        super(TransactionStartEvent, self).__init__(timestamp, faddr)
        self.event_type = TRANSACTION_START_EVENT

    def __str__(self):
        return '<TransactionStartEvent timestamp %d faddr %s>' % (
            self.timestamp,
            self.faddr.as_faddr_str())

class TimerStartEvent(Event):
    """Event indicating the starting of a hardware timer to send a WU.

    Hardware timers may be cancelled and may not always fire.
    """
    def __init__(self, timestamp, faddr, timer, wuid, wu_name, dest, arg0):
        super(TimerStartEvent, self).__init__(timestamp, faddr)
        self.event_type = TIMER_START_EVENT
       # Timer id for timer being started.
        self.timer = timer
        # WU id for handler that will run when timer expires.
        self.wuid = wuid
        # Name for WU.
        self.name = wu_name
        # faddr of VP where handler WU should run.
        self.dest_faddr = dest
        # Single argument provided to timer WU.
        # For timers, arg0 is provided by the caller; arg1 is
        # the timer id shifted.
        self.arg0 = arg0

    def __str__(self):
        return '<TimerStartEvent timestamp %d faddr %s timer 0x%x wuid 0x%x name %s dest_faddr %s arg0 0x%x>' % (
            self.timestamp,
            self.faddr.as_faddr_str(),
            self.timer, self.wuid, self.name,
            self.dest_faddr.as_faddr_str(), self.arg0)

class TimeSyncEvent(Event):
    """ A TIME SYNC event.

    This provides a full 64-bit timestamp so full timestamps
    from the other event types can be reconstructed from partial timestamps
    stored in the raw event on the F1.
    """

    def __init__(self, timestamp, faddr, full_timestamp):
        super(TimeSyncEvent, self).__init__(timestamp, faddr)
        self.event_type = TIME_SYNC_EVENT
        # 64 bit timestamp that matches up with 32 bit timestamp in event.
        self.full_timestamp = full_timestamp

    def __str__(self):
        return '<TimeSyncEvent timestamp %d faddr %s fulltimestamp %d>' % (
            self.timestamp,
            self.faddr.as_faddr_str(),
            self.full_timestamp)
