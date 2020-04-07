#!/usr/bin/python
from __future__ import print_function
import datetime
import errno
import glob
import os
import subprocess
import sys
import time

INPUT_DUMP_DIR = '/var/lib/tftpboot/'
OUTPUT_DUMP_DIR = '/var/log/hbm_dumps/'
DUMP_PREFIX = 'HBM'
DUMPS_TO_KEEP = 3
PIECES_TOTAL = 12
DUMP_TIMEOUT = (PIECES_TOTAL + 5) * 50 # 50 seconds per part

def ensure_dir(path):
  try:
      os.makedirs(path)
  except OSError as e:
      if errno.EEXIST != e.errno:
          raise

def eval_f1_mac(bmc_mac, dpu_num):
  offsets = [8, 52]
  f1_mac = int(bmc_mac.replace(':', '').strip(), 16) + offsets[dpu_num]
  return hex(f1_mac)

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

# Fetch new one with timeout
dump_parts_wildcard = INPUT_DUMP_DIR + f1_mac + '*'
while len(glob.glob(dump_parts_wildcard)) < PIECES_TOTAL:
  time.sleep(1)

# Timeout the dump is partial
if len(glob.glob(dump_parts_wildcard)) < PIECES_TOTAL:
  print('Timeout')
  sys.exit(2)

# Assemble
output_file_name = OUTPUT_DUMP_DIR + DUMP_PREFIX + "_" + str(dpu_num) + \
      datetime.datetime.now().strftime('%m-%d-%Y-%H-%M-%S') + '_BLD' + build + '.core'

with open(output_file_name, 'wb') as out:
  for input_file_name in sorted(glob.glob(dump_parts_wildcard)):
    with open(input_file_name, 'rb') as input_file:
      out.write(input_file.read())

subprocess.call(['/bin/tar' '-cjf',
  output_file_name + '.bz2', output_file_name, '--remove-files'], shell=True)