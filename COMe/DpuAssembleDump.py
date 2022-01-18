#!/usr/bin/env python2.7
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
FIRST_PIECE_TIMEOUT = 200
PIECES_TOTAL = 16
DUMP_TIMEOUT = (PIECES_TOTAL + 5) * TIME_PER_PART # 50 seconds per part


def ensure_dir(path):
  try:
      os.makedirs(path)
  except OSError as e:
      if errno.EEXIST != e.errno:
          raise


def eval_f1_mac(bmc_mac, dpu_num):
  offsets = [8 + 24, 52 + 24]
  f1_mac = int(bmc_mac.replace(':', '').strip(), 16) + offsets[dpu_num]
  return hex(f1_mac)[2:]


def wait_for(wildcard, num_parts, timeout, min_size):
  start_time = time.time()
  while time.time() < start_time + timeout:
    files = glob.glob(wildcard)
    if len(files) >= num_parts and \
        all(map(lambda x: os.path.getsize(x) >= min_size, files)):
      return True
    time.sleep(1)
  return False


def unlink_verbose(filename):
  print('Unlink: ' + filename)
  os.unlink(filename)


def dump_parts_all_wildcard(f1_mac):
  return INPUT_DUMP_PREFIX + f1_mac + '*'


# This function normally returns prefixed dump name:
# dir/hbmdump_c82c2b00346c_e90924*
def dump_parts_latest_wildcard(f1_mac):
  all_parts = glob.glob(dump_parts_all_wildcard(f1_mac))
  if len(all_parts) == 0:
    return dump_parts_all_wildcard(f1_mac)
  ts_part = zip(map(os.path.getmtime, all_parts), all_parts)
  ts_part.sort(key = lambda x: x[0], reverse = True)

  return "_".join(ts_part[0][1].split('_')[:-1]) + '*'


if len(sys.argv) < 4:
  print('Usage ' + sys.argv[0] + ' <BMC_MAC> <DPU_NUMBER> <BUILD>')
  print('Example: ' + sys.argv[0] + ' aa:bb:cc:dd:ee:ff 0 UNKNOWN')
  print('Args received: ' + str(sys.argv))
  sys.exit(1)

dpu_num = int(sys.argv[2])
f1_mac = eval_f1_mac(sys.argv[1], dpu_num)
build = sys.argv[3]
start_time = time.time()
print('Assembling for DPU#' + str(dpu_num) + ' MAC: ' + f1_mac)

ensure_dir(OUTPUT_DUMP_DIR)
# Delete old dumps
dump_wildcard = OUTPUT_DUMP_DIR + DUMP_PREFIX + "_D" + str(dpu_num) + '*.bz2'
map(unlink_verbose, sorted(glob.glob(dump_wildcard), reverse = True)[3:])

# Wait for pieces with timeout
dump_parts_wildcard = dump_parts_all_wildcard(f1_mac)
if not wait_for(dump_parts_wildcard, 1, FIRST_PIECE_TIMEOUT, 0) or \
   not wait_for(dump_parts_latest_wildcard(f1_mac), PIECES_TOTAL, DUMP_TIMEOUT, PART_COMPLETE_SIZE):
  subprocess.call('ls -l ' + dump_parts_wildcard, shell=True)
  map(unlink_verbose, sorted(glob.glob(dump_parts_wildcard)))
  print('Timeout')
  sys.exit(2)

# Assemble
output_file_name = OUTPUT_DUMP_DIR + DUMP_PREFIX + '_D' + str(dpu_num) + '_' + \
      datetime.datetime.now().strftime('%m-%d-%Y-%H-%M-%S') + '_BLD' + build + '.core'

with open(output_file_name, 'wb') as out:
  dump_parts_wildcard = dump_parts_latest_wildcard(f1_mac)
  for input_file_name in sorted(glob.glob(dump_parts_wildcard)):
    with open(input_file_name, 'rb') as input_file:
      out.write(input_file.read())
      print('Consumed: ' + input_file_name)
    unlink_verbose(input_file_name)
  out.flush()

subprocess.call('/bin/tar -cjf ' + \
  output_file_name + '.bz2 --remove-files ' + output_file_name, shell=True)

print('Elapsed time: ' + str(time.time() - start_time) + ' seconds')

