import os
import subprocess
import tempfile

def gdb_prepare_addr_func(gdb, bin_file, addr_list):
  a2f_map ={}
  if len(addr_list) == 0:
    return a2f_map
  # run x/i on all addr, parse output and return (addr,func) for each
  (tmp_fd, tmp_path) = tempfile.mkstemp()
  with os.fdopen(tmp_fd, 'w') as f:
    gdb_cmds = []
    for addr in addr_list:
      gdb_cmds.append('x/i %s' % addr)
    f.write('\n'.join(gdb_cmds))
  
  cmd = [gdb, '--batch', '-x', tmp_path, bin_file]
  #print '\t%s' % cmd
  output = subprocess.check_output(cmd)
  for line in output.splitlines():
    v = line.split(':')[0].strip().split(' ', 2)
    if len(v) == 2:
      (addr, func) = v
      a2f_map[addr] = func

  os.remove(tmp_path)
  return a2f_map

def gdb_prepare_addr_line(gdb, bin_file, addr_list, is_full_path=False):
  a2l_map = {}
  if len(addr_list) == 0:
    return a2l_map
  # run info line *addr on all addr, parse output and return (addr,func) for each
  (tmp_fd, tmp_path) = tempfile.mkstemp()
  with os.fdopen(tmp_fd, 'w') as f:
    gdb_cmds = []
    for addr in addr_list:
      gdb_cmds.append('printf "%s "' % addr)
      gdb_cmds.append('info line *%s' % addr)
    f.write('\n'.join(gdb_cmds))

  cmd = [gdb, '--batch', '-x', tmp_path, bin_file]
  #print '\t%s' % cmd
  output = subprocess.check_output(cmd)
  for line in output.splitlines():
    v = line.split(' ', 5)
    addr = v[0]
    loc = '??:?'
    if len(v) >= 5 and v[1] == 'Line':
      loc_l = v[2]
      loc_f = v[4].replace('"', '')
      if not is_full_path:
        loc_f = loc_f.split('/')[-1]
      loc = '%s:%s' % (loc_f, loc_l)
    a2l_map[addr] = loc

  os.remove(tmp_path)
  return a2l_map

def objdump_disassemble(objdump, bin_file):
  cmd = '%s -d "%s"' % (objdump, bin_file)
  #print '\t%s' % cmd
  return subprocess.check_output(cmd, shell=True)

# this is a bit slow, use gdb_prepare_addr_line 
def a2l_prepare_addr_line(a2l, bin_file, addr_list):
  a2l_map = {}
  if len(addr_list) == 0:
    return a2l_map
  
  cmd = [a2l, '-a', '-s', '-p', '-e', bin_file]
  #print '\t%s' % cmd
  proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  (output, err_data) = proc.communicate('\n'.join(addr_list))
  for line in output.splitlines():
    (addr, loc) = line.split(' ', 1)
    addr = addr.split(':')[0]
    addr_to_loc_map[addr] = loc
  return a2l_map


