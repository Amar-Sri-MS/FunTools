#!/usr/bin/env python3

import subprocess

COMMANDS = """
unset key
set title "WU Arrival Histogram"
set terminal svg size 1200,350
set style data histogram
set style histogram cluster gap 0
set style fill solid
set boxwidth 0.8
set xtics out nomirror
set xtics rotate by -45 offset 0,-.04
set rmargin 8
set xlabel "time (s)"
set ylabel "wus (count)"

plot "-" index 0 using 0:2:3:xtic( (int($0) == 0 || ((int($0) % 5) == 4)) ? stringcolumn(1) : "") with boxes fillcolor rgb variable
"""

###
##  actual plot
#

def plot_svg(hist):

    # convert to text for gnuplot
    data = "\n".join([ "%g\t%d\t0x%x" % (x, y, col) for (x, y, col) in hist])

    # run gnuplot
    try:
        p = subprocess.Popen(["gnuplot"],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        s = p.communicate(COMMANDS + data)[0]

        # strip the xml banner
        n = s.index("<svg")
        s = s[n:]
    except:
        s = "<i>[data generated without gnuplot installed]</i>"
        
    return s
    
