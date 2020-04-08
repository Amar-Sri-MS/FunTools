#!/usr/bin/python
from __future__ import print_function
import datetime
import errno
import glob
import os
import subprocess
import sys
import time

INPUT_DUMP_PREFIX = '/var/lib/tftpboot/hbmdump_'
OUTPUT_DUMP_DIR = '/var/log/hbm_dumps/'
DUMP_PREFIX = 'HBM'
DUMPS_TO_KEEP = 3
PART_COMPLETE_SIZE = 536805376
TIME_PER_PART = 50
FIRST_PIECE_TIMEOUT = TIME_PER_PART * 2
PIECES_TOTAL = 16
DUMP_TIMEOUT = (PIECES_TOTAL + 5) * TIME_PER_PART # 50 seconds per part

def ensure_dir(path):
  try:
      os.makedirs(path)
  except OSError as e:
      if errno.EEXIST != e.errno:
          raise

def eval_f1_mac(bmc_mac, dpu_num):
  offsets = [8, 52]
  f1_mac = int(bmc_mac.replace(':', '').strip(), 16) + offsets[dpu_num]
  return hex(f1_mac)[2:]

def wait_for(wildcard, num_parts, timeout, min_size):
  for _ in range(0, timeout):
    files = glob.glob(wildcard)
    if len(files) >= num_parts and \
        all(map(lambda x: os.path.getsize(x) >= min_size, files)):
      return True
    time.sleep(1)
  return False

if len(sys.argv) < 4:
  print('Usage ' + sys.argv[0] + ' <BMC_MAC> <DPU_NUMBER> <BUILD>')
  print('Example: ' + sys.argv[0] + ' aa:bb:cc:dd:ee:ff 0 UNKNOWN')
  sys.exit(1)

dpu_num = int(sys.argv[2])
f1_mac = eval_f1_mac(sys.argv[1], dpu_num)
build = sys.argv[3]
print('Assembling for DPU#' + str(dpu_num) + ' MAC: ' + f1_mac)

ensure_dir(OUTPUT_DUMP_DIR)
# Delete old dumps
dump_wildcard = OUTPUT_DUMP_DIR + DUMP_PREFIX + "_" + str(dpu_num) + '*.bz2'
map(os.unlink, sorted(glob.glob(dump_wildcard), reverse = True)[3:])

# Wait for pieces with timeout
dump_parts_wildcard = INPUT_DUMP_PREFIX + f1_mac + '*'
if not wait_for(dump_parts_wildcard, 1, FIRST_PIECE_TIMEOUT, 0) or \
   not wait_for(dump_parts_wildcard, PIECES_TOTAL, DUMP_TIMEOUT, PART_COMPLETE_SIZE):
  print('Timeout')
  sys.exit(2)

# Assemble
output_file_name = OUTPUT_DUMP_DIR + DUMP_PREFIX + '_D' + str(dpu_num) + '_' + \
      datetime.datetime.now().strftime('%m-%d-%Y-%H-%M-%S') + '_BLD' + build + '.core'

with open(output_file_name, 'wb') as out:
  for input_file_name in sorted(glob.glob(dump_parts_wildcard)):
    with open(input_file_name, 'rb') as input_file:
      out.write(input_file.read())
    os.unlink(input_file_name)

subprocess.call('/bin/tar -cjf ' + \
  output_file_name + '.bz2 --remove-files ' + output_file_name, shell=True)