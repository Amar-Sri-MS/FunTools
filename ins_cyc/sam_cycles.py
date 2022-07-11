#!/usr/bin/env python3

# input:  dir containining .annotate (use sam_enc_ann.py to generate .annotate from samurai data)
# output: .annotate_detail .cost_tree .cost_tree_detail

import argparse
import os
import sys
import subprocess
import glob
import tempfile

import obj_tools

import platform

tool_map = {}
_hostOS = platform.system()
if _hostOS == 'Linux':
  tool_map['gdb']     = '/opt/cross/mips64/bin/mips64-unknown-elf-gdb'
  tool_map['objdump'] = '/opt/cross/mips64/bin/mips64-unknown-elf-objdump'
  tool_map['nm']      = '/opt/cross/mips64/bin/mips64-unknown-elf-nm'
elif _hostOS == 'Darwin':
  tool_map['gdb']     = '/Users/Shared/cross/mips64/bin/mips64-unknown-elf-gdb'
  tool_map['objdump'] = '/Users/Shared/cross/mips64/bin/mips64-unknown-elf-objdump'
  tool_map['nm']      = '/Users/Shared/cross/mips64/bin/mips64-unknown-elf-nm'
else:
  print("Unsupported OS:", _hostOS)
  assert False

addr_to_func_map = {}
addr_to_loc_map = {}

def funos_path(wdir):
  funos = 'funos-f1-emu'
  if wdir:
    funos = '%s/%s' % (wdir, funos)
  if not os.path.exists(funos):
    print('%s not found' % funos)
    sys.exit(-1)
  return funos

def gdb_get_addr_func_loc(addr):
  func = addr_to_func_map.get(addr, '<unknown>')
  loc = addr_to_loc_map.get(addr, '??:?')
  return (func, loc)

class FunctionState(object):
  bubble_limit = 30
  prev_i_row = None

  def __init__(self, func, depth, caller):
    self.func = func
    self.depth = depth
    self.caller = caller
    self.rows = []
    self.i_row_first = None
    self.i_row_last = None
    self.execution_summary = None
    self.execution_start_row = FunctionState.prev_i_row

  def _row_add_real(self, row):
      self.rows.append(row)

  def i_row_add(self, row):
      # update first, last
      if self.i_row_first == None:
        self.i_row_first = row
      self.i_row_last = row

      bubble = self.compute_bubble(row)
      if bubble:
        assert len(row) == 2
        row.append(bubble)
        self._row_add_real(row)

  def row_add(self, row):
    assert self.execution_summary == None
    if isinstance(row, list):
      self.i_row_add(row)
    else:
      self._row_add_real(row)

  def compute_summary(self):
    if not self.execution_start_row:
      self.execution_start_row = self.i_row_first
    num_cycles = self.i_row_last[0][1] - self.execution_start_row[0][1]
    num_instr  = self.i_row_last[1][0] - self.execution_start_row[1][0]
    assert self.execution_summary == None
    self.execution_summary = '%s: (%s cycles, %s instr)' % (self.func, num_cycles, num_instr)
    self.execution_summary += '\t%s %s' % (self.i_row_first[0][0], self.i_row_first[0][1])

  def compute_bubble(self, next_row):
    prev_row = FunctionState.prev_i_row
    FunctionState.prev_i_row = next_row
    if prev_row != None:
      cycles = int(next_row[0][1]) - int(prev_row[0][1])
      if cycles >= FunctionState.bubble_limit:
        bubble = 'bubble(%s cycles)' % cycles
        return bubble
    return None

  def func_call(self, row):
    fst = FunctionState(row[1][1], self.depth + 1, self)
    self.row_add(fst)
    fst.row_add(row)
    return fst

  def func_ret(self, row):
    self.compute_summary()

    if row:
      if self.caller and (self.caller.func != row[1][1]):
        return self.caller.func_ret(row)
    return self.caller

  def func_same(self, row):
    self.row_add(row)

  def output_string(self, s, out_func, is_honor_tabs, extra_tabs=0):
    num_tabs = 0
    if is_honor_tabs:
      num_tabs = self.depth + extra_tabs
    out_func('%s%s\n' % ('\t' * num_tabs, s))

  def output_cost_tree(self, out_func, is_detail, is_honor_tabs):
    self.output_string(self.execution_summary, out_func, is_honor_tabs)

  def output_row(self, r, out_func, is_detail, is_honor_tabs):
    if not is_detail:
      return
    if isinstance(r, list):
      bubble = '%s: ' % r[2] if len(r) > 2 else ''
      r = bubble + '%s %s: %s %s %s %s' % r[0]
    assert isinstance(r, str)
    self.output_string(r, out_func, is_honor_tabs, extra_tabs=1)

  def incr_depth_recursive(self):
    self.depth += 1
    for r in self.rows:
      if isinstance(r, FunctionState):
        r.incr_depth_recursive()

  def dump_recursive(self, out_func, is_detail, is_honor_tabs=True):
    self.output_cost_tree(out_func, is_detail, is_honor_tabs)
    for r in self.rows:
      if isinstance(r, FunctionState):
        r.dump_recursive(out_func, is_detail, is_honor_tabs)
      else:
        self.output_row(r, out_func, is_detail, is_honor_tabs)

class SummaryOutputState(object):
  def __init__(self, is_honor_tabs=True):
    self.is_honor_tabs = is_honor_tabs
    self.out_f = None
    self.old_row = None
    self.fst = None
    self.fst_list = []

  def set_output_file_hdl(self, out_f):
    self.out_f = out_f

  def bubble_output(self, new_row):
    if self.old_row and new_row:
      cycles = int(new_row[0][1]) - int(self.old_row[0][1])
      if cycles > 4:
        return 'bubble(%s cycles)' % cycles
    return None

  def output_string(self, s):
    num_tabs = 0
    if self.is_honor_tabs and self.fst:
      num_tabs = self.fst.depth
    self.out_f.write('%s%s\n' % ('\t' * num_tabs, s))

  def output_row(self, row):
    bubble = self.bubble_output(row)
    if bubble:
      self.output_string(bubble)

    self.output_string('%s %s: %s %-50s %-32s %s' % row[0])

    self.old_row = row

  def is_func_changed(self, row):
    if self.old_row == None:
      return True
    return row[1][1] != self.old_row[1][1]

  #def is_old_row_asm_call(self):
    #if self.old_row:
      #asm_instr = self.old_row[0][5].strip().split(' ', 1)[0]
      #if asm_instr in ['bc', 'balc']:
        #return True
    #return False

  def is_func_begin(self, row):
    if row[1][2] <= 4:
      return True
    #if self.is_old_row_asm_call():
    #  return True
    return False

  def func_call(self, row, depth=0):
    if self.fst:
      self.fst = self.fst.func_call(row)
    else:
      self.fst = FunctionState(row[1][1], depth, None)
      self.fst.row_add(row)
      self.fst_list.append(self.fst)

  def func_ret(self, row):
    if self.fst:
      self.fst = self.fst.func_ret(row)
    if not self.fst:
      for fst in self.fst_list:
        fst.incr_depth_recursive()
      self.func_call(row)
    else:
      self.fst.row_add(row)

  def func_same(self, row):
    self.fst.func_same(row)
    return None

  def check_new_row(self, row):
    dbg = None
    if self.is_func_changed(row):
      if self.is_func_begin(row):
        dbg = self.func_call(row)
      else:
        dbg = self.func_ret(row)
    else:
        dbg = self.func_same(row)

    self.output_row(row)

  def finish_output(self, out_file_list):
    # func ret all
    while self.fst:
      self.fst = self.fst.func_ret(None)
    # dump
    for inx in [0, 1]:
      print('\twriting file %s' % out_file_list[inx])
      with open(out_file_list[inx], 'w') as out_f:
        for fst in self.fst_list:
          fst.dump_recursive(out_f.write, is_detail=inx)

def output_cost_tree(in_file, out_file_list):
  st = SummaryOutputState(is_honor_tabs=True)

  lnum = 0 # line number
  with open(in_file, 'r') as f:
    print('\twriting file %s' % out_file_list[0])
    with open(out_file_list[0], 'w') as out_f:
      #out_f = sys.stdout
      st.set_output_file_hdl(out_f)
      for line in f:
        lnum += 1
        (rec_type, cycle_inx, addr, asm_code) = line.strip().split(' ', 3)
        cycle_inx = int(cycle_inx.split(':')[0])
        (func, loc) = gdb_get_addr_func_loc('0x%s' % addr)
        tmp = func[1:-1].split('+')
        func_name = tmp[0]
        func_offset = int(tmp[1]) if len(tmp) == 2 else 0
        (loc_f, loc_l) = loc.split(':')
        row = [(rec_type, cycle_inx, addr, func, loc, asm_code), [lnum, func_name, func_offset, loc_f, loc_l]]
        st.check_new_row(row)

      st.finish_output(out_file_list[1:])

def annotate_single(funos, in_file, is_detail=False):
  print('processing %s' % in_file)
  with open(in_file, 'r') as f:
    addr_list = []
    for line in f:
      (rec_type, cycle_inx, addr, other) = line.strip().split(' ', 3)
      addr = '0x%s' % addr
      addr_list.append(addr)

  addr_list = set(addr_list)

  print('running: addr to func')
  d = obj_tools.prepare_addr_func(tool_map, funos, addr_list)
  addr_to_func_map.update(d)

  print('running: addr to line')
  d = obj_tools.prepare_addr_line(tool_map, funos, addr_list)
  addr_to_loc_map.update(d)

  out_file = in_file.replace('.annotate', '')
  suffixes = ['.annotate_detail', '.cost_tree', '.cost_tree_detail']
  output_cost_tree(in_file, [ out_file + s for s in suffixes])

def annotate_many(funos, in_file_list):
  for in_file in in_file_list:
    annotate_single(funos, in_file, is_detail=True)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('input_file_or_dir', type=str,
                      help='Path to <file>.annotate or directory containing '
                           '.annotate files')
  parser.add_argument('--funos-binary', type=str, default=None,
                      help='Path to FunOS binary. If not specified, assumes '
                           'the binary is in the same directory as the first '
                           '.annotate file and is named funos-f1-emu.')
  args = parser.parse_args()

  in_file_list = []
  in_file_arg = args.input_file_or_dir

  if os.path.isdir(in_file_arg):
    in_file_list = glob.glob('%s/*.annotate' % in_file_arg)
    if len(in_file_list) == 0:
      sys.stderr.write('No .annotate files in %s\n' % in_file_arg)
      sys.exit(0)
  else:
    if not in_file_arg.endswith('.annotate'):
      sys.stderr.write('Input file should have .annotate extension\n')
      sys.exit(-1)
    in_file_list = [in_file_arg]

  funos = None
  if args.funos_binary:
    funos = args.funos_binary
  else:
    funos = funos_path(os.path.dirname(in_file_list[0]))

  annotate_many(funos, in_file_list)

