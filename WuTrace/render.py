#
# render.py: Render trace data in HTML or graphviz.
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.
#

import math
import sys

import event

def TruncatedSecs(time_usec):
    """Returns the number of seconds, truncated to two digits, for more compact displays."""
    return (time_usec / 1000000) % 100

def TruncatedUsecs(time_usec):
    return time_usec % 1000000

def TimeString(microseconds):
    """Returns a string showing a specific time in human-readable form."""
    startSecs = TruncatedSecs(microseconds)
    startUsecs = TruncatedUsecs(microseconds)
    return '%02d.%06d' % (startSecs, startUsecs)

def RangeString(start_time, end_time):
    """Prints start and end formatted nicely."""
    startSecs = TruncatedSecs(start_time)
    startUsecs = TruncatedUsecs(start_time)
    endSecs = TruncatedSecs(end_time)
    endUsecs = TruncatedUsecs(end_time)
    return '%02d.%06d - %02d.%06d' % (startSecs, startUsecs, endSecs, endUsecs)

def DurationString(duration):
    """Returns a human-readable string representing duration as microseconds."""
    duration_secs = duration / 1000000
    duration_usecs = duration % 1000000

    if duration_secs == 0 and duration_usecs < 1000:
        return '%d usec' % duration_usecs
    elif duration_secs == 0:
        return '%0.3f msec' % (duration_usecs / 1000.0)
    else:
        return '%0.6f sec' % (duration / 1000000.0)

# Size the divs to 90% of full - 100% tends to cause problems
# if a margin throws an object over 100%
MAX_WIDTH = 90.0
def RenderEvent(out, event, group_start, group_duration):
    """Render the HMTL for one event in a larger transaction."""
    if group_duration == 0:
        group_duration = 1

    wholePercent = MAX_WIDTH
    out.write('<div class="row">\n')
    start_offset = event.start_time - group_start
    duration = event.Duration()

    leadingSpace = wholePercent * start_offset / group_duration
    width = wholePercent * duration / group_duration
    color = 'red'

    if event.is_timer:
        timer_offset = event.start_time - event.timer_start
        leadingSpace = wholePercent * start_offset / group_duration
        triggerSpace = wholePercent * timer_offset / group_duration
        width = wholePercent * duration / group_duration


        out.write('  <div class="label"><i>%s</i></div>\n' % (event.Label()))
        out.write('  <div class="time"><i>%s</i></div>\n' % (
                RangeString(event.start_time, event.end_time)))
        out.write('  <div class="duration"><i>%s</i></div>\n' % (
                DurationString(event.end_time - event.start_time)))
        out.write('  <div class="vp"></div>\n')
        out.write('  <div class="timeline">\n')

        out.write('    <div style="width: %d%%"; class="space"></div>\n' % (
                leadingSpace))
        out.write('    <div style="width: 0%" class="bar schedule tooltip">\n')
        out.write('    <div class="tooltiptext">timer set at %s</div></div>\n' % (
                TimeString(event.timer_start)))
        out.write('    <div style="width: %d%%"; class="space"></div>\n' % (
                triggerSpace))
        out.write('    <div style="width: %d%%"; class="bar timer">\n' % width)
        out.write('    </div>\n')
        out.write('  </div>\n')
    elif event.is_annotation:
        out.write('  <div class="label"></div>\n')
        out.write('  <div class="time">%s</div>\n' % (
                RangeString(event.start_time, event.end_time)))
        out.write('  <div class="duration"></div>\n')
        out.write('  <div class="vp">%s</div>\n' % event.vp)
        out.write('  <div class="timeline">\n')

        out.write('    <div style="width: %d%%" class="space"></div>\n' % (
                leadingSpace))
        out.write('    <div style="width: 0%%" class="bar annotation-bar"></div>\n')
        out.write('    <div class="annotation">%s</div>\n' % (
                    event.Label()))
        out.write('  </div>\n')
    else:
        out.write('  <div class="label">%s</div>\n' % (event.Label()))
        out.write('  <div class="time">%s</div>\n' % (
                RangeString(event.start_time, event.end_time)))
        out.write('  <div class="duration">%s</div>\n' % (
                DurationString(event.end_time - event.start_time)))
        out.write('  <div class="vp">%s</div>\n' % event.vp)
        out.write('  <div class="timeline">\n')

        out.write('    <div style="width: %d%%" class="space"></div>\n' % (
                leadingSpace))
        out.write('    <div style="width: %d%%" class="bar wu"></div>\n' % (
                    width))
        out.write('  </div>\n')
    out.write('</div>\n')


def RenderHeader(out):
    """Outputs HTML for the event visualization."""
    out.write("""
<html>
<head>
<style>
/* CSS for the time bars. */

/* formatting for div representing blank space */
.space {
  display: inline-block;
  height: 15px;
}

/* formatting for div representing activity. */
.bar {
  display: inline-block;
  border: solid 1px;
  height: 15px;
}

.annotation {
  display: inline-block;
  height: 15px;
  color: #111111;
  font-size: small;
}

/* CSS for kinds of bars. */

/* How to draw WUs. */
.wu {
  background-color: red;
}

.annotation-bar {
  background-color: DarkGray;
}

/* How to draw top-level objects. */
.allrow {
  background-color: gray;
}

/* How to draw span representing a call. */
.call {
  background-color: #ffe0e0;

}

/* How to draw span representing a timer. */
.timer {
  background-color: #e0e0ff;
  height: 10px;
  margin-top: 5px;margin-bottom: 5px;
  border: 1px solid blue;
}

/* Bar representing a timer start. */
.schedule {
  background-color: #0000ff;
  height: 10px;
  margin-top: 5px;margin-bottom: 5px;
}

/* How to format the rest of the display */
/* Column with the WU name. */
.label {
   width: 15%;
  display: inline-block;
  font-size: small;
}
/* Column showing the time range in the WU. */
.time {
   width: 12%;
  display: inline-block;
  border-left: dotted 1px;
  font-size: small;
}

/* Column represeting the duration of the WU. */
.duration {
  width: 8%;
  display: inline-block;
  border-left: dotted 1px;
  font-size: small;
}

/* Column representing the VP where the WU ran. */
.vp {
  width: 5%;
  display: inline-block;
  border-left: dotted 1px;
  font-size: small;
}

.row {
  border: dotted 1px;
}

.timeline {
  display: inline-block;
  border-left : solid;
  width: 55%;
}

.request {
  margin-top: 40px;
  padding-top: 10px;
  border: none;
  border-top: solid 2px;
}

/* CSS definitions needed to allow hover to show text */
.tooltip {
  position: relative;
  display: inline-block;
  border-bottom: 1px dotted black;
}
.tooltip .tooltiptext {
  visibility: hidden;
  width: 120px;
  background-color:black;
  color: #fff;
  text-align:center;
  padding: 5px 0;
  border-radius: 6px;
  position: absolute;
  z-index: 1;
}
.tooltip:hover .tooltiptext { visibility: visible }
</style>
<script>
</script>
</head>
""")

def RenderTransaction(out, transaction):
    """Render an event which is the root of a transaction."""
    sys.stderr.write('Rendering transaction for %s\n' % transaction.Label())
    start_time = transaction.StartTime()
    end_time = transaction.EndTime()
    duration = transaction.EndTime() - transaction.StartTime()
    out.write('<a name="%s"></a>\n' % TimeString(transaction.StartTime()))
    out.write('<div class="row request">\n')
    out.write('  <div class="label">All</div>\n')
    out.write('  <div class="time">%s</div>\n' % RangeString(transaction.StartTime(), transaction.EndTime()))
    out.write('  <div class="duration">%s</div>\n' % DurationString(duration))
    out.write('  <div class="vp"></div>\n')
    out.write('  <div class="timeline">\n')
    out.write('    <div style="width: %d%%"; class="bar allrow"></div>\n' % MAX_WIDTH)
    out.write('  </div>\n')
    out.write('</div>\n')
    for event in transaction.Flatten():
        RenderEvent(out, event, start_time, duration)

def PercentileIndex(percent, itemCount):
    """Returns the index of element in an array representing the nth percentile."""
    if itemCount == 0:
        return None
    assert(percent > 0)
    assert(percent < 100)
    index = int(math.ceil(percent * itemCount / 100.0))
    return index - 1

def DistributionString(durationArray):
    """Returns HTML describing the distribution of durations of WU chains.
    durationArray should be an array of durations for each
    """
    count = len(durationArray)

    values = sorted(durationArray)

    if count == 0:
        return 'no samples'

    min = durationArray[0]
    max = durationArray[-1]

    sum_duration = sum(durationArray)

    percentile50Index = PercentileIndex(50, count)
    percentile90Index = PercentileIndex(90, count)
    percentile95Index = PercentileIndex(95, count)

    percentile50Duration = values[percentile50Index]
    percentile90Duration = values[percentile90Index]
    percentile95Duration = values[percentile95Index]

    output = '<table border="1">'
    output += '<tr><td>Number of occurrences:</td><td>%d</td></tr>\n' %(
        count)

    output += '<tr><td>Minimum duration:</td><td>%s</td></tr>\n' % (
        DurationString(min))
    output += '<tr><td>Maximum duration:</td><td>%s</td></tr>\n' % (
        DurationString(max))
    output += '<tr><td>Average duration:</td><td>%s</td></tr>\n' % (
        DurationString(sum_duration / count))
    output += '<tr><td>50%%ile:</td><td>%s</td></tr>\n' % (
        DurationString(percentile50Duration))
    output += '<tr><td>90%%ile:</td><td>%s</td></tr>\n' % (
        DurationString(percentile90Duration))
    output += '<tr><td>95%%ile:</td><td>%s</td></tr>\n' % (
        DurationString(percentile95Duration))
    output += '</table>\n'
    return output


def RenderSummary(out, transactions):
    """Generate summary data describing the kinds of WU sequences that
    we saw.  This data is grouped by the starting WU, and allows
    comparing runs of equivalent WUs.
    """
    root_to_group = {}
    for transaction in transactions:
        if transaction.Label() not in root_to_group:
            root_to_group[transaction.Label()] = []
        root_to_group[transaction.Label()].append(transaction)

    for label in root_to_group:
        root_to_group[label] = sorted(root_to_group[label],
                                      key=lambda x: x.Duration())

    out.write('<h1>Transactions</h1>\n')
    for label in root_to_group:
        durations = [x.Duration() for x in root_to_group[label]]
        out.write('<b>WU sequence starting with %s:</b><br>' % label)
        out.write('Duration of sequence: %s\n' % (
                DistributionString(durations)))
        out.write('<ul>\n')
        for transaction in root_to_group[label]:
          out.write('<li> <a href="#%s">%s</a>\n' % (
                  TimeString(transaction.StartTime()),
                  DurationString(transaction.Duration())))
        out.write('</ul>\n')

def RenderHTML(out, transactions):
    """Generates HTML page showing the listed events."""
    RenderHeader(out)
    out.write('<body>\n')

    RenderSummary(out, transactions)
    out.write('<h1>Timelines</h1>\n')
    for transaction in transactions:
        RenderTransaction(out, transaction)
    out.write('</body></html>')

def GraphvizSafeLabel(event):
    """Generates a label that will be parsed as a single item by GraphViz."""
    return event.Label().replace('$', 'dollar')

common_wus = ["timer_trigger", "wuh_join", "nop_wuh", "wuh_resource_lock"]
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

