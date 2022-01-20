#!/usr/bin/python2.7
#
# python s1_nu_intr_gen.py <output dir> input_file.h
# eg.
#

import argparse
import os
import sys
import datetime

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template

h_tmpl="s1_nu_intr_h.tmpl"
c_tmpl="s1_nu_intr.tmpl"
inst_line_begin="enum csr2dev_"
inst_line_end="_instances {"
inst_end=","
inst_list_end="};"
reg_line_begin="struct csr2fields_"
reg_line_end="_status {"
bit_line_end="};"
check_fatal="fatal"

def Usage():
  sys.stderr.write("s1_nu_intr_gen.py: usage: <filename>\n")
  sys.stderr.write("  <filename>: input source (*.h) for code generation.\n")

def IsInst(x):
    match1 = x.find(inst_line_begin)
    match2 = x.find(inst_line_end)
    ret = match1 != -1 and match2 != -1
    return ret

def ParseInst(f, base):
    #print "Instance found"
    inst_list=list()
    for y in f:
        if y.find(inst_list_end) != -1:
            #print "end of inst"
            break
        match1 = y.find(base.upper())
        match2 = y.find(inst_end)
        if (match1 != -1 and match2 != -1):
            inst = y[match1:match2]
            inst_list.append(inst)
    #print inst_list
    return inst_list

def ParseReg(x):
    match1 = x.find(reg_line_begin)
    match2 = x.find(reg_line_end)
    if match1 != -1 and match2 != -1:
      #print "ParseReg MATCH", match1, match2
      ret = x[(match1 + len(reg_line_begin)):match2]
      if ret.find(check_fatal) != -1:
        return ret
    return None

def ParseBit(y):
    if y.find(bit_line_end) != -1:
      #print "PraseBit end", y
      return None
    y = y.strip();
    tok0 = y.split(" ")
    #print tok0
    tok1 = tok0[1].split(";");
    #print tok1
    return tok1[0]

def Parse(filename, base):
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
    if IsInst(x):
      inst_list = ParseInst(f, base)
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
  #print inst_list
  #print reg_list
  #print bit_list
  #print "start done"
  return inst_list, reg_list

def Gen(base, filebase, dst, inst_list, reg_list):
  this_dir = os.path.dirname(os.path.abspath(__file__))
  env = Environment(loader=FileSystemLoader(this_dir))

  #print "base =", base
  #print reg_list
  d = datetime.datetime.now()

  jinja_docs = {
    'output_base' : base,
    'filebase' : filebase,
    'inst_list' : inst_list,
    'reg_list' : reg_list,
    'date' : d.strftime("%x"),
    'year' : d.year
  }

  outfn = dst + '/' + 'hw_nu_' + base + '.h'
  f = open(outfn, "w")
  tmpl = env.get_template(h_tmpl)
  f.write(tmpl.render(jinja_docs))
  f.close()

  outfn = dst + '/' + 'hw_nu_' + base + '.c'
  f = open(outfn, "w")
  tmpl = env.get_template(c_tmpl)
  f.write(tmpl.render(jinja_docs))
  f.close()

  #for i in reg_list:
  #  print i.name
  #  del i.bit_list
  del reg_list
  del inst_list

def main():
  pargs = argparse.ArgumentParser(description='Command-line example')
  pargs.add_argument(nargs='*', action='store', dest='inputs', help='input filenames')
  args = pargs.parse_args()
  #print args.__dict__

  for filename in args.inputs:
    if filename == args.inputs[0]:
      dst = filename
      continue
    print "Processing file", filename, "output directory", dst
    # extra filename -> output_base
    toklist = filename.split("/")
    #print "tklist ", toklist[-1]
    tmp0 = toklist[-1].split(".")
    filebase = tmp0[0]
    base = tmp0
    """
    tmp1 = filebase.split("nu_")
    for x in tmp1:
	base = x.split("_nu")
    #print "base ", base
    """
    reg_list, inst_list = Parse(filename, base[0])
    Gen(base[0], filebase, dst, reg_list, inst_list)

if __name__ == '__main__':
  main()
