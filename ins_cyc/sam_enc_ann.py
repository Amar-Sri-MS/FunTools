#!/usr/bin/env python3

# input: directory containing samurai .trace files
# output: .annotate (use sam_cycles.py for further analysis)

import argparse
import glob
import os
import re
import sys
import subprocess

funtools = None
objdump = '/opt/cross/mips64/bin/mips64-unknown-elf-objdump'

def funos_dasm_path(wdir):
  funos = 'funos-f1-emu'
  if wdir:
    funos = '%s/%s' % (wdir, funos)

  if not os.path.exists(funos):
    print('%s not found' % funos)
    sys.exit(-1)

  funos_dasm = '%s.dasm' % funos
  if not os.path.exists(funos_dasm):
    if not os.path.isfile(objdump):
      print('objdump does not exist')
      sys.exit(-1)
    #
    # These options match the -d option that was provided, only that
    # -D deals better with debug symbols in the dispatch loop
    #
    cmd = ('%s -z -D '
           '-j .text_ram '
           '-j .text_init '
           '-j .sandbox "%s" > "%s"' % (objdump, funos, funos_dasm))
    subprocess.check_output(cmd, shell=True)
  return funos_dasm

def setup_funtools_path():
  global funtools
  funtools = os.getenv('FUNTOOLS')
  if not funtools:
    print('please set FUNTOOLS environment variable')
    sys.exit(-1)
  if not os.path.isdir(funtools):
    print('%s is not a directory' % funtools)
    sys.exit(-1)

def encode_single(in_file):
  arg2 = in_file.replace('samurai_', '').replace('.trace', '')
  print(in_file, arg2)
  cmd = ['%s/ins-trace/build/encode' % funtools, in_file, arg2]
  if not os.path.isfile(cmd[0]):
    print('%s does not exist' % cmd[0])
    sys.exit(-1)

  subprocess.check_output(cmd)

def annotate_single(funos_dasm, in_file):
  out_file = in_file.replace('.te', '.annotate')
  print('annotate', in_file, out_file)
  
  cmd = ['%s/ins-trace/build/annotate' % funtools, funos_dasm, in_file]
  if not os.path.isfile(cmd[0]):
    print('%s does not exist' % cmd[0])
    sys.exit(-1)

  #if os.stat(cmd[0]).st_size < 2:
  #  print '%s: too small, skipping' % cmd[0]
  #  sys.exit(-1)
  try:
    output = subprocess.check_output(cmd)
    if not output:
      print('empty, skip writing of %s' % out_file)
      return
    with open(out_file, 'w') as f:
      f.write(output)
  except subprocess.CalledProcessError as e:
    print('Exception while running %s, skipping annotate for %s' % (cmd,
                                                                    in_file))

def encode_and_annotate(in_file_list, funos_dasm):
  setup_funtools_path()

  # encode
  for in_file in in_file_list:
    encode_single(in_file)

  wdir = os.path.dirname(in_file_list[0])

  for in_file in in_file_list:
    # Try to select those files relevant to the specified in file, or
    # we'll be doing n^2 work if we run this on a per-file basis.
    match = re.match(r'.*samurai_core(\d+_\d+)\.trace', in_file)
    core_id = ''
    if match:
      core_id = match.group(1)
    else:
      sys.stderr.write('Skipping %s: did not match expected trace '
                       'filename pattern\n' % in_file)
      continue

    enc_file_list = glob.glob('%s/*%s*.te' % (wdir, core_id))

    # annotate
    for enc_file in enc_file_list:
      annotate_single(funos_dasm, enc_file)

def usage():
  print('usage: %s <file.trace|dir>' % sys.argv[0])

if __name__ == '__main__':
  print(sys.argv)
  parser = argparse.ArgumentParser()
  parser.add_argument('trace_file_or_dir', type=str,
                      help='<file>.trace or directory containing trace files')
  parser.add_argument('--dasm-file', type=str, default=None,
                      help='Path to dasm file. If not provided, this script '
                           'generates the dasm assuming the FunOS binary is '
                           'in the same directory as the trace files.')
  args = parser.parse_args()

  in_file_list = []

  if os.path.isdir(args.trace_file_or_dir):
    in_file_list = glob.glob('%s/*.trace' % args.trace_file_or_dir)
    if len(in_file_list) == 0:
      sys.stderr.write('No .trace files found in directory %s\n' %
                       args.trace_file_or_dir)
      sys.exit(0)
  else:
    # TODO: handle gzipped .trace files, also zero-length trace files
    if not args.trace_file_or_dir.endswith('.trace'):
      usage()
      sys.exit(-1)
    in_file_list = [os.path.abspath(args.trace_file_or_dir)]

  # Allow override of the default location for the dasm file. This allows
  # reuse of this script when the dasm file has already been generated
  # beforehand, and avoids assumptions about file locations.
  funos_dasm = None
  if args.dasm_file:
    funos_dasm = args.dasm_file
  else:
    funos_dasm = funos_dasm_path(os.path.dirname(in_file_list[0]))
  encode_and_annotate(in_file_list, funos_dasm)

