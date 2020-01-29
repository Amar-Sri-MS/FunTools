#!/usr/bin/env python
from __future__ import print_function
import json
import os
import sys
from bpf_client import bpf
from test_dpc import init_dpc
from bpf_elf import extract_function_ptr
from bpf_pack import pack_uint
import dpc_client

# Generic probe with counter, modifications: nop posthook, remove posthook relocation
probe = {'code': [{'name': u'probe', 'value': [103, 189, 255, 168, 255, 191, 0, 8, 255, 190, 0, 0, 255, 188, 0, 16, 255, 164, 0, 24, 255, 165, 0, 32, 255, 166, 0, 40, 255, 167, 0, 48, 255, 168, 0, 56, 255, 169, 0, 64, 255, 170, 0, 72, 255, 171, 0, 80, 3, 160, 240, 37, 12, 0, 0, 0, 0, 0, 0, 0, 3, 192, 232, 37, 223, 164, 0, 24, 223, 165, 0, 32, 223, 166, 0, 40, 223, 167, 0, 48, 223, 168, 0, 56, 223, 169, 0, 64, 223, 170, 0, 72, 223, 171, 0, 80, 223, 188, 0, 16, 223, 190, 0, 0, 223, 191, 0, 8, 103, 189, 0, 88, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
{'name': u'prehook', 'value': [103, 189, 255, 224, 255, 191, 0, 24, 255, 190, 0, 16, 3, 160, 240, 37, 175, 192, 0, 12, 60, 1, 0, 0, 100, 33, 0, 0, 0, 1, 12, 56, 100, 33, 0, 0, 0, 1, 12, 56, 100, 36, 0, 0, 12, 0, 0, 0, 103, 197, 0, 12, 216, 64, 0, 3, 220, 65, 0, 0, 100, 33, 0, 1, 252, 65, 0, 0, 3, 192, 232, 37, 223, 190, 0, 16, 223, 191, 0, 24, 3, 224, 0, 9, 103, 189, 0, 32]}],
'section': 'probe', 'maps': [{'name': u'counter', 'value_size': 8, 'max_entries': 1, 'key_size': 4, 'flags': 0, 'type': 6}], 'big_endian': True, 'data': [],
'relocations': [
{'source': {'index': 0, 'kind': 'map', 'name': u'counter'}, 'type': 29, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 20}, {'source': {'index': 0, 'kind': 'map', 'name': u'counter'}, 'type': 28, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 24}, {'source': {'index': 0, 'kind': 'map', 'name': u'counter'}, 'type': 5, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 32}, {'source': {'index': 0, 'kind': 'map', 'name': u'counter'}, 'type': 6, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 40},
{'source': {'kind': 'external', 'name': u'bpf_map_lookup_elem'}, 'type': 4, 'target': {'index': 1, 'kind': 'code', 'name': u'prehook'}, 'offset': 44},
{'source': {'index': 1, 'kind': 'code', 'name': u'prehook'},
     'target': {'index': 0, 'kind': 'code', 'name': u'probe'},
     'offset': 52, 'type': 4}
]}

def error(message):
    print(message)
    sys.exit(1)

if __name__ == '__main__':
  dpc_client = init_dpc()
  funos_image = '../../FunOS/build/funos-f1-qemu'
  target_function = 'fun_malloc_threaded'

  with bpf(dpc_client) as b:
    print("Client created")
    location = extract_function_ptr(funos_image, target_function)
    location['ptr'] = pack_uint(location['ptr'], 8, probe['big_endian'])
    probe['location'] = location

    bid = b.attach(hook = probe, name = 'malloc_probe', arch = 'mips')
    print("Attached, id = " + str(bid))

    l = b.list_hooks()
    print("List:")
    print(l)

    r = b.map_get(bid, 0, [0, 0, 0, 0])
    print("Counts:")
    print(r)

    r = b.map_get(bid, 0, [0, 0, 0, 0])
    print("Counts:")
    print(r)

    r = b.map_get(bid, 0, [0, 0, 0, 0])
    print("Counts:")
    print(r)
