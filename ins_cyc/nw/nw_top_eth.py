#!/usr/bin/env python2.7

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

    print(mf)
    print('  epsq')
    for e in m.get('epsq', []):
      print '    %s %s: sqe_count=%s db_count=%s' % (e['flow']['id'], e['flow']['dest'], e['sqe_count'], e['db_count'])

    print('  eth')
    for e in m.get('ethernet', []):
      print '    %s %s: lport=%s pkts=%s/bytes=%s' % (e['flow']['id'], e['flow']['dest'], e['logical_port'], e['packets'], e['bytes'])

    print('  vi')
    for e in m.get('virtual_interface', []):
      print '    %s %s: lport=%s %s' % (e['flow']['id'], e['flow']['dest'], e['lport'], e.get('flows/sub', ''))

    print('  epcq')
    for e in m.get('epcq', []):
      print '    %s %s: cqe_count=%s db_count=%s int_count=%s' % (e['flow']['id'], e['flow']['dest'], e['cqe_count'], e['db_count'], e['int_count'])


def main(argv):
  mf_flow_dump(argv)

if __name__ == '__main__':
  main(sys.argv)
