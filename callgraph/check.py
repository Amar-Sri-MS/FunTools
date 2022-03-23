#!/usr/bin/env python3

import sys
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from elftools.elf.relocation import RelocationSection
from elftools.dwarf.descriptions import describe_form_class, describe_attr_value
from elftools.dwarf.die import DIE
import json


def visit_all(d, func):
  func(d)
  if not d.has_children:
    return
  for d1 in d.iter_children():
    visit_all(d1, func)


def einc(d, key):
  if key in d:
    d[key] += 1
  else:
    d[key] = 1


def has_attrs(d, l):
  return all([attr in d.attributes for attr in l])


def get_origin_name(d, compile_unit, dwarfinfo):
  if has_attrs(d, ['DW_AT_name']):
    return d.attributes['DW_AT_name'].value
  if has_attrs(d, ['DW_AT_abstract_origin']):
    return get_origin_name(DIE(compile_unit, dwarfinfo.debug_info_sec.stream,
        compile_unit.cu_offset + d.attributes['DW_AT_abstract_origin'].value), compile_unit, dwarfinfo)


def add_calls(f, d, compile_unit, dwarfinfo):
  if d.tag in ['DW_TAG_GNU_call_site', 'DW_TAG_inlined_subroutine']:
    f['calls'].append(get_origin_name(d, compile_unit, dwarfinfo))


def get_path(name, shortest):
  if name not in shortest:
    return [name]
  return [name] + get_path(shortest[name], shortest)


def print_error(wu_name, from_func, shortest):
  path = get_path(from_func, shortest)
  print('Error: ', wu_name, ' is calling ', ' -> '.join(path))


def get_functions_info(dwarfinfo):
  functions = {}

  for compile_unit in dwarfinfo.iter_CUs():
    top_die = compile_unit.get_top_DIE()
    for d in top_die.iter_children():
      if d.tag == 'DW_TAG_subprogram' and has_attrs(d, ['DW_AT_name', 'DW_AT_low_pc']):
        name = d.attributes['DW_AT_name'].value
        low_pc = d.attributes['DW_AT_low_pc'].value
        functions[name] = {'low_pc': low_pc, 'calls': []}
        visit_all(d, lambda x: add_calls(functions[name], x, compile_unit, dwarfinfo))

  return functions


def get_callers(functions):
  callers = {}
  for n, f in list(functions.items()):
    for c in f['calls']:
      if c not in callers:
        callers[c] = set()
      callers[c].add(n)
  return callers


def get_wu_information(wu_table_file):
  with open(wu_table_file, 'r') as f:
    wu_table = json.load(f)

  thread_prefix = '__thread__'
  threaded_wus = set()
  regular_wus = set()
  for wu in wu_table['wu_table']:
    if wu['name'].startswith(thread_prefix):
      threaded_wus.add(wu['name'][len(thread_prefix):])
    else:
      regular_wus.add(wu['name'])

  return threaded_wus, regular_wus


def check_if_regular_call_threaded(functions, callers, regular_wus):
  found = False
  shortest = {}
  queue = set()
  queue.add('assert_is_threaded')

  while len(queue) > 0:
    next_queue = set()
    for n in queue:
      if n not in callers:
        continue

      for c in callers[n]:
        if c in shortest:
          continue
        if c in regular_wus:
          found = True
          print_error(c, n, shortest)
          continue
        shortest[c] = n
        next_queue.add(c)
    queue = next_queue

  return found


def check_calls(elf_file, wu_table_file):
  _, regular_wus = get_wu_information(wu_table_file)

  with open(elf_file, 'rb') as f:
    elffile = ELFFile(f)

    if not elffile.has_dwarf_info():
      print('No DWARF info')
      return None

    dwarfinfo = elffile.get_dwarf_info()
    functions = get_functions_info(dwarfinfo)
    callers = get_callers(functions)

    return check_if_regular_call_threaded(functions, callers, regular_wus)


if __name__ == '__main__':
  if len(sys.argv) < 3:
    print('Usage: ' + sys.argv[0] + ' <ELF> <WU_TABLE.json>')
    sys.exit(1)

  res = check_calls(sys.argv[1], sys.argv[2])
  sys.exit(0 if res == False else 1)

# No code below, useful information
# Tags in FunOS code
# {'DW_TAG_pointer_type': 54111,
# 'DW_TAG_dwarf_procedure': 41,
# 'DW_TAG_base_type': 14046,
# 'DW_TAG_enumerator': 84799,
# 'DW_TAG_formal_parameter': 162379,
# 'DW_TAG_structure_type': 63981,
# 'DW_TAG_subroutine_type': 10877,
# 'DW_TAG_GNU_call_site': 146281,
# 'DW_TAG_GNU_call_site_parameter': 250609,
# 'DW_TAG_lexical_block': 66917,
# 'DW_TAG_member': 399586,
# 'DW_TAG_subprogram': 60605,
# 'DW_TAG_enumeration_type': 11024,
# 'DW_TAG_subrange_type': 40103,
# 'DW_TAG_typedef': 33171,
# 'DW_TAG_union_type': 7520,
# 'DW_TAG_volatile_type': 1026,
# 'DW_TAG_inlined_subroutine': 44114,
# 'DW_TAG_array_type': 38857,
# 'DW_TAG_variable': 335498,
# 'DW_TAG_const_type': 20451,
# 'DW_TAG_unspecified_parameters': 300,
# 'DW_TAG_label': 1670,
# 'DW_TAG_restrict_type': 67}
