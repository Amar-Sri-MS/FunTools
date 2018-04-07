#!/usr/bin/python
#
# Created by Nag Ponugoti March 28 2018
# Copyright Fungible Inc. 2018

import glob, os, sys, re, datetime
import getopt, platform, tempfile

from itertools import chain
import json
from string import Template
import re
from json_reader import CFG_Reader
from module import ModuleRoot

input_base = ""
output_base = ""

# Merge two dictionaries
def merge_dicts(cfg, cfg_j):
	new_cfg = cfg
	for key in cfg_j.keys():
		print "Adding key: %s" % key
		if key in new_cfg.keys():
			new_cfg[key].update(cfg_j[key])
		else:
			new_cfg[key] = cfg_j[key]

	return new_cfg

# generate the source code
def generate_source_code(cfg):
    api = ""
    args = ""
    #print cfg.get()
    for i, (key, value) in enumerate(cfg.get().iteritems()):
        print key
        for k2,v2 in value.items():
            print k2
            for k3,v3 in v2.items():
                print k3
                if k3 == "input":
                    print "INPUT"
                    inputs  = ['%s,' % (v) for v in value[k2][k3]]
                    args = "".join(inputs)[:-1]
                    print args
                else:
                    print "API"
                    api += "{}_read_{}_stats({})".format(key, k2, args)
                    print api



#Groups the range strings
def group_to_range(group):
  group = ''.join(group.split())
  sign, g = ('-', group[1:]) if group.startswith('-') else ('', group)
  r = g.split('-', 1)
  r[0] = sign + r[0]
  r = sorted(int(__) for __ in r)
  return range(r[0], 1 + r[-1])

#Groups and expands range strings
def rangeexpand(txt):
  ranges = chain.from_iterable(group_to_range(__) for __ in txt.split(','))
  return sorted(set(ranges))

def parse_output_config():
        print "+ Generate cfg"

def Usage():
	sys.stderr.write('stats_gen.py: usage: [-i [cfg input dir] [-o cfg output dir]\n')

def main():
        global output_base
        global input_base
        global cfg_code_gen_out_base

	print "Stats File Generation"
	try:
            opts, args = getopt.getopt(sys.argv[1:], 'hi:o:')

	except getopt.GetoptError as err:
		print str(err)
    		Usage()
    		sys.exit(2)

  	for o, a in opts:
    		if o in ('-h', '--help'):
      			Usage()
      			sys.exit(1)
    		elif o in ('-i', '--input'):
      			input_base = a
      			print "input dir: " + a
    		elif o in ('-o', '--output'):
      			output_base = a
      			print "output dir: " + a
    		else:
      			assert False, 'Unhandled option %s' % o

        cfg = CFG_Reader(input_base)

	#Generate the funos source code
        for i, (k,v) in enumerate(cfg.get().iteritems()):
	    ModuleRoot(k, v)

if __name__ == "__main__":
	main()
