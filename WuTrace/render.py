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

def truncated_secs(time_nsecs):
    """Returns the number of seconds.
    Time is truncated to two digits for more compact displays.
    """

    return (time_nsecs // NSECS_PER_SEC) % 100

def truncated_usecs(time_nsecs):
    """Returns number of microseconds in fractional seconds of given time."""
    return (time_nsecs % NSECS_PER_SEC) / 1000

def truncated_nsecs(time_nsecs):
    """Returns number of nanoseconds in fractional seconds of given time."""
    return time_nsecs % NSECS_PER_SEC

def time_string(nanoseconds):
    """Returns a string showing a specific time in human-readable form.

    This function only displays time in microseconds so it's easier for a
    human to read, and should be used for general output.
    """
    startSecs = truncated_secs(nanoseconds)
    startUsecs = truncated_usecs(nanoseconds)
    return '%02d.%06d' % (startSecs, startUsecs)

def nanosecond_time_string(nanoseconds):
    """Returns a string showing a specific time in human-readable form.

    This function displays time in nanoseconds to match file input.
    """
    startSecs = truncated_secs(nanoseconds)
    startNsecs = truncated_nsecs(nanoseconds)
    return '%02d.%09d' % (startSecs, startNsecs)

def range_string(start_time, end_time):
    """Prints start and end formatted nicely."""
    startSecs = truncated_secs(start_time)
    startUsecs = truncated_usecs(start_time)
    endSecs = truncated_secs(end_time)
    endUsecs = truncated_usecs(end_time)
    return '%02d.%06d - %02d.%06d' % (startSecs, startUsecs, endSecs, endUsecs)

def duration_string(duration_nsecs):
    """Returns a human-readable string showingduration as microseconds."""
    if duration_nsecs < 1000:
        return '%d nsec' % duration_nsecs
    if duration_nsecs < 100000:
        return '%0.1f usec' % (duration_nsecs / 1000.0)
    if duration_nsecs < 1000000:
        return '%d usec' % (duration_nsecs / 1000.0)
    elif duration_nsecs < NSECS_PER_SEC:
        return '%0.3f msec' % (duration_nsecs / 1000000.0)
    else:
        return '%0.6f sec' % (duration_nsecs / float(NSECS_PER_SEC))

def percentile_index(percent, itemCount):
    """Returns the index of element in an array representing the nth percentile."""
    if itemCount == 0:
        return None
    assert(percent > 0)
    assert(percent < 100)
    index = int(math.ceil(percent * itemCount / 100.0))
    return index - 1

def calculate_outlier(events_list):
    mean = 0
    number_of_events = 0
    standard_deviation = 0
    event_dictionary = {}
    duration_list = []
    for event in events_list:
        for e in event:
            mean += e.duration()
            # we need a unique key to represent every event
            event_dictionary['%s-%s' % (e.start_time, e.end_time)] = e
            number_of_events += 1
            duration_list.append(e.duration())

    if number_of_events == 0:
        return []

    mean = mean / number_of_events
    duration_list = sorted(duration_list)
    q1 = duration_list[int(number_of_events * (1/4))]
    q3 = duration_list[int(number_of_events * (3/4))]
    iqr = q3 - q1 # Interquartile range
    upper_fence = q3 + (1.5 * iqr)
    lower_fence = q1 - (1.5 * iqr)

    outliers = []
    for i in event_dictionary:
        # not adding events with duration < lower_fence because we do not want
        # events that took too less time as outliers.
        if (event_dictionary[i].duration() > upper_fence and
                event_dictionary[i].duration() > 1000000 and
                event_dictionary[i].label != "timer"):
            # Should not add events with duration < 1000 usec
            outliers.append(event_dictionary[i])
    return outliers

def transaction_group_stats(transactions):
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
              '95ile_nsec': 0,
              'outliers'  : [],
              }

    count = len(transactions)
    if count == 0:
        return result
    events_list = [x.flatten() for x in transactions]
    durations = [x.duration() for x in transactions]
    sorted_durations = sorted(durations)

    result['min_nsec'] = sorted_durations[0]
    result['max_nsec'] = sorted_durations[-1]
    result['average_nsec'] = sum(durations) / len(transactions)
    result['count'] = count

    result['outliers'] = calculate_outlier(events_list)

    percentile50Index = percentile_index(50, count)
    percentile90Index = percentile_index(90, count)
    percentile95Index = percentile_index(95, count)

    result['50ile_nsec'] = sorted_durations[percentile50Index]
    result['90ile_nsec'] = sorted_durations[percentile90Index]
    result['95ile_nsec'] = sorted_durations[percentile95Index]
    return result

next_id = 0

def get_unique_id():
    """Returns a unique global id for numbering nodes.

    TODO(bowdidge): Lock so supports multiple threads.
    """
    global next_id
    next_id += 1
    return next_id

def get_groups(transactions):
    """Generate summary data describing the kinds of WU sequences that
    we saw.  This data is grouped by the starting WU, and allows
    comparing runs of equivalent WUs.
    """
    root_to_group = {}
    for transaction in transactions:
        label = transaction.label
        if label not in root_to_group:
            root_to_group[label] = []
        root_to_group[label].append(transaction)

    for label in root_to_group:
        root_to_group[label] = sorted(root_to_group[label],
                                      key=lambda x: x.duration(),
                                      reverse=True)

    groups = []
    for label in root_to_group:
        durations = [x.duration() for x in root_to_group[label]]
        group = {'count': len(root_to_group[label]),
                 'label': label,
                 'stats': transaction_group_stats(root_to_group[label]),
                 'transactions': get_transaction_dicts(root_to_group[label]),
                 'id': get_unique_id()
                 }
        if label == 'boot':
            boot_group = group
        groups.append(group)

    return groups

def get_transaction_dicts(transactions):
    result = []
    for tr in transactions:
        transaction_dict = tr.as_dict()
        transaction_dict['id'] = get_unique_id()
        result.append(transaction_dict)
    return result

def outlier_string(outlier_list):
    # TODO(SanyaSriv): Sort the events in decreasing order of duration
    if len(outlier_list) == 0: # there are no outliers
        return "There are 0 outliers for this sequence."
    k = ''
    for i in range(0, len(outlier_list)):
        outlier = outlier_list[i]
        k += '%s: %s: %s' % (outlier.label,
                             range_string(outlier.start_time, outlier.end_time),
                             duration_string(outlier.duration()))
        if i != len(outlier_list) - 1:
            k += '\n'
    return k

def render_html(transactions):
    """Generates HTML page showing the listed events."""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(this_dir))
    env.filters['as_duration'] = lambda nsecs: duration_string(nsecs)
    env.filters['as_time'] = lambda nsecs: time_string(nsecs)
    env.filters['as_ns'] = lambda nsecs: nanosecond_time_string(nsecs)
    env.filters['as_string'] = lambda lis: outlier_string(lis)
    page_dict = {
        'groups': get_groups(transactions)
        }

    template = env.get_template('report.html')
    return template.render(page_dict)

class TransactionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, event.FabricAddress):
            return obj.as_faddr_str()
        return json.JSONEncoder.default(self, obj)

def render_json(transactions):
    page_dict = {
        'groups': get_groups(transactions),
        }
    return json.dumps(page_dict, cls=TransactionEncoder)


def graphviz_safe_label(event):
    """Generates a label that will be parsed as a single item by GraphViz."""
    return event.label.replace('$', 'dollar')

common_wus = ['timer', 'wuh_join', 'nop_wuh', 'wuh_resource_lock',
              'DMA', 'vol_submit_op_done', 'lsvtest_write']
common_prefixes = ['ikv_']

def is_common(label):
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

def render_graphviz_transaction(out, transaction):
    """Output all edges from trace_event in dot style.
    The events in each transaction represent each time a function
    was run.  For graphviz, we output only the label so duplicate
    (predecessor, successor) pairs may be output multiple times.
    """
    all_nodes = transaction.flatten()

    for e in all_nodes:
      for successor in e.successors:
        # Process explicit sends.
        style = 'bold'
        if successor.is_timer:
            style = 'dotted'
        source_label = graphviz_safe_label(e)
        dest_label = graphviz_safe_label(successor)

        # Use separate node names for the common WUs so that the
        # trees for different transactions don't get too jumbled.
        if is_common(source_label):
            source_label = '{%s [label="%s"]}' % (
                source_label + '_' + transaction.label,
                source_label)
        if is_common(dest_label):
            dest_label = '{%s [label="%s" style=%s]}' % (
                dest_label + '_' + transaction.label,
                dest_label, style)
        else:
            dest_label = '%s [style=%s]' % (dest_label, style)

        out.write('%s -> %s;\n' % (
                source_label, dest_label))


def render_graphviz(out, transactions):
    """Generate the call graph for all events in trace_events in
    dot format used by GraphViz.
    """
    out.write('strict digraph foo {\n')
    for transaction in transactions:
        render_graphviz_transaction(out, transaction)
    out.write('label="\\nbold: wu send\\ndot: timer"\n')
    out.write('}\n')

def dump(output_file, transaction):
    """Writes a text dump to the output file for list of trace events."""
    output_file.write('%s (%s): transaction "%s"\n' % (
            range_string(transaction.start_time(), transaction.end_time()),
            duration_string(transaction.duration()),
            transaction.label))
    worklist = transaction.flatten()
    for event in worklist:
        duration  = duration_string(event.duration())
        output_file.write('+ %s (%s): %s\n' % (range_string(event.start_time,
                                                            event.end_time),
                                               duration,
                                               event.label))

def dump_transactions(output_file, transactions):
  """Writes text dump to the output file describing list of transactions."""
  for tr in transactions:
    dump(output_file, tr)
