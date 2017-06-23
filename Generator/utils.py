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


