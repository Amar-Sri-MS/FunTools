#!/usr/bin/env python3

import sys
import subprocess
import json
import os

dpcsh_path = os.getenv('DPCSH', 'dpcsh')

def dpcsh_cmd(cmd):
  cmd = [dpcsh_path, '-Q', cmd]
  output = subprocess.check_output(cmd)
  j_output = json.loads(output)
  return j_output['result']

def mf_flow_dump(mf_list):
  res = dpcsh_cmd('flow list')
  if isinstance(mf_list, str):
    mf_list = [mf_list]

  for mf in mf_list:
    m = res.get(mf, None)
    if not m:
      continue

    print('====== %s ======' % mf)
    print(json.dumps(m, indent=4, sort_keys=True))

def main(argv):
  mf_flow_dump(argv)

if __name__ == '__main__':
  main(sys.argv)
