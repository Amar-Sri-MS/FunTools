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


