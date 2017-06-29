#!/usr/bin/python
#
# Utility code for generator.

import re

def AsGuardName(filename):
  """Convert a filename to an all-caps string for an include guard."""
  name = AsUppercaseMacro(filename)
  return '__' + re.sub('\.', '_', name).upper() + '__'


def AsUppercaseMacro(the_str):
  # Convert a CamelCase name to all uppercase with underbars.
  s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', the_str)
  s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
  return s2.upper()

def RemoveWhitespace(the_str):
  # Removes any spaces or carriage returns from the provided string.
  if the_str == None or len(the_str) == 0:
    return ''
  return re.sub('\s+', '', the_str)

def StripComment(the_str):
  the_str = the_str.lstrip(' ')
  # Removes any C commenting from the comment so it can be reformatted as needed.
  if the_str.startswith('//'):
    return the_str[2:].lstrip(' ').rstrip(' ')
  if the_str.startswith('/*'):
    # Match /* */ with anything in between and whitespace after.
    match = re.match('/\*\s*(.*)\*/\s*', the_str)
    if not match:
      print('Badly formatted comment "%s"' % the_str)
      return the_str
    return match.group(1).lstrip(' ').rstrip(' ')
    
def AsComment(str):
  """Returns string inside a C comment, removing any trailing whitespace."""
  str = str.rstrip(' \n\t')
  if len(str) == 0:
    return ''

  lines = str.split('\n')
  if len(lines) < 2:
    return '/* %s */' % str
  return '/*\n' + '\n'.join([' * ' + l for l in lines]) + '\n */'

def ReadableList(l):
  """Generates a human-readable list of string items."""
  if l is None or len(l) == 0:
    return ""
  if len(l) == 1:
    return l[0]
  if len(l) == 2:
    return l[0] + " and " + l[1]

  return ", ".join(l[0:-1]) + ", and " + l[-1]

def ParseInt(the_str):
  # Returns int value of string, or None if not a number.
  base = 10
  if the_str.startswith('0b'):
    base = 2
  if the_str.startswith('0x'):
    base = 16
  try:
    return int(the_str, base)
  except ValueError:
    return None

def ParseBitSpec(the_str):
  """Returns the (flit number, start bit, end bit) by parsing start of field.

  Returns None if invalid.
  """
  if ':' in the_str:
    bits_match = re.match('(\w+)\s+(\w+):(\w+)$', the_str)
    if bits_match is None:
      return None
    flit_str = bits_match.group(1)
    start_bit_str = bits_match.group(2)
    end_bit_str = bits_match.group(3)
  else:
    # Assume single bit.
    bits_match = re.match('(\w+)\s+(\w+)$', the_str)
    if bits_match is None:
      return None

    flit_str = bits_match.group(1)
    start_bit_str = bits_match.group(2)
    end_bit_str = start_bit_str

  flit_number = ParseInt(flit_str)

  if flit_number is None:
    return None
  if flit_number < 0:
    return None
  
  start_bit = ParseInt(start_bit_str)

  if start_bit is None:
    return None
  if start_bit < 0:
    return None

  end_bit = ParseInt(end_bit_str)
  if end_bit is None:
    return None
  if end_bit < 0:
    return None

  return (flit_number, start_bit, end_bit)
