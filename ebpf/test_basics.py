#!/usr/bin/env python3

import json
import os
import sys
from bpf_client import bpf
from test_dpc import init_dpc
import dpc_client

# Source in kernels/counter.c
generic_counter = {'code': [{'name': 'socket_filter', 'value': [103, 189, 255, 224, 255, 191, 0, 24, 255, 190, 0, 16, 3, 160, 240, 37, 175, 192, 0, 12, 60, 1, 0, 0, 100, 33, 0, 0, 0, 1, 12, 56, 100, 33, 0, 0, 0, 1, 12, 56, 100, 36, 0, 0, 12, 0, 0, 0, 103, 197, 0, 12, 216, 64, 0, 3, 220, 65, 0, 0, 100, 33, 0, 1, 252, 65, 0, 0, 100, 2, 0, 1, 3, 192, 232, 37, 223, 190, 0, 16, 223, 191, 0, 24, 3, 224, 0, 9, 103, 189, 0, 32]}], 'section': 'socket_filter', 'maps': [{'name': 'counter', 'value_size': 8, 'max_entries': 1, 'key_size': 4, 'flags': 0, 'type': 6}], 'big_endian': True, 'data': [], 'relocations': [{'source': {'kind': 'external', 'name': 'bpf_map_lookup_elem'}, 'type': 4, 'target': {'index': 0, 'kind': 'code', 'name': 'socket_filter'}, 'offset': 44}, {'source': {'index': 0, 'kind': 'map', 'name': 'counter'}, 'type': 29, 'target': {'index': 0, 'kind': 'code', 'name': 'socket_filter'}, 'offset': 20}, {'source': {'index': 0, 'kind': 'map', 'name': 'counter'}, 'type': 28, 'target': {'index': 0, 'kind': 'code', 'name': 'socket_filter'}, 'offset': 24}, {'source': {'index': 0, 'kind': 'map', 'name': 'counter'}, 'type': 5, 'target': {'index': 0, 'kind': 'code', 'name': 'socket_filter'}, 'offset': 32}, {'source': {'index': 0, 'kind': 'map', 'name': 'counter'}, 'type': 6, 'target': {'index': 0, 'kind': 'code', 'name': 'socket_filter'}, 'offset': 40}]}

# Source in kernels/packet_counter.c, socket_filter -> xdp, percpu -> regular
packet_counter = {'code': [{'name': 'xdp', 'value': [183, 1, 0, 0, 0, 0, 0, 0, 99, 26, 252, 255, 0, 0, 0, 0, 191, 162, 0, 0, 0, 0, 0, 0, 7, 2, 0, 0, 252, 255, 255, 255, 24, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 133, 0, 0, 0, 1, 0, 0, 0, 21, 0, 3, 0, 0, 0, 0, 0, 121, 1, 0, 0, 0, 0, 0, 0, 7, 1, 0, 0, 1, 0, 0, 0, 123, 16, 0, 0, 0, 0, 0, 0, 183, 0, 0, 0, 1, 0, 0, 0, 149, 0, 0, 0, 0, 0, 0, 0]}], 'section': 'xdp', 'maps': [{'name': 'counter', 'value_size': 8, 'max_entries': 1, 'key_size': 4, 'flags': 0, 'type': 2}], 'big_endian': False, 'data': [], 'relocations': [{'source': {'index': 0, 'kind': 'map', 'name': 'counter'}, 'type': 1, 'target': {'index': 0, 'kind': 'code', 'name': 'socket_filter'}, 'offset': 32}]}

# Source in kernels/hello_world.c
hello_world = {'code': [{'name': 'socket_filter', 'value': [24, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 183, 2, 0, 0, 0, 0, 0, 0, 133, 0, 0, 0, 6, 0, 0, 0, 24, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 183, 2, 0, 0, 0, 0, 0, 0, 133, 0, 0, 0, 6, 0, 0, 0, 183, 0, 0, 0, 1, 0, 0, 0, 149, 0, 0, 0, 0, 0, 0, 0]}], 'section': 'socket_filter', 'maps': [], 'big_endian': False, 'data': [{'name': '.L.str', 'value': 'Hello, \x00', 'locations': [{'source': {'index': 0, 'kind': 'data', 'name': '.L.str'}, 'type': 1, 'target': {'index': 0, 'kind': 'code', 'name': 'socket_filter'}, 'offset': 0}]}, {'name': '.L.str.1', 'value': 'World!\\n\x00', 'locations': [{'source': {'index': 1, 'kind': 'data', 'name': '.L.str.1'}, 'type': 1, 'target': {'index': 0, 'kind': 'code', 'name': 'socket_filter'}, 'offset': 32}]}], 'relocations': [{'source': {'index': 0, 'kind': 'data', 'name': '.L.str'}, 'type': 1, 'target': {'index': 0, 'kind': 'code', 'name': 'socket_filter'}, 'offset': 0}, {'source': {'index': 1, 'kind': 'data', 'name': '.L.str.1'}, 'type': 1, 'target': {'index': 0, 'kind': 'code', 'name': 'socket_filter'}, 'offset': 32}]}

def error(message):
    print(message)
    sys.exit(1)

if __name__ == '__main__':
  dpc_client = init_dpc()

  with bpf(dpc_client) as b:
    print("Client created")
    l = b.list_hooks()
    print("List:")
    print(l)
    if len(l) != 0:
      error("Incorrect initial list")

    bid = b.attach(hook = packet_counter, name = 'packet_counter', arch = 'bpf')
    print("Attached, id = " + str(bid))

    l = b.list_hooks()
    print("List:")
    print(l)

    if len(l) != 1:
      error("Incorrect list after attach")

    r = b.map_get_uints(bid, 0, 0)
    if r != [0]:
      error("Incorrect initial value")

    b.map_set_uints(bid, 0, 0, 4242)

    r = b.map_get_uints(bid, 0, 0)
    print("Got " + str(r))

    if r != [4242]:
      error("Incorrect updated value")
