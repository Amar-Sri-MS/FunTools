#!/usr/bin/env python
from __future__ import print_function

from bpf_pack import unpack_u32
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from elftools.elf.relocation import RelocationSection
from elftools.dwarf.descriptions import describe_form_class, describe_attr_value

# extracted from kernels/hook.c
central_hook = {
  'code': {'name': u'probe',
    'value': [103, 189, 255, 192, 255, 191, 0, 24, 255, 190, 0, 16, 3, 160, 240, 37, 255, 164, 0, 32, 255, 165, 0, 40, 255, 166, 0, 48, 255, 167, 0, 56, 0, 0, 0, 0, 223, 164, 0, 32, 223, 165, 0, 40, 223, 166, 0, 48, 223, 167, 0, 56, 0, 0, 0, 0, 255, 162, 0, 32, 255, 163, 0, 40, 0, 0, 0, 0, 223, 162, 0, 32, 223, 163, 0, 40, 3, 192, 232, 37, 223, 191, 0, 24, 223, 190, 0, 16, 103, 189, 0, 64, 3, 224, 0, 8, 0, 0, 0, 0]},
  'relocations': [
    {'source': {'kind': 'code', 'name': u'prehook'},
     'target': {'index': 0, 'kind': 'code', 'name': u'probe'},
     'offset': 8, 'type': 4},
    {'source': {'kind': 'original'},
     'target': {'index': 0, 'kind': 'code', 'name': u'probe'},
     'offset': 13, 'type': 4},
    {'source': {'kind': 'code', 'name': u'posthook'},
     'target': {'index': 0, 'kind': 'code', 'name': u'probe'},
     'offset': 16, 'type': 4}]}


def unpack_map(data, big_endian):
  # data[20:40] contains some kind of a name which is all zeros in my case
  unpack = lambda x: unpack_u32(x, big_endian)
  return {
    'type': unpack(data[:4]),
    'key_size': unpack(data[4:8]),
    'value_size': unpack(data[8:12]),
    'max_entries': unpack(data[12:16]),
    'flags': unpack(data[16:20])}

def get_map_section_index(elffile):
  map_section = 'maps'
  idx = -1
  for section in elffile.iter_sections():
    idx += 1
    if section.name == map_section:
      return idx
  return -1

def read_symbol_section(elffile):
  symbols = {}
  data = []
  for section in elffile.iter_sections():
    if isinstance(section, SymbolTableSection):
      for symbol in section.iter_symbols():
        if not symbol.entry['st_shndx'] in symbols:
          symbols[symbol.entry['st_shndx']] = {}
        symbols[symbol.entry['st_shndx']][symbol.entry['st_value']] = symbol.name
        data.append({'name': symbol.name, 'section': symbol.entry['st_shndx'], 'locations': []})
      break
  return symbols, data

def set_data(data, name, value):
  for d in data:
    if d['name'] == name:
      d['value'] = value
      break

def copy_fields(d1, d2, fields):
  for f in fields:
    d2[f] = d1[f]

def annotate(l, ref):
  for el in l:
    el['source'] = ref
  return l

def extract_finals(data, map_index, big_endian):
  relocations = []
  final_data = []
  maps = []
  for d in data:
    if d['section'] == map_index:
      definition = unpack_map(d['value'], big_endian)
      copy_fields(d, definition, ['name'])
      relocations += annotate(d['locations'], {'kind': 'map', 'index': len(maps), 'name': d['name']})
      maps.append(definition)
      continue
    if not d['name'] or len(d['locations']) == 0:
      continue
    if d['section'] == 'SHN_UNDEF':
      del d['section']
      relocations += annotate(d['locations'], {'kind': 'external', 'name': d['name']})
      continue
    if 'value' in d:
      del d['section']
      definition = {'name': d['name'], 'value': map(ord, list(d['value']))}
      relocations += annotate(d['locations'], {'kind': 'data', 'index': len(final_data), 'name': d['name']})
      final_data.append(definition)

  return final_data, maps, relocations

def remove_rel_prefix(s):
  if s.startswith(".rela"):
    return s[5:]
  if s.startswith(".rel"):
    return s[4:]
  return s

def read_relocations(data, code, elffile):
  code_indexes = {}
  idx = 0
  for c in code:
    code_indexes[c['name']] = idx
    idx += 1

  for section in elffile.iter_sections():
    if isinstance(section, RelocationSection):
      target_name = remove_rel_prefix(section.name)
      if target_name not in code_indexes:
        continue

      target = {'kind': 'code', 'name': target_name, 'index': code_indexes[target_name]}

      for symbol in section.iter_relocations():
        data[symbol['r_info_sym']]['locations'].append(
          {'type': symbol['r_info_type'], 'offset': symbol['r_offset'], 'target': target})

    if 'probe' in code_indexes:
      for r in central_hook['relocations']:
        if 'name' in r['source'] and r['source']['name'] in code_indexes:
          r['source']['index'] = code_indexes[r['source']['name']]


def extract_hook(filename):
  code = []
  code_sections = ['xdp', 'socket_filter', 'prehook', 'posthook', '.text'] # '.text' to extract central
  with open(filename, 'rb') as f:
    elffile = ELFFile(f)
    big_endian = not elffile.little_endian
    symbols, data = read_symbol_section(elffile)

    idx = -1
    for section in elffile.iter_sections():
      idx += 1
      if section.name in code_sections:
        section_name = section.name
        code.append({'name': section.name, 'value': map(ord, list(section.data()))})
        continue
      if idx in symbols:
        positions = sorted(symbols[idx].keys(), reverse = True)
        section_data = section.data()
        for p in positions:
          set_data(data, symbols[idx][p], section_data[p:])
          section_data = section_data[:p]

    section_name = 'probe' if section_name in ['prehook', 'posthook'] else section_name

    if section_name == 'probe':
      code.insert(0, central_hook['code'])
    read_relocations(data, code, elffile)

    data, maps, relocations = extract_finals(data, get_map_section_index(elffile), big_endian)

    if section_name == 'probe':
      relocations += central_hook['relocations']

  return {'maps': maps, 'section': section_name, 'code': code, 'data': data, 'relocations': relocations, 'big_endian': big_endian }


def get_pc_range(function):
  low_pc = function.attributes['DW_AT_low_pc'].value
  high_pc_attr = function.attributes['DW_AT_high_pc']
  high_pc_attr_class = describe_form_class(high_pc_attr.form)
  if high_pc_attr_class == 'address':
    high_pc = high_pc_attr.value
  elif high_pc_attr_class == 'constant':
    high_pc = low_pc + high_pc_attr.value
  else:
    high_pc = low_pc
  return (low_pc, high_pc)


def decode_function_pc(dwarfinfo, function_name):
  for compile_unit in dwarfinfo.iter_CUs():
    top_die = compile_unit.get_top_DIE()
    for d in top_die.iter_children():
      if d.tag == 'DW_TAG_subprogram' and 'DW_AT_name' in d.attributes and 'DW_AT_low_pc' in d.attributes:
        if d.attributes['DW_AT_name'].value == function_name:
          return get_pc_range(d)

  return None


def extract_function_ptr(filename, function_name):
  print('Processing file:', filename)
  with open(filename, 'rb') as f:
      elffile = ELFFile(f)

      if not elffile.has_dwarf_info():
        print('No DWARF info')
        return None

      dwarfinfo = elffile.get_dwarf_info()
      pc_range = decode_function_pc(dwarfinfo, function_name)

      if pc_range is None:
        print('Function not found')
        return None

      return {'ptr': pc_range[0], 'size': (pc_range[1] - pc_range[0])}
