#!/usr/bin/env python
import os
import json
import os.path
import time
import subprocess32
import sys
import struct
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
import dpc_client

def unpack_le_u32(data):
  return struct.unpack('<I', data)[0]

def unpack_map(data):
  # data[20:40] contains some kind of a name which is all zeros in my case
  return {
    'type': unpack_le_u32(data[:4]),
    'key_size': unpack_le_u32(data[4:8]),
    'value_size': unpack_le_u32(data[8:12]),
    'max_entries': unpack_le_u32(data[12:16]),
    'flags': unpack_le_u32(data[16:20])}

def extract_hook(filename):
  symbols = {}
  code = None
  maps = []
  map_section = 'maps'
  map_size = 40
  code_sections = ['xdp', 'socket_filter']
  section_name = None
  with open(filename, 'rb') as f:
    elffile = ELFFile(f)
    for section in elffile.iter_sections():
      if isinstance(section, SymbolTableSection):
        for symbol in section.iter_symbols():
          if not symbol.entry['st_shndx'] in symbols:
            symbols[symbol.entry['st_shndx']] = {}
          symbols[symbol.entry['st_shndx']][symbol.entry['st_value']] = symbol.name

    idx = -1
    for section in elffile.iter_sections():
      idx += 1
      if section.name == map_section:
        offset = 0
        data = section.data()
        while offset < section.data_size:
          map_data = unpack_map(data[offset:])
          map_data['name'] = symbols[idx][offset]
          maps.append(map_data)
          offset += map_size
        continue
      if section.name in code_sections:
        section_name = section.name
        code = map(ord, list(section.data()))
  return {'maps': maps, 'code': code, 'section': section_name}

def list_bpf():
  client = dpc_client.DpcClient(False)
  return client.execute('ebpf', ['list'])

class bpf:
  def __init__(self, **kwargs):
    self.client = dpc_client.DpcClient(False)
    if 'elf' in kwargs:
      self.hook = extract_hook(kwargs['elf'])
    result = self.client.execute('ebpf', ['attach', self.hook])
    if 'bid' not in result:
      raise Exception(json.dumps(result))
    self.hook['bid'] = result['bid']

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    result = self.client.execute('ebpf', ['detach', self.id()])
    if 'bid' not in result:
      raise Exception(json.dumps(result))

  def id(self):
    return {k: self.hook[k] for k in ['bid', 'section', 'key']}

  def trace_print(self):
    while True:
      result = self.client.execute('ebpf', ['trace', self.id()])
      print result
      time.sleep(1)
