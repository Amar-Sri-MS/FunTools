#!/usr/bin/env python
from __future__ import print_function
import sys

from elftools.common.py3compat import maxint, bytes2str
from elftools.dwarf.descriptions import describe_form_class, describe_attr_value
from elftools.dwarf.die import DIE
from elftools.elf.elffile import ELFFile


def decode_function_pc(dwarfinfo, function_name):
    for compile_unit in dwarfinfo.iter_CUs():
      top_die = compile_unit.get_top_DIE()
      for d in top_die.iter_children():
        if d.tag == 'DW_TAG_subprogram' and 'DW_AT_name' in d.attributes and 'DW_AT_low_pc' in d.attributes:
          if d.attributes['DW_AT_name'].value == function_name:
            return [d.attributes['DW_AT_low_pc'].value]

    return []


def extract_function_ptr(filename, function_name):
  print('Processing file:', filename)
  with open(filename, 'rb') as f:
      elffile = ELFFile(f)

      if not elffile.has_dwarf_info():
        print('No DWARF info')
        return

      dwarfinfo = elffile.get_dwarf_info()
      addresses = decode_function_pc(dwarfinfo, function_name)

      if len(addresses) == 0:
        print('Function not found')
        return

      print(addresses)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: ' + sys.argv[0] + ' <binary> <function_name>')
        sys.exit(1)

    extract_function_ptr(sys.argv[1], sys.argv[2])