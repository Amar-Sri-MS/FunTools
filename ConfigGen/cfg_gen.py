#!/usr/bin/python

# cfg_gen.py
# The config generator is intended to simplify configuration file maintenance,
# now that we are getting more files. The files are all stored in a flat
# layout (configs/*.cfg) and are combined into one out/default.cfg. This is
# subject to change as requirements for different configurations grow.
#
# The input files are allowed to make two side-steps from the standard JSON
# specification:
#	- Allow comments
#	- Allow hex values
#
# Both are intended to improve readability of the files, and leverage our
# own jsonutil (which has a lenient parser) to do the initial parsing.
#
# Created by Michael Boksanyi, August 10 2017
# Copyright Fungible Inc. 2017

import glob, os, sys, re

import json

##### jsonutil-related commands #####
def jsonutil_path():
	return os.path.join('..', 'jsonutil')


def build_jsonutil():

	startdir = os.getcwd()

	os.chdir(jsonutil_path())

	if os.path.isfile('jsonutil'):
		os.chdir(startdir)
		return True

	rc = os.system('make clean; make')
	if rc != 0:
		os.chdir(startdir)
		return False

	os.chdir(startdir)

	return True

# Input: json with comments and hex values
# Output: json
def standardize_json(in_cfg, out_cfg):

	jsonutil_tool = os.path.join(jsonutil_path(), 'jsonutil')

	os.system('%s -i %s -o %s' % (jsonutil_tool, in_cfg, out_cfg));

# Merge two dictionaries
# If they have the same key, merge contents
# This is necessary e.g. for the pipeline:
# 	Both the PRS and FFE images fall under the "pipeline" key,
#	so we need to merge them properly
def merge_dicts(full_cfg, cfg_j):

	new_cfg = full_cfg

	for key in cfg_j.keys():
		print "Adding key: %s" % key
		if key in new_cfg.keys():
			new_cfg[key].update(cfg_j[key])
		else:
			new_cfg[key] = cfg_j[key]

	return new_cfg


# Standardize and combine multiple configuration files
# into one config that will be used by FunOS
# TBD: handle cases where different files refer to
# the same keys
def generate_config():

	full_cfg = {}
	sku_cfg = {}

	#get full_cfg
	for cfg in glob.glob("configs/*.cfg"):
		print "handling general %s" % cfg
	    	skupattern = re.compile('configs/*sku*', re.IGNORECASE)
	    	if skupattern.match(cfg):
	        	continue

		standardize_json(cfg, cfg+'.tmp')
		f = open("%s.tmp" % cfg, 'r')
		cfg_j = json.load(f)
		f.close()
		os.system('rm %s.tmp' % cfg)
		full_cfg = merge_dicts(full_cfg, cfg_j)

	if not os.path.exists('out'):
		os.mkdir('out')

	fout = open("out/default.cfg", 'w')

	# indent=4 does pretty printing for us
	json.dump(full_cfg, fout, indent=4)

	fout.close()

	#for each sku_cfg create a file in out dir
	for cfg in glob.glob("configs/*.cfg"):
	    	skupattern = re.compile('configs/*sku*', re.IGNORECASE)
	    	if skupattern.match(cfg):
			print "handling sku configs %s" % cfg
			standardize_json(cfg, cfg+'.tmp')
			f = open("%s.tmp" % cfg, 'r')
			cfg_j = json.load(f)
			f.close()
			os.system('rm %s.tmp' % cfg)

			sku_cfg = merge_dicts(full_cfg, cfg_j)
			if not os.path.exists('out'):
				os.mkdir('out')

	    		skufilename = re.search(r'^(.*)/sku_(.*)', cfg, re.IGNORECASE)
			filename = "out/"+ skufilename.group(2)
			fout = open(filename, 'w')

			# indent=4 does pretty printing for us
			json.dump(sku_cfg, fout, indent=4)

			fout.close()

	# XXX next step: output bjson

if __name__ == "__main__":

	rc = build_jsonutil()
	if rc == False:
		print 'Failed to build jsonutil'
		sys.exit(1)
	
	rc = generate_config()
	if rc == False:
		print 'Failed to generate config'
		sys.exit(1)
