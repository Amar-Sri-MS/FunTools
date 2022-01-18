#!/usr/bin/env python2.7
from __future__ import print_function
import json
import os
import sys
import dpc_client

def init_dpc():
  env_file_name = './env.json'
  if not os.path.exists(env_file_name):
    print('Env config not found')
    return dpc_client.DpcClient(False)

  f = open(env_file_name, 'r')
  env_dict = json.load(f)
  
  if len(env_dict['dpc_hosts']) != 1:
    print('Invalid env config')
    sys.exit(1)

  dpc_host = env_dict['dpc_hosts'][0]
  host = dpc_host['host']
  port = dpc_host['tcp_port']
  print('Connecting to dpc host at %s:%s' % (host, port))
  client = dpc_client.DpcClient(server_address=(host, port))
  # command required due to a bug
  client.execute('echo', ['first dpc command!'])
  return client
