#!/usr/bin/env python

from bpf_pack import unpack_u32
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from elftools.elf.relocation import RelocationSection

def unpack_map(data, big_endian):
  # data[20:40] contains some kind of a name which is all zeros in my case
  unpack = lambda x: unpack_u32(x, big_endian)
  return {
    'type': unpack(data[:4]),
    'key_size': unpack(data[4:8]),
    'value_size': unpack(data[8:12]),
    'max_entries': unpack(data[12:16]),
    'flags': unpack(data[16:20])}

def map_section_index(elffile):
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

def extract_finals(data, map_index, big_endian):
  external = []
  final_data = []
  maps = []
  for d in data:
    if d['section'] == map_index:
      definition = unpack_map(d['value'], big_endian)
      copy_fields(d, definition, ['name', 'locations'])
      maps.append(definition)
      continue
    if not d['name'] or len(d['locations']) == 0:
      continue
    if d['section'] == 'SHN_UNDEF':
      del d['section']
      external.append(d)
      continue
    if 'value' in d:
      del d['section']
      d['value'] = map(ord, list(d['value']))
      final_data.append(d)

  return final_data, maps, external

def extract_hook(filename):
  code = None
  code_sections = ['xdp', 'socket_filter', 'probe']
  section_name = None
  with open(filename, 'rb') as f:
    elffile = ELFFile(f)
    big_endian = not elffile.little_endian
    symbols, data = read_symbol_section(elffile)

    idx = -1
    for section in elffile.iter_sections():
      idx += 1
      if isinstance(section, RelocationSection):
        for symbol in section.iter_relocations():
          data[symbol['r_info_sym']]['locations'].append(
            {'type': symbol['r_info_type'], 'offset': symbol['r_offset']})
      if section.name in code_sections:
        section_name = section.name
        code = map(ord, list(section.data()))
        continue
      if idx in symbols:
        positions = sorted(symbols[idx].keys(), reverse = True)
        section_data = section.data()
        for p in positions:
          set_data(data, symbols[idx][p], section_data[p:])
          section_data = section_data[:p]

    data, maps, external = extract_finals(data, map_section_index(elffile), big_endian)
  return {'maps': maps, 'code': code, 'section': section_name, 'data': data, 'external': external, 'big_endian': big_endian }
