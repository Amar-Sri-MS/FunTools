#!/usr/bin/env python3

import os
import subprocess

testdata = 'testdata/'

for file in os.listdir(testdata):
  if file.endswith('.bjson') and os.path.isfile(testdata + file):
    subprocess.check_call('./posix-build/fun_json_lite_tester ' + testdata + file + ' out.bjson', shell=True)
    subprocess.check_call('diff -b ' + testdata + file + ' out.bjson', shell=True)
    print(file + ' -- OK')