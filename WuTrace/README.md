# WuTrace

This directory contains scripts for converting WU log messages (generated by the --wulog option for the funos_posix
environment) into either HTML, text logs, or call graphs describing the WUs performed.

# Operation

Basic operation:

  funos_posix --wulog > foo.raw_trace

  cat foo.raw_trace | grep TRACE | sort -n -k1,20 -s > foo.trace

  wu_trace.py foo.trace > foo.html

wu_trace.py also takes the following options:
* --format xxxx changes the output style to HTML, text, or graphviz.
* --debug prints out status messages during parsing.
* --output sets the output file.

The --format flag changes the style of output.  'text' displays each
individual sequence of events in a textual tree format.  'html' outputs
the timeline-based view of each separate transaction.  'graphviz' draws
the call graph of all events seen in a single graph.

Note that the wu_log mechanism relies on the arguments passed to the
wu - frame pointer in arg0 and flow pointer in arg1 - to identify
related work units.  It assumes that these values will be unique, and
that only one WU can be running with the same flow (or frame).  If the
same flow pointer is used for several simultaneous WUs (such as
passing an integer rather than an explicit flow object), then the
analysis can be confused.

# Output Style

In HTML style, WUs are described in a timeline view, grouped by transaction or access.
All WUs related to a single access (such as a single read, or single network request)
are grouped on the same timeline.  The top of each trace summarizes all the requests seen,
and groups transformations with the same starting WU.  This output is modeled on RPC tracing tools.

Here is an example of an HTML trace:

http://dochub.fungible.local/doc/WUTrace/epnvme.html

http://dochub.fungible.local/doc/WUTrace/funflix.html

In Graphviz mode, WUs are described in a call graph showing which WUs might call other WUs.

Here is an example of a Graphviz trace:

http://dochub.fungible.local/doc/WUTrace/funflix.new.jpg

# Development

To test code, do:
python trace_test.py
python render_test.py
