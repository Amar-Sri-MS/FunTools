#
# render.py: Render trace data in HTML or graphviz.
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.
#

import jinja2
import json
import math
import os
import sys

import event

NSECS_PER_SEC = 1000000000

def TruncatedSecs(time_nsecs):
    """Returns the number of seconds.
    Time is truncated to two digits for more compact displays.
    """
    return (time_nsecs / NSECS_PER_SEC) % 100

def TruncatedUsecs(time_nsecs):
    """Returns number of microseconds in fractional seconds of given time."""
    return (time_nsecs % NSECS_PER_SEC) / 1000

def TruncatedNsecs(time_nsecs):
    """Returns number of nanoseconds in fractional seconds of given time."""
    return time_nsecs % NSECS_PER_SEC

def TimeString(nanoseconds):
    """Returns a string showing a specific time in human-readable form.

    This function only displays time in microseconds so it's easier for a
    human to read, and should be used for general output.
    """
    startSecs = TruncatedSecs(nanoseconds)
    startUsecs = TruncatedUsecs(nanoseconds)
    return '%02d.%06d' % (startSecs, startUsecs)

def NanosecondTimeString(nanoseconds):
    """Returns a string showing a specific time in human-readable form.

    This function displays time in nanoseconds to match file input.
    """
    startSecs = TruncatedSecs(nanoseconds)
    startNsecs = TruncatedNsecs(nanoseconds)
    return '%02d.%09d' % (startSecs, startNsecs)

def RangeString(start_time, end_time):
    """Prints start and end formatted nicely."""
    startSecs = TruncatedSecs(start_time)
    startUsecs = TruncatedUsecs(start_time)
    endSecs = TruncatedSecs(end_time)
    endUsecs = TruncatedUsecs(end_time)
    return '%02d.%06d - %02d.%06d' % (startSecs, startUsecs, endSecs, endUsecs)

def DurationString(duration_nsecs):
    """Returns a human-readable string showingduration as microseconds."""
    if duration_nsecs < 1000:
        return '%d nsec' % duration_nsecs
    if duration_nsecs < 1000000:
        return '%d usec' % (duration_nsecs / 1000.0)
    elif duration_nsecs < NSECS_PER_SEC:
        return '%0.3f msec' % (duration_nsecs / 1000000.0)
    else:
        return '%0.6f sec' % (duration_nsecs / float(NSECS_PER_SEC))

def PercentileIndex(percent, itemCount):
    """Returns the index of element in an array representing the nth percentile."""
    if itemCount == 0:
        return None
    assert(percent > 0)
    assert(percent < 100)
    index = int(math.ceil(percent * itemCount / 100.0))
    return index - 1

def TransactionGroupStats(transactions):
    """Returns dictionary describing stats on a set of transactions.

    This is used to describe min, max, average, etc. times for the same
    WU.
    """
    result = {'count': 0,
              'min_nsec': 0,
              'max_nsec': 0,
              'average_nsec': 0,
              '50ile_nsec': 0,
              '90ile_nsec': 0,
              '95ile_nsec': 0
              }

    count = len(transactions)
    if count == 0:
        return result

    durations = [x.Duration() for x in transactions]
    sorted_durations = sorted(durations)

    result['min_nsec'] = sorted_durations[0]
    result['max_nsec'] = sorted_durations[-1]
    result['average_nsec'] = sum(durations) / len(transactions)

    percentile50Index = PercentileIndex(50, count)
    percentile90Index = PercentileIndex(90, count)
    percentile95Index = PercentileIndex(95, count)

    result['50ile_nsec'] = sorted_durations[percentile50Index]
    result['90ile_nsec'] = sorted_durations[percentile90Index]
    result['95ile_nsec'] = sorted_durations[percentile95Index]
    return result

next_id = 0

def GetUniqueId():
    """Returns a unique global id for numbering nodes.
    
    TODO(bowdidge): Lock so supports multiple threads.
    """
    global next_id
    next_id += 1
    return next_id

def GetGroups(transactions):
    """Generate summary data describing the kinds of WU sequences that
    we saw.  This data is grouped by the starting WU, and allows
    comparing runs of equivalent WUs.
    """
    root_to_group = {}
    for transaction in transactions:
        label = transaction.Label()
        if label not in root_to_group:
            root_to_group[label] = []
        root_to_group[label].append(transaction)

    for label in root_to_group:
        root_to_group[label] = sorted(root_to_group[label],
                                      key=lambda x: x.Duration())

    groups = []
    for label in root_to_group:
        durations = [x.Duration() for x in root_to_group[label]]
        group = {'count': len(root_to_group[label]),
                 'label': label,
                 'stats': TransactionGroupStats(root_to_group[label]),
                 'transactions': GetTransactionDicts(root_to_group[label]),
                 'id': GetUniqueId()
                 }
        if label == 'boot':
            boot_group = group
        groups.append(group)

    return groups

def GetTransactionDicts(transactions):
    result = []
    for tr in transactions:
        transaction_dict = tr.AsDict()
        transaction_dict['id'] = GetUniqueId()
        result.append(transaction_dict)
    return result

def RenderHTML(transactions):
    """Generates HTML page showing the listed events."""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(this_dir))
    env.filters['as_duration'] = lambda nsecs: DurationString(nsecs)
    env.filters['as_time'] = lambda nsecs: TimeString(nsecs)
    env.filters['as_ns'] = lambda nsecs: NanosecondTimeString(nsecs)

    page_dict = {
        'groups': GetGroups(transactions)
        }

    template = env.get_template('report.html')
    return template.render(page_dict)

def RenderJSON(transactions):
    page_dict = {
        'groups': GetGroups(transactions),
        }
    return json.dumps(page_dict)


def GraphvizSafeLabel(event):
    """Generates a label that will be parsed as a single item by GraphViz."""
    return event.Label().replace('$', 'dollar')

common_wus = ["timer", "wuh_join", "nop_wuh", "wuh_resource_lock"]
common_prefixes = ["ikv_"]

def IsCommon(label):
    """Returns true if the WU in the label is an extremely common WU.
    Common low level functions cause graphs for different transactions to get
    tied together in inappropriate ways, so we create
    separate nodes for these in each transaction.
    """
    if label in common_wus:
        return True
    for prefix in common_prefixes:
        if label.startswith(prefix):
            return True
    return False

def RenderGraphvizTransaction(out, transaction):
    """Output all edges from trace_event in dot style.
    The events in each transaction represent each time a function
    was run.  For graphviz, we output only the label so duplicate
    (predecessor, successor) pairs may be output multiple times.
    """
    all_nodes = transaction.Flatten()

    for e in all_nodes:
      for successor in e.successors:
        # Process explicit sends.
        style = "bold"
        if successor.is_timer:
            style = "dotted"
        source_label = GraphvizSafeLabel(e)
        dest_label = GraphvizSafeLabel(successor)

        # Use separate node names for the common WUs so that the
        # trees for different transactions don't get too jumbled.
        if IsCommon(source_label):
            source_label = '{%s [label="%s"]}' % (
                source_label + '_' + transaction.label,
                source_label)
        if IsCommon(dest_label):
            dest_label = '{%s [label="%s" style=%s]}' % (
                dest_label + '_' + transaction.label,
                dest_label, style)
        else:
            dest_label = '%s [style=%s]' % (dest_label, style)

        out.write('%s -> %s;\n' % (
                source_label, dest_label))


def RenderGraphviz(out, transactions):
    """Generate the call graph for all events in trace_events in
    dot format used by GraphViz.
    """
    out.write('strict digraph foo {\n')
    for transaction in transactions:
        RenderGraphvizTransaction(out, transaction)
    out.write('label="\\nbold: wu send\\ndot: timer"\n')
    out.write('}\n')

def Dump(output_file, transaction):
  """Writes a text dump to the output file describing a set of trace events."""
  output_file.write('%s (%s): transaction "%s"\n' % (
      RangeString(transaction.StartTime(), transaction.EndTime()),
      DurationString(transaction.Duration()),
      transaction.label))
  worklist = transaction.Flatten()
  for event in worklist:
    output_file.write('+ %s (%s): %s\n' % (RangeString(event.start_time, event.end_time),
                                           DurationString(event.Duration()),
                                           event.label))

def DumpTransactions(output_file, transactions):
  """Writes a text dump to the output file describing a set of traced transactions."""
  for tr in transactions:
    Dump(output_file, tr)

