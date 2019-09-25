#!/usr/bin/python

import argparse
import os
import re
import sys

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template

my_tmpl="s1_nu_intr.tmpl"
reg_line_begin="struct csr2fields_"
reg_line_end="_int_status {"
bit_line_begin="bool "
bit_line_end=";"

def Usage():
  sys.stderr.write("s1_nu_intr_gen.py: usage: <filename>\n")
  sys.stderr.write("  <filename>: input source (*.h) for code generation.\n")

def ParseReg(x):
    match1 = re.search(reg_line_begin, x)
    match2 = re.search(reg_line_end, x)
    if match1 and match2:
      return x[match1.end():match2.start()]
    return None

def ParseBit(y):
    m1 = re.search(bit_line_begin, y)
    m2 = re.search(bit_line_end, y)
    if m1 and m2:
      return y[m1.end():m2.start()]
    return None

def Parse(filename):
  try:
    #print("file open ", filename)
    f = open(filename)
    reg_bit = 0
  except Exception as err:
    """ No file?  Probably testing or stdin. """
    print("file open failed")
    return None

  #print("loop start...")
  reg_list=list()
  for x in f:
    if reg_bit == 0:
      reg = ParseReg(x)
      if reg:
        reg_bit = 1
        bit_list=list()
      continue
    else:
      bit = ParseBit(x)
      if bit:
          bit_list.append(bit)
      else:
        reg_list.append(dict(name=reg, bit_list=bit_list))
        reg_bit = 0
        continue
  f.close()
  #print "input done"
  #print reg_list
  #print bit_list
  #print "start done"
  return reg_list

def Gen(base, reg_list):
  this_dir = os.path.dirname(os.path.abspath(__file__))
  env = Environment(loader=FileSystemLoader(this_dir))
  tmpl = env.get_template(my_tmpl)

  print "base =", base
  outfn = 'hw_nu_' + base + '.c'
  print "outfn =", outfn
  #print reg_list

  f = open(outfn, "w")
  jinja_docs = {
    'output_base' : base,
    'reg_list' : reg_list,
  }
  f.write(tmpl.render(jinja_docs))
  f.close()
  #for i in reg_list:
  #  print i.name
  #  del i.bit_list
  del reg_list

def main():
  pargs = argparse.ArgumentParser(description='Command-line example')
  pargs.add_argument(nargs='*', action='store', dest='inputs', help='input filenames')
  args = pargs.parse_args()
  #print args.__dict__

  for filename in args.inputs:
    print "Processing file", filename
    # extra filename -> output_base
    toklist = re.split("/", filename)
    #print "tklist ", toklist[-1]
    tmp0 = re.split("\.", toklist[-1])
    tmp1 = re.split("nu_", tmp0[0])
    for x in tmp1:
	base = re.split("_nu", x)
    #print "base ", base

    Gen(base[0], Parse(filename))

if __name__ == '__main__':
  main()
