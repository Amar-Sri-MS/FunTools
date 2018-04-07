#
#  module.py
#
#  Created by Nag Ponugoti on 2018-03-29
#
#  Copyright 2018 Fungible Inc. All rights reserved.
#
# Process stats config file

import collections
import os
import jinja2
import pdb
import re
import string
import csr.csr_main as csr
from csr.utils.artifacts import CSRRoot, Walker, RingUtil, TmplMgr
from csr.utils.schema import Entity

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

#Groups and expands range strings
def rangeexpand(txt):
  ranges = chain.from_iterable(group_to_range(__) for __ in txt.split(','))
  return sorted(set(ranges))

#It comes here for poer and queue inputs
class InputNode(object):
	def __init__(self, name, info):
		self.name = name
		self.range_min = 0
		self.range_max = 0
		self.incr = 0
		print "INPUT NODE:{}".format(name)
		self.__process_input(info)
		print "ADDED INPUT NODE:{} min:{} max:{} incr:{}".format(name, self.range_min, self.range_max, self.incr)

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

	def get_csr_width(self):
		return self.csr_width

	def get_num_fields(self):
		return len(self.fields)

	def get_num_counters(self):
		num_cnt = 1
		num_fields = self.get_num_fields()
		for k,v in self.input_map.iteritems():
			rmin = v.range_min
			rmax = v.range_max
			print k, rmin, rmax, num_fields
			num_cnt *= (rmax - rmin)
		return num_cnt * num_fields

	def read_api(self, csr_root, boffset):
		items = self.input_map.keys()
		max_depth = len(items)
		csr_metadata = csr_root.get_csr_metadata(self.reg, self.rn_class, self.rn_inst,
									  self.an_path, self.an, self.an_inst)
		#print csr_metadata
		an_base_addr = csr_metadata.get_an_base_addr()
		csr_entity = csr_metadata.get_csr_data()
		self.csr_width = (csr_entity.width+63)/64;
		print csr_entity
		reg = ""
		if csr_entity.type == "CSR_TYPE::TBL":
			reg += indent(max_depth + 1) + (self.reg +"_iread").upper()
			reg += string.Formatter().vformat("({baddr}, rbuf, {ridxob}ridx{ridxcb});", (), SafeDict(baddr=hex(an_base_addr))) + "\n"
		else:
			reg += indent(max_depth + 1) + (self.reg +"_read").upper()
			reg += string.Formatter().vformat("({baddr}, rbuf);", (), SafeDict(baddr=hex(an_base_addr))) + "\n"


		for i, (k,v) in enumerate(self.fields.items()):
			reg += indent(max_depth + 1) + (self.reg + "_" + v + "_read").upper()
			reg += "(rbuf, &{ptrob}bptr{ptrcb}[{offsetob}offset{offsetcb}+"+str(i)+"]);" + "\n"
		reg = reg[:-1]

		r_str = reg

		num_fields = len(self.fields)
		num_counters = num_fields
		if self.offset:
			idx_str = "{}".format(self.offset)
		else:
			idx_str = ""
		if boffset > 0:
			boffset_str = "{}".format(boffset)
		else:
			boffset_str = ""
		for i in range(max_depth):
			idx = max_depth - i - 1
			k = items[idx]
			#print k
			rmin = self.input_map[k].range_min
			rmax = self.input_map[k].range_max
			print i, max_depth, rmax, rmin, num_counters, num_fields
			num_counters = num_counters * (rmax - rmin)
			incr = self.input_map[k].incr
			if idx_str:
				idx_str += "+"
			idx_str += ("((i_{i}" + ("-{rmin}" if rmin > 0 else "") + ")"
					   + ("*{incr}" if incr > 1 else "")
					   + ")").format(i=idx,rmin=rmin,incr=incr)
			if boffset_str:
				boffset_str += "+"
			boffset_str += ("((i_{i}" + ("-{rmin}" if rmin > 0 else "") + ")"
					   + ("*{incr}" if incr > 1 else "")
					   + ")").format(i=idx,rmin=rmin,incr=incr)

			tw = 4 #tab width
			print type(r_str)
			l_str = string.Formatter().vformat(" "* tw * (idx+1) + 'for (unsigned int i_{i} = {rmin};'
					+ ' i_{i} < {rmax}; i_{i}++) {ob}' + '\n' + '{r}' + '\n' +" "* tw *(idx+1) + '{cb}' , (),
					SafeDict(i=idx, rmin=rmin, rmax=rmax, r=r_str))
			r_str = l_str
		#print r_str
		r_str = string.Formatter().vformat(r_str, (), SafeDict(ridxob='{', ridxcb='}',
				offsetob='{', offsetcb='}'))
		boffset_str += "* {}".format(len(self.fields))
		r_str = string.Formatter().vformat(r_str, (), SafeDict(ridx=idx_str, offset=boffset_str))
		#r_str = string.Formatter().vformat(" "* tw + "uint64_t rbuf[{bsize}] = {ob}0{cb};\n", (),
		#		SafeDict(bsize=csr_width)) + r_str
		#r_str = string.Formatter().vformat(r_str, (), SafeDict(ob='{', cb='}'))
		#print idx_str
		#r_str = r_str % ("rbuf", idx_str)
		#r_str =  string.Formatter().vformat(str(r_str), (), SafeDict(index=idx_str, bptr='sds'))
		print "{} NUM COUNTERS: {}".format(self.reg, num_counters)
		return r_str

	def create_json(self, csr_root, boffset):
		items = self.input_map.keys()
		max_depth = len(items)
		csr_metadata = csr_root.get_csr_metadata(self.reg, self.rn_class, self.rn_inst,
									  self.an_path, self.an, self.an_inst)
		#print csr_metadata
		an_base_addr = csr_metadata.get_an_base_addr()
		csr_entity = csr_metadata.get_csr_data()
		self.csr_width = (csr_entity.width+63)/64;
		print csr_entity
		reg = ""
		if csr_entity.type == "CSR_TYPE::TBL":
			reg += indent(max_depth + 1) + (self.reg +"_iread").upper()
			reg += string.Formatter().vformat("({baddr}, rbuf, {ridxob}ridx{ridxcb});", (), SafeDict(baddr=hex(an_base_addr))) + "\n"
		else:
			reg += indent(max_depth + 1) + (self.reg +"_read").upper()
			reg += string.Formatter().vformat("({baddr}, rbuf);", (), SafeDict(baddr=hex(an_base_addr))) + "\n"


		for i, (k,v) in enumerate(self.fields.items()):
			reg += indent(max_depth + 1) + (self.reg + "_" + v + "_read").upper()
			reg += "(rbuf, &{ptrob}bptr{ptrcb}[{offsetob}offset{offsetcb}+"+str(i)+"]);" + "\n"
		reg = reg[:-1]

		r_str = reg

		num_fields = len(self.fields)
		num_counters = num_fields
		if self.offset:
			idx_str = "{}".format(self.offset)
		else:
			idx_str = ""
		if boffset > 0:
			boffset_str = "{}".format(boffset)
		else:
			boffset_str = ""
		for i in range(max_depth):
			idx = max_depth - i - 1
			k = items[idx]
			#print k
			rmin = self.input_map[k].range_min
			rmax = self.input_map[k].range_max
			print i, max_depth, rmax, rmin, num_counters, num_fields
			num_counters = num_counters * (rmax - rmin)
			incr = self.input_map[k].incr
			if idx_str:
				idx_str += "+"
			idx_str += ("((i_{i}" + ("-{rmin}" if rmin > 0 else "") + ")"
					   + ("*{incr}" if incr > 1 else "")
					   + ")").format(i=idx,rmin=rmin,incr=incr)
			if boffset_str:
				boffset_str += "+"
			boffset_str += ("((i_{i}" + ("-{rmin}" if rmin > 0 else "") + ")"
					   + ("*{incr}" if incr > 1 else "")
					   + ")").format(i=idx,rmin=rmin,incr=incr)

			tw = 4 #tab width
			print type(r_str)
			l_str = string.Formatter().vformat(" "* tw * (idx+1) + 'for (unsigned int i_{i} = {rmin};'
					+ ' i_{i} < {rmax}; i_{i}++) {ob}' + '\n' + '{r}' + '\n' +" "* tw *(idx+1) + '{cb}' , (),
					SafeDict(i=idx, rmin=rmin, rmax=rmax, r=r_str))
			r_str = l_str
		#print r_str
		r_str = string.Formatter().vformat(r_str, (), SafeDict(ridxob='{', ridxcb='}',
				offsetob='{', offsetcb='}'))
		boffset_str += "* {}".format(len(self.fields))
		r_str = string.Formatter().vformat(r_str, (), SafeDict(ridx=idx_str, offset=boffset_str))
		#r_str = string.Formatter().vformat(" "* tw + "uint64_t rbuf[{bsize}] = {ob}0{cb};\n", (),
		#		SafeDict(bsize=csr_width)) + r_str
		#r_str = string.Formatter().vformat(r_str, (), SafeDict(ob='{', cb='}'))
		#print idx_str
		#r_str = r_str % ("rbuf", idx_str)
		#r_str =  string.Formatter().vformat(str(r_str), (), SafeDict(index=idx_str, bptr='sds'))
		print "{} NUM COUNTERS: {}".format(self.reg, num_counters)
		return r_str


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

	def read_api(self, csr_root):
		r_str = ""
		boffset = 0
		rbuf_size = 0;
		for i in self.subnodes:
			r_str += '\n' + i.read_api(csr_root, boffset)
			print "NUM COUNTERS: {}".format(i.get_num_counters())
			boffset += i.get_num_counters()
			if i.get_csr_width() > rbuf_size:
				rbuf_size = i.get_csr_width()

		ctr_name = string.Formatter().vformat("{e_name}_{node}_stats", (),
						SafeDict(node=self.name, s=r_str))
		ctr_name = string.Formatter().vformat(ctr_name, (), SafeDict(node=self.name))
		print "COUNTER: {}".format(ctr_name)
		r_str = string.Formatter().vformat(r_str, (), SafeDict(ptrob='{', ptrcb='}'))

		r_str = string.Formatter().vformat(r_str, (),
				SafeDict(s=r_str, bptr=ctr_name))

		#print "R_STR1: {}".format(r_str)

		tw = 4
		r_str = "static uint64_t " + ctr_name + "[{boffset}];\n" + "void {e_name}_{node}_read() {ob}\n"+ " "* tw + "uint64_t rbuf[{bsize}] = {ob}0{cb};\n" + r_str + "\n{cb}\n"

		r_str = string.Formatter().vformat(r_str, (),
				SafeDict(boffset=boffset, node=self.name, bsize=rbuf_size))
		#r_str = string.Formatter().vformat(r_str, (), SafeDict(ob='{', cb='}'))
		#print r_str
		return r_str

	#def gen_props_bridge_api(self):





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

	def read_api(self, csr_root):
		for k,v in self.entry_map.iteritems():
			print k
			e_str = self.entry_map[k].read_api(csr_root)
			#print e_str
			e_str = string.Formatter().vformat(e_str, (), SafeDict(e_name = self.name))
			#print e_str
			e_str = string.Formatter().vformat(e_str, (), SafeDict(ob='{', cb='}'))
			print e_str
	def gen_props_bridge_api(self):
		for k,v in self.entry_map.iteritems():
			api = self.entry_map[k].gen_props_bridge_api(csr_root)

#	def get_props(self):



class ModuleRoot(object):
	def __init__(self, mod, data):
		self.element_map = collections.OrderedDict()
		self.name = mod
		print "\nMOD:{}".format(mod)
		self.__mod_process(mod, data)
		csr_slrp = csr.Slurper(os.getcwd())
		self.csr_root = csr_slrp.run()
		self.gen_code()

	def get_map(self):
		return self.element_map

	def __mod_process(self, m_name, m_data):
		for elem, data in m_data.iteritems():
			self.__add_element_instance(elem, data)

	def __add_element_instance(self, e_name, data):
		element = self.element_map.get(e_name, ElementNode(e_name, data))
		self.element_map[e_name] = element

	def gen_code(self):
		for k,v in self.element_map.iteritems():
			print k
			self.element_map.get(k).read_api(self.csr_root)
			self.props_bridge_paths()

	#props bridge install
	def props_bridge_paths(self):
		props_path = "stat_{}_prop_path".format(self.name).upper()
		props_tmpl = ("\tstruct fun_props_bridge_point *"+ self.name +"_{elem}_bridge MAYBE_UNUSED = " +
					"fun_props_install_bridge_point(" +
					"{mpath} {epath}, NULL, {gen});\n")

		props_str = ""
		elem_path = ""
		path_defs = "#define " + props_path + " " + "/stat/" + self.name + "\n"
		for k,v in self.element_map.iteritems():
			elem_path_macro = ("stat_" + self.name + "_{}_path".format(k)).upper()
			path_defs += "#define " + elem_path_macro + " " + k + "\n"
			gen_api = self.name + "_{elem}_generate_json".format(elem=k)
			props_str += props_tmpl.format(mpath=props_path, elem=k, epath=elem_path_macro, gen=gen_api) + "\n"

		str = path_defs + "\n"
		str += ("void "+ self.name + "_props_bridge_install(void) {\n" +
				props_str + "}")
		print str
