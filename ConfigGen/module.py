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
		self.reg = ""
		self.fields = collections.OrderedDict()
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


	def read_api(self):
		items = self.input_map.keys()
		max_depth = len(items)
		reg = ""
		reg += indent(max_depth + 1) + (self.reg +"_read").upper() + "\n"
		for k,v in self.fields.iteritems():
			reg += indent(max_depth + 1) + (self.reg + v + "_read").upper() + "\n"
		reg = reg[:-1]

		r_str = reg
		for i in range(max_depth):
			idx = max_depth - i - 1
			k = items[idx]
			print k
			l_str = string.Formatter().vformat(" "*4*(idx+1) + 'for (unsigned int i{i} = {rmin};'
					+ ' i{i} < {rmax}; i{i}++) {{' + '\n' + '{r}' + '\n' +" "*4*(idx+1) + '}}' , (),
					SafeDict(i=i, rmin=self.input_map[k].range_min,
					rmax=self.input_map[k].range_max, r=r_str))
			r_str = l_str
		#print r_str
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

	def read_api(self):
		r_str = ""
		for i in self.subnodes:
			print "NAGES"
			r_str += '\n' + i.read_api()
		r_str = ("_{node}_read() {{\n"+ "{s}" + "\n}}\n").format(node=self.name, s=r_str)
		#print r_str
		return r_str

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

	def read_api(self):
		for k,v in self.entry_map.iteritems():
			print 'NAG ' + k
			e_str = self.entry_map[k].read_api()
			print "void {e_name}{e_str}".format(e_name = self.name, e_str=e_str)


class ModuleRoot(object):
	def __init__(self, mod, data):
		self.element_map = collections.OrderedDict()
		print "\nMOD:{}".format(mod)
		self.__mod_process(mod, data)
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
			self.element_map.get(k).read_api()

