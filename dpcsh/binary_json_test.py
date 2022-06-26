#!/usr/bin/env python3
##
##  binary_json_test.py
##
##  Created by Renat Idrisov on 2022-06-25
##  Copyright (C) 2022 Fungible. All rights reserved.
##

import binary_json
import glob
import json
import os
import unittest

TEST_DATA_LOCATION = '../fun_json_lite/testdata'

# the test below is skipped because python's json is losing some precision
# while decoding big integers as floats
TEST_SKIP_DOUBLE_ENCODE = ['test-array-complex']

# several tests are skipped because unable to match key ordering in dictionaries
TEST_SKIP_EXACT_ENCODE = ['test-case1', 'test-dict-complex',
  'test-dict-complex-with-array', 'test-dict-leafs']

class TestsContainer(unittest.TestCase):
  longMessage = True

def make_test_function(name):
  def test(self):
    with open(TEST_DATA_LOCATION + '/' + name + '.json', 'r') as f:
      json_source = f.read()
    with open(TEST_DATA_LOCATION + '/' + name + '.bjson', 'rb') as f:
      binary_source = bytes(f.read())
    json_data = json.loads(json_source)
    binary_result = binary_json.encode(json_data)
    if name not in TEST_SKIP_EXACT_ENCODE:
      self.assertEqual(binary_result, binary_source)
    if name in TEST_SKIP_DOUBLE_ENCODE:
      return
    binary_data = binary_json.decode(binary_result)
    binary_double_decode =  binary_json.encode(binary_data)
    self.assertEqual(binary_result, binary_double_decode)
  return test

if __name__ == '__main__':
  test_cases = glob.glob(TEST_DATA_LOCATION + '/*.json')

  for t in test_cases:
    name = os.path.splitext(os.path.basename(t))[0]
    setattr(TestsContainer, name, make_test_function(name))

  unittest.main()