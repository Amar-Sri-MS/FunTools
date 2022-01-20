#!/usr/bin/env python2.7

import sys
import subprocess

def irq_affinity_set(pat, cpu_list):
  cmd = 'ls -d /proc/irq/*/%s | sort' % pat
  data = subprocess.check_output(cmd, shell=True)
  flist = data.strip().splitlines()
  for i in range(len(flist)):
    cpu = cpu_list[i % len(cpu_list)]
    cmd = 'echo %s > %s/smp_affinity_list' % (cpu, flist[i].rsplit('/', 1)[0])
    print cmd
    subprocess.check_output(cmd, shell=True)
    (intf_name, tx_rx, qid) = flist[i].rsplit('/', 1)[1].rsplit('-', 2)
    if tx_rx == 'tx':
      core_mask = '%x' % (1 << cpu)
      if len(core_mask) > 8:
        loc = len(core_mask) - 8
        core_mask = core_mask[:loc] + ',' + core_mask[loc:]
      cmd = 'echo %s > /sys/class/net/%s/queues/%s-%s/xps_cpus' % (core_mask, intf_name, tx_rx, qid)
      print cmd
      try:
        subprocess.check_output(cmd, shell=True)
      except:
        pass
 
if __name__ == '__main__':
    irq_affinity_set('hu1-f1*tx*', range(20, 23))
    irq_affinity_set('hu1-f1*rx*', [23, 24, 26])
    irq_affinity_set('hu1-f2*tx*', range(30, 33))
    irq_affinity_set('hu1-f2*rx*', range(33, 36))
