#!/usr/bin/python

import os
import re

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template

my_tmpl="s1_nu_intr.tmpl"
reg_line_begin="struct csr2fields_"
reg_line_end="_status {"
bit_line_begin="bool "
bit_line_end=";"
reg_list = []
bit_list = []

def parse_reg(x):
    match1 = re.search(reg_line_begin, x)
    match2 = re.search(reg_line_end, x)
    if match1 and match2:
      return x[match1.end():match2.start()]
    return None

def parse_bit(y):
    m1 = re.search(bit_line_begin, y)
    m2 = re.search(bit_line_end, y)
    if m1 and m2:
      return y[m1.end():m2.start()]
    return None

def start(filename):
  try:
    print("file open ", filename)
    f = open(filename)
    reg_bit = 0
  except Exception as err:
    """ No file?  Probably testing or stdin. """
    print("file open failed")
    return None

  print("file open ok")
  reg_cnt = 0
  print("loop start...")
  for x in f:
    if reg_bit == 0:
      reg = parse_reg(x)
      if reg:
        print "reg", reg_cnt, reg
        reg_list.append(reg)
        bit_cnt = 0
        reg_bit = 1
      continue
    else:
      bit = parse_bit(x)
      if bit:
        if bit_cnt == 0:
            new_list = list()
        print "\tbit", reg_cnt, bit_cnt, bit
        new_list.append(bit)
        bit_cnt += 1
      else:
        bit_list.append(new_list)
        reg_cnt += 1
        reg_bit = 0
        continue
  f.close()
  print "input done"
  print reg_list
  print bit_list
  print "start done"

def gen():
  this_dir = os.path.dirname(os.path.abspath(__file__))
  env = Environment(loader=FileSystemLoader(this_dir))
  tmpl = env.get_template(my_tmpl)

  jinja_docs = {
    'output_base' : "SFG",
    'reg_list' : reg_list,
    'bit_list' : bit_list
  }
  print(tmpl.render(jinja_docs))

def main():
  start("../../FunSDK/FunSDK/chip/s1/include/FunChip/csr2/sfg.h")
  gen()

if __name__ == '__main__':
  main()
