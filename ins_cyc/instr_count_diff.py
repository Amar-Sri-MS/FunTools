#!/usr/bin/env python3

# input: .instr_dasm (generated by instr_dasm.py)
# output: .instr_count

import os
import sys
import argparse
import subprocess
import itertools
import functools
import instr_count_query

is_debug = False

def dprint(s):
  if is_debug:
    print(s, file=sys.stderr)

# sometimes i see constprop moving to different location getting flagged as ADD and DEL
#        +3558   jrdump_sec_sha_cmn_dbg.constprop.1444   ADD
#        -3558   jrdump_sec_sha_cmn_dbg.constprop.1357   DEL
def constprop_moves_remove(data):
  i = len(data) - 1
  while i > 0:
    v = data[i]
    if len(v) > 2 and '.' in v[1]:
      j = i - 1
      vfunc = v[1].rsplit('.', 1)[0]
      while j >= 0:
        p = data[j]
        if abs(abs(p[0]) - abs(v[0])) > 5:
          break
        if p[1].rsplit('.', 1)[0] == vfunc:
          if p[2] != v[2]:
            del data[i]
            del data[j]
            i = i - 1
            break

        j = j - 1

    i = i - 1

  return data

def instr_count_diff(group_by, in_file1, in_file2, out_f, pattern=None, is_track_add_del=True):
  cmp_func = None
  if group_by == 'func':
    cmp_func = instr_count_query.count_fname_cmp
  elif group_by == 'loc':
    cmp_func = instr_count_query.count_loc_fname_cmp
  else:
    assert False, 'unknonw group_by %s' % group_by

  is_group_by_func = group_by == 'func'

  data1 = instr_count_query.group_data_prepare(in_file1, group_by=group_by, pattern=pattern)
  data2 = instr_count_query.group_data_prepare(in_file2, group_by=group_by, pattern=pattern)

  data = []

  d1 = set(data1.keys())
  d2 = set(data2.keys())

  if is_track_add_del:
    for kname in d2 - d1:
      c2 = data2[kname][0]
      v = [c2, kname]
      if group_by == 'loc':
        v +=  data2[kname][1][0][3:]
      v += ['ADD']
      data.append(v)

    for kname in d1 - d2:
      c1 = data1[kname][0]
      v = [-c1, kname]
      if group_by == 'loc':
        v +=  data1[kname][1][0][3:]
      v += ['DEL']
      data.append(v)

    if group_by == 'func':
      data = sorted(data, key=functools.cmp_to_key(cmp_func), reverse=True)
      data = constprop_moves_remove(data)

  for kname in sorted(d1 & d2):
    c1 = data1[kname][0]
    c2 = data2[kname][0]
    c_diff = c2 - c1
    if c_diff:
      v = [c_diff, kname]
      if group_by == 'loc':
        if data1[kname][1][0][3:] == data2[kname][1][0][3:]:
          v +=  data1[kname][1][0][3:]
      data.append(v)

  dprint('sort by instr_count diff')
  data = sorted(data, key=functools.cmp_to_key(cmp_func), reverse=True)

  # write output
  for v in data:
    out_f.write('%+d\t%s\n' % (v[0], '\t'.join(v[1:])))

  return data

def main():
  def usage():
    print('usage: %s [-a] [--pattern <pattern>] <instr_count_file1> <instr_count_file2>' % sys.argv[0])

  parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-d', choices=['func', 'loc'], default='func', help='diff type')
  parser.add_argument('--pattern', action='store', default=None, help='input filter regex pattern')
  parser.add_argument('-a', action='store_true', default=False, help='include added and deleted functions')
  parser.add_argument('instr_count_file1')
  parser.add_argument('instr_count_file2')
  args = parser.parse_args()

  if os.path.isdir(args.instr_count_file1):
    args.instr_count_file1 = os.path.join(args.instr_count_file1, 'funos-f1-emu.instr_count')
  if os.path.isdir(args.instr_count_file2):
    args.instr_count_file2 = os.path.join(args.instr_count_file2, 'funos-f1-emu.instr_count')

  for f in [args.instr_count_file1, args.instr_count_file2]:
    if not f.endswith('.instr_count'):
      print('WARNING: File does not end with .instr_count: %s' % f)
    if not os.path.isfile(f):
      print('File does not exist: %s' % f)
      usage()
      return -1

  out_f = sys.stdout
  data = instr_count_diff(args.d, args.instr_count_file1, args.instr_count_file2, out_f,\
                          pattern=args.pattern, is_track_add_del=args.a)
  return 0

if __name__ == '__main__':
  sys.exit(main())
