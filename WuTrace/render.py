#
# render.py: Render trace data in HTML.
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
    return '%d.%06d' % (startSecs, startUsecs)

def RangeString(start_time, end_time):
    """Prints start and end formatted nicely."""
    startSecs = TruncatedSecs(start_time)
    startUsecs = TruncatedUsecs(start_time)
    endSecs = TruncatedSecs(end_time)
    endUsecs = TruncatedUsecs(end_time)
    return '%d.%06d - %d.%06d' % (startSecs, startUsecs, endSecs, endUsecs)

def DurationString(duration):
    duration_secs = duration / 1000000
    duration_usecs = duration % 1000000

    if duration_secs == 0 and duration_usecs < 1000:
        return "%d usecs" % duration_usecs
    elif duration_secs == 0:
        return "%0.3f ms" % (duration_usecs / 1000)
    else:
        return "%0.6f secs" % (duration / 1000000)

# Number of microseconds to show in a bar.
BAR_WIDTH = 40000

def RenderEvent(output_file, event, start_time, full_bar_duration, indent):
    if full_bar_duration == 0:
        full_bar_duration = 1
    """Renders HTML for a single event."""
    leadingSpace = 100 * (event.start_time - start_time) / full_bar_duration
    width = 100 * (event.end_time - event.start_time) / full_bar_duration
    color = 'red'
    indentString = '&nbsp;' * indent

    if event.label == 'top':
        output_file.write('<div class="row request">\n')
        output_file.write('  <div class="label">All</div>\n')
        output_file.write('  <div class="time">%s</div>\n' % RangeString(event.start_time, event.end_time))
        output_file.write('  <div class="duration">%s</div>\n' % DurationString(event.end_time - event.start_time))
        output_file.write('  <div class="vp"></div>\n')
        output_file.write('  <div class="timeline">\n')
        output_file.write('    <div style="width: %d%%"; class="bar allrow"></div>\n' % 100)
        output_file.write('  </div>\n')
        output_file.write('</div>\n')

    elif event.label == 'wuh_request':
        output_file.write('<div class="row request">\n')
        output_file.write('  <div class="label">All</div>\n')
        (start, end) = event.Interval()
        output_file.write('  <div class="time">%s</div>\n' % RangeString(start, end))
        output_file.write('  <div class="duration">%s</div>\n' % DurationString(event.Span()))
        output_file.write('  <div class="vp"></div>\n')
        output_file.write('  <div class="timeline">\n')
        output_file.write('    <div style="width: %d%%"; class="bar allrow"></div>\n' % 100)
        output_file.write('  </div>\n')
        output_file.write('</div>\n')

        output_file.write('<div class="row request">\n')
        output_file.write('  <div class="label">wuh_request</div>\n')
        output_file.write('  <div class="time">%s</div>\n' % RangeString(event.start_time, event.end_time))
        output_file.write('  <div class="duration">%s</div>\n' % DurationString(event.end_time - event.start_time))
        output_file.write('  <div class="vp">%s</div>\n' % event.vp)
        output_file.write('  <div class="timeline">\n')
        output_file.write('    <div style="width: %d%%"; class="space"></div>\n' % leadingSpace)
        output_file.write('    <div style="width: %d%%"; class="bar"></div>\n' % width)
        output_file.write('  </div>\n')
        output_file.write('</div>\n')
    else:
        output_file.write('<div class="row">\n')

    if event.label == 'timer trigger':
        leadingSpace = 100 * (event.timerStart - start_time) / full_bar_duration
        triggerSpace = 100 * (event.start_time - event.timerStart) / full_bar_duration
        width = 100 * (event.end_time - event.start_time) / full_bar_duration

        
        output_file.write('  <div class="label"><i>%s</i></div>\n' % (indentString + event.label))
        output_file.write('  <div class="time"><i>%s</i></div>\n' % RangeString(event.start_time, event.end_time))
        output_file.write('  <div class="duration"><i>%s</i></div>\n' % (
                DurationString(event.end_time - event.start_time)))
        output_file.write('  <div class="vp"></div>\n')
        output_file.write('  <div class="timeline">\n')

        output_file.write('    <div style="width: %d%%"; class="space"></div>\n' % leadingSpace)
        output_file.write('    <div style="width: 0%%"; class="bar schedule tooltip">\n')
        output_file.write('    <div class="tooltiptext">timer set at %s</div></div>\n' % TimeString(event.timerStart))
        output_file.write('    <div style="width: %d%%"; class="space"></div>\n' % triggerSpace)
        output_file.write('    <div style="width: %d%%"; class="bar timer">\n' % width)
        output_file.write('    </div>\n')
        output_file.write('  </div>\n')
    else:
        output_file.write('  <div class="label">%s</div>\n' % (indentString + event.label))
        output_file.write('  <div class="time">%s</div>\n' % RangeString(event.start_time, event.end_time))
        output_file.write('  <div class="duration">%s</div>\n' % (DurationString(event.end_time - event.start_time)))
        output_file.write('  <div class="vp">%s</div>\n' % event.vp)
        output_file.write('  <div class="timeline">\n')

        output_file.write('    <div style="width: %d%%"; class="space"></div>\n' % leadingSpace)
        output_file.write('    <div style="width: %d%%"; class="bar wu"></div>\n' % width)
        output_file.write('  </div>\n')
    output_file.write('</div>\n')

    for subevent in event.subevents:
        RenderEvent(output_file, subevent, start_time, full_bar_duration, indent + 2)

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

def RenderGroup(output_file, group, start_time, full_bar_duration):
    sys.stderr.write("Rendering %s\n" % group.label)
    if group.Span() > 500000:
        for event in group.subevents:
            RenderGroup(output_file, event, event.start_time, event.Span())
    else:
        RenderEvent(output_file, group, group.start_time, group.Span(), 0)

def RenderHTML(output_file, trace_events):
    """Generates HTML page showing the listed events."""
    RenderHeader(output_file)
    output_file.write("<body>\n")

    firstEvent = trace_events.subevents[0]
    lastEvent = trace_events.subevents[len(trace_events.subevents)-1]
    # TODO(bowdidge): Break trace up into separate pieces.
    # 1) Find things smaller than 15 ms.
    # 2) Anything done on a repetitive timer in 
    for group in trace_events.subevents:
        RenderGroup(output_file, group, firstEvent.start_time, group.Span())
    output_file.write("</body></html>")
