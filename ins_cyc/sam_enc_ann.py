#!/usr/bin/python2.7

# input: directory containing samurai .trace files
# output: .annotate (use sam_cycles.py for further analysis)

import os
import sys
import subprocess
import glob

funtools = None
objdump = '/opt/cross/mips64/bin/mips64-unknown-elf-objdump'

def funos_dasm_path(wdir):
  funos = 'funos-f1-emu'
  if wdir:
    funos = '%s/%s' % (wdir, funos)

  if not os.path.exists(funos):
    print '%s not found' % funos
    sys.exit(-1)

  funos_dasm = '%s.dasm' % funos
  if not os.path.exists(funos_dasm):
    if not os.path.isfile(objdump):
      print 'objdump does not exist'
      sys.exit(-1)

    cmd = '%s -z -d "%s" > "%s"' % (objdump, funos, funos_dasm)
    subprocess.check_output(cmd, shell=True)
  return funos_dasm

def setup_funtools_path():
  global funtools
  funtools = os.getenv('FUNTOOLS')
  if not funtools:
    print 'please set FUNTOOLS environment variable'
    sys.exit(-1)
  if not os.path.isdir(funtools):
    print '%s is not a directory' % funtools
    sys.exit(-1)

def encode_single(in_file):
  arg2 = in_file.replace('samurai_', '').replace('.trace', '')
  print in_file, arg2
  cmd = ['%s/ins-trace/build/encode' % funtools, in_file, arg2]
  if not os.path.isfile(cmd[0]):
    print '%s does not exist' % cmd[0]
    sys.exit(-1)

  subprocess.check_output(cmd)

def annotate_single(funos_dasm, in_file):
  out_file = in_file.replace('.te', '.annotate')
  print 'annotate', in_file, out_file
  
  cmd = ['%s/ins-trace/build/annotate' % funtools, funos_dasm, in_file]
  if not os.path.isfile(cmd[0]):
    print '%s does not exist' % cmd[0]
    sys.exit(-1)

  #if os.stat(cmd[0]).st_size < 2:
  #  print '%s: too small, skipping' % cmd[0]
  #  sys.exit(-1)

  output = subprocess.check_output(cmd)
  if not output:
    print 'empty, skip writing of %s' % out_file
    return
  with open(out_file, 'w') as f:
    f.write(output)

def encode_and_annotate(in_file_list):
  if len(in_file_list) == 0:
    return

  funos_dasm = funos_dasm_path(os.path.dirname(in_file_list[0]))
  setup_funtools_path()

  # encode
  for in_file in in_file_list:
    encode_single(in_file)

  wdir = os.path.dirname(in_file_list[0])
  enc_file_list = glob.glob('%s/*.te' % wdir)

  # annotate
  for in_file in enc_file_list:
    annotate_single(funos_dasm, in_file)

def usage():
  print 'usage: %s <file.trace|dir>' % sys.argv[0]

if __name__ == '__main__':
  print sys.argv
  if len(sys.argv) != 2:
    usage()
    sys.exit(-1)

  in_file_list = []

  if os.path.isdir(sys.argv[1]):
    in_file_list = glob.glob('%s/*.trace' % sys.argv[1])
  else:
    if not sys.argv[1].endswith('.trace'):
      usage()
      sys.exit(-1)
    in_file_list = [sys.argv[1]]

  encode_and_annotate(in_file_list)
