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

import glob, os, sys, re, datetime
import getopt, platform, tempfile

from itertools import chain
import json
from string import Template

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

#hw capalibilty catalog
cfg_data_catalog = {}

#hw capalibilty config
hwcap_cfg = {}

input_base = ""
output_base = ""
jsonutil_base = ""
hwcap_gen = 0
cfg_code_gen_out_base = ""

header = """
// AUTOGENERATED FILE - DO NOT EDIT
"""

# Input: json with comments and hex values
# Output: json
def standardize_json(in_cfg, out_cfg):
	global jsonutil_base

	jsonutil_tool = os.path.join(jsonutil_base, 'jsonutil')

        cmd = '%s -i %s -o %s' % (jsonutil_tool, in_cfg, out_cfg)

        # print "running command '%s'" % cmd

	r = os.system(cmd)

        if (r != 0):
	        # Failures of jsontool are often caused by jsontool being built
	        # on a different system/OS than the one currently running.
		sys.stderr.write('Unable to run jsonutil tool. Exiting.\n')
                sys.exit(1)

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
  	global input_base

	print "==== Module config ===="
	for cfg in glob.glob(input_base + "/configs/*.cfg"):
		print "handling module config %s" % cfg
                f = tempfile.NamedTemporaryFile(mode="r")
                print "working with temp file %s" % f.name
		standardize_json(cfg, f.name)
		cfg_j = json.load(f)
		f.close() # auto-deleted
		module_cfg = merge_dicts(module_cfg, cfg_j)

# generate build override config.
def generate_build_override_config(build):
	global build_override_cfg
	global module_cfg
  	global input_base
	build_override_cfg.clear()

	#update build specific config
	filedir = input_base + "/" + build
	if os.path.exists(filedir):
		filename = input_base + "/" + build+ "/*.cfg"
		print filename
		for cfg in glob.glob(filename):
			print "handling " + build + " cfg %s" % cfg
                        f = tempfile.NamedTemporaryFile(mode="r")
			standardize_json(cfg, f.name)
			cfg_replace = json.load(f)
			f.close() # auto-delete
			build_override_cfg = merge_dicts(module_cfg,
                                                         cfg_replace)
	else:
		build_override_cfg = module_cfg.copy()

	#TODO FRED
	global final_cfg
	final_cfg = build_override_cfg.copy()

# Generate all hw capabilities config
def generate_hwcap_config(build):
	global hwcap_cfg
	global input_base
	hwcap_cfg.clear()

        for cfg in glob.glob(input_base +"/sku/hwcap/*.cfg"):
		print "handling hwcap configs %s" % cfg
		standardize_json(cfg, cfg+'.tmp')
		f = open("%s.tmp" % cfg, 'r')
		cfg_j = json.load(f)
		f.close()
		os.system('rm %s.tmp' % cfg)
		hwcap_cfg = merge_dicts(hwcap_cfg, cfg_j)

# generate all sku specific json
def generate_sku_config(build):
	global final_cfg
	global build_override_cfg
	global hwcap_cfg
  	global input_base
	final_cfg.clear()

	print "handling sku configs"
	for cfg in glob.glob(input_base +"/sku/*.cfg"):
		print "handling sku configs %s" % cfg
                f = tempfile.NamedTemporaryFile(mode="r")
		standardize_json(cfg, f.name)
		cfg_j = json.load(f)
		f.close() # auto-delete
		final_cfg = merge_dicts(build_override_cfg, cfg_j)

        for sku in final_cfg["skus"].iterkeys():
            if hwcap_cfg.has_key("skus"):
                if hwcap_cfg["skus"].has_key(sku):
                    print "Adding hwcap of sku %s" % sku
                    final_cfg["skus"][sku].update(hwcap_cfg["skus"][sku])

#Generates struct members initialization code
def generate_struct_member_init(struct, data, shift):
        init_field = Template('.$key = $value,')
        s =''
        dictItemCount = len(data)
        dictPosition = 1
        for k,v in data.items():
	    if k in cfg_data_catalog["modules"][struct]["info"]:
	        s += '\t'*shift+init_field.substitute(key=k, value=v)
                if not (dictPosition == dictItemCount):
                    s+="\n"
                dictPosition += 1
            else:
		print "hwcap: %s does not exist in hwcap catalog of %s" %(k, struct)
        return s

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

#Generates enum definition
def generate_data_catalog_enum(enums):
	enum= Template('enum $name {\n$defs\n};\n\n')
        enum_field = Template('\t$f = $v,')
        enum_defs = ''
        for ename,elist in enums.items():
            s =''
            dictItemCount = len(elist)
            dictPosition = 1
            for k, v in elist.items():
                s += enum_field.substitute(f=k, v=v)
                if not (dictPosition == dictItemCount):
                    s+="\n"
                dictPosition += 1
            enum_defs += enum.substitute(name=ename, defs=s)
        return enum_defs

#Generates bit-field structure definition
def generate_catalog_structure(s_name, value, indent, instance):
        not_nested = 0
        if(instance == 0):
            not_nested = 1;
	struct = Template((indent -1) *'\t' + 'struct __attribute__ ((packed)) $name {\n'
                + '$fields\n'
                + (indent -1) * '\t' + '}'
                + instance * (" " + s_name)
                + ';\n' + not_nested * '\n')
        struct_field = Template(indent * '\t'+'unsigned int $field:$size;')
        s =""
        dictItemCount = len(value)
        dictPosition = 1
        for i in value:
            size = 1
            if type(i) == dict:
                if len(i) == 1:
                    key = list(i.keys())[0]
                    value = i[key]
                    if type(value) == list:
                        indent1 = indent + 1
                        s += generate_catalog_structure(key, value, indent1, 1)
                    else:
                        s += struct_field.substitute(field=key, size=value)
                else:
                    indent1 = indent + 1
                    for k,v in i.items():
                        s += generate_catalog_structure(k, v, indent1, 1)
            else:
                s += struct_field.substitute(field=i, size=size)
            if not (dictPosition == dictItemCount):
                s+="\n"
            dictPosition += 1
        return struct.substitute(name=s_name+"_cfg", fields=s)

#Generates structure definition
def generate_structure_definition(s_name, value):
	struct = Template('struct __attribute__ ((packed)) $sname {\n$fields\n};\n\n')
        struct_field = Template('\tstruct ${field}_cfg $field;')
        struct_field_array = Template('\tstruct ${field}_cfg $field[$size];')
        s =''
        dictItemCount = len(value)
        dictPosition = 1
        for k,v in value.items():
	    if v > 1:
                s += struct_field_array.substitute(field=k, size=v)
	    else:
		s += struct_field.substitute(field=k)

            if not (dictPosition == dictItemCount):
                s+="\n"
            dictPosition += 1
        return struct.substitute(sname=s_name+"_cfg", fields=s)

#Build cfg data catalog
def generate_hwcap_data_catalog():
    global cfg_data_catalog

    for cfg in glob.glob(input_base +"/sku/hwcap/*catalog.cfg"):
	    print "handling hwcap catalog %s" % cfg
	    standardize_json(cfg, cfg+'.tmp')
	    f = open("%s.tmp" % cfg, 'r')
	    cfg_j = json.load(f)
	    f.close()
	    os.system('rm %s.tmp' % cfg)
	    cfg_data_catalog = merge_dicts(cfg_data_catalog, cfg_j)

#Generate c header file for the config data catalog
def generate_cfg_header_file(cfg_name, data_catalog, out_base, header_file, input_base):
    struct_defs = ""
    structs_catalog = {}

    print "Generating config data header file"
    file_templ = Template('// Source file generated by ' + __file__ + ' at $date \n'\
			  '// Do not change this file\n'\
			  '// Change the ' + cfg_name + ' files in ' + input_base + '\n\n\n$data\n')
    extern_struct_array_templ = Template('\nextern struct ${s_name}_cfg ${s_name}[];\n');

    f = open("%s" % out_base + header_file, 'w')
    for k, v in data_catalog["modules"].items():
	struct_defs += generate_catalog_structure(k, v["info"], 1, 0)
	structs_catalog[k] = v["inst_cnt"]

    struct_defs += generate_structure_definition(cfg_name, structs_catalog)
    enums = generate_data_catalog_enum(data_catalog["enums"])
    extern_struct_decl = extern_struct_array_templ.substitute(s_name=cfg_name)

    f.write(file_templ.substitute(data=enums + struct_defs + extern_struct_decl,
		input_base=input_base,
		date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    f.close()

#Generate c file for the config data
def generate_cfg_c_file(cfg_name, cfg_data, out_base, c_file, header_file, input_base):
    sku_cfg = ""

    print "Generating config data c file"
    src_file_templ = Template('// Source file generated by ' + __file__ + ' at $date \n'\
			  '// Do not change this file\n'\
			  '// Change the ' + cfg_name + ' files in ' + input_base + '\n\n\n$data\n')

    c_file_templ = Template('#include <$include_file>\n\n\n'\
			    'struct ' + cfg_name + '_cfg ' +  cfg_name + '[] = {\n$cfg\n};')

    f = open("%s" % cfg_code_gen_out_base + c_file, 'w')
    sku_init = Template('[$sku] = {\n$struct\n\t},\n')
    struct_init = Template('.$struct = {\n$init\n\t\t},\n')
    for k1,v1 in cfg_data.items():
	cfg_str = ""
        for k2,v2 in v1[cfg_name].items():
            if (isinstance(v2,(list,))):
                for item in v2:
		    for i in rangeexpand(item["id"]):
			if i < cfg_data_catalog["modules"][k2]["inst_cnt"]:
                            cfg_str += '\t'*2+struct_init.substitute(struct=k2+"["+str(i)+"]",
				 init=generate_struct_member_init(k2, item["info"], 3))
            else :
                cfg_str += '\t'*2+struct_init.substitute(struct=k2,
					init=generate_struct_member_init(k2, v2["info"], 3))
	sku_cfg+='\t'+sku_init.substitute(sku=k1,struct=cfg_str)

    sku_cfg = c_file_templ.substitute(cfg=sku_cfg,
                include_file = out_base + header_file)
    f.write(src_file_templ.substitute(data=sku_cfg, input_base=input_base,
				  date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
				  include_file=header_file))
    f.close()

#Generates sku hw capability config source code
def generate_hwcap_config_code():
    global hwcap_cfg
    c_file = "hw_cap_config.c"
    header_file = "hw_cap_config.h"

    print "Generating config source code"
    generate_cfg_header_file("hwcap", cfg_data_catalog, cfg_code_gen_out_base, header_file, input_base)
    generate_cfg_c_file("hwcap", hwcap_cfg["skus"], cfg_code_gen_out_base, c_file, header_file, input_base)

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
	global output_base
	global module_cfg
	global final_cfg

	filepath = output_base
	if not os.path.exists(filepath):
		os.makedirs(filepath)

	filename = output_base + "default_" + build + ".cfg"
	print filename
	fout = open(filename, 'w')

	output_header(fout)
	output_cfg(fout)
	fout.close()

	#TODO fred fix with build based runtime override
	# for now use posix as default.cfg
	if build == "posix":
		filename = output_base + "default.cfg"
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
        generate_hwcap_data_catalog()
        generate_hwcap_config(build)
        generate_sku_config(build)
        print "+ Output cfg"
        output_default_config(build)
        if hwcap_gen == 1:
            print "Generating hwcap config src code"
            generate_hwcap_config_code()


def Usage():
	sys.stderr.write('cfg_gen.py: usage: [-i [cfg input dir] [-o cfg output dir] [-s hwcap src code out dir]\n')

def main():
  	global output_base
  	global input_base
  	global jsonutil_base
        global cfg_code_gen_out_base
        global hwcap_gen

	print "Configfile Generation"
	try:
            opts, args = getopt.getopt(sys.argv[1:], 'hi:o:s:j:g:')

	except getopt.GetoptError as err:
		print str(err)
    		Usage()
    		sys.exit(2)

  	for o, a in opts:
    		if o in ('-h', '--help'):
      			Usage()
      			sys.exit(1)
    		elif o in ('-j', '--jsonutil'):
      			jsonutil_base = a
      			print "jsonutil dir: " + a
    		elif o in ('-i', '--input'):
      			input_base = a
      			print "input dir: " + a
    		elif o in ('-o', '--output'):
      			output_base = a
      			print "output dir: " + a
                elif o in ('-s', '--src'):
                        cfg_code_gen_out_base = a
                        hwcap_gen = 1
                        print "hwcap source code output dir: " + a
    		else:
      			assert False, 'Unhandled option %s' % o

        if (jsonutil_base is None):
                jsonutil_base = jsonutil_path()

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



if __name__ == "__main__":
	main()
