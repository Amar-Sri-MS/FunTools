#
# render.py: Render trace data in HTML or graphviz.
#
# Copyright (c) 2017 Fungible Inc.  All rights reserved.
#

import event
import sys

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

def RenderEvent(output_file, event, group_start, group_duration):
    """Render the HMTL for one event in a larger transaction."""
    if group_duration == 0:
        group_duration = 1

    leadingSpace = 100 * (event.start_time - group_start) / group_duration
    width = 100 * (event.end_time - event.start_time) / group_duration
    color = 'red'

    if event.is_timer is True:
        leadingSpace = 100 * (event.timerStart - group_start) / group_duration
        triggerSpace = 100 * (event.start_time - event.timerStart) / group_duration
        width = 100 * (event.end_time - event.start_time) / group_duration


        output_file.write('  <div class="label"><i>%s</i></div>\n' % (event.label))
        output_file.write('  <div class="time"><i>%s</i></div>\n' % RangeString(event.start_time, event.end_time))
        output_file.write('  <div class="duration"><i>%s</i></div>\n' % (
                DurationString(event.end_time - event.start_time)))
        output_file.write('  <div class="vp"></div>\n')
        output_file.write('  <div class="timeline">\n')

        output_file.write('    <div style="width: %d%%"; class="space"></div>\n' % leadingSpace)
        output_file.write('    <div style="width: 0%"; class="bar schedule tooltip">\n')
        output_file.write('    <div class="tooltiptext">timer set at %s</div></div>\n' % TimeString(event.timerStart))
        output_file.write('    <div style="width: %d%%"; class="space"></div>\n' % triggerSpace)
        output_file.write('    <div style="width: %d%%"; class="bar timer">\n' % width)
        output_file.write('    </div>\n')
        output_file.write('  </div>\n')
    else:
        output_file.write('  <div class="label">%s</div>\n' % (event.label))
        output_file.write('  <div class="time">%s</div>\n' % RangeString(event.start_time, event.end_time))
        output_file.write('  <div class="duration">%s</div>\n' % (DurationString(event.end_time - event.start_time)))
        output_file.write('  <div class="vp">%s</div>\n' % event.vp)
        output_file.write('  <div class="timeline">\n')

        output_file.write('    <div style="width: %d%%"; class="space"></div>\n' % leadingSpace)
        output_file.write('    <div style="width: %d%%"; class="bar wu"></div>\n' % width)
        output_file.write('  </div>\n')
    output_file.write('</div>\n')

    for wu in sorted(event.next_wus):
        RenderEvent(output_file, wu, group_start, group_duration)


    for subevent in sorted(event.subevents):
        RenderEvent(output_file, subevent, group_start, group_duration)

def RenderHeader(output_file):
    """Outputs HTML for the event visualization."""
    output_file.write("""
<html>
<head>
<style>
/* CSS for the time bars. */

/* formatting for div representing blank space */
.space {
  display: inline-block;
  height: 20px;
}

/* formatting for div representing activity. */
.bar {
  display: inline-block;
  border: solid 1px;
  height: 20px;
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
   width: 10%;
  display: inline-block;
}
/* Column showing the time range in the WU. */
.time {
   width: 12%;
  display: inline-block;
  border-left: dotted 1px;
}

/* Column represeting the duration of the WU. */
.duration {
  width: 10%;
  display: inline-block;
  border-left: dotted 1px;}

/* Column representing the VP where the WU ran. */
.vp {
  width: 5%;
  display: inline-block;
  border-left: dotted 1px;
}

.row {
  border: dotted 1px;
}

.timeline {
  display: inline-block;
  border-left : solid;
  width: 60%;
}

request {
  margin-top: 20px;
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

def RenderGroup(output_file, group):
    """Render an event which is the root of a transaction."""
    sys.stderr.write("Rendering group for %s\n" % group.label)
    (group_start, group_end) = group.Interval()
    group_duration = group_end - group_start
    output_file.write('<div class="row request">\n')
    output_file.write('  <div class="label">All</div>\n')
    output_file.write('  <div class="time">%s</div>\n' % RangeString(group_start, group_end))
    output_file.write('  <div class="duration">%s</div>\n' % DurationString(group_duration))
    output_file.write('  <div class="vp"></div>\n')
    output_file.write('  <div class="timeline">\n')
    output_file.write('    <div style="width: %d%%"; class="bar allrow"></div>\n' % 100)
    output_file.write('  </div>\n')
    output_file.write('</div>\n')

    RenderEvent(output_file, group, group_start, group_duration)

def RenderHTML(output_file, trace_events):
    """Generates HTML page showing the listed events."""
    RenderHeader(output_file)
    output_file.write('<body>\n')

    for group in trace_events.subevents:
        (group_start, group_end) = group.Interval()
        RenderGroup(output_file, group)
    output_file.write('</body></html>')

def GraphvizSafeLabel(label):
    return label.replace('$', 'dollar')

def RenderGraphvizEvent(output_file, trace_event):
    """Output all edges from trace_event in dot style."""
    for successor in trace_event.next_wus:
      # Process explicit sends.
      output_file.write('%s -> %s [style=bold];\n' % (
              GraphvizSafeLabel(trace_event.label),
              GraphvizSafeLabel(successor.label)))
      RenderGraphvizEvent(output_file, successor)

    for successor in trace_event.subevents:
      # Process calls and timers.
      if successor.is_timer:
        # TODO(bowdidge): Consider representing timer as an edge from
        # WU setting timer to WU receiving trigger rather than treating the
        # timer like a WU.
        assert(len(successor.next_wus) == 1)
        timer_successor = successor.next_wus[0]

        from_label = GraphvizSafeLabel(trace_event.label)
        to_label = GraphvizSafeLabel(timer_successor.label)
        # Create a node with the from/to embedded in the label so that
        # different timers map to different nodes.
        output_file.write('%s -> %s_to_timer_to_%s -> %s [style=dotted]; \n' % (
          from_label, from_label, to_label, to_label))
        RenderGraphvizEvent(output_file, timer_successor)
      else:
        style = '[style=bold]'
        output_file.write('%s -> %s %s;\n' % (
                GraphvizSafeLabel(trace_event.label),
                GraphvizSafeLabel(successor.label), style))
        RenderGraphvizEvent(output_file, successor)


def RenderGraphviz(output_file, trace_events):
    """Generate the call graph for all events in trace_events in
    dot format used by GraphViz.
    """
    output_file.write('strict digraph foo {\n')
    for group in trace_events.subevents:
      output_file.write('start -> %s;\n' % (
              GraphvizSafeLabel(group.label)))
      RenderGraphvizEvent(output_file, group)
    output_file.write('label="\\nbold: wu send\\nsolid: wu call\\ndot: timer"\n')
    output_file.write('}\n')
