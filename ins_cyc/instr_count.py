#!/usr/bin/env python2.7

# input: .instr_dasm (generated by instr_dasm.py)
# output: .instr_count

import os
import sys
import argparse
import subprocess
import itertools

def parse_instr_dasm_unique(in_file):
  # format: addr func_loc file_loc asm_stmt
  data = {}
  with open(in_file, 'r') as f:
    for line in f:
      v = line.strip().split(' ', 3)
      data[v[0]] = v
  return data.values()

def func_cmp(a, b):
  v = a.translate(None, '<>').split('+')
  f1 = v[0]
  l1 = v[1] if len(v) > 1 else 0
  v = b.translate(None, '<>').split('+')
  f2 = v[0]
  l2 = v[1] if len(v) > 1 else 0
  if f1 == f2:
    try:
      l1 = int(l1)
      l2 = int(l2)
    except:
      pass
    if l1 == l2:
      return 0
    return -1 if l1 < l2 else 1
  return -1 if f1 < f2 else 1

def loc_cmp(a, b):
  (f1, l1) = a.split(':')
  (f2, l2) = b.split(':')
  if f1 == f2:
    try:
      l1 = int(l1)
      l2 = int(l2)
    except:
      pass
    if l1 == l2:
      return 0
    return -1 if l1 < l2 else 1
  return -1 if f1 < f2 else 1

def loc_and_func_cmp(a, b):
  ret = loc_cmp(a[2], b[2])
  if ret == 0:
    ret = func_cmp(a[1], b[1])
  return ret

def group_key(a):
  loc = a[2]
  fname = a[1].translate(None, '<>').split('+')[0]
  return [loc, fname]

def location_sorted_loc_func(data):
  return sorted(data, cmp=loc_and_func_cmp)

def group_by_loc_fname(data):
  g_data = []
  for k, v in itertools.groupby(data, key=group_key):
    v = list(v)
    instr_count = len(v)
    instr_list = [[x[1], x[3]] for x in v]
    g_data.append([str(instr_count), v[0][2], instr_list])
  return g_data

def instr_count_cmp(a, b):
  c1 = int(a[0])
  c2 = int(b[0])
  if c1 == c2:
    return 0
  return -1 if c1 < c2 else 1

def instr_count_sorted(data, reverse=False):
  return sorted(data, cmp=instr_count_cmp, reverse=reverse)

def instr_data_add_code(data, code_dirs=None):
  f_l_map = {}
  for v in data:
    try:
      (loc_f, loc_l) = v[1].split(':', 1)
      loc_l = int(loc_l)
      if loc_f in f_l_map:
        f_l_map[loc_f].append(loc_l)
      else:
        f_l_map[loc_f] = [loc_l]
    except Exception as e:
      pass

  f_n_map = {}
  for loc_f in f_l_map.keys():
    full_loc_f = None
    if code_dirs:
      for d in code_dirs:
        f = os.path.join(d, loc_f)
        if os.path.isfile(f):
          full_loc_f = f
          break
      if full_loc_f and os.path.isfile(full_loc_f):
        f_n_map[loc_f] = full_loc_f

  fl_code_map = {}
  for loc_f, lines in f_l_map.iteritems():
    lines = sorted(lines)
    try:
      full_loc_f = f_n_map[loc_f]
      with open(full_loc_f, 'r') as in_f:
        code_lines = in_f.readlines()
        for loc_l in lines:
          k = '%s:%s' % (loc_f, loc_l)
          v = code_lines[loc_l - 1].rstrip()
          fl_code_map[k] = v
    except Exception as e:
      pass

  for v in data:
    text = fl_code_map.get(v[1], None)
    if text:
      v.append(text)

  return data

def instr_count_write(data, out_f, show_instr=False, show_unknown=False):
  for v in data:
    (instr_count, loc, instr_list) = v[0:3]
    if show_unknown == False and loc == '??:?':
      continue
    s = instr_list[0][0]
    if len(instr_list) > 1:
      s += '...%s' % instr_list[-1][0]
    s = [instr_count, loc, s]
    if len(v) > 3:
      text = v[3]
      if text:
        s.append(text.strip())
    out_f.write('\t'.join(s) + '\n')
    if show_instr:
      for a in instr_list:
        out_f.write('\t\t%s\t%s\n' % (a[0], a[1]))

def instr_count_generate(in_file, code_dirs=None):
  print 'parsing %s' % in_file
  data = parse_instr_dasm_unique(in_file)

  print 'sorting by location'
  data = location_sorted_loc_func(data)

  print 'grouping by code location and function name'
  data = group_by_loc_fname(data)

  print 'sorting by count'
  data = instr_count_sorted(data, reverse=True)

  if code_dirs:
    print 'adding code'
    data = instr_data_add_code(data, code_dirs=code_dirs)

  return data

def main():
  def usage():
    print 'usage: %s [-siu] <funos-f1-emu.instr_dasm|samurai.instr_dasm>' % sys.argv[0]

  parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-s', action='store', default=None, help='source code directory (delimit \',\' for many)')
  parser.add_argument('-i', action='store_true', default=False, help='show instructions')
  parser.add_argument('-u', action='store_true', default=False, help='show unknown')
  parser.add_argument('instr_dasm_file', nargs='?', default='funos-f1-emu.instr_dasm')
  args = parser.parse_args()

  in_file = 'funos-f1-emu.instr_dasm'
  if os.path.isdir(args.instr_dasm_file):
    in_file = os.path.join(args.instr_dasm_file, in_file)
  else:
    in_file = args.instr_dasm_file

  if not os.path.isfile(in_file):
    print 'File does not exist: %s' % in_file
    usage()
    return -1
  if not in_file.endswith('.instr_dasm'):
    print 'WARNING: File does not end with .instr_dasm: %s' % in_file

  if args.s:
    code_dirs = []
    for d in args.s.split(','):
      d = os.path.expanduser(d)
      if os.path.isdir(d):
        code_dirs.append(d)
      else:
        print 'Directory does not exist: %s, ignoring it' % d
    args.s = code_dirs if len(code_dirs) else None

  # generate
  data = instr_count_generate(in_file, code_dirs=args.s)

  # write output
  out_file = in_file.replace('.instr_dasm', '.instr_count')
  if args.i:
    out_file += '_i'
  if args.u:
    out_file += '_u'
  print 'saving output to %s' % out_file
  with open(out_file, 'w') as out_f:
    instr_count_write(data, out_f, show_instr=args.i, show_unknown=args.u)

  return 0

if __name__ == '__main__':
  sys.exit(main())
