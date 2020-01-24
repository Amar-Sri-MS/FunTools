#!/usr/bin/env python
from __future__ import print_function
import json
import os
import sys
from bpf_client import bpf
import dpc_client

# Source in kernels/counter.c
generic_counter = {'code': [103, 189, 255, 224, 255, 191, 0, 24, 255, 190, 0, 16, 3, 160, 240, 37, 175, 192, 0, 12, 60, 1, 0, 0, 100, 33, 0, 0, 0, 1, 12, 56, 100, 33, 0, 0, 0, 1, 12, 56, 100, 36, 0, 0, 12, 0, 0, 0, 103, 197, 0, 12, 216, 64, 0, 3, 220, 65, 0, 0, 100, 33, 0, 1, 252, 65, 0, 0, 3, 192, 232, 37, 223, 190, 0, 16, 223, 191, 0, 24, 3, 224, 0, 9, 103, 189, 0, 32], 'section': u'probe', 'maps': [{'name': u'counter', 'value_size': 8, 'locations': [{'type': 29, 'offset': 20}, {'type': 28, 'offset': 24}, {'type': 5, 'offset': 32}, {'type': 6, 'offset': 40}], 'max_entries': 1, 'key_size': 4, 'flags': 0, 'type': 6}], 'external': [{'name': u'bpf_map_lookup_elem', 'locations': [{'type': 4, 'offset': 44}]}], 'big_endian': True, 'data': []}

# Source in kernels/packet_counter.c, socket_filter -> xdp, percpu -> regular
packet_counter = {'code': [183, 1, 0, 0, 0, 0, 0, 0, 99, 26, 252, 255, 0, 0, 0, 0, 191, 162, 0, 0, 0, 0, 0, 0, 7, 2, 0, 0, 252, 255, 255, 255, 24, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 133, 0, 0, 0, 1, 0, 0, 0, 21, 0, 3, 0, 0, 0, 0, 0, 121, 1, 0, 0, 0, 0, 0, 0, 7, 1, 0, 0, 1, 0, 0, 0, 123, 16, 0, 0, 0, 0, 0, 0, 183, 0, 0, 0, 1, 0, 0, 0, 149, 0, 0, 0, 0, 0, 0, 0], 'section': u'xdp', 'maps': [{'name': u'counter', 'value_size': 8, 'locations': [{'type': 1, 'offset': 32}], 'max_entries': 1, 'key_size': 4, 'flags': 0, 'type': 2}], 'external': [], 'big_endian': False, 'data': []}

# Source in kernels/hello_world.c
hello_world = {'code': [24, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 183, 2, 0, 0, 0, 0, 0, 0, 133, 0, 0, 0, 6, 0, 0, 0, 24, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 183, 2, 0, 0, 0, 0, 0, 0, 133, 0, 0, 0, 6, 0, 0, 0, 183, 0, 0, 0, 1, 0, 0, 0, 149, 0, 0, 0, 0, 0, 0, 0], 'section': u'socket_filter', 'maps': [], 'external': [], 'big_endian': False, 'data': [{'name': u'.L.str', 'value': [72, 101, 108, 108, 111, 44, 32, 0], 'locations': [{'type': 1, 'offset': 0}]}, {'name': u'.L.str.1', 'value': [87, 111, 114, 108, 100, 33, 92, 110, 0], 'locations': [{'type': 1, 'offset': 32}]}]}

def error(message):
    print(message)
    sys.exit(1)

def init_dpc():
  env_file_name = './env.json'
  if not os.path.exists(env_file_name):
    print('Env config not found')
    return dpc_client.DpcClient(False)

  f = open(env_file_name, 'r')
  env_dict = json.load(f)
  
  if len(env_dict['dpc_hosts']) != 1:
    error('Invalid env config')

  dpc_host = env_dict['dpc_hosts'][0]
  host = dpc_host['host']
  port = dpc_host['tcp_port']
  print('Connecting to dpc host at %s:%s' % (host, port))
  client = dpc_client.DpcClient(server_address=(host, port))
  # command required due to a bug
  client.execute('echo', ['first dpc command!'])
  return client

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
    if r != 0:
      error("Incorrect initial value")

    b.map_set_uints(bid, 0, 0, 4242)

    r = b.map_get_uints(bid, 0, 0)
    print("Got " + str(r))

    if r != 4242:
      error("Incorrect updated value")
