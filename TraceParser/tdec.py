#!/usr/bin/python

#external libs
import pickle, sys
from optparse import OptionParser

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


if __name__ == "__main__":

	parser = OptionParser()

	parser.add_option("-t", "--funtrc", dest="funtrc_f", help="fungible trace object", metavar="FILE")
	parser.add_option("-v", "--vp", dest="vp", help="VP")

	(options, args) = parser.parse_args()

	if options.funtrc_f is None:
		print "Need to specify a fungible option trace file"
		sys.exit(0)


	f = open(options.funtrc_f, 'r')

	funtrc = pickle.load(f)

	f.close()

	#filter_tree(funtrc, "int2base",10)
	filter_tree(funtrc[0], "verif_issue_loop",1)
	#print ""
	#funtrc[int(options.vp)].print_tree(0)
