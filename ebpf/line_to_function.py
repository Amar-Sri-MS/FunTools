#!/usr/bin/env python3

import sys

from elftools.common.py3compat import maxint, bytes2str
from elftools.dwarf.descriptions import describe_form_class, describe_attr_value
from elftools.dwarf.die import DIE
from elftools.elf.elffile import ELFFile

def decode_type(variable, compile_unit, dwarfinfo):
  if 'DW_AT_type' not in variable.attributes:
    return {'name': '<no name>'}
  type_die = DIE(compile_unit, dwarfinfo.debug_info_sec.stream,
    compile_unit.cu_offset + variable.attributes['DW_AT_type'].value)
  if type_die.tag == 'DW_TAG_structure_type':
    kind = 'structure'
  elif type_die.tag == 'DW_TAG_pointer_type':
    kind = 'pointer'
  elif type_die.tag == 'DW_TAG_array_type':
    kind = 'array'
  elif type_die.tag == 'DW_TAG_base_type':
    kind = type_die.attributes['DW_AT_name'].value
  else:
    kind = 'unknown'
  if 'DW_AT_byte_size' in type_die.attributes:
    type_size = type_die.attributes['DW_AT_byte_size'].value
  else:
    type_size = -1

  if 'DW_AT_location' in variable.attributes:
    location = describe_attr_value(variable.attributes['DW_AT_location'], variable, compile_unit.cu_offset)
  else:
    location = 'unknown'

  return {'name': variable.attributes['DW_AT_name'].value, 'kind': kind, 'size': type_size, 'location': location}

def extract_locals(parameters, local_variables, child, compile_unit, dwarfinfo):
  if child.tag is None or 'DW_AT_name' not in child.attributes:
    return
  if child.tag == 'DW_TAG_formal_parameter':
    parameters.append(decode_type(child, compile_unit, dwarfinfo))
  if child.tag == 'DW_TAG_variable':
    local_variables.append(decode_type(child, compile_unit, dwarfinfo))

def in_pc_range(function, addresses):
  if function.tag is None or \
    ('DW_AT_low_pc' not in function.attributes) or \
    ('DW_AT_high_pc' not in function.attributes):
    return False
  low_pc = function.attributes['DW_AT_low_pc'].value
  high_pc_attr = function.attributes['DW_AT_high_pc']
  high_pc_attr_class = describe_form_class(high_pc_attr.form)
  if high_pc_attr_class == 'address':
    high_pc = high_pc_attr.value
  elif high_pc_attr_class == 'constant':
    high_pc = low_pc + high_pc_attr.value
  else:
    return False
  return any([low_pc <= x <= high_pc for x in addresses])

def extract_rec(parameters, local_variables, function, compile_unit, dwarfinfo, addresses):
  match = in_pc_range(function, addresses)
  extract_locals(parameters, local_variables, function, compile_unit, dwarfinfo)
  if function.has_children:
    for child in function.iter_children():
      if extract_rec(parameters, local_variables, child, compile_unit, dwarfinfo, addresses):
        match = True
  return match

def decode_funcname(dwarfinfo, compile_unit_name, addresses):
    global_variables = []
    parameters = []
    local_variables = []
    function_name = None
    for compile_unit in dwarfinfo.iter_CUs():
      top_die = compile_unit.get_top_DIE()
      if not top_die.get_full_path().endswith(compile_unit_name):
        continue
      for d in top_die.iter_children():
        if d.tag == 'DW_TAG_variable':
          global_variables.append(decode_type(d, compile_unit, dwarfinfo))

        if d.tag == 'DW_TAG_subprogram' and 'DW_AT_name' in d.attributes:
          parameters = []
          local_variables = []
          if extract_rec(parameters, local_variables, d, compile_unit, dwarfinfo, addresses):
            function_name = d.attributes['DW_AT_name'].value
            print(d)
            break

      break

    print("Addresses:")
    print(addresses)
    print("Parameters:")
    print(parameters)
    print("Locals:")
    print(local_variables)
    print("Globals:")
    print(global_variables)
    return function_name

def line_to_addresses(dwarfinfo, compile_unit, line_number):
  addresses = []
  for CU in dwarfinfo.iter_CUs():
    if not CU.get_top_DIE().get_full_path().endswith(compile_unit):
      continue

    lineprog = dwarfinfo.line_program_for_CU(CU)
    prevstate = None
    for entry in lineprog.get_entries():
      if entry.state is None:
        continue
      if entry.state.end_sequence:
        prevstate = None
        continue
      if prevstate and prevstate.line == line_number:
        addresses.append(prevstate.address)
      prevstate = entry.state
    return addresses
  return addresses


def extract_location_info(filename, compile_unit, line_number):
  print('Processing file:', filename)
  with open(filename, 'rb') as f:
      elffile = ELFFile(f)

      if not elffile.has_dwarf_info():
        print('No DWARF info')
        return

      dwarfinfo = elffile.get_dwarf_info()
      addresses = line_to_addresses(dwarfinfo, compile_unit, line_number)

      if len(addresses) == 0:
        print('Location not found')
        return

      funcname = decode_funcname(dwarfinfo, compile_unit, addresses)

      print('Function:', bytes2str(funcname))


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: ' + sys.argv[0] + ' <binary> <compile_unit> <line_number>')
        sys.exit(1)

    extract_location_info(sys.argv[1], sys.argv[2], int(sys.argv[3]))