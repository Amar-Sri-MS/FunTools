#!/usr/bin/env python2.7

import sys
import cgi
import optparse

ANCHORS = {
    "welcome": ("Welcome to FunOS", "[kernel] Welcome to FunOS!"),
    "ready": ("System Ready Notification", "System event posted: system_event_ready_to_start"),
    "soak": ("soaklib Results", 'System event posted: system_event_ready_to_start'),
    "freeze": ("crash started", ">>> FunOS entering bug_check handler <<<"),
    "bug_check": ("bug_check", ">>>>>> bug_check on vp 0x"),
    "assert": ("assertion failure", "Assertion failed: "),
    "tlbl": ("Bad pointer exception (load)", "cause.ExcCode: 2 (0x2): TLB exception (load or instruction fetch)"),
    "tlbs": ("Bad pointer exception (store)", "cause.ExcCode: 3 (0x3): TLB exception (store)"),
    "idle_final": ("Exit Cleanup", 'INFO nucleus "Idle state = IDLE_STATE_FINAL"'),
    "platform_halt": ("Platform Halt", 'platform_halt: exit status '),
    }

###
##  actual work
#

HTML_HEADER = """<html>
<body>
"""

HTML_FOOTER = """</body>
</html>
"""

def make_header(index, opts):

    html = ""

    if (not opts.partial):
        html += HTML_HEADER

    if ("__ordered__" not in index):
        return html

    # process index in order
    html += "Notable events<br />"
    html += "<ul>\n"
    for (aname, hread) in index["__ordered__"]:
        line = '<li><a href="#%s">%s</a></li>\n' % (aname, hread)
        html += line
    html += "</ul>\n"
    html += "<pre>\n"

    return html

def make_footer(opts):

    html = ""
    
    html += "</pre>\n"
    if (not opts.partial):
        html += HTML_FOOTER

    return html

def mkanchor(ak, line, index, opts):

    l = index.setdefault(ak, [])
    o = index.setdefault("__ordered__", [])

    # construct the anchor name
    aname = "%s%s" % (opts.prefix, ak)
    if (len(l) > 0):
        aname += len(l)
    l.append(aname)

    # add an ordered entry of the human readable name
    o.append((aname, ANCHORS[ak][0]))

    # make the line right
    line = line.strip()
    line = '<a name="%s"><font color="red">%s</font></a>\n' % (aname, line)

    return line
    
def markup_line(line, index, opts):

    # make an escaped copy
    htmlline = cgi.escape(line)
    
    # see if the original line matches anything
    for ak in ANCHORS:
        t = ANCHORS[ak]
        s = t[1]

        if (s in line):
            htmlline = mkanchor(ak, htmlline, index, opts)
    
    return htmlline

# process a list of lines
def lines2html(lines, opts):

    log = ""
    index = {}
    
    for line in lines:
        outline = markup_line(line, index, opts)
        log += outline

    hdr = make_header(index, opts)
    ftr = make_footer(opts)
    
    return hdr + log + ftr
        
def str2html(s, opts):
    lines = s.split("\n")
    return lines2html(lines)

###
##  option parsing
#
def get_options():

    parser = optparse.OptionParser(usage="usage: %prog [options] [<input_filename>]")
    parser.add_option("-P", "--partial", action="store_true", default=False)
    parser.add_option("-v", "--verbose", action="store_true", default=False)
    parser.add_option("-o", "--output", action="store", dest="out_fname", default="-")
    parser.add_option("-p", "--prefix", action="store", default="")

    (opts, args) = parser.parse_args()

    if (len(args) == 0):
        opts.in_fname = "-"
    elif (len(args) == 1):
        opts.in_fname = args[0]
    elif (len(args) > 1):
        parser.error("extraneous arguments")
    
    return opts

###
##  handling args
#

def main():

    opts = get_options()

    if (opts.in_fname == "-"):
        infl = sys.stdin
    else:
        infl = open(opts.in_fname)

    if (opts.out_fname == "-"):
        outfl = sys.stdout
    else:
        outfl = open(opts.out_fname)
        
    lines = infl.readlines()
    html = lines2html(lines, opts)

    outfl.write(html)

###
##  command-line entrypoint
#
if (__name__ == "__main__"):
    main()
