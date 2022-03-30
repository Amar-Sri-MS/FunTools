#!/usr/bin/env python3
import os
import json
import math
import os.path
import time
import subprocess32
import sys
from bpf_pack import pack_uint, unpack_uint, unpack_uint_array

class bpf:
  def __init__(self, dpc_client, big_endian = True):
    self.client = dpc_client
    self.attached_hooks = {}
    self.position = 0
    self.big_endian = big_endian

  def __enter__(self):
    return self

  def list_hooks(self):
    return self.client.execute('ebpf', ['list'])

  def attach(self, **kwargs):
    props = kwargs['hook']
    props['arch'] = 'mips' if 'arch' not in kwargs else kwargs['arch']
    props['name'] = 'noname' if 'name' not in kwargs else kwargs['name']

    if 'location' in kwargs:
      props['location'] = kwargs['location']

    result = self.client.execute('ebpf', ['attach', props])
    if 'bid' not in result:
      raise Exception(json.dumps(result))

    bid = int(result['bid'])
    self.attached_hooks[bid] = props

    return bid

  def __exit__(self, exc_type, exc_value, traceback):
    for bid in list(self.attached_hooks.keys()):
      result = self.client.execute('ebpf', ['detach', {'bid': bid}])
      if result != 'Ok':
        raise Exception(json.dumps(result))

  def map_first(self, bid, map_idx):
    result = self.client.execute('ebpf', ['map', 'first', {'bid': bid, 'index': map_idx}])
    if 'key' in result:
      return result['key']
    return None

  def map_next(self, bid, map_idx, packed_key):
    result = self.client.execute('ebpf', ['map', 'next', {'bid': bid, 'index': map_idx, 'key': packed_key}])
    if 'key' in result:
      return result['key']
    return None

  def map_set(self, bid, map_idx, packed_key, packed_value):
    result = self.client.execute('ebpf', ['map', 'update', {'bid': bid, 'index': map_idx, 'key': packed_key, 'value': packed_value}])
    return result == 'Ok'

  def map_get(self, bid, map_idx, packed_key):
    result = self.client.execute('ebpf', ['map', 'lookup', {'bid': bid, 'index': map_idx, 'key': packed_key}])
    if 'value' in result:
      return result['value']
    return None

  def map_delete(self, bid, map_idx, packed_key):
    result = self.client.execute('ebpf', ['map', 'delete', {'bid': bid, 'index': map_idx, 'key': packed_key}])
    return result == 'Ok'

  def map_set_uints(self, bid, map_idx, key, value):
    map_props = self.attached_hooks[bid]['maps'][map_idx]
    packed_key = pack_uint(key, map_props['key_size'], self.big_endian)
    packed_value = pack_uint(value, map_props['value_size'], self.big_endian)
    return self.map_set(bid, map_idx, packed_key, packed_value)

  def map_get_uints(self, bid, map_idx, key):
    map_props = self.attached_hooks[bid]['maps'][map_idx]
    packed_key = pack_uint(key, map_props['key_size'], self.big_endian)
    packed_value = self.map_get(bid, map_idx, packed_key)
    return unpack_uint_array(packed_value, map_props['value_size'], self.big_endian)

  def map_dump(self, bid, map_idx):
    key = self.map_first(bid, map_idx)
    if key is None:
      print('Map is empty')
      return

    while True:
      value = self.map_get(bid, map_idx, key)
      print(json.dumps(key) + ' => ' + json.dumps(value))
      key = self.map_next(bid, map_idx, key)
      if key is None:
        break

  def histogram_dump(self, bid, map_idx):
    prefix = lambda x, y: (' ' * (y - len(x))) + x
    values = []
    for i in range(0, 64):
      r = self.map_get_uints(bid, map_idx, i)
      values.append(sum(r))

    while values[len(values) - 1] == 0:
      values.pop()

    if len(values) == 0:
      print("Histogram is empty")

    max_val = max(values)
    max_len = int(math.log10(max_val)) + 1
    low = 0
    high = 2

    for v in values:
      print(prefix(str(low) + " -> " + str(high - 1) + ": ", 40) + prefix(str(v), max_len) + " | " + ('*' * (v * 40 / max_val)))
      low = high
      high *= 2

  def trace_print(self):
    while True:
      result = self.client.execute('ebpf', ['trace', {'position': self.position}])
      if ('trace' not in result) or ('position' not in result):
        raise Exception(json.dumps(result))
      print(result['trace'])
      self.position = int(result['position'])
      time.sleep(1)
