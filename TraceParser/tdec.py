#!/usr/bin/python

#external libs
import pickle, sys, os
from optparse import OptionParser
import tutils_hdr as tutils

#internal libs
from ttypes import TEntry
from ttypes import TTree


def filter_tree(tree, fname, depth):
	
	if tree.get_name() == fname:
		print ""
		tree.print_tree_ltd(0, depth)
	else:
		for el in tree.get_calls():
			filter_tree(el, fname, depth)

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


def hdr_links(funcs):
	hdrs = ""

	funcs.sort()

	for f in funcs:
		hdrs = hdrs + "Go to function <a href=\"#%s\">%s</a>" % (f, f)
		hdrs = hdrs + "<br>\n"

	return hdrs

if __name__ == "__main__":

	parser = OptionParser()

	parser.add_option("-t", "--funtrc", dest="funtrc_f", help="fungible trace object", metavar="FILE")
	parser.add_option("-v", "--vp", dest="vp", help="VP")
	parser.add_option("-f", "--filter", dest="filterlist_f", help="Filter list", metavar="FILE")
	parser.add_option("-c", "--core", dest="core_id", help="Core ID")
	parser.add_option("-d", "--data", dest="data_f", help="Data folder", metavar="FOLDER")

	(options, args) = parser.parse_args()

	if options.funtrc_f is None:
		print "Need to specify a fungible option trace file"
		sys.exit(0)

	dst = ''
	if options.data_f != None:
		dst = os.path.abspath(options.data_f)


	f = open(options.funtrc_f, 'r')
	funtrc = pickle.load(f)
	f.close()

	#filter_tree(funtrc, "int2base",10)
	#filter_tree(funtrc[0], "verif_issue_loop",1)
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
		f = open(options.filterlist_f)

		filterlist = f.readlines()
		filterlist = [x.strip() for x in filterlist]

		f.close()

	statsd = [{}, {}, {}, {}]

	for vpid in range(vpid_start, vpid_end):
		fname = "c%svp%s.html" % (coreid, vpid)

		gather_stats_rec(funtrc[vpid], statsd[vpid])

		report = tutils.html_hdr()
		report = report + hdr_links(statsd[vpid].keys())

		#print "STATS[%s]: %s" % (vpid, statsd[vpid])

		if funtrc[vpid] == None:
			pass
			#print "VP did not run"
		else:
			report = report + funtrc[vpid].html_tree(filterlist, 0)

		#summarize(statsd[vpid])
		report = report + tutils.output_html(statsd[vpid])
		report = report +  tutils.html_end()

		f = open(os.path.join(dst, fname), 'w')
		f.write(report)
		f.close()


	f = open(os.path.join(dst, 'statsd_c%s' % coreid), 'w')
	pickle.dump(statsd, f)
	f.close()


