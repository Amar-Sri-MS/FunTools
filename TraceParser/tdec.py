#!/usr/bin/env python2.7

#external libs
import pickle, sys, os
from optparse import OptionParser
import tutils_hdr as tutils

#internal libs
from ttypes import TEntry
from ttypes import TTree
import html_gen


def filter_tree(tree, fname, depth, excl_sub_calls):
    
    if tree.get_name() == fname:
        print ""
        tree.print_tree_ltd(0, depth, excl_sub_calls)
    else:
        for el in tree.get_calls():
            filter_tree(el, fname, depth, excl_sub_calls)

def gather_stats_rec(tree, statsd):

    if tree is None:
        return

    if tree.get_name() not in statsd:
        statsd[tree.get_name()] = []
    
    # XXX enhance to gather more stats
    statsd[tree.get_name()].append(tree.get_ccount())

    for el in tree.get_calls():
        gather_stats_rec(el, statsd)
        

def summarize(statsd):
    print """<div style="height: 3000px"></div>
<h1>Summary</h1>"""


    funcs = statsd.keys()
    funcs.sort()

    for funcname in funcs:
        print "<a name=\"%s\"></a>" % funcname
        print "<h2>%s</h2>" % funcname
        print "Details on %s." % funcname
        print "<br>"
        print "<br>"
        print "Called at ticks: "
        for cyc in statsd[funcname]:
            print "<a href=\"#%s\">%s</a> " % (cyc, cyc)
        print "<br>"


def hdr_info(statsd):

    hdrs = ""

    funcs = statsd.keys()
    funcs.sort()

    outstats = []

    for f in funcs:
        outstats.append([f, len(statsd[f])])

    outstats = sorted(outstats, key=lambda x:x[1])
    outstats = reversed(outstats)

    for f in outstats:
        hdrs = hdrs + "<a href=\"#%s\">%s</a> (%s calls)" % (f[0], f[0], f[1])
        hdrs = hdrs + "<br>\n"

    return hdrs

if __name__ == "__main__":
    sys.setrecursionlimit(0x1000000)
    parser = OptionParser()

    parser.add_option("-t", "--funtrc", dest="funtrc_f", help="fungible trace object", metavar="FILE")
    parser.add_option("-v", "--vp", dest="vp", help="VP")
    parser.add_option("-f", "--filter", dest="filterlist_f", help="Filter list", metavar="FILE")
    parser.add_option("-c", "--core", dest="core_id", help="Core ID")
    parser.add_option("-d", "--data", dest="data_f", help="Data folder", metavar="FOLDER")
    parser.add_option("-r", "--remove-filtered", dest="exclude_filtered", help="Do not put filtered functions in the output", action="store_true")
    parser.add_option("-e", "--excl-sub-calls", dest="excl_sub_calls", help="Only count this function's metrics, excluding its sub calls", action="store_true")

    (options, args) = parser.parse_args()

    if options.funtrc_f is None:
        print "Need to specify a fungible option trace file"
        sys.exit(1)

    dst = ''
    if options.data_f != None:
        dst = os.path.abspath(options.data_f)


    f = open(options.funtrc_f, 'r')
    funtrc = pickle.load(f)
    f.close()

    #filter_tree(funtrc, "int2base",10, options.excl_sub_calls)
    #filter_tree(funtrc[0], "verif_issue_loop",1, options.excl_sub_calls)
    #print ""

    vpid_start = 0
    vpid_end = 4

    if options.vp != None:
        vpid_start = int(options.vp)
        vpid_end = vpid_start + 1

    filterlist = []

    coreid = 0
    if options.core_id != None:
        coreid = int(options.core_id)

    if options.filterlist_f != None:
        for fname in options.filterlist_f.split(','):

            f = open(fname)

            flist = f.readlines()
            flist = [x.strip() for x in flist]

            filterlist = filterlist + flist

            f.close()

    statsd = [{}, {}, {}, {}]

    # VP outputs
    for vpid in range(vpid_start, vpid_end):
        fname = "c%svp%s.html" % (coreid, vpid)

        gather_stats_rec(funtrc[vpid], statsd[vpid])

        report = html_gen.vp_html_hdr()
        report = report + hdr_info(statsd[vpid])

        #print "STATS[%s]: %s" % (vpid, statsd[vpid])

        if funtrc[vpid] == None:
            pass
            #print "VP did not run"
        else:
            report = report + funtrc[vpid].html_tree(filterlist, 0, options.exclude_filtered, options.excl_sub_calls)

        #summarize(statsd[vpid])
        report = report + html_gen.vpstats_output_html(statsd[vpid])
        report = report +  html_gen.generic_html_end()

        f = open(os.path.join(dst, fname), 'w')
        f.write(report)
        f.close()

    f = open(os.path.join(dst, 'statsd_c%s' % coreid), 'w')
    pickle.dump(statsd, f)
    f.close()


    # Core outputs
    core_fname = "c%s.html" % (coreid)

    # part 1: Overview
    core_report = html_gen.core_html_hdr()

    core_report = core_report + "<a href=\"index.html\">Cluster overview</a><br>"

    core_report = core_report + "<table>"

    core_report = core_report + "<tr>"
    core_report = core_report + "<td><a href=\"c%svp0.html\">VP0 details</a></td>" % coreid
    core_report = core_report + "<td><a href=\"c%svp1.html\">VP1 details</a></td>" % coreid
    core_report = core_report + "<td><a href=\"c%svp2.html\">VP2 details</a></td>" % coreid
    core_report = core_report + "<td><a href=\"c%svp3.html\">VP3 details</a></td>" % coreid
    core_report = core_report + "</tr>"

    core_report = core_report + "<tr>"
    for c in range(0,4):
        core_report = core_report + "<td>"

        for fcall in statsd[c].keys():
            core_report = core_report + "%s<br>" % fcall

        core_report = core_report + "</td>"

    core_report = core_report + "</table>"
    core_report = core_report + "</tr>"

    # part 2: Tree


    # part 3: End
    core_report = core_report + html_gen.generic_html_end()

    f = open(os.path.join(dst, core_fname), 'w')
    f.write(core_report)
    f.close()

