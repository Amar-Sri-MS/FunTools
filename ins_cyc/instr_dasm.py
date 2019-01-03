#!/usr/bin/python2.7

# input: funos_bin, optionally samurai_dir
# output: .instr_dasm (use instr_count.py for further analysis)

import os
import sys
import subprocess
import glob

import obj_tools

gdb = '/opt/cross/mips64/bin/mips64-unknown-elf-gdb'
objdump = '/opt/cross/mips64/bin/mips64-unknown-elf-objdump'

addr_to_func_map = {}
addr_to_loc_map = {}

def gdb_get_addr_func_loc(addr):
  func = addr_to_func_map.get(addr, '<unknown>')
  loc = addr_to_loc_map.get(addr, '??:?')
  return (func, loc)

def instr_annotate(bin_file, out_file, data):
  addr_list = set([v[0] for v in data])

  print 'running gdb: for addr to func'
  d = obj_tools.gdb_prepare_addr_func(gdb, bin_file, addr_list)
  addr_to_func_map.update(d)

  print 'running gdb: for addr to line'
  d = obj_tools.gdb_prepare_addr_line(gdb, bin_file, addr_list, is_full_path=True)
  addr_to_loc_map.update(d)

  print 'writing output to file %s' % out_file
  with open(out_file, 'w') as f:
    for v in data:
      (addr, asm) = v
      (func, loc) = gdb_get_addr_func_loc(addr)
      # format: addr func_loc file_loc asm_stmt
      f.write('%s %s %s %s\n' % (addr, func, loc, asm))

def bin_instr_dasm_annotate(bin_file):
  print 'running objdump'
  output = obj_tools.objdump_disassemble(objdump, bin_file)

  print 'parse objdump output'
  data = []
  for line in output.splitlines():
    v = line.strip().split('\t', 2)
    if len(v) < 3:
      continue
    addr = v[0].split(':', 1)
    if len(addr) != 2:
      print v
      print addr
      assert False

    addr = '0x' + addr[0]
    asm = v[2]
    data.append([addr, asm])

  out_file = '%s.instr_dasm' % bin_file
  instr_annotate(bin_file, out_file, data)

def sam_instr_dasm_annotate(bin_file, sam_dir):
  sam_ann_flist = glob.glob('%s/*.annotate' % sam_dir)
  if len(sam_ann_flist) == 0:
    print '%s has no *.annotate files' % sam_dir
    return

  data = []
  for fname in sam_ann_flist:
    print 'parsing %s' % fname
    with open(fname, 'r') as f:
      for line in f:
        v = line.strip().split(' ', 3)
        addr = '0x' + v[2]
        asm = v[3].strip()
        data.append([addr, asm])
 
  out_file = os.path.join(sam_dir, 'samurai.instr_dasm')
  instr_annotate(bin_file, out_file, data)

def usage():
  print 'usage: %s <funos-f1-emu|funos_dir> [samurai_dir]' % sys.argv[0]

if __name__ == '__main__':
  if len(sys.argv) not in [2, 3]:
    usage()
    sys.exit(-1)

  bin_file = 'funos-f1-emu'

  if os.path.isdir(sys.argv[1]):
    bin_file = os.path.join(sys.argv[1], bin_file)
  else:
    bin_file = sys.argv[1]

  if not os.path.isfile(bin_file):
    print 'File does not exist: %s' % bin_file
    usage()
    sys.exit(-1)

  if len(sys.argv) == 2:
    bin_instr_dasm_annotate(bin_file)
  else:
    sam_dir = sys.argv[2]
    if not os.path.isdir(sam_dir):
      print 'Directory does not exist: %s' % sam_dir
      usage()
      sys.exit(-1)
    sam_instr_dasm_annotate(bin_file, sam_dir)
