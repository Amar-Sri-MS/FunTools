#
# Utility code for generator.

import re

# Default size of a word.  Input is specified in flits and bit offsets.
FLIT_SIZE = 64

def AsGuardName(filename):
  """Convert a filename to an all-caps string for an include guard."""
  name = AsUppercaseMacro(filename)
  return '__' + re.sub('\.', '_', name).upper() + '__'

def AsUppercaseMacro(the_str):
  if not the_str:
    return ''

  # Convert a CamelCase name to all uppercase with underbars.
  s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', the_str)
  s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
  
  return s2.upper().replace('.', '_')

def RemoveWhitespace(the_str):
  # Removes any spaces or carriage returns from the provided string.
  if the_str == None or len(the_str) == 0:
    return ''
  return re.sub('\s+', '', the_str)

def AsComment(str):
  """Returns string inside a C comment, removing any trailing whitespace."""
  if not str:
    return ''
  str = str.rstrip(' \n\t')
  if len(str) == 0:
    return ''

  lines = str.split('\n')
  if len(lines) < 2:
    return '/* %s */' % str
  return '/*\n' + '\n'.join([' * ' + l for l in lines]) + '\n */'

def AsHTMLComment(str):
   """Returns human-readable string in form that maintains formatting
   when converted to HTML.
   """
   return re.sub('\n', '\n<br>\n', str)

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

def MaxBit(value):
  """Returns the highest position bit set in the number provided."""
  max_bits = 0
  while (value != 0):
    value = value >> 1
    max_bits += 1

  return max_bits

def BitPatternString(value, max_bits):
  """Returns a string showing the base-2 representation of the number provided.

  max_bits sets how many leading zeros should be printed.
  """
  out = ''
  for i in range(0, max_bits):
    bit = max_bits - i - 1
    if (value & (1 << bit)) != 0:
      out += '1'
    else:
      out += '0'
  return out

def IsValidCIdentifier(name):
  """Returns false if name would be an invalid C or C++ field name."""
  c_keywords = ['auto', 'break', 'case', 'char', 'const', 'continue',
                'default', 'do', 'double',' else', 'enum', 'extern',
                'float', 'for', 'goto', 'if', 'int', 'long', 'register',
                'return', 'short', 'signed', 'sizeof', 'static', 'struct',
                'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile',
                'while']

  cpp_keywords = ['alignas', 'alignof', 'and', 'and_eq', 'asm', 'atomic_cancel',
                  'atomic_commit', 'atomic_noexcept', 'bitand', 'bitor', 'bool',
                  'catch', 'char16_t', 'char32_t', 'class', 'compl', 'concept',
                  'constexpr', 'const_cast', 'co_await', 'co_return', 'co_yield',
                  'decltype', 'delete', 'dynamic_cast', 'explicit', 'export',
                  'false', 'friend', 'import', 'inline', 'module', 'mutable',
                  'namespace', 'new', 'noexcept', 'not', 'not_eq', 'nullptr',
                  'operator', 'or', 'or_eq', 'private', 'protected', 'public',
                  'reinterpret_cast', 'rquires', 'static_assert', 'static_cast',
                  'synchronized', 'template', 'this', 'thread_local', 'throw',
                  'true', 'try', 'typeid', 'typename', 'using', 'virtual',
                  'wchar_t', 'xor', 'xor_eq' ]

  if name in c_keywords:
    return False

  if name in cpp_keywords:
    return False
  
  match = re.match('[a-zA-Z_][a-zA-Z_0-9]*', name)
  if match:
    return True
  return False

def BitFlitString(offset):
  """Returns a human-readable string describing the offset as flit/bit."""
  return '%d:%d' % (offset / FLIT_SIZE, 63 - offset % FLIT_SIZE)

def AsLine(str):
  if not str:
    return ''
  str = str.rstrip(' \n\t')
  str = str.lstrip(' \n\t')
  str = str.replace('\n', ' ')
  return str

def AsLower(str):
  if not str:
    return ''
  return str.lower()

def Indent(str, offset):
  """ Indents the provided string by the given offset."""
  out = ''
  lines = str.split('\n')
  if len(lines[-1]) == 0:
    lines = lines[0:-1]
  for line in lines:
    spaces = ' ' * offset
    out += spaces + line + '\n'
  return out
