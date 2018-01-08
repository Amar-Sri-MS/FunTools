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
# Modified by Fred stanley, Nov 9 2017
# Copyright Fungible Inc. 2017

import glob, os, sys, re, datetime, platform

import json

##### jsonutil-related commands #####
SDKDIR = os.environ.get("SDKDIR")
if (SDKDIR is None):
        SDKDIR = "../../FunSDK"

def jsonutil_path():
        p = "%s/bin/%s/%s" % (SDKDIR, platform.system(), platform.machine())
        print "Using jsonutil path '%s'" % p
        return p

#Funos module specifig configs
module_cfg = {}

#Build specific module config overrides
build_override_cfg = {}

#final config has build_override_cfg and sku config
final_cfg = {}

header = """ 
// AUTOGENERATED FILE - DO NOT EDIT
"""

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

def parser_handling_old(key, new_cfg, cfg_j):
	matchparser = "PARSER"
	for key2 in cfg_j[key].keys():
		if key2 == matchparser:
			new_cfg[key][key2] = new_cfg[key][key2] + cfg_j[key][key2]
		else:
			new_cfg[key].update(cfg_j[key])


def spl_parser_handling(keyword1, keyword2, new_cfg, cfg_j):
	new_cfg[keyword1][keyword2] = new_cfg[keyword1][keyword2] + cfg_j[keyword1][keyword2]

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
			keyword1 = "pipeline"
			keyword2 = 'PARSER'
			if keyword1 == key and keyword2 in new_cfg[key].keys() and keyword2 in cfg_j[key].keys():
				spl_parser_handling(keyword1, keyword2, new_cfg, cfg_j)
			else:
				new_cfg[key].update(cfg_j[key])
		else:
			new_cfg[key] = cfg_j[key]

	return new_cfg


# generate the default module config
def generate_default_moduleconfig():
	global module_cfg

	print "==== Module config ===="
	for cfg in glob.glob("configs/*.cfg"):
		print "handling module config %s" % cfg
		standardize_json(cfg, cfg+'.tmp')
		f = open("%s.tmp" % cfg, 'r')
		cfg_j = json.load(f)
		f.close()
		os.system('rm %s.tmp' % cfg)
		module_cfg = merge_dicts(module_cfg, cfg_j)

# generate build override config.
def generate_build_override_config(build):
	global build_override_cfg
	global module_cfg
	build_override_cfg.clear()

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
			build_override_cfg = merge_dicts(module_cfg, cfg_replace)
	else:
		build_override_cfg = module_cfg.copy()
	#TODO FRED
	global final_cfg
	final_cfg = build_override_cfg.copy()

# generate all sku specific json
def generate_skuconfig(build):
	global final_cfg
	global build_override_cfg
	final_cfg.clear()

	for cfg in glob.glob("sku/*.cfg"):
		print "handling sku configs %s" % cfg
		standardize_json(cfg, cfg+'.tmp')
		f = open("%s.tmp" % cfg, 'r')
		cfg_j = json.load(f)
		f.close()
		os.system('rm %s.tmp' % cfg)
		final_cfg = merge_dicts(build_override_cfg, cfg_j)

#output the header to the file
def output_header(fout):
	date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	fileheader = header + "// Generated by " + os.path.basename(__file__) + " on " + date + " \n";
	fout.write(fileheader)

#output config
def output_cfg(fout):
	global final_cfg

	# indent=4 does pretty printing for us
	json.dump(final_cfg, fout, indent=4, sort_keys=True)
	
#output the default.cfg file
def output_default_config(build):
	global module_cfg
	global final_cfg
	if not os.path.exists('out'):
		os.mkdir('out')

	filepath = "out/" + build
	if not os.path.exists(filepath):
		os.mkdir(filepath)
	
	filename = "out/" + build + "/" + "default_" + build + ".cfg"
	print filename
	fout = open(filename, 'w')

	output_header(fout)
	output_cfg(fout)
	
	fout.close()

# Standardize and combine multiple configuration files
# into one config that will be used by FunOS
# TBD: handle cases where different files refer to
# the same keys
def parse_output_config(build):
	print "====" + build + "===="
	print "+ Generate cfg"
	generate_build_override_config(build)
	generate_skuconfig(build)
	print "+ Output cfg"
	output_default_config(build)


if __name__ == "__main__":

	#Generate the funos module specific config
	generate_default_moduleconfig()

	#ouput cfg for each build type
	rc = parse_output_config("posix")
	if rc == False:
		print 'Failed to generate config'
		sys.exit(1)

	rc = parse_output_config("malta")
	if rc == False:
 		print 'Failed to generate malta config'
		sys.exit(1)
