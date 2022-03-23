import os
import subprocess
import tempfile
import bisect

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

def nm_sym_parse(nm, bin_file):
  sym_map = {}

  cmd = [nm, '-S', bin_file]
  proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

  for line in proc.stdout:
    line = line.strip().split()
    if len(line) < 4:
      continue
    addr = '0x' + line[0]
    sz = line[1]
    e_addr = '0x%016x' % (int(addr, 16) + int(sz, 16))
    fname = line[3]
    # if dup addr likely similar function or constprop/lto_priv etc
    sym_map[addr] = [e_addr, fname]

  return sym_map

def nm_prepare_addr_func(nm, bin_file, addr_list):
  a2f_map = {}
  f2a_map = {}
  if len(addr_list) == 0:
    return (a2f_map, f2a_map)

  sym_map = nm_sym_parse(nm, bin_file)
  klist = sorted(sym_map.keys())

  for addr in addr_list:
    if addr in sym_map:
      fname = sym_map[addr][1]
      a2f_map[addr] = '<%s>' % fname
      f2a_map[fname] = addr
      continue
    i = bisect.bisect(klist, addr)
    if i > 0:
      k = klist[i - 1]
      v = sym_map[k]
      if addr < v[0]:
        off = int(addr, 16) - int(k, 16)
        a2f_map[addr] = '<%s+%s>' % (v[1], off)

  return a2f_map

def objdump_debug_line_parse(objdump, bin_file, is_full_path=False):
  a2l_map = {}

  cmd = [objdump, '-WL', bin_file]
  proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

  cur_fname = None
  cur_fname_cu = None
  for line in proc.stdout:
    line = line.strip().split()

    if len(line) == 0:
      cur_fname = None
      continue

    if len(line) > 3:
      continue

    if len(line) == 2:
      if line[0] == 'CU:':
        cur_fname_cu = line[1].rsplit(':', 1)[0]
        continue

    if len(line) == 1:
      assert cur_fname == None
      cur_fname = line[0].rsplit(':', 1)[0]
      continue

    try:
      loc_l = int(line[1])
      loc_f = cur_fname if cur_fname else cur_fname_cu

      # objdump may produce the following sequence when it cannot find the
      # file and line number for the address:
      #
      # ['<unknown>', '1', '0xa80000000058a368']
      #
      # Print a message and skip the line.
      if not loc_f.endswith(line[0]) and line[0] == '<unknown>':
        print('Unknown file and line from objdump: %s' % line)
        continue

      assert loc_f.endswith(line[0])
      if not is_full_path:
        loc_f = loc_f.split('/')[-1]
      loc = '%s:%s' % (loc_f, loc_l)
      addr = line[2]
      # if dup, last one is the deepest in inlining
      a2l_map[addr] = loc
    except Exception as e:
      raise

  return a2l_map

def objdump_prepare_addr_line(objdump, nm, bin_file, addr_list, is_full_path=False):
  a2l_map = {}
  if len(addr_list) == 0:
    return a2l_map

  a2f_map = nm_prepare_addr_func(nm, bin_file, addr_list)

  def is_addr_in_same_func_scope(a1, a2):
    if a1 in a2f_map and a2 in a2f_map:
      f1 = a2f_map[a1].split('>', 1)[0].split('+', 1)[0]
      f2 = a2f_map[a2].split('>', 1)[0].split('+', 1)[0]
      return f1 == f2
    return False

  dl_map = objdump_debug_line_parse(objdump, bin_file, is_full_path)
  klist = sorted(dl_map.keys())

  def addr_to_loc_bisect(addr):
    i = bisect.bisect(klist, addr)
    if i > 0:
      # or i < len(klist) - 1:
      k = klist[i - 1]
      if is_addr_in_same_func_scope(k, addr):
        return dl_map[k]
    return None

  for addr in addr_list:
    if addr in dl_map:
      if addr not in a2f_map:
        continue
      a2l_map[addr] = dl_map[addr]
      continue

    v = addr_to_loc_bisect(addr)
    if v:
      a2l_map[addr] = v

  return a2l_map

def objdump_disassemble(tool_map, bin_file):
  objdump = tool_map['objdump'] if isinstance(tool_map, dict) else tool_map
  cmd = '%s -d "%s"' % (objdump, bin_file)
  return subprocess.check_output(cmd, shell=True)

# this is a bit slow, use other prepare_addr_line 
def a2l_prepare_addr_line(a2l, bin_file, addr_list):
  a2l_map = {}
  if len(addr_list) == 0:
    return a2l_map

  cmd = [a2l, '-a', '-s', '-p', '-e', bin_file]
  proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  (output, err_data) = proc.communicate('\n'.join(addr_list))
  for line in output.splitlines():
    (addr, loc) = line.split(' ', 1)
    addr = addr.split(':')[0]
    addr_to_loc_map[addr] = loc
  return a2l_map

prefer_gdb = False

def prepare_addr_func(tool_map, bin_file, addr_list):
  nm = tool_map.get('nm', None)
  if nm and not prefer_gdb:
    return nm_prepare_addr_func(nm, bin_file, addr_list)

  gdb = tool_map.get('gdb', None)
  if gdb:
    return gdb_prepare_addr_func(gdb, bin_file, addr_list)

  assert False

def prepare_addr_line(tool_map, bin_file, addr_list, is_full_path=False):
  objdump = tool_map.get('objdump', None)
  nm = tool_map.get('nm', None)
  if objdump and nm and not prefer_gdb:
    return objdump_prepare_addr_line(objdump, nm, bin_file, addr_list, is_full_path)

  gdb = tool_map.get('gdb', None)
  if gdb:
    return gdb_prepare_addr_line(gdb, bin_file, addr_list, is_full_path)

  assert False
