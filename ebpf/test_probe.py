#!/usr/bin/env python2.7
from __future__ import print_function
import json
import os
import sys
from bpf_client import bpf
from test_dpc import init_dpc
from bpf_elf import extract_function_ptr
from bpf_pack import pack_uint
import dpc_client

# Generic probe with counter, modifications: order map relocations
counter_probe = {'code': [{'name': u'probe', 'value': [103, 189, 255, 168, 255, 191, 0, 8, 255, 190, 0, 0, 255, 188, 0, 16, 255, 164, 0, 24, 255, 165, 0, 32, 255, 166, 0, 40, 255, 167, 0, 48, 255, 168, 0, 56, 255, 169, 0, 64, 255, 170, 0, 72, 255, 171, 0, 80, 3, 160, 240, 37, 12, 0, 0, 0, 0, 0, 0, 0, 3, 192, 232, 37, 223, 164, 0, 24, 223, 165, 0, 32, 223, 166, 0, 40, 223, 167, 0, 48, 223, 168, 0, 56, 223, 169, 0, 64, 223, 170, 0, 72, 223, 171, 0, 80, 223, 188, 0, 16, 223, 190, 0, 0, 223, 191, 0, 8, 103, 189, 0, 88, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
{'name': u'prehook', 'value': [103, 189, 255, 224, 255, 191, 0, 24, 255, 190, 0, 16, 3, 160, 240, 37, 175, 192, 0, 12, 60, 1, 0, 0, 100, 33, 0, 0, 0, 1, 12, 56, 100, 33, 0, 0, 0, 1, 12, 56, 100, 36, 0, 0, 12, 0, 0, 0, 103, 197, 0, 12, 216, 64, 0, 3, 220, 65, 0, 0, 100, 33, 0, 1, 252, 65, 0, 0, 3, 192, 232, 37, 223, 190, 0, 16, 223, 191, 0, 24, 3, 224, 0, 9, 103, 189, 0, 32]}],
'section': 'probe', 'maps': [{'name': u'counter', 'value_size': 8, 'max_entries': 1, 'key_size': 4, 'flags': 0, 'type': 6}], 'big_endian': True, 'data': [],
'relocations': [
{'source': {'index': 0, 'kind': 'map', 'name': u'counter'}, 'type': 29, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 20}, {'source': {'index': 0, 'kind': 'map', 'name': u'counter'}, 'type': 28, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 24}, {'source': {'index': 0, 'kind': 'map', 'name': u'counter'}, 'type': 5, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 32}, {'source': {'index': 0, 'kind': 'map', 'name': u'counter'}, 'type': 6, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 40},
{'source': {'kind': 'external', 'name': u'bpf_map_lookup_elem'}, 'type': 4, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 44},
{'source': {'index': 1, 'kind': 'code', 'name': u'prehook'},
     'target': {'index': 0, 'kind': 'code', 'name': u'probe'},
     'offset': 52, 'type': 4}
]}

histogram_probe = {'code': [{'name': u'probe', 'value': [103, 189, 255, 168, 255, 191, 0, 8, 255, 190, 0, 0, 255, 188, 0, 16, 255, 164, 0, 24, 255, 165, 0, 32, 255, 166, 0, 40, 255, 167, 0, 48, 255, 168, 0, 56, 255, 169, 0, 64, 255, 170, 0, 72, 255, 171, 0, 80, 3, 160, 240, 37, 12, 0, 0, 0, 0, 0, 0, 0, 3, 192, 232, 37, 223, 164, 0, 24, 223, 165, 0, 32, 223, 166, 0, 40, 223, 167, 0, 48, 223, 168, 0, 56, 223, 169, 0, 64, 223, 170, 0, 72, 223, 171, 0, 80, 223, 188, 0, 16, 223, 190, 0, 0, 223, 191, 0, 8, 103, 189, 0, 88, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
{'name': u'prehook', 'value': [103, 189, 255, 240, 255, 191, 0, 8, 255, 190, 0, 0, 3, 160, 240, 37, 0, 128, 40, 37, 60, 1, 0, 0, 100, 33, 0, 0, 0, 1, 12, 56, 100, 33, 0, 0, 0, 1, 12, 56, 12, 0, 0, 0, 100, 36, 0, 0, 3, 192, 232, 37, 223, 190, 0, 0, 223, 191, 0, 8, 3, 224, 0, 9, 103, 189, 0, 16]}],
'section': 'probe', 'maps': [{'name': u'hist', 'value_size': 8, 'max_entries': 64, 'key_size': 4, 'flags': 0, 'type': 6}], 'big_endian': True, 'data': [],
'relocations': [
  {'source': {'index': 0, 'kind': 'map', 'name': u'hist'}, 'type': 29, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 20}, {'source': {'index': 0, 'kind': 'map', 'name': u'hist'}, 'type': 28, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 24}, {'source': {'index': 0, 'kind': 'map', 'name': u'hist'}, 'type': 5, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 32}, {'source': {'index': 0, 'kind': 'map', 'name': u'hist'}, 'type': 6, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 44},
  {'source': {'kind': 'external', 'name': u'bpf_histogram_log_inc'}, 'type': 4, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 40},
  {'source': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'type': 4, 'target': {'index': 0, 'kind': 'code', 'name': u'probe'}, 'offset': 52}]}

latency_probe = {'code': [{'name': u'probe', 'value': [103, 189, 255, 168, 255, 191, 0, 8, 255, 190, 0, 0, 255, 188, 0, 16, 255, 164, 0, 24, 255, 165, 0, 32, 255, 166, 0, 40, 255, 167, 0, 48, 255, 168, 0, 56, 255, 169, 0, 64, 255, 170, 0, 72, 255, 171, 0, 80, 3, 160, 240, 37, 12, 0, 0, 0, 0, 0, 0, 0, 3, 192, 232, 37, 223, 164, 0, 24, 223, 165, 0, 32, 223, 166, 0, 40, 223, 167, 0, 48, 223, 168, 0, 56, 223, 169, 0, 64, 223, 170, 0, 72, 223, 171, 0, 80, 223, 188, 0, 16, 223, 190, 0, 0, 223, 191, 0, 8, 103, 189, 0, 88, 103, 189, 255, 224, 255, 191, 0, 8, 255, 162, 0, 0, 60, 1, 0, 0, 100, 33, 0, 0, 0, 1, 12, 56, 100, 33, 0, 0, 0, 1, 12, 56, 100, 63, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
{'name': u'probe_posthook', 'value': [223, 164, 0, 0, 255, 162, 0, 16, 255, 163, 0, 24, 255, 190, 0, 0, 3, 160, 240, 37, 12, 0, 0, 0, 0, 0, 0, 0, 3, 192, 232, 37, 223, 190, 0, 0, 223, 162, 0, 16, 223, 163, 0, 24, 223, 191, 0, 8, 103, 189, 0, 32, 3, 224, 0, 9]},
{'name': u'prehook', 'value': [103, 189, 255, 240, 255, 191, 0, 8, 255, 190, 0, 0, 3, 160, 240, 37, 12, 0, 0, 0, 0, 0, 0, 0, 3, 192, 232, 37, 223, 190, 0, 0, 223, 191, 0, 8, 3, 224, 0, 9, 103, 189, 0, 16]},
{'name': u'posthook', 'value': [103, 189, 255, 224, 255, 191, 0, 24, 255, 190, 0, 16, 255, 176, 0, 8, 3, 160, 240, 37, 12, 0, 0, 0, 0, 128, 128, 37, 0, 80, 40, 47, 60, 1, 0, 0, 100, 33, 0, 0, 0, 1, 12, 56, 100, 33, 0, 0, 0, 1, 12, 56, 12, 0, 0, 0, 100, 36, 0, 0, 3, 192, 232, 37, 223, 176, 0, 8, 223, 190, 0, 16, 223, 191, 0, 24, 3, 224, 0, 9, 103, 189, 0, 32]}],
'section': 'probe', 'maps': [{'name': u'hist', 'value_size': 8, 'max_entries': 64, 'key_size': 4, 'flags': 0, 'type': 6}], 'big_endian': True, 'data': [],
'relocations': [
  {'source': {'index': 0, 'kind': 'map', 'name': u'hist'}, 'type': 29, 'target': {'index': 3, 'kind': 'code', 'name': u'posthook'}, 'offset': 32}, {'source': {'index': 0, 'kind': 'map', 'name': u'hist'}, 'type': 28, 'target': {'index': 3, 'kind': 'code', 'name': u'posthook'}, 'offset': 36}, {'source': {'index': 0, 'kind': 'map', 'name': u'hist'}, 'type': 5, 'target': {'index': 3, 'kind': 'code', 'name': u'posthook'}, 'offset': 44}, {'source': {'index': 0, 'kind': 'map', 'name': u'hist'}, 'type': 6, 'target': {'index': 3, 'kind': 'code', 'name': u'posthook'}, 'offset': 56},
  {'source': {'kind': 'external', 'name': u'bpf_histogram_log_inc'}, 'type': 4, 'target': {'index': 3, 'kind': 'code', 'name': u'posthook'}, 'offset': 52}, {'source': {'kind': 'external', 'name': u'bpf_ktime_get_ns'}, 'type': 4, 'target': {'index': 2, 'kind': 'code', 'name': u'prehook'}, 'offset': 16}, {'source': {'kind': 'external', 'name': u'bpf_ktime_get_ns'}, 'type': 4, 'target': {'index': 3, 'kind': 'code', 'name': u'posthook'}, 'offset': 20},
  {'source': {'index': 2, 'kind': 'code', 'name': u'prehook'}, 'type': 4, 'target': {'index': 0, 'kind': 'code', 'name': u'probe'}, 'offset': 52},

  {'source': {'index': 1, 'kind': 'code', 'name': u'probe_posthook'}, 'type': 29, 'target': {'index': 0, 'kind': 'code', 'name': u'probe'}, 'offset': 124},
  {'source': {'index': 1, 'kind': 'code', 'name': u'probe_posthook'}, 'type': 28, 'target': {'index': 0, 'kind': 'code', 'name': u'probe'}, 'offset': 128},
  {'source': {'index': 1, 'kind': 'code', 'name': u'probe_posthook'}, 'type': 5, 'target': {'index': 0, 'kind': 'code', 'name': u'probe'}, 'offset': 136},
  {'source': {'index': 1, 'kind': 'code', 'name': u'probe_posthook'}, 'type': 6, 'target': {'index': 0, 'kind': 'code', 'name': u'probe'}, 'offset': 144},
  {'source': {'index': 3, 'kind': 'code', 'name': u'posthook'}, 'type': 4, 'target': {'index': 1, 'kind': 'code', 'name': u'probe_posthook'}, 'offset': 20}]}

def funos_image_search():
  path = ['funos-f1.stripped', '../../FunOS/build/funos-f1-qemu']
  for p in path:
    if os.path.isfile(p):
      return p
  print('Cant locate FunOS image')
  sys.exit(1)

def error(message):
  print(message)
  sys.exit(1)

if __name__ == '__main__':
  dpc_client = init_dpc()
  funos_image = funos_image_search()
  target_function = 'fun_malloc_threaded'
  cases = {'histogram': histogram_probe, 'counter': counter_probe, 'latency': latency_probe }
  testcase = 'latency'

  with bpf(dpc_client) as b:
    print("Client created, testcase: " + testcase)
    probe = cases[testcase]
    location = extract_function_ptr(funos_image, target_function)
    location['ptr'] = pack_uint(location['ptr'], 8, probe['big_endian'])
    probe['location'] = location

    bid = b.attach(hook = probe, name = 'malloc_probe', arch = 'mips')
    print("Attached, id = " + str(bid))

    l = b.list_hooks()
    print("List:")
    print(l)

    r = b.map_get(bid, 0, [0, 0, 0, 0])
    print("Raw bytes:")
    print(r)

    r = b.map_get_uints(bid, 0, 0)
    print("Counts:")
    print(r)

    dpc_client.execute('test', ['malloc'])

    if testcase != 'counter':
      print("Counts after the test:")
      b.histogram_dump(bid, 0)
    else:
      r = b.map_get_uints(bid, 0, 0)
      print("Counts after the test:")
      print(r)
