#!/usr/bin/env python3

import sys
import subprocess
import json
import time
from collections import OrderedDict
from tabulate import tabulate

pattern_list = ['-tx-', '-rx-']
# if you want mellanox
#pattern_list += ['mlx']
# if you want eno1
#pattern_list += ['TxRx']

def intr_info(pat):
  cmd = 'cat /proc/interrupts | tr -s " "'
  data = subprocess.check_output(cmd, shell=True)
  data = data.strip().splitlines()
  num_cpu = len(data[0].strip().split())
  data = data[1:]
  result = OrderedDict()
  for line in data:
    line = line.strip().split()
    intr_id = line[0].split(':')[0]
    intr_count_list = list(map(int, line[1:num_cpu+1]))
    other = line[num_cpu + 1:]
    if other:
      intr_name = other[-1]
      for pattern in pattern_list:
        if pattern in intr_name:
          k = int(intr_id)
          result[k] = [intr_name, intr_id, intr_count_list]
          break
  return result

def intr_info_delta(res1, res2):
  res = []
  for (k, v1) in res1.items():
    v2 = res2.get(k, None)
    if not v2:
      continue
    v = list(v2)
    delta_count_list = []
    for i in range(len(v[2])):
      count_delta = int(v2[2][i]) - int(v1[2][i])
      delta_count_list.append(count_delta)
    delta_count = max(delta_count_list)
    intr_cpu = delta_count_list.index(delta_count)
    if delta_count:
      v = [v2[0], v2[1], v2[2][intr_cpu], '+%s' % delta_count, 'CPU%s' % intr_cpu]
      res.append(v)
  hdr=['name', 'intr', 'count', '+count', 'CPU']
  return (res, hdr)

def intr_funeth(pat):
  res1 = intr_info(pat)
  time.sleep(1)
  res2 = intr_info(pat)
  (res, hdr) = intr_info_delta(res1, res2)
  print(tabulate(res, headers=hdr))

def main(argv):
  mf_flow_dump(argv)

if __name__ == '__main__':
  intr_funeth(sys.argv)

