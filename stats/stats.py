#!/usr/bin/python
#
# Created by Nag Ponugoti March 28 2018
# Copyright Fungible Inc. 2018

import glob, os, sys, re, datetime
import getopt, platform, tempfile
import string, json, collections
import pdb, argparse
from jinja2 import Environment, FileSystemLoader
from subprocess import call
from itertools import chain

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
				self.poll_interval = 0
				self.clear_on_read = False
				self.__process_entry_subnode(e, input)
				print "ENTRY SUBNODE ADDED"

		def __process_entry_subnode(self, e, input):
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
				self.poll_interval = e.get("poll_interval", 0)
				self.clear_on_read = e.get("clear_on_read", False)
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

		def get_poll_interval(self):
			return self.poll_interval

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
						print k, rmin, rmax, num_fields
						num_cnt *= (rmax - rmin)
				return num_cnt * num_fields

		def get_gen_objs(self):
				csr_metadata = csr_defs.get_csr_metadata(self.reg, self.rn_class,
								self.rn_inst, self.an_path, self.an, self.an_inst)
				#print csr_metadata
				an_base_addr = csr_metadata.get_an_base_addr()
				csr_entity = csr_metadata.get_csr_data()

				subnode = dict()
				subnode["csr"] = self.reg
				subnode["base_addr"] = hex(an_base_addr)
				subnode["csr_width"] = (csr_entity.width+63)/64
				subnode["csr_type"] = csr_entity.type
				fields = collections.OrderedDict()
				csr_flds = csr_entity.fld_lst
				for csr_fld in csr_flds:
					for k,v in self.fields.iteritems():
						if csr_fld.fld_name == v:
							fields[k] = (csr_fld.fld_name, csr_fld.width)
				subnode["fields"] = fields
				subnode["csr_offset"] = self.offset
				subnode["input"] = self.input_map

				print "CSR: {}".format(csr_entity)
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

		def get_gen_objs(self):
				num_cntrs = 0
				rbuf_size = 0;
				poll_interval = sys.maxsize;
				subnodes = list()

				for i in self.subnodes:
						subnode = i.get_gen_objs()
						subnode["cntr_offset"] = num_cntrs
						subnodes.append(subnode)
						num_cntrs += i.get_num_cntrs()
						if subnode["csr_width"] > rbuf_size:
								rbuf_size = subnode["csr_width"]
						if i.get_poll_interval() < poll_interval:
							poll_interval = i.get_poll_interval()

				gen_objs = dict()
				gen_objs["rbuf_size"] = rbuf_size
				gen_objs["num_cntrs"] = num_cntrs
				gen_objs["subnodes"] = subnodes
				if poll_interval == sys.maxsize:
					gen_objs["poll_interval"] = 0
				else:
					gen_objs["poll_interval"] = poll_interval
				print "{} POLL INTERVAL: {}".format(self.name, poll_interval)

				return gen_objs

		def get_an_list(self):
				an_set = set()
				for i in self.subnodes:
						an_set |= i.get_an_list()
				return an_set

#For "queue" it comes here
class EndPoint(object):
		EXCLUDE = ["input"]
		def __init__(self, name, info):
				self.name = name
				self.input = list()
				self.entry_map = collections.OrderedDict()
				print "ELEMENT:{}".format(name)
				self.__process_endpoint(info)

		def __process_endpoint(self, info):
				if 'input' in info:
						self.__process_input(info["input"]);
				else:
						self.__process_input();

				for k,v in info.iteritems():
						if k not in EndPoint.EXCLUDE:
								self.__add_entry_instance(k, v)

		def __process_input(self, valid_inputs=None):
				self.input = valid_inputs

		def __add_entry_instance(self, entry, data):
				node = self.entry_map.get(entry, EntryNode(entry, self.input, data))
				self.entry_map[entry] = node

		def get_gen_objs(self):
				modules = collections.OrderedDict()
				modules["input"] = self.input
				nodes = collections.OrderedDict()
				for k,v in self.entry_map.iteritems():
						print "EntryNode: {}".format(k)
						nodes[k] = v.get_gen_objs()
				modules["nodes"] = nodes
				return modules

		def get_an_list(self):
				an_set = set()
				for k,v in self.entry_map.iteritems():
						an_set |= v.get_an_list()
				return an_set

#For "qos" it comes here
class ModuleNode(object):
		def __init__(self, name, info):
				print "MODULE:{}".format(name)
				self.name = name
				self.endpoint_map = collections.OrderedDict()
				self.__process_module(info)

		def __process_module(self, info):
			for k,v in info.iteritems():
				self.__add_endpoint_instance(k, v)

		def __add_endpoint_instance(self, endpoint, data):
				node = self.endpoint_map.get(endpoint, EndPoint(endpoint, data))
				self.endpoint_map[endpoint] = node

		def get_gen_objs(self):
				endpoints = collections.OrderedDict()
				for k,v in self.endpoint_map.iteritems():
					print "Endpoint: {}".format(k)
					endpoints[k] = v.get_gen_objs()
				return endpoints

		def get_an_list(self):
				an_set = set()
				for k,v in self.endpoint_map.iteritems():
						an_set |= v.get_an_list()
				return an_set

class BlockRoot(object):
		def __init__(self, block, data):
				self.module_map = collections.OrderedDict()
				self.name = block
				print "\nMOD:{}".format(block)
				self.__block_process(data)

		def __block_process(self, data):
				for k,v in data.iteritems():
						self.__add_module_instance(k, v)

		def __add_module_instance(self, k, v):
				module = self.module_map.get(k, ModuleNode(k, v))
				self.module_map[k] = module

		def get_gen_objs(self):
				modules = dict()
				for k,v in self.module_map.iteritems():
						print "BlockRoot {}".format(k)
						modules[k] = v.get_gen_objs()
				return modules

		def get_an_list(self):
				an_set = set()
				for k,v in self.module_map.iteritems():
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
						block = BlockRoot(k, v)
						headers= block.get_an_list()
						gen_objs = dict()
						gen_objs["modules"] = block.get_gen_objs()
						gen_objs["dyn_headers"] = headers
						gen_objs["block"] = k
						file = "fun_{}_stats.c".format(k)
						gen_objs["file"] = file
						print file
						with open(os.path.join(args.out_dir, file), 'w') as f:
							f.write(template.render(gen_objs))
						f.close()
						cmd = "indent -br -npsl -l120 -i4 -nut " + os.path.join(args.out_dir, file)
						os.system(cmd)

csr_def = None
if __name__ == "__main__":
		stats_gen = StatsGen(os.getcwd())
		stats_gen.run()

