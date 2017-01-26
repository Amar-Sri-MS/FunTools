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
    duration = event.end_time - event.start_time

    leadingSpace = wholePercent * start_offset / group_duration
    width = wholePercent * duration / group_duration
    color = 'red'

    if event.is_timer is True:
        timer_offset = event.start_time - event.timer_start
        leadingSpace = wholePercent * start_offset / group_duration
        triggerSpace = wholePercent * timer_offset / group_duration
        width = wholePercent * duration / group_duration


        out.write('  <div class="label"><i>%s</i></div>\n' % (event.label))
        out.write('  <div class="time"><i>%s</i></div>\n' % (
                RangeString(event.start_time, event.end_time)))
        out.write('  <div class="duration"><i>%s</i></div>\n' % (
                DurationString(event.end_time - event.start_time)))
        out.write('  <div class="vp"></div>\n')
        out.write('  <div class="timeline">\n')

        out.write('    <div style="width: %d%%"; class="space"></div>\n' % (
                leadingSpace))
        out.write('    <div style="width: 0%" class="bar schedule tooltip">\n')
        out.write('    <div class="tooltiptext">timer set at %s</div>\n' % (
                TimeString(event.timerStart)))
        out.write('    <div style="width: %d%%"; class="space"></div>\n' % (
                triggerSpace))
        out.write('    <div style="width: %d%%"; class="bar timer">\n' % width)
        out.write('    </div>\n')
        out.write('  </div>\n')
    else:
        out.write('  <div class="label">%s</div>\n' % (event.label))
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

    for wu in sorted(event.next_wus):
        RenderEvent(out, wu, group_start, group_duration)


    for subevent in sorted(event.subevents):
        RenderEvent(out, subevent, group_start, group_duration)

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

/* CSS for kinds of bars. */

/* How to draw WUs. */
.wu {
  background-color: red;
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

def RenderGroup(out, group):
    """Render an event which is the root of a transaction."""
    sys.stderr.write('Rendering group for %s\n' % group.label)
    (group_start, group_end) = group.Interval()
    group_duration = group_end - group_start
    out.write('<a name="%s"></a>\n' % TimeString(group_start))
    out.write('<div class="row request">\n')
    out.write('  <div class="label">All</div>\n')
    out.write('  <div class="time">%s</div>\n' % RangeString(group_start, group_end))
    out.write('  <div class="duration">%s</div>\n' % DurationString(group_duration))
    out.write('  <div class="vp"></div>\n')
    out.write('  <div class="timeline">\n')
    out.write('    <div style="width: %d%%"; class="bar allrow"></div>\n' % MAX_WIDTH)
    out.write('  </div>\n')
    out.write('</div>\n')
    RenderEvent(out, group, group_start, group_duration)
    #out.write('<div class="detail" style="font-size: small; padding-top: 20px;"> Calling sequence was:<ul> <li> A called B <li> B called C <li> C called D <li> D called E </ul> e</div>')


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

    sum = sum(durationArray)

    percentile50Index = PercentileIndex(50, count)
    percentile90Index = PercentileIndex(90, count)
    percentile95Index = PercentileIndex(95, count)

    percentile50Duration = values[percentile50Index]
    percentile90Duration = values[percentile90Index]
    percentile95Duration = values[percentile95Index]

    output = '<table border="1">'
    output += '<tr><td>Minimum duration:</td><td>%s</td></tr>\n' % (
        DurationString(min))
    output += '<tr><td>Maximum duration:</td><td>%s</td></tr>\n' % (
        DurationString(max))
    output += '<tr><td>Average duration:</td><td>%s</td></tr>\n' % (
        DurationString(sum / count))
    output += '<tr><td>50%%ile:</td><td>%s</td></tr>\n' % (
        DurationString(percentile50Duration))
    output += '<tr><td>90%%ile:</td><td>%s</td></tr>\n' % (
        DurationString(percentile90Duration))
    output += '<tr><td>95%%ile:</td><td>%s</td></tr>\n' % (
        DurationString(percentile95Duration))
    output += '</table>\n'
    return output


def RenderSummary(out, trace_events):
    """Generate summary data describing the kinds of WU sequences that
    we saw.  This data is grouped by the starting WU, and allows
    comparing runs of equivalent WUs.
    """
    root_to_group = {}
    for group in trace_events.subevents:
        if group.label not in root_to_group:
            root_to_group[group.label] = []
        root_to_group[group.label].append(group)

    for label in root_to_group:
        root_to_group[label] = sorted(root_to_group[label],
                                      key=lambda x: x.Span())

    out.write('<h1>Transactions</h1>\n')
    for label in root_to_group:
        durations = [x.Span() for x in root_to_group[label]]
        out.write('<b>WU sequence starting with %s:</b><br>' % label)
        out.write('Duration of sequence: %s\n' % (
                DistributionString(durations)))
        out.write('<ul>\n')
        for group in root_to_group[label]:
          (start_time, end_time) = group.Interval()
          out.write('<li> <a href="#%s">%s</a> %s\n' % (
                  TimeString(start_time),
                  RangeString(start_time, end_time),
                  DurationString(group.Span())))
        out.write('</ul>\n')

def RenderHTML(out, trace_events):
    """Generates HTML page showing the listed events."""
    RenderHeader(out)
    out.write('<body>\n')

    RenderSummary(out, trace_events)
    out.write('<h1>Timelines</h1>\n')
    for group in trace_events.subevents:
        (group_start, group_end) = group.Interval()
        RenderGroup(out, group)
    out.write('</body></html>')

def GraphvizSafeLabel(label):
    """Generates a label that will be parsed as a single item by GraphViz."""
    return label.replace('$', 'dollar')

def RenderGraphvizEvent(out, trace_event):
    """Output all edges from trace_event in dot style."""
    for successor in trace_event.next_wus:
      # Process explicit sends.
      out.write('%s -> %s [style=bold];\n' % (
              GraphvizSafeLabel(trace_event.label),
              GraphvizSafeLabel(successor.label)))
      RenderGraphvizEvent(out, successor)

    for successor in trace_event.subevents:
      # Process calls and timers.
      if successor.is_timer:
        # TODO(bowdidge): Consider representing timer as an edge from
        # WU setting timer to WU receiving trigger rather than treating the
        # timer like a WU.
        if (len(successor.next_wus) != 1):
            # Never saw trigger from timer.
            continue
        timer_successor = successor.next_wus[0]

        from_label = GraphvizSafeLabel(trace_event.label)
        to_label = GraphvizSafeLabel(timer_successor.label)
        # Create a node with the from/to embedded in the label so that
        # different timers map to different nodes.
        style = '[style=dotted]'
        out.write('%s -> %s_to_timer_to_%s -> %s %s; \n' % (
          from_label, from_label, to_label, to_label, style))
        RenderGraphvizEvent(out, timer_successor)
      else:
        style = '[style=bold]'
        out.write('%s -> %s %s;\n' % (
                GraphvizSafeLabel(trace_event.label),
                GraphvizSafeLabel(successor.label), style))
        RenderGraphvizEvent(out, successor)


def RenderGraphviz(out, trace_events):
    """Generate the call graph for all events in trace_events in
    dot format used by GraphViz.
    """
    out.write('strict digraph foo {\n')
    for group in trace_events.subevents:
        out.write('start -> %s;\n' % ( 
            GraphvizSafeLabel(group.label)))
        RenderGraphvizEvent(out, group)
    output_file.write('label="\\nbold: wu send\\nsolid: wu call\\ndot: timer"\n')
    output_file.write('}\n')
