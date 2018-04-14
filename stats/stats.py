#!/usr/bin/python
#
# Created by Nag Ponugoti March 28 2018
# Copyright Fungible Inc. 2018

import collections
import glob, os, sys, re, datetime
import getopt, platform, tempfile
import string
import json
from jinja2 import Environment, FileSystemLoader
import pdb
import argparse

from itertools import chain
print os.getcwd()
#sys.path.append('../FunSDK/bin/csr_peek/')

import csr.csr_main as csr
from csr.utils.artifacts import CSRRoot
from csr.utils.schema import Entity
from json_reader import CFG_Reader

class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'

#Groups the range strings
def group_to_range(group):
  group = ''.join(group.split())
  sign, g = ('-', group[1:]) if group.startswith('-') else ('', group)
  r = g.split('-', 1)
  r[0] = sign + r[0]
  r = sorted(int(__) for __ in r)

#Groups the range strings
def range_min_max(group):
  group = ''.join(group.split())
  sign, g = ('-', group[1:]) if group.startswith('-') else ('', group)
  r = g.split('-', 1)
  r[0] = sign + r[0]
  r = sorted(int(__) for __ in r)
  return r[0], 1 + r[-1]

#It comes here for port and queue inputs
class InputNode(object):
	def __init__(self, name, info):
		self.name = name
		self.range_min = 0
		self.range_max = 0
		self.incr = 0
		print "INPUT NODE:{}".format(name)
		self.__process_input(info)
		print ("ADDED INPUT NODE:{} min:{} max:{} incr:{}".format(name,
							self.range_min, self.range_max, self.incr))

	def __process_input(self, info):
		if info["range"] != None:
			min, max = range_min_max(info["range"])
			self.__set_range(min, max)
			self.__set_incr(info["index_incr"])

	def __set_range(self, min, max):
		self.range_min = min
		self.range_max = max

	def __set_incr(self, incr=0):
		self.incr = incr

def indent(tabs):
	return " " * (tabs * 4)

#Comes here for deffirent sub nodes inside q_in but not for q_in
class EntrySubNode(object):
	def __init__(self, e, input):
		self.input_map = collections.OrderedDict()
		self.reg = None
		self.fields = collections.OrderedDict()
		self.offset = None
		self.an_path = None
		self.an = None
		self.an_inst = None
		self.rn_class = None
		self.rn_inst = None
		self.width = None
		self.__process_entry_sub_node(e, input)
		print "ENTRY SUB NODE ADDED"

	def __process_entry_sub_node(self, e, input):
		if input:
			for i in input:
				if e[i] == None or self.input_map.get(i, None) != None:
					sys.exit(1)
				self.input_map[i] = InputNode(i, e[i])
		if e["reg"] is None or not bool(e["fields"]):
			sys.exit(1)
		self.reg = e["reg"]
		self.fields = e["fields"]
		self.offset = e["offset"]
		ring = e.get("ring", None)
		if ring != None:
			self.rn_class = ring.get("class", None)
			self.rn_inst = ring.get("inst", None)
		anode = e.get("anode", None)
		if anode != None:
			self.an_path = anode.get("root", None)
			self.an = anode.get("an", None)
			self.an_inst = anode.get("inst", None)

	def get_fields(self):
		return self.fields

	def get_an_list(self):
		an_set = set()
		an_set.add(self.an)
		print "AN_SET.{}".format(an_set)
		return an_set

	def get_csr_width(self):
		return self.csr_width

	def get_num_fields(self):
		return len(self.fields)

	def get_num_cntrs(self):
		num_cnt = 1
		num_fields = self.get_num_fields()
		for k,v in self.input_map.iteritems():
			rmin = v.range_min
			rmax = v.range_max
			#print k, rmin, rmax, num_fields
			num_cnt *= (rmax - rmin)
		return num_cnt * num_fields

	def gen_objs(self, cnt_offset, callers):
		items = self.input_map.keys()
		max_depth = len(items)
		csr_metadata = csr_defs.get_csr_metadata(self.reg, self.rn_class,
						self.rn_inst, self.an_path, self.an, self.an_inst)
		#print csr_metadata
		an_base_addr = csr_metadata.get_an_base_addr()
		csr_entity = csr_metadata.get_csr_data()
		self.csr_width = (csr_entity.width+63)/64;
		print "CSR ENTITY: {}", format(csr_entity)
		csr_read_objs = ""
		if csr_entity.type == "CSR_TYPE::TBL":
			csr_read_objs += indent(max_depth + 1) + (self.reg +"_iread").upper()
			csr_read_objs += string.Formatter().vformat(("({baddr}, rbuf, {ridxob}ridx{ridxcb});"), (), SafeDict(baddr=hex(an_base_addr))) + "\n"
		else:
			csr_read_objs += indent(max_depth + 1) + (self.reg +"_read").upper()
			csr_read_objs += string.Formatter().vformat("({baddr}, rbuf);", (),
					SafeDict(baddr=hex(an_base_addr))) + "\n"

		cntr_name = callers["element"] + "_" + callers["entry"] + "_stats"
		for i, (k,v) in enumerate(self.fields.items()):
			csr_read_objs += (indent(max_depth + 1) +
							(self.reg + "_" + v + "_read").upper())
			csr_read_objs += ("(rbuf, &" + cntr_name + "[{offsetob}offset{offsetcb} +"+str(i)+"]);") + "\n"
		csr_read_objs = csr_read_objs[:-1]
		num_fields = len(self.fields)

		jstr = ""
		for i, (k,v) in enumerate(self.fields.items()):
			if jstr:
				jstr += ', '
			jstr += cntr_name + "[{offsetob}offset{offsetcb}+" +str(i)+"]"

		jstr = (indent(max_depth + 1) + "const int64_t values[] = {ob}" +
				jstr + "{cb};\n")

		jstr  += (indent(max_depth + 1) + "struct fun_json *dict{j}= " +
				 "fun_json_create_dict_from_int64s(" + str(num_fields) +
				 ", keys, fun_json_no_copy_no_own, values);\n")

		num_counters = num_fields
		if self.offset:
			idx_str = "{}".format(self.offset)
		else:
			idx_str = ""
		if cnt_offset > 0:
			cnt_offset_str = "{}".format(cnt_offset)
		else:
			cnt_offset_str = ""

		for i in range(max_depth):
			idx = max_depth - i - 1
			k = items[idx]
			#print k
			rmin = self.input_map[k].range_min
			rmax = self.input_map[k].range_max
			#print i, max_depth, rmax, rmin, num_counters, num_fields
			num_counters = num_counters * (rmax - rmin)
			incr = self.input_map[k].incr
			if idx_str:
				idx_str += "+"
			idx_str += ("((i_{i}" + ("-{rmin}" if rmin > 0 else "") + ")"
					   + ("*{incr}" if incr > 1 else "")
					   + ")").format(i=idx+1,rmin=rmin,incr=incr)
			if cnt_offset_str:
				cnt_offset_str += "+"
			cnt_offset_str += ("((i_{i}" + ("-{rmin}" if rmin > 0 else "") + ")"
					   + ("*{incr}" if incr > 1 else "")
					   + ")").format(i=idx+1,rmin=rmin,incr=incr)

			r_str = string.Formatter().vformat(indent(idx+1) +
					'for (unsigned int i_{i} = {rmin};'
					+ ' i_{i} < {rmax}; i_{i}++) {ob}' + '\n'
					+ '{r}' + '\n' + indent(idx+1) + '{cb}' , (),
					SafeDict(i=idx+1, rmin=rmin, rmax=rmax, r=csr_read_objs))

			jstr = string.Formatter().vformat(jstr, (),  SafeDict(j=idx+1))
			json_create_objs = string.Formatter().vformat((indent(idx+1)
					+ "struct fun_json *dict{j} = fun_json_create_empty_dict();\n"
					+ indent(idx+1) + 'for (unsigned int i_{i} = {rmin};'
					+ ' i_{i} < {rmax}; i_{i}++) {ob}' + '\n' + '{r}' + '\n'
					+ indent(idx+2) + "char key[32] = {ob}0{cb};\n"
					+ indent(idx+2) + "snprintf(key, 32, \""
					+ items[idx] + "%d\", i_{i});\n" + indent(idx+2) + "fun_json_dict_add(dict{j}, key, fun_json_no_copy_no_own, dict{i}, false);\n"
					+ indent(idx+1) + '{cb}'), (), SafeDict(i=idx+1,
									rmin=rmin, rmax=rmax, r=jstr, j=idx))
			csr_read_objs = r_str
			jstr = json_create_objs
		csr_read_objs = string.Formatter().vformat(csr_read_objs,
				(), SafeDict(ridxob='{', ridxcb='}',
				offsetob='{', offsetcb='}'))

		json_create_objs = string.Formatter().vformat(json_create_objs,
				(), SafeDict(ridxob='{', ridxcb='}',
				offsetob='{', offsetcb='}'))

		cnt_offset_str += "* {}".format(len(self.fields))
		csr_read_objs = string.Formatter().vformat(csr_read_objs,
				(), SafeDict(ridx=idx_str, offset=cnt_offset_str, ob='{', cb='}'))
		json_create_objs = string.Formatter().vformat(json_create_objs,
				(), SafeDict(ridx=idx_str, offset=cnt_offset_str, ob='{', cb='}'))
		return csr_read_objs,json_create_objs

	def get_subnode(self):
		csr_metadata = csr_defs.get_csr_metadata(self.reg, self.rn_class,
				self.rn_inst, self.an_path, self.an, self.an_inst)
		#print csr_metadata
		an_base_addr = csr_metadata.get_an_base_addr()
		csr_entity = csr_metadata.get_csr_data()

		subnode = dict()
		subnode["csr"] = self.reg
		subnode["base_addr"] = an_base_addr
		subnode["csr_width"] = (csr_entity.width+63)/64;
		subnode["fields"] = self.fields
		subnode["csr_idx"] = self.offset
		subnode["input"] = self.input_map
		return subnode



#for q_in it comes here
class EntryNode(object):
	def __init__(self, name, input, info):
		self.name = name
		self.subnodes = list()
		print "PROCESSING ENTRY NODE:{}".format(name)
		self.__process_entry(input, info)
		print "ENTRY NODE ADDED:{}\n".format(name)

	def __process_entry(self, input, info):
		for e in info:
			self.subnodes.append(EntrySubNode(e, input))

	def read_api(self, caller):
		num_cntrs = 0
		rbuf_size = 0;
		subnodes = list()
		for i in self.subnodes:
			subnode = i.get_subnode()
			subnode["cntr_offset"] = num_cntrs
			subnodes.append(subnode)
			num_cntrs += i.get_num_cntrs()
			if subnode["csr_width"] > rbuf_size:
				rbuf_size = subnode["csr_width"]


		#print "\nr_str: {}\n\n".format(r_str)
		#print "\nj_str: {}\n\n".format(j_str)

		gen_objs = dict()
		gen_objs["rbuf_size"] = rbuf_size
		gen_objs["num_cntrs"] = num_cntrs
		gen_objs["subnodes"] = subnodes

		print gen_objs
		return gen_objs

	def get_an_list(self):
		an_set = set()
		for i in self.subnodes:
			an_set |= i.get_an_list()
		return an_set

#For "queue" it comes here
class ElementNode(object):
	EXCLUDE = ["input"]
	def __init__(self, name, info):
		self.name = name
		self.input = list()
		self.entry_map = collections.OrderedDict()
		print "ELEMENT:{}".format(name)
		self.__process_element(info)

	def __process_element(self, info):
		if 'input' in info:
			self.__process_input(info["input"]);
		else:
			self.__process_input();

		for entry in info.keys():
			if entry not in ElementNode.EXCLUDE:
				self.__add_entry_instance(entry, info[entry])

	def __process_input(self, valid_inputs=None):
		self.input = valid_inputs

	def __add_entry_instance(self, entry, data):
		node = self.entry_map.get(entry, EntryNode(entry, self.input, data))
		self.entry_map[entry] = node

	def get_elements(self, callers):
		elements = collections.OrderedDict()
                elements["input"] = self.input
                nodes = collections.OrderedDict()
		for k,v in self.entry_map.iteritems():
			callers["element"] = self.name
			print "ElementNode: {}".format(k)
			nodes[k] = v.read_api(callers)
                elements["nodes"] = nodes
		return elements

	def get_props_bridge_api(self):
		str = ""
		for k,v in self.entry_map.iteritems():
			str += (indent(1) + "fun_json_dict_add(dict, \"" + k + "\"," +
                            "fun_json_no_copy_no_own, " + "{e_name}_{node}_create_json(), false);\n").format(e_name=self.name, node=k);
		return str

	def get_an_list(self):
		an_set = set()
		for k,v in self.entry_map.iteritems():
			an_set |= v.get_an_list()
		return an_set



class ModuleRoot(object):
	def __init__(self, mod, data):
		self.element_map = collections.OrderedDict()
		self.name = mod
		print "\nMOD:{}".format(mod)
		self.__mod_process(mod, data)

	def get_map(self):
		return self.element_map

	def __mod_process(self, m_name, m_data):
		for elem, data in m_data.iteritems():
			self.__add_element_instance(elem, data)

	def __add_element_instance(self, e_name, data):
		element = self.element_map.get(e_name, ElementNode(e_name, data))
		self.element_map[e_name] = element

	def get_elements(self):
		elements = dict()
		for k,v in self.element_map.iteritems():
			callers = {}
			print "ModuleRoot {}".format(k)
			callers["module"] = self.name
			elements[k] = v.get_elements(callers)
		return elements

	def gen_code(self):
		str = ""
		for k,v in self.element_map.iteritems():
			#print k
			str += self.element_map.get(k).read_api()
		str += self.props_bridge_paths()
		return str

	def get_an_list(self):
		an_set = set()
		for k,v in self.element_map.iteritems():
			an_set |= v.get_an_list()
		return an_set

class StatsGen(object):
	def __init__(self, cwd):
		print "Stats Code Generate"
		self.cwd = cwd
		print "CWD: {}".format(cwd)
		self.cmd_parser = argparse.ArgumentParser(description="Stats Code Generatation")
		self.other_args = {}
		self.__arg_process(self.cmd_parser, self.other_args)

	def __arg_process(self, cmd_parser, other_args):
		def_dir = os.path.join(self.cwd, "Configfiles/stats")
		cmd_parser.add_argument("-c", "--cfg-dir", help="Dir for config files",
				default=def_dir, required=False, type=str)

		cmd_parser.add_argument("-o", "--out-dir", help="Dir for generated files",
				required=True, type=str)

		sdk_dir = os.path.join(self.cwd, "../FunSDK")
		cmd_parser.add_argument("-s", "--sdk-dir", help="SDK root directory",
				default=sdk_dir, required=False, type=str)

		self.other_args['tmpl_dir'] = os.path.join(self.cwd, "template")

	def __update_loc(self, loc):
		if not os.path.isabs(loc):
			loc = os.path.join(self.cwd, loc)

		assert os.path.exists(loc), "{}: directory does not exist!".format(loc)
		return loc

	def run(self):
		global csr_defs
		args = self.cmd_parser.parse_args()
		args.cfg_dir = self.__update_loc(args.cfg_dir)
		args.out_dir = self.__update_loc(args.out_dir)
		args.sdk_dir = self.__update_loc(args.sdk_dir)

		cfg = CFG_Reader(args.cfg_dir)
		sdk_csr_cfg_dir = args.sdk_dir + "/FunSDK/config/"
		csr_slrp = csr.Slurper(os.getcwd(), sdk_csr_cfg_dir)
		csr_defs = csr_slrp.get_csr_defs()

		path = os.path.dirname(os.path.abspath(__file__))
		print os.path.join(path, 'templates')
		ENVIRONMENT = Environment( autoescape=False,
			loader=FileSystemLoader(os.path.join(path, 'templates')),
		trim_blocks=False)
		template = ENVIRONMENT.get_template("source.j2")

		#Generate the funos source code
		inc_path = ""
		code_str = ""
		for i, (k,v) in enumerate(cfg.get().iteritems()):
			mod = ModuleRoot(k, v)
			headers= mod.get_an_list()
			gen_objs = dict()
			gen_objs["elements"] = mod.get_elements()
			gen_objs["dyn_headers"] = headers
			gen_objs["block"] = k
                        fname = "fun_{}_stats.c".format(k)
			gen_objs["fname"] = fname
                        print fname
                        with open(os.path.join(args.out_dir, fname), 'w') as f:
                            f.write(template.render(gen_objs))
                        f.close()

csr_def = None
if __name__ == "__main__":
	stats_gen = StatsGen(os.getcwd())
	stats_gen.run()

