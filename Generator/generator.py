#!/usr/bin/python

# generator.py
# Generator takes descriptions of structures describing device commands
# and automatically generates header files, documentation, and other
# products from the description.
#
# Generator can also pack structures with many small fields into
# single fields accessed via macros.  By explicitly providing accessor
# macros, we can avoid cases where compiled code may be inefficient.
#
# Robert Bowdidge August 8, 2016.
# Copyright Fungible Inc. 2016.

import fileinput
import getopt
import os
import re
import subprocess
import sys

import codegen
import htmlgen
import parser
import utils

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template

# Fake value for width of field, used when we can't define the value
# correctly on creation.
FAKE_WIDTH = 8675309

class Checker:
  # Walk through a document and identify any likely problems.
  def __init__(self):
    # Errors noted.
    self.errors = []
    self.current_document = None

  def AddError(self, node, msg):
    if self.current_document and self.current_document.filename:
      location = '%s:%d: ' % (self.current_document.filename, node.line_number)
    else:
      location = '%d: ' % node.line_number
    self.errors.append(location + msg)

  def VisitDocument(self, the_doc):
    for struct in the_doc.Structs():
      self.VisitStruct(struct)

  def VisitStruct(self, the_struct):
    last_type = None
    last_end_flit = None
    last_start_bit = 0
    last_end_bit = 0
    last_field_name = None

    for field in the_struct.fields:
      if field.IsNoOffset():
        if field != the_struct.fields[-1]:
          self.AddError(field, 'field "%s" is an array of zero size, but is not the last field.')

    fields_with_offsets = [f for f in the_struct.fields if not f.IsNoOffset()]

    if len(fields_with_offsets) == 0:
      return

    last_start_offset = fields_with_offsets[0].StartOffset() - 1
    last_end_offset = fields_with_offsets[0].StartOffset() - 1

    for field in fields_with_offsets:
      start_offset = field.StartOffset()
      end_offset = field.EndOffset()


      if field.BitWidth() == field.type.BitWidth():
        if start_offset % field.type.Alignment() != 0:
          self.AddError(field, 'Field "%s" cannot be placed in a location that '
                        'does not match its natural alignment.' % field.name)

      if not the_struct.is_union:
        if (last_start_offset >= end_offset and
             last_end_offset >= end_offset):
          self.AddError(field, 'field "%s" and "%s" not in bit order' % (
              last_field_name, field.name))
        elif last_end_offset >= start_offset:
          self.AddError(field, 'field "%s" overlaps field "%s"  '
                        '("%s" ends at %s, "%s" begins at %s)' % (
              last_field_name, field.name,
              last_field_name, utils.BitFlitString(last_end_offset),
              field.name, utils.BitFlitString(start_offset)))

        elif start_offset != last_end_offset + 1:
          self.AddError(field, 'unexpected space between field "%s" and "%s".  '
                        '("%s" ends at %s, "%s" begins at %s)'
                        % (last_field_name, field.name,
                           last_field_name,
                           utils.BitFlitString(last_end_offset),
                           field.name, utils.BitFlitString(start_offset)))

      last_start_offset = field.StartOffset()
      last_end_offset = field.EndOffset()
      last_field_name = field.name

  def VisitField(self, the_field):
    pass


def CommonPrefix(name_list):
  """Returns the longest prefix (followed by underbar) of all names.
  Returns None if no longest prefix.
  """
  if len(name_list) < 2:
    return None

  first_name = name_list[0]
  if not '_' in first_name:
    return None

  prefix = name_list[0].split('_')[0]
  for name in name_list[1:]:
    if not name.startswith(prefix + '_'):
      return None
  return prefix

def FirstNonReservedName(field_list):
  """Returns name of first field that is not a reserved field.
  Returns None if no such field exists.
  """
  first_name = None
  for field in field_list:
    if not field.is_reserved:
      return field.name
  return None

def LastNonReservedName(field_list):
  """Returns name of last field that is not a reserved field.
  Returns None if no such field exists.
  """
  last_name = None
  for field in field_list:
    if not field.is_reserved:
      last_name = field.name
  return last_name

def ChoosePackedFieldName(fields):
  """Chooses the name for a packed field base on the fields in that field."""
  not_reserved_names = [f.name for f in fields if not f.is_reserved]
  common_prefix = CommonPrefix(not_reserved_names)

  if common_prefix:
    return common_prefix + '_pack'

  first_name = FirstNonReservedName(fields)
  last_name = LastNonReservedName(fields)
  # No fields.
  if first_name is None and last_name is None:
    return "empty_pack"

  # One field.
  if first_name == last_name:
    return first_name + '_pack'

  return first_name + "_to_" + last_name


class Packer:
  """ Searches all structures for bitfields that can be combined.

  We generally don't trust compilers to do a good job on accessing
  bitfields, especially for registers.  By convention, we'd prefer to
  combine those accesses into explicit shifts and masks so we know
  what our code is doing.

  This pass runs through all structures, and looks for adjacent
  bitfields with identical types.  These bitfields are replaced with
  a single field declaration; macros are then added for accessing
  the contents of the field.
  """

  def __init__(self):
    self.current_document = None
    self.errors = []

  def AddError(self, node, msg):
    if self.current_document and self.current_document.filename:
      location = '%s:%d: ' % (self.current_document.filename, node.line_number)
    else:
      location = '%d: ' % node.line_number
    self.errors.append(location + msg)

  def VisitDocument(self, doc):
    # Pack all structures in the named documents.
    self.doc = doc
    for struct in doc.Structs():
      self.VisitStruct(struct)
    return self.errors

  def VisitStruct(self, the_struct):
    # Gather fields by flit, then create macros for each.
    # Should make sure that adjacent fields are same types.
    if not the_struct.is_union:
      self.PackStruct(the_struct)

  def ChoosePackGroups(self, the_fields):
    """Identify and group fields in a flit that deserve to be packed.
    Returns array of proposed packed variables, with each group being
    a tuple of (type, [fields to pack in variable) in that group.
    """
    # Contiguous fields to pack.  When we reach the end of a set of fields to be packed togther,
    # we move them to fields_to_pack.
    fields_to_pack = []

    # Current group of fields to be packed together.
    current_group = []

    # Common type for all in current group of fields to be packed together.
    current_type = None
    # total bits of space used by current_group
    bits_occupied = 0

    for field in the_fields:

      # End the previous group of packed fields if the current field
      # can be a field on its own, if the current field does not match the group's
      # field, or if the packed field is already full (or too full).
      # Code outside checks for packed fields too large for the type.
      if (field.type.BitWidth() == field.BitWidth() or
          current_type != field.type or
          bits_occupied >= field.type.BitWidth()):
        fields_to_pack.append((current_type, current_group))
        current_group = []
        current_type = None
        bits_occupied = 0

      current_group.append(field)
      if (len(current_group) == 1):
        current_type = field.type
      bits_occupied += field.BitWidth()

    fields_to_pack.append((current_type, current_group))

    # Return only the groups that had more than one field in them.
    return [pack_group for pack_group in fields_to_pack if len(pack_group[1]) > 1]

  def PackFlit(self, the_struct, flit_number, the_fields):
    """Replaces contiguous sets of bitfields with macros to access.
    the_struct: structure containing fields to be packed.
    flit_number: which flit of the structure is handled this time.
    the_fields: list of fields in this flit.
    """
    # All fields to pack. List of tuples of (type, [fields to pack])
    fields_to_pack = []

    fields_to_pack = self.ChoosePackGroups(the_fields)

    if len(fields_to_pack) == 0:
      # Nothing to pack.
      return
    for (type, fields) in fields_to_pack:
      packed_field_width = 0
      min_start_bit = min([f.StartBit() for f in fields])
      for f in fields:
        packed_field_width += f.BitWidth()

      if (packed_field_width > type.BitWidth()):
        self.AddError(the_struct,
                      'Width of packed bit-field containing %s (%d bits) exceeds width of its type (%d bits). '% (
            utils.ReadableList([f.name for f in fields]),
            packed_field_width,
            type.BitWidth()))

      new_field_name = ChoosePackedFieldName(fields)
      new_field = parser.Field(new_field_name, type, min_start_bit,
                               packed_field_width)
      new_field.line_number = fields[0].line_number

      non_reserved_fields = [f.name for f in fields if not f.is_reserved]
      bitfield_name_str = utils.ReadableList(non_reserved_fields)
      bitfield_layout_str = ''

      min_end_bit = min([f.EndBit() for f in fields])
      for f in fields:
        # TODO(bowdidge): Fix.
        bitfield_layout_str += '      %d:%d: %s\n' % (f.StartBit() - min_end_bit,
                                                      f.EndBit() - min_end_bit,
                                                      f.name)
        new_field.body_comment = "Combines bitfields %s.\n%s" % (bitfield_name_str,
                                                                bitfield_layout_str)

      # Replace first field to be removed with new field, and delete rest.
      for i, f in enumerate(the_struct.fields):
        if f == fields[0]:
          new_field.packed_fields.append(f)
          the_struct.fields[i] = new_field
          new_field.parent_struct = the_struct
          f.packed_field = new_field
          break
      for f in fields[1:]:
        new_field.packed_fields.append(f)
        f.packed_field = new_field
        the_struct.fields.remove(f)


  def PackStruct(self, the_struct):
    # Get rid of old struct fields, and use macros on flit-sized
    # fields to access.
    new_fields = []
    flit_field_map = the_struct.FlitFieldMap()

    for flit, fields_in_flit in flit_field_map.iteritems():
      self.PackFlit(the_struct, flit, fields_in_flit)


# Enums used to indicate the kind of object being processed.
# Used on the stack.
DocBuilderStateStruct = 1
DocBuilderTopLevel = 3
DocBuilderStateEnum = 4
DocBuilderStateFlagSet = 5


class DocBuilder:
  # Parses a generated header document and creates the internal data structure
  # describing the file.

  def __init__(self):
    # Create a DocBuilder.
    # current_document is the top level object.
    self.current_document = parser.Document()
    # stack is a list of (state, object) pairs showing all objects
    # currently being parsed.  New containers (enum, struct, union) are put in the
    # last object.
    self.stack = [(DocBuilderTopLevel, self.current_document)]
    # strings describing any errors encountered during parsing.
    self.errors = []
    # Comment being formed for next object.
    self.current_comment = ''
    # Current field that stretches across flits.
    self.flit_crossing_field = None
    # Number of extra bits still to be consumed by the flit_crossing_field
    self.bits_remaining = 0
    # Number of extra bits already cosumed.
    self.bits_consumed = 0
    # Current line being parsed.
    self.current_line = 0

    self.base_types = {}
    for name in parser.builtin_type_widths:
      self.base_types[name] = parser.BaseType(name, 
                                              parser.builtin_type_widths[name])

  def AddError(self, msg):
    if self.current_document.filename:
      location = '%s:%d: ' % (self.current_document.filename, self.current_line)
    else:
      location = '%d: ' % self.current_line
    self.errors.append(location + msg)

  def ParseStructStart(self, line):
    # Handle a STRUCT directive opening a new structure.
    # Returns created structure.
    (state, containing_object) = self.stack[-1]
    if state not in [DocBuilderTopLevel, DocBuilderStateStruct]:
      self.AddError('Struct starting in inappropriate context')

      return None

    # Struct syntax is STRUCT struct-identifier var-name comment
    match = re.match('STRUCT\s+(\w+)(\s+\w+|)(\s*.*)$', line)

    if not match:
      self.AddError('Invalid STRUCT line: "%s"' % line)
      return None

    identifier = match.group(1)
    variable_name = match.group(2)
    key_comment = match.group(3)
    variable_name = utils.RemoveWhitespace(variable_name)

    if not utils.IsValidCIdentifier(identifier):
      self.AddError(
        'struct name "%s" is not a valid identifier name.' % identifier)

    if variable_name and not utils.IsValidCIdentifier(variable_name):
      self.AddError(
        'variable "%s" is not a valid identifier name.' % variable_name)

    current_struct = parser.Struct(identifier, False)
    current_struct.line_number = self.current_line
    current_struct.key_comment = self.StripKeyComment(key_comment)

    if len(self.current_comment) > 0:
      current_struct.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((DocBuilderStateStruct, current_struct))

    self.current_document.AddStruct(current_struct)

    # Add the struct to the symbol table.  We don't know
    self.base_types[identifier] = parser.BaseType(identifier, FAKE_WIDTH,
                                                  current_struct)

    if state != DocBuilderTopLevel:
      new_field = parser.Field(variable_name, self.MakeType(identifier),
                               0, 0)
      new_field.line_number = self.current_line

      containing_object.AddField(new_field)
      current_struct.inline = True
      current_struct.parent_struct = containing_object

    # TODO(bowdidge): Instantiate field with struct if necessary.
    # Need to pass variable.

  def ParseEnumStart(self, line):
    # Handle an ENUM directive opening a new enum.
    state, containing_struct = self.stack[len(self.stack)-1]
    match = re.match('ENUM\s+(\w+)(.*)$', line)
    if match is None:
      self.AddError('Invalid enum start line: "%s"' % line)
      return

    name = match.group(1)
    key_comment = match.group(2)

    name = utils.RemoveWhitespace(name)

    if not utils.IsValidCIdentifier(name):
      self.AddError('"%s" is not a valid identifier name.' % name)

    current_enum = parser.Enum(name)
    current_enum.line_number = self.current_line
    current_enum.key_comment = self.StripKeyComment(key_comment)

    if len(self.current_comment) > 0:
      current_enum.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((DocBuilderStateEnum, current_enum))
    self.current_document.AddEnum(current_enum)

  def ParseFlagSetStart(self, line):
    # Handle an FLAGS directive opening a new type represeting bit flags.
    state, containing_struct = self.stack[len(self.stack)-1]
    match = re.match('FLAGS\s+(\w+)(.*)$', line)
    if match is None:
      self.AddError('Invalid flags start line: "%s"' % line)
      return

    name = match.group(1)
    key_comment = match.group(2)

    if not utils.IsValidCIdentifier(name):
      self.AddError('"%s" is not a valid identifier name.' % name)

    name = utils.RemoveWhitespace(name)
    current_flags = parser.FlagSet(name)
    current_flags.line_number = self.current_line
    current_flags.key_comment = self.StripKeyComment(key_comment)

    if len(self.current_comment) > 0:
      current_flags.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((DocBuilderStateFlagSet, current_flags))
    self.current_document.AddFlagSet(current_flags)

  def ParseEnumLine(self, line):
    # Parse the line describing a new enum variable.
    # This regexp matches:
    # Foo = 1 Arbitrary-following-comment
    match = re.match('(\w+)\s*=\s*(\w+)\s*(.*)$', line)
    if match is None:
      self.AddError('Invalid enum line: "%s"' % line)
      return None

    var = match.group(1)

    value_str = match.group(2)
    value = utils.ParseInt(value_str)
    if value is None:
      self.AddError('Invalid enum value for %s: "%s"' % (value_str, var))
      return None

    if not utils.IsValidCIdentifier(var):
        self.AddError('"%s" is not a valid identifier name.' % var)

    if value > 0x100000000:
        self.AddError(
          'Value for enum variable "%s" is %d, is larger than the 2^32 C allows.' % (
            var, value))

    # Parse a line describing an enum variable.
    # TODO(bowdidge): Remember whether value was hex or decimal for better printing.
    new_enum = parser.EnumVariable(var, value)
    new_enum.line_number = self.current_line

    if len(self.current_comment) > 0:
      new_enum.body_comment = self.current_comment
    self.current_comment = ''

    if match.group(3):
        new_enum.key_comment = self.StripKeyComment(match.group(3))
    return new_enum

  def ParseLine(self, line):
    """Parse a single line of a gen file that wasn't the start or end of container.

    Use the state on top of the stack to decide what to do.
    """
    (state, containing_decl) = self.stack[len(self.stack)-1]
    if line.startswith('//'):
      self.current_comment += self.StripKeyComment(line)
    elif state == DocBuilderTopLevel:
      return
    elif state == DocBuilderStateEnum or state == DocBuilderStateFlagSet:
      enum = self.ParseEnumLine(line)
      if enum is not None:
        containing_decl.AddVariable(enum)
    else:
      # Try parsing as continuation of previous field
      if (not self.ParseMultiFlitFieldLine(line, containing_decl) and
          not self.ParseFieldLine(line, containing_decl)):
        self.AddError('Invalid line: "%s"' % line)
        return

  def ParseEnd(self, line):
    # Handle an END directive.
    if len(self.stack) < 2:
      self.AddError('END without matching STRUCT, UNION, or ENUM')
      return None

    (_, current_object) = self.stack[-1]
    self.stack.pop()
    (state, containing_object) = self.stack[-1]

    if len(self.current_comment) > 0:
      current_object.tail_comment = self.current_comment

    if not isinstance(current_object, parser.Struct):
      return

    if self.flit_crossing_field:
      self.AddError('Field spec for "%s" too short: expected %d bits, got %d' %
                    (self.flit_crossing_field.name,
                     self.flit_crossing_field.type.BitWidth(),
                     self.flit_crossing_field.type.BitWidth() - self.bits_remaining))

    self.base_types[current_object.Name()].bit_width = current_object.BitWidth()

    self.current_comment = ''

    if state != DocBuilderTopLevel:
      # Sub-structures and sub-unions are numbered starting at 0.
      # Check the previous field to find where this struct should start.
      next_offset = 0
      if not containing_object.is_union:
        previous_fields = containing_object.fields[0:-1]
        if len(previous_fields) > 0:
          next_offset = previous_fields[-1].EndOffset() + 1

      new_field = containing_object.fields[-1]
      new_field.offset_start = next_offset
      new_field.bit_width = current_object.BitWidth()
      new_field.CreateSubfields()

  def ParseUnionStart(self, line):
    # Handle a UNION directive opening a new union.
    (state, containing_object) = self.stack[-1]
    union_args = line.split(' ')
    if len(union_args) != 3:
      self.AddError('Malformed union declaration: %s\n' % line)
      return
    (_, name, variable) = union_args
    identifier = utils.RemoveWhitespace(name)
    variable = utils.RemoveWhitespace(variable)

    if not utils.IsValidCIdentifier(name):
      self.AddError('"%s" is not a valid union identifier name.' % name)

    if not utils.IsValidCIdentifier(variable):
      self.AddError('"%s" is not a valid identifier name.' % variable)

    current_union = parser.Struct(name, True)
    current_union.line_number = self.current_line
    if len(self.current_comment) > 0:
      current_union.body_comment = self.current_comment
    self.current_comment = ''
    self.stack.append((DocBuilderStateStruct, current_union))
    self.current_document.AddStruct(current_union)

    self.base_types[identifier] = parser.BaseType(identifier, FAKE_WIDTH,
                                                  current_union)
    if state != DocBuilderTopLevel:
      # Inline union.  Define the field.
      new_field = parser.Field(variable, self.MakeType(identifier), 0, 0)
      new_field.line_number = self.current_line
      containing_object.fields.append(new_field)

      current_union.inline = True
      current_union.parent_struct = containing_object

  def StripKeyComment(self, the_str):
    """Removes C commenting from the comment at the end of a line.

    Returns None if a valid comment was not found.
    """
    the_str = the_str.lstrip(' \t\n')
    if the_str.startswith('//'):
      return the_str[2:].lstrip(' ').rstrip(' ')

    if len(the_str) == 0:
      return None

    if not the_str.startswith('/*'):
      self.AddError('Unexpected stuff where comment should be: "%s".' % the_str)
      return None

    # Match /* */ with anything in between and whitespace after.
    match = re.match('/\*\s*(.*)\*/\s*', the_str)
    if not match:
      self.AddError('Badly formatted comment "%s"' % the_str)
      return None

    return match.group(1).lstrip(' ').rstrip(' ')

  def ParseMultiFlitFieldLine(self, line, containing_struct):
    """Parse the current line as if it were a multi-flit line.

    Return false if it were not a multi-flit line
    """
    match = re.match('(\w+\s+(\w+:\w+|\w+))\s+\.\.\.\s*(.*)', line)
    if match is None:
      return False

    if self.flit_crossing_field is None:
      self.AddError('Multi-line flit continuation seen without pending field.')
      return True

    # Continuation.
    flit_bit_spec_str = match.group(1)
    key_comment = match.group(3)

    result = utils.ParseBitSpec(flit_bit_spec_str)

    if not result:
      self.AddError('Invalid bit pattern: "%s"' % flit_bit_spec_str)
      return True

    # Tests
    # Flag error if uses more bits than was available in previous declaration.
    # Flag error if larger than flit.
    # Flag if flit number wasn't increasing.
    # Checker will determine if there's overlap.

    result = utils.ParseBitSpec(flit_bit_spec_str)
    if not result:
      self.AddError('Invalid bit pattern: "%s"' % flit_bit_spec_str)
      return True
    (flit, start_bit, end_bit) = result

    size = start_bit - end_bit + 1

    if not self.flit_crossing_field.tail_comment:
      self.flit_crossing_field.tail_comment = key_comment
    else:
      self.flit_crossing_field.tail_comment += '\n' + key_comment

    self.flit_crossing_field.crosses_flit = True

    self.flit_crossing_field.ExtendSize(size)

    if self.bits_remaining < size:
      self.AddError('Continuation for multi-flit field "%s" too large: '
                    'expected %d bits, got %d.' % (
          self.flit_crossing_field.name,
          self.flit_crossing_field.type.BitWidth(),
          size + self.bits_consumed))
      self.flit_crossing_field = None
      return True

    self.bits_remaining -= size
    self.bits_consumed += size

    if self.bits_remaining == 0:
      self.flit_crossing_field = None

    return True


  def MakeType(self, base_name, array_size=None):
    """Creates an instance of the named type, or None if no such type exists."""
    if base_name not in self.base_types:
      return None
    base_type = self.base_types[base_name]
    if array_size is not None:
      return parser.Type(base_type, array_size)
    else:
      return parser.Type(base_type)


  def ParseFieldLine(self, line, containing_struct):
    """Returns true if the line could be parsed as a field description.

     Struct line is one of the following

    Defines field
    flit start_bit:end_bit type name /* comment */
    flit single_bit type name /* comment */

    Defines continuation of multi-flit field.
    flit start_bit:end_bit ...
    """

    match = re.match('(\w+\s+(\w+:\w+|\w+))\s+(\w+)\s+(\w+)(\[[0-9]+\]|)\s*(.*)', line)

    if match is None:
      # Assume it's a comment.
      return False

    is_array = False
    array_size = 1

    flit_bit_spec_str = match.group(1)
    type_name = match.group(3)
    name = match.group(4)
    if len(match.group(5)) != 0:
      is_array = True
      array_size = utils.ParseInt(match.group(5).lstrip('[').rstrip(']'))
      if array_size is None:
        print("Eek, thought %s was a number, but didn't parse!\n" % match.group(5))
    key_comment = match.group(6)

    if not utils.IsValidCIdentifier(name):
      self.AddError(
        'field name "%s" is not a valid identifier name.' % name)

    if key_comment == '':
      key_comment = None
    else:
      key_comment = self.StripKeyComment(key_comment)

    body_comment = None
    if len(self.current_comment) > 0:
      body_comment = self.current_comment
      self.current_comment = ''

    type = None
    if is_array:
      type = self.MakeType(type_name, array_size)
    else:
      type = self.MakeType(type_name)

    if type is None:
      self.AddError('Unknown type name "%s"' % type_name)
      return True

    if array_size == 0:
      if flit_bit_spec_str != '_ _:_':
        self.AddError('Bit pattern specified for zero-length array: "%s".' % flit_bit_spec_str)
        return True

      zero_array = parser.Field(name, type, -1, -1)
      zero_array.no_offset = True
      zero_array.key_comment = key_comment
      zero_array.body_comment = body_comment
      containing_struct.AddField(zero_array)
      return True

    result = utils.ParseBitSpec(flit_bit_spec_str)

    if not result:
      self.AddError('Invalid bit pattern: "%s"' % flit_bit_spec_str)
      return True

    (flit, start_bit, end_bit) = result

    if start_bit > 63:
      self.AddError('Field "%s" has start bit "%d" too large for 8 byte flit.' % (
          name, start_bit))
      return True

    if start_bit < end_bit:
      self.AddError('Start bit %d greater than end bit %d in field %s' %
                    (start_bit, end_bit, name))

    start_offset = flit * 64 + (utils.FLIT_SIZE - start_bit - 1)
    end_offset = flit * 64 + (utils.FLIT_SIZE - end_bit - 1)
    bit_size = end_offset - start_offset + 1
    new_field = parser.Field(name, type, start_offset, bit_size)
    new_field.line_number = self.current_line

    expected_width = type.BitWidth()
    actual_width = new_field.BitWidth()

    # Copy the sub-fields in.
    if type.IsRecord():
      new_field.CreateSubfields()

    if not type.IsScalar() and end_bit == 0 and actual_width < expected_width:
      # Field may stretch across flits.
      self.flit_crossing_field = new_field
      self.bits_remaining = expected_width - actual_width
      self.bits_consumed = actual_width

    new_field.key_comment = key_comment

    new_field.body_comment = body_comment

    type_width = new_field.type.BitWidth()
    var_width = new_field.BitWidth()
    if (var_width < type_width and not new_field.type.IsScalar()
        and end_bit != 0):
      # Using too few bits is only an error for arrays - scalar fields might always
      # be treated as bitfields.  Arrays that end on a flit could continue, so don't
      # flag an error in that case.
      self.AddError('Field smaller than type: '
                    'field "%s" is %d bits, type "%s" is %d.' % (
          new_field.name, new_field.BitWidth(), new_field.type.TypeName(),
          new_field.type.BitWidth()))
    elif var_width > type_width:
      warning = 'Field larger than type: field "%s" is %d bits, type "%s" is %d.' % (
        new_field.name, new_field.BitWidth(), new_field.type.TypeName(),
        new_field.type.BitWidth())
      self.AddError(warning)
    containing_struct.AddField(new_field)
    return True

  def ParsePlainLine(self, line):
    # TODO(bowdidge): Save test in order for printing as comments.
    return

  def Parse(self, input_filename, the_file):
    # Begin parsing a generated file provided as text.  Returns errors if any, or None.
    self.current_document.filename = input_filename
    self.current_line = 1
    for line in the_file:
      # Remove whitespace to allow for meaningful indenting.
      line = line.lstrip(' ')
      if line.startswith('STRUCT'):
        self.ParseStructStart(line)
      elif line.startswith('UNION'):
        self.ParseUnionStart(line)
      elif line.startswith('ENUM'):
        self.ParseEnumStart(line)
      elif line.startswith('FLAGS'):
        self.ParseFlagSetStart(line)
      elif line.startswith('END'):
        self.ParseEnd(line)
      else:
        self.ParseLine(line)
      self.current_line += 1
    if len(self.errors) > 0:
      return self.errors
    return None

def Usage():
  sys.stderr.write('generator.py: usage: [-p] [-g [code, html] [-o file]\n')
  sys.stderr.write('-c options: change codegen options.\n')
  sys.stderr.write('-g code: generate header file to stdout (default)\n')
  sys.stderr.write('-g html: generate HTML description of header\n')
  sys.stderr.write('-o filename_base: send output to named file\n')
  sys.stderr.write('                  for code generation, appends correct extension.\n')
  sys.stderr.write('Codegen options include:\n')
  sys.stderr.write('  pack: combine multiple bitfields into a single:\n')
  sys.stderr.write('        field, and create accessor macros.\n')
  sys.stderr.write('  json: generate routines for initializing a structure\n')
  sys.stderr.write('        from a JSON representation.')
  sys.stderr.write('Example: -c json,nopack enables json, and disables packing.\n')

def ReformatCode(source):
  """Rewrites the source to match Linux coding style.

  Tries several tools to see what's available.
  """
  # We prefer clang-format because it reformats source code much nicer,
  # and because it does a better job of removing blank lines.
  out = ReformatCodeWithClangFormat(source)
  if out:
    return out

  out = ReformatCodeWithIndent(source)
  if out:
    return out

  # If no indent tool is available, just provide the un-formatted code.
  return source


def ReformatCodeWithIndent(source):
  """Reformats provided source with GNU indent.

  Returns None if indent not found.
  """
  possible_indent_binaries = ['/usr/bin/indent']

  indent_path = None
  for bin in possible_indent_binaries:
    if os.path.isfile(bin):
      indent_path = bin
      break

  if not indent_path:
    return None

  args = [indent_path, '-sob', '-nfc1', '-nfcb', '-nbad', '-bap',
          '-nbc', '-br', '-brs', '-c33', '-cd33', '-ncdb', '-ce', '-ci4',
          '-cli0', '-d0', '-i8', '-ip0', '-l80', '-lp', '-npcs', '-npsl',
          # Don't format comments, get rid of extra blank lines.
          # Don't add whitespace in the middle of declarations.
          '-nsc', '-sob', '-di0']

  p = subprocess.Popen(args,
                       stdout=subprocess.PIPE,
                       stdin=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       bufsize=1)
  # indent requires line feed after last line.
  out = p.communicate(source + '\n')

  # If there was an indent fail
  if (p.returncode != 0):
    print "%s returned error %d, ignoring output" % (indent_path, p.returncode)
    return None

  return out[0]

def ReformatCodeWithClangFormat(source):
  """Reformats provided source with clang-format.

  Returns None if indent not found.
  """
  possible_indent_binaries = ['/usr/bin/clang-format',
                              '/usr/local/bin/clang-format']

  indent_path = None
  for bin in possible_indent_binaries:
    if os.path.isfile(bin):
      indent_path = bin
      break

  if not indent_path:
    return None

  args = [indent_path,
          '-style={BasedOnStyle: LLVM, IndentWidth: 8, UseTab: Always, '
          'BreakBeforeBraces: Linux, MaxEmptyLinesToKeep: 1, '
          'ColumnLimit: 80}']

  p = subprocess.Popen(args,
                       stdout=subprocess.PIPE,
                       stdin=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       bufsize=1)
  # Make sure there's a line feed after last line.
  out = p.communicate(source + '\n')
  # If there was an indent fail
  if (p.returncode != 0):
    print "%s returned error %d, ignoring output" % (indent_path, p.returncode)
    return None

  return out[0]

def GenerateFromTemplate(doc, template_filename, generator_file, output_base,
                         extra_vars):
  """Creates source file and header for parsed gen file from templates.
  doc: reference to parsed gen file.
  template_filename: the file containing the template to render.
  generator_file: name of the .gen file, used for identifying origins in code.
  output_base: prefix to use on output file
  extra_vars: array of additional variables to set in template.
  """
  this_dir = os.path.dirname(os.path.abspath(__file__))

  env = Environment(loader=FileSystemLoader(this_dir))
  env.lstrip_blocks = True
  env.trim_blocks = True

  # Filters - to do more complex transformations.
  # Filers for strings and names.
  env.filters['as_macro'] = utils.AsUppercaseMacro
  env.filters['as_html'] = utils.AsHTMLComment
  env.filters['as_line'] = utils.AsLine
  env.filters['as_lower'] = utils.AsLower
  env.filters['as_comment'] = utils.AsComment

  # Filters for numbers.
  env.filters['as_hex'] = lambda num: "0x%x" % num

  # Filters for declarations.
  env.filters['as_definition'] = lambda decl : decl.DefinitionString()
  env.filters['as_declaration'] = lambda decl : decl.DeclarationString()
  env.filters['as_cast'] = lambda type : type.CastString()

  if output_base:
    output_base = os.path.basename(output_base)
  else:
    output_base = 'foo_gen'

  jinja_docs = {
    'gen_file' : os.path.basename(generator_file),
    'output_base' : output_base,
    'original_filename' : generator_file,
    'enums': doc.Enums(),
    'flagsets': doc.Flagsets(),
    'structs' : [x for x in doc.Structs() if not x.is_union],
    'declarations': doc.Declarations(),
    'extra_vars': extra_vars
    }

  for var in extra_vars:
    jinja_docs[var] = True

  template = env.get_template(template_filename)
  return template.render(jinja_docs, env=env)

# TODO(bowdidge): Create options dictionary to replace all these arguments.
def GenerateFile(output_style, output_base, input_stream, input_filename,
                 options):
  """Generate header or HTML based on options.

  Return the generated source (if output_base was None) or None.
  """
  # Process a single .gen file and create the appropriate header/docs.
  doc_builder = DocBuilder()

  errors = doc_builder.Parse(input_filename, input_stream)

  if errors is not None:
    for error in errors:
      print(error)
    sys.exit(1)

  doc = doc_builder.current_document

  c = Checker()
  c.VisitDocument(doc)
  if len(c.errors) != 0:
    for checker_error in c.errors:
      sys.stderr.write(checker_error + '\n')

  if 'pack' in options:
    p = Packer()
    errors = p.VisitDocument(doc)
    if len(errors) > 0:
      for error in errors:
        sys.stderr.write(error + '\n')

  # Convert list of extra codegen features into variables named
  #  generate_{{codegen-style}} that will be in the template.
  extra_vars = ['generate_' + o for o in options]
  if output_style is OutputStyleHTML:
    html_generator = htmlgen.HTMLGenerator()
    codegen.CodeGenerator(options)
    source = html_generator.VisitDocument(doc)
    if output_base:
      fname = output_base + '.html'
      f = open(fname, 'w')
      f.write(source)
      f.close()
    else:
      return source
  elif output_style is OutputStyleHeader:
    header = GenerateFromTemplate(doc, 'header.tmpl', input_filename,
                                  output_base, extra_vars)
    source = GenerateFromTemplate(doc, 'source.tmpl', input_filename,
                                  output_base, extra_vars)

    if not header or not source:
      print("Not generating header and source -errors.")
      return None

    header = ReformatCode(header)
    source = ReformatCode(source)

    if output_base:
      f = open(output_base + '.h', 'w')
      f.write(header)
      f.close()
      f = open(output_base + '.c', 'w')
      f.write(source)
      f.close()
      return None

    return '/* Header file */\n' +  header + '/* Source file */\n' + source


OutputStyleHeader = 1
OutputStyleHTML = 2


def SetFromArgs(key, codegen_args, default_value):
  """Returns whether setting 'key' should be set based on provided args.
  key is a name for a codegen setting.
  codegen_args is an array of arguments provided by the user which can
  include either name (to set the value) or noname (to not set the value).
  default_value names the value for the key if it is not in codegen_args.
  """

  if key in codegen_args:
    return True
  if 'no' + key in codegen_args:
    return False
  return default_value

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'tc:g:o:',
                               ['help', 'output=', 'codegen='])
  except getopt.GetoptError as err:
    print str(err)
    Usage()
    sys.exit(2)

  output_style = OutputStyleHeader
  output_base = None
  codegen_args = []

  for o, a in opts:
    if o in ('-h', '--help'):
      Usage()
      sys.exit(2)
    elif o in ('-o', '--output'):
      output_base = a
    elif o in ('-c', '--codegen'):
      codegen_args = a.split(',')
    elif o == '-g':
      if a == 'code':
        output_style = OutputStyleHeader
      elif a == 'html':
        output_style = OutputStyleHTML
      else:
        sys.stderr.write('Unknown output style "%s"' % a)
        sys.exit(2)
    else:
      assert False, 'Unhandled option %s' % o

  codegen_pack = SetFromArgs('pack', codegen_args, False)
  codegen_json = SetFromArgs('json', codegen_args, False)
  codegen_swap = SetFromArgs('swap', codegen_args, False)

  codegen_options = []

  if codegen_pack:
    codegen_options.append('pack')
  if codegen_json:
    codegen_options.append('json')
  if codegen_swap:
    codegen_options.append('swap')

  if (codegen_swap and not codegen_pack):
    print('WARNING - swapping will not work correctly on '
          'unpacked bitfields.')

  if len(args) == 0:
      sys.stderr.write('No genfile named.\n')
      sys.exit(2)

  if len(args) > 1:
      print('Can only process one gen file at a time.')
      sys.exit(2)

  input_stream = open(args[0], 'r')
  out = GenerateFile(output_style, output_base, input_stream, args[0],
                     codegen_options)
  input_stream.close()
  if out:
    print out

if __name__ == '__main__':
  main()
