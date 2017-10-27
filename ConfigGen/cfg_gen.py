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

sw_cfg = {}
build_cfg = {}

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

# if the key is in the cfg_replace file use it and replace that on the cfg 
def replace_dicts(cfg, cfg_replace):

	new_cfg = cfg

	for key in cfg_replace.keys():
		print "Replace key: %s" % key
		new_cfg[key] = cfg_replace[key]

	return new_cfg

# Merge two dictionaries
# If they have the same key, merge contents
# This is necessary e.g. for the pipeline:
# 	Both the PRS and FFE images fall under the "pipeline" key,
#	so we need to merge them properly
def merge_dicts(cfg, cfg_j):

	new_cfg = cfg

	for key in cfg_j.keys():
		print "Adding key: %s" % key
		if key in new_cfg.keys():
			new_cfg[key].update(cfg_j[key])
		else:
			new_cfg[key] = cfg_j[key]

	return new_cfg


# generate the default sw config
def generate_default_swconfig():
	global sw_cfg

	print "==== sw config ===="
	for cfg in glob.glob("configs/*.cfg"):
		print "handling general sw %s" % cfg
		standardize_json(cfg, cfg+'.tmp')
		f = open("%s.tmp" % cfg, 'r')
		cfg_j = json.load(f)
		f.close()
		os.system('rm %s.tmp' % cfg)
		sw_cfg = merge_dicts(sw_cfg, cfg_j)

# generate build specific config
def generate_build_specific_config(build):
	global build_cfg
	global sw_cfg
	build_cfg.clear()

	#update build specific config
	if os.path.exists(build):
		filename = build+ "/*cfg"
		for cfg in glob.glob(filename):
			print "handling " + build + " cfg %s" % cfg
			standardize_json(cfg, cfg+'.tmp')
			f = open("%s.tmp" % cfg, 'r')
			cfg_replace = json.load(f)
			f.close()
			os.system('rm %s.tmp' % cfg)
			build_cfg = replace_dicts(sw_cfg, cfg_replace)
	else:
		build_cfg = sw_cfg.copy()

# output a cfg file with sku data
def output_per_skuconfig(build):
	global build_cfg
	sku_cfg = {}
	#for each sku_cfg create a file in out dir
	for cfg in glob.glob("sku/*.cfg"):
	    	skupattern = re.compile('sku/*sku*', re.IGNORECASE)
	    	if skupattern.match(cfg):
			print "handling sku configs %s" % cfg
			standardize_json(cfg, cfg+'.tmp')
			f = open("%s.tmp" % cfg, 'r')
			cfg_j = json.load(f)
			f.close()
			os.system('rm %s.tmp' % cfg)
			sku_cfg = replace_dicts(build_cfg, cfg_j)
	    		skufilename = re.search(r'^(.*)/sku_(.*)', cfg, re.IGNORECASE)
			filename = "out/"+ build + "/" +  skufilename.group(2)
			fout = open(filename, 'w')

			# indent=4 does pretty printing for us
			json.dump(sku_cfg, fout, indent=4)

			fout.close()

#output the default.cfg file
def output_default_config(build):
	global sw_cfg
	if not os.path.exists('out'):
		os.mkdir('out')

	filepath = "out/" + build
	if not os.path.exists(filepath):
		os.mkdir(filepath)
	
	filename = "out/" + build + "/" + "default.cfg"
	fout = open(filename, 'w')

	# indent=4 does pretty printing for us
	json.dump(sw_cfg, fout, indent=4)
	fout.close()

# Standardize and combine multiple configuration files
# into one config that will be used by FunOS
# TBD: handle cases where different files refer to
# the same keys
def generate_config(build):
	print "====" + build + "===="
	generate_build_specific_config(build)
	output_default_config(build)
	output_per_skuconfig(build)


if __name__ == "__main__":

	rc = build_jsonutil()
	if rc == False:
		print 'Failed to build jsonutil'
		sys.exit(1)

	#Generate the software config
	generate_default_swconfig()

	#ouput cfg for each build type
	rc = generate_config("posix")
	if rc == False:
		print 'Failed to generate config'
		sys.exit(1)

	rc = generate_config("malta")
	if rc == False:
		print 'Failed to generate malta config'
		sys.exit(1)
