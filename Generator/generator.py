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
# TODO(bowdidge): Should create C code to test that structure compiles
# and has correct size.
#
# Robert Bowdidge August 8, 2016.
# Copyright Fungible Inc. 2016.

import fileinput
import getopt
import re
import sys

import codegen
import utils

type_widths = {
  # width of type in bytes.
  'unsigned' : 32,
  'signed' : 32,

  'char': 8,
  'uint8_t' : 8,
  'uint16_t': 16,
  'int16_t': 16,
  'short': 16,
  'int' : 32,
  'uint32_t': 32,
  'int32_t': 32,
  'long': 32,
  'float' : 32,
  'double': 64,
  'uint64_t': 64,
  'int64_t' : 64
}

class Type:
  """Represents C type for a field."""

  def __init__(self, base_name, array_size=None):
    self.base_name = base_name
    # Number of elements in the array.
    self.array_size = 0
    # Size of the total object in bits.
    self.bit_width = 0
    # True if type represents an array type.
    self.is_array = False

    if array_size:
      self.is_array = True
      self.array_size = array_size
    else:
      self.is_array = False
      self.array_size = None

    self.alignment = type_widths.get(base_name)

    if self.alignment is None:
      print("Unknown base type name %s\n", base_name)
      return None

    if self.is_array:
      self.bit_width = self.alignment * array_size
    else:
      self.bit_width = self.alignment

  def IsArray(self):
    """Returns true if the type is an array type."""
    return self.is_array

  def BaseName(self):
    """Returns base type name without array and other modifiers."""
    return self.base_name

  def ArraySize(self):
    """Returns the size of an array.  Throws exception if not an array type."""
    if not self.is_array:
      raise ValueError('Not array')
    return self.array_size

  def TypeName(self):
    """Returns type name."""
    if self.is_array:
      return "%s[%d]" % (self.base_name, self.array_size)
    else:
      return self.base_name

  def DeclarationType(self):
    """Returns type name as function parameter type."""
    if self.is_array:
      return '%s[%d]' % (self.base_name, self.array_size)
    else:
      return self.base_name

  def Alignment(self):
    """Returns natural alignment for the type in bits."""
    return self.alignment

  def BitWidth(self):
    """Returns width of type in bits."""
    return self.bit_width

  def __cmp__(self, other_type):
    if other_type is None:
      return -1

    if self.base_name != other_type.base_name:
      if self.base_name < other_type.base_name:
        return -1
      else:
        return 1
    if self.is_array != other_type.is_array:
      return self.is_array.__cmp__(other_type.is_array)
    if self.is_array:
      return self.array_size.__cmp__(other_type.array_size)
    return 0

  def __str__(self):
    if self.is_array:
      return '<Type: %s[%d]>' % (self.base_name, self.array_size)
    else:
      return '<Type: %s>' % (self.base_name)


class Visitor:
  # Visitor abstract class for walking the specification tree.
  def VisitField(self, field):
    pass
  def VisitStruct(self, struct):
    pass
  def VisitUnion(self, union):
    pass
  def VisitEnum(self, enum):
    pass
  def VisitEnumVariable(self, enumVariable):
    pass
  def VisitComment(self, comment):
    pass
  def VisitDocument(self, document):
    pass


class Node:
  def __init__(self):
    # Primary, short comment for an item.  Appears on same line.
    # Contains either the comment, or None if never set.
    self.key_comment = None
    # Longer descriptive comment.  Always appears before the declaration.
    # Contains either the comment, or None if never set.
    self.body_comment = None
    # Tail comment, usually inside structures.
    # Contains either the comment, or None if never set.
    self.tail_comment = None
    # Short comment used by generator to hint at transformation.
    # Contains either the comment, or None if never set.
    self.generator_comment = None

    # All macros related to this Node in string form.
    self.macros = []

    # Location where Node appeared in source.
    self.line_number = 0


def BitFlitToString(bitflit):
  """Converts an absolute bit offset from top of struct to a top=64 string."""
  bit = 63 - (bitflit % 64)
  flit = bitflit / 64
  return "flit %d, bit %d" (flit, bit)


class Field(Node):
  # Representation of a field in a structure or union.

  def __init__(self, name, type, flit, start_bit, end_bit):
    Node.__init__(self)
    # name of the field declaration.
    self.name = name
    # String name of the C type, or a generic type for signed-ness.
    self.type = type
    # Integer representing the 8 byte "flit" that the field belongs to.
    self.start_flit = flit
    # Integer representing the 8 byte flit that the end bit belongs to.
    # Not all fields fit in a single flit.
    self.end_flit = flit
    # Highest bit holding the contents of the field.
    self.start_bit = start_bit
    # Lowest order bit holding the contents of the field.
    self.end_bit = end_bit
    self.crosses_flit = False
    # Fields that have been packed in this field.
    self.packed_fields = []
    # True if field was explicitly defined to be less than its natural size.
    self.is_bitfield = False

  def __str__(self):
    if self.start_flit == self.end_flit:
      return('<Field: name=%s, type=%s, flit=%d, bits=%d:%d>' %
             (self.name, self.type, self.start_flit,
              self.start_bit, self.end_bit))
    else:
      return('<Field: name=%s, type=%s, start: flit=%d, bit=%d, '
             'end: flit=%d, bit=%d>' % (self.name, self.type,
                                        self.start_flit, self.start_bit,
                                        self.end_flit, self.end_bit))

  def StartFlit(self):
    return self.start_flit

  def EndFlit(self):
    return self.end_flit

  def StartBitFlit(self):
    """Returns offset from top of first flit.

    Bitflits are an absolute, always increasing index for a particular bit,
    starting at 0.  The checker's tests for overlapping fields are done using
    bitflits so the logic doesn't have to think about flits or about the fact that
    we start bit ordering at 63 and go down.
    """
    return (63 - self.start_bit) + 64 * self.start_flit

  def EndBitFlit(self):
    """Returns offset from top of first flit."""
    return (63 - self.end_bit) + 64 * self.end_flit

  def BitWidth(self):
    # Returns the number of bits in the field.
    return (self.EndBitFlit() - self.StartBitFlit() + 1)

  def Mask(self):
    # Returns a hexadecimal number that can be used as a mask in the flit.
    return '0x%x' %  ((1 << self.BitWidth()) - 1)

  def SmallerThanType(self):
    return self.BitWidth() < self.type.BitWidth()

  def IsReserved(self):
    """True if the field is a placeholder that doesn't need to be initialized."""
    return self.name.startswith('reserved') or self.name.startswith('rsvd')


class EnumVariable(Node):
  # Representation of an enum variable in an enum declaration.

  def __init__(self, name, value):
     # Create an EnumVariable.
     Node.__init__(self)
     # name is a string.
     self.name = name
     # value is an string value for the variable.
     self.value = value

  def __str__(self):
     return('<EnumVariable: %s = %s>' % self.name, self.value)


class Enum(Node):
  # Representation of an enum declaration.

  def __init__(self, name):
    # Create an Enum declaration.
    # name is a string.
    # variables holds the EnumVariables associated with the enum.
    # Multiple enum variables may hold the same value.
    Node.__init__(self)
    self.name = name
    self.variables = []

  def __str__(self):
    return('<Enum %s:\n  %s\n>\n' % (self.name, self.values))


class Union(Node):
  # Representation of a union declaration.

  def __init__(self, name, variable):
    # Create a union declaration.
    Node.__init__(self)
    # name is a string representing the name or variable of the union.
    self.name = name
    # variable is a string representing the variable to use for the union when
    # accessing it within a structure.
    self.variable = variable
    # fields are the list of structure fields in the union.
    self.fields = []
    # structs are the list of nested structures in the union.
    # structures will be placed after any fields.
    self.structs = []

  def Bytes(self):
    """Returns the total number of bytes for the union object."""
    return max([s.Flits() * 8 for s in self.structs])

  def Flits(self):
    """Returns the total number of flits (words) in the union object."""
    return max([s.Flits() for s in self.structs])

  def __str__(self):
    return('<Union %s, variable %s:\n fields: %s\n structs: %s\n>\n' %
           (self.name, self.variable, self.fields, self.structs))


class Struct(Node):
  # Representation of a structure.

  def __init__(self, name, variable):
    # Create a struct declaration.
    Node.__init__(self)
    # name is a string representing the name of the struct..
    self.name = name
    # variable is a string representing the variable to use in a nested structure
    # or none if no variable is specified.
    self.variable = variable
    # fields is the list of fields in the struct.
    self.fields = []
    # structs is the nested structures in this struct.
    self.structs = []
    # union is the list of union fields in the struct.
    self.unions = []

    # Source code for function declarations related to this structure.
    self.declarations = []

    # Source code for function definitions related to this structure.
    self.definitions = []

  def AllFields(self):
    """Returns all fields of the struct as seen before packing."""
    fields = []

    for field in self.fields:
      if len(field.packed_fields) == 0:
        fields.append(field)
      else:
        fields += field.packed_fields
    return fields

  def __str__(self):
    return('<Struct %s, variable %s:\n fields: %s\n structs: %s\n unions: %s\n>\n' %
           (self.name, self.variable, self.fields, self.structs, self.unions))

  def Flits(self):
    return max([field.EndFlit() for field in self.fields])

  def Bytes(self):
    """Returns the number of bytes in the structure."""
    if len(self.fields) == 0:
      return 0
    return (max([field.EndFlit() for field in self.fields]) + 1) * 8


class Document(Node):
  # Representation of an entire generated header specification.
  def __init__(self):
    Node.__init__(self)
    # structs is all the structures defined in the document.
    self.structs = []
    # unions is all unions declared in the document.
    # this should be empty - all unions should be inside a struct.
    self.unions = []
    # All enums declared in the file.
    self.enums = []

    # Original filename containing the specifications.
    self.filename = None

  def __str__(self):
    return('<Document>')

  def AddMacro(self, macro_str):
    # Record a macro to output.
    self.macros.append(macro_str)


class HTMLGenerator(Visitor):

  def VisitDocument(self, doc):
    # Generates all the HTML to document the structures.
    css = ('.structTable {\n'
           '  border: solid 1px black;\n'
           '  border-collapse: collapse;\n'
           '}\n'
           '.structTable td {\n'
           '   font-family: "Courier"\n'
           '}\n'
           '.structTable .description {\n'
           '  font-family: "Times New Roman"\n'
           '}\n'
           '.structBits {\n'
           '  background: #eeeeee;\n'
           '}\n'
           '.structTable td {\n'
           '  padding: 10px;\n'
           '}\n'
           '.structTable th {\n'
           '  background: #dddddd;\n'
           '}\n')

    out = '<!-- Documentation created by generator.py.\n'
    out += '     Do not change this file; '
    out += 'change the gen file "%s" instead. -->\n' % doc.filename
    out += '<html>\n<head>\n'
    out += '<style>\n%s</style>\n' % css
    out += '</head>\n<body>\n'
    for enum in doc.enums:
      out += self.VisitEnum(enum)
    for struct in doc.structs:
      out += self.VisitStruct(struct)
    for macro in doc.macros:
      pass
    out += '</body></html>'
    return out

  def VisitEnumVariable(self, enum_variable):
    # Generates HTML Documentation for a specific enum variable.
    return '<li> <b>%s</b> = %s' % (enum_variable.name, enum_variable.value)

  def VisitEnum(self, enum):
    # Generates HTML documentation for a specific enum type.
    out = ''
    out += '<h3>enum %s</h3>\n' % enum.name
    if enum.key_comment:
      out += '<p>%s</p>\n' % enum.key_comment
    if enum.body_comment:
      out += '<p>%s</p>\n' % enum.body_comment
    out += '<b>Values</b><br>\n'
    out += '<ul>\n'
    for enum_variable in enum.variables:
      out += self.VisitEnumVariable(enum_variable)
    out += '</ul>\n'
    return out

  def VisitUnionInStruct(self, union):
    """Draws a union as rows in a containing structure."""
    out = '<tr>\n'

    flit_str = "0"
    if union.Flits() > 1:
      flit_str = "0 ... %d" % (union.Flits() -1)

    comment = ""
    if union.key_comment:
      comment = union.key_comment

    out += '  <td class="structBits"h>%s</td>\n' % flit_str
    out += '  <td class="structBits">%d-0</td>\n' % (union.Bytes() * 8 - 1)
    out += '  <td>union %s</td>\n' % union.name
    out += '  <td>%s</td>\n' % union.variable
    out += '  <td>%s</td>\n' % comment
    out += '</tr>\n'

    for s in union.structs:
      out += '<tr>\n'
      out += '  <td class="structBits">0..%d</td>\n' % (s.Flits() - 1)
      out += '  <td class="structBits">%d-0</td>\n' % (s.Bytes() * 8 - 1)
      out += '  <td></td>\n'
      out += '  <td>%s</td>\n' % s.name
      out += '  <td>%s</td>\n' % s.key_comment
      out += '</tr>\n'
    return out

  def VisitStruct(self, struct):
    # Generates HTML documentation for a specific structure.
    out = ''
    out += '<h3>struct %s:\n</h3>\n' % struct.name
    if struct.key_comment:
      out += '<p>%s</p>\n' % struct.key_comment
    out += '<p>%s</p>\n' % struct.body_comment
    out += '<table class="structTable">\n'
    out += '<tr>\n'
    out += '  <th class="structBits">Flit</th>\n'
    out += '  <th class="structBits">Bits</th>\n'
    out += '  <th>Type</th>'
    out += '  <th>Name</th><th>Description</th></tr>\n'
    for field in struct.fields:
      out += self.VisitField(field)
    if struct.tail_comment:
      out += '<tr>\n'
      out += '  <td class="description" colspan="5">\n'
      out += '  <center>%s</center>\n' % struct.tail_comment
      out += '  </td>\n'
      out += '</tr>\n'
    for union in struct.unions:
      out += self.VisitUnionInStruct(union)
    out += "</table>\n"

    for union in struct.unions:
      for s in union.structs:
        out += self.VisitStruct(s)

    return out

  def VisitField(self, field, note=''):
    """Generates HTML documentation for a specific field."""
    if len(field.packed_fields) != 0:
      out = ''
      for packed_field in field.packed_fields:
        out += self.VisitField(packed_field,
                               'In packed field %s.' % field.name)
      return out

    # Draw a solid line at start of each flit to visually separate flits.
    solid = ''
    if field.start_bit == 63:
      solid = 'border-top: solid 1px'
    elif field.crosses_flit:
      solid = 'border-bottom: solid 1px'
    out = ''
    out += '<tr style="%s">\n' % solid
    if field.crosses_flit:
      out += '  <td class="structBits" colspan=2>%d:%d-%d:%d</td>\n' % (
        field.start_flit, field.start_bit, field.end_flit, field.end_bit)
      out += '  <td>%s</td>\n  <td>%s</td>\n' % (field.type.DeclarationType(),
                                                 field.name)
    else:
      out += '  <td class="structBits">%d</td>\n' % field.start_flit
      out += '  <td class="structBits">%d-%d</td>\n' % (field.start_bit, field.end_bit)
      out += '  <td>%s</td>\n  <td>%s</td>\n' % (field.type.DeclarationType(),
                                                 field.name)

    out += '<td class="description">\n'
    if field.key_comment:
      out += field.key_comment + '<br>'
    if note:
      out += '<i>' + note + '</i><br>'
    if field.body_comment:
        out += '<p>%s</p>/' % (field.body_comment)
    out += '</td>\n'
    out += '</tr>\n'
    return out

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
    for struct in the_doc.structs:
      self.VisitStruct(struct)

  def VisitStruct(self, the_struct):
    last_type = None
    last_end_flit = None
    last_start_bit = 0
    last_end_bit = 0
    last_field_name = None


    if len(the_struct.fields) == 0:
      return

    last_start_bitflit = the_struct.fields[0].StartBitFlit() - 1
    last_end_bitflit = the_struct.fields[0].StartBitFlit() - 1

    # Iterate through the fields from 0 to make sure LSB is aligned
    # correctly.
    for field in the_struct.fields:
      if last_type is None:
        last_type = field.type
      elif last_type != field.type:
        # If the type of the variables changes, make sure the current offset would
        # allow the provided alignment.
        # TODO(bowdidge): Assumes type width = type alignment.
        if (field.StartBitFlit() % field.type.Alignment() != 0):
          self.AddError(field,
            'In structure %s, type won\'t allow alignment: "%s %s" at bit %d' %
            (the_struct.name, field.type, field.name, field.end_bit))

      start_bitflit = field.StartBitFlit()
      end_bitflit = field.EndBitFlit()

      if (last_start_bitflit >= end_bitflit and
           last_end_bitflit >= end_bitflit):
        self.AddError(field, 'field "%s" and "%s" not in bit order' % (
            last_field_name, field.name))
      elif last_end_bitflit >= start_bitflit:
        self.AddError(field, 'field "%s" overlaps field "%s"' % (
            last_field_name, field.name))
      elif start_bitflit != last_end_bitflit + 1:
        self.AddError(field, 'unexpected space between field "%s" and "%s"'
                      % (last_field_name, field.name))

      last_start_bitflit = field.StartBitFlit()
      last_end_bitflit = field.EndBitFlit()
      last_field_name = field.name

    for struct in the_struct.structs:
      # Check adjacent structures match up with bit patterns.
      self.VisitStruct(struct)

  def VisitUnion(self, the_union):
    for struct in the_union.structs:
      self.VisitStruct(struct)

  def VisitField(self, the_field):
    pass


def LastNonReservedName(field_list):
  last_name = None
  first_name = None
  for field in field_list:
    if not field.IsReserved():
      last_name = field.name
      if first_name is None:
        first_name = field.name
  if last_name is not None:
    return last_name
  if last_name is first_name:
    return 'z'

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
    for struct in doc.structs:
      self.VisitStruct(struct)
    return self.errors

  def VisitStruct(self, the_struct):
    # Gather fields by flit, then create macros for each.
    # Should make sure that adjacent fields are same types.
    for struct in the_struct.structs:
      self.VisitStruct(struct)
    for union in the_struct.unions:
      self.VisitUnion(union)
    self.PackStruct(the_struct)

  def VisitUnion(self, the_union):
    # Handle packing fields in union.
    # TODO(bowdidge): Union fields start the packing all over again, so if the
    # common bit is not a full word, then need to copy fields over.
    for struct in the_union.structs:
      self.VisitStruct(struct)


  def PackFlit(self, the_struct, flit_number, the_fields):
    """Replaces contiguous sets of bitfields with macros to access.
    the_struct: structure containing fields to be packed.
    flit_number: which flit of the structure is handled this time.
    the_fields: list of fields in this flit.
    """
    # All fields to pack. List of tuples of (type, [fields to pack])
    fields_to_pack = []
    # Contiguous fields to pack.  When we reach the end of a group
    # move to fields_to_pack.
    current_group = []
    current_type = None

    for field in the_fields:
      # Loop through the fields, grouping contiguous bitfields into a larger
      # single variable.
      if field.type.BitWidth() != field.BitWidth():
         if current_type == None or field.type == current_type:
           current_type = field.type
           current_group.append(field)
         else:
           if len(current_group) > 1:
             fields_to_pack.append((current_type, current_group))
           current_group = [field]
           current_type = field.type
      else:
        if len(current_group) > 1:
          fields_to_pack.append((current_type, current_group))
        current_group = []
        current_type = None

    if len(current_group) > 1:
      fields_to_pack.append((current_type, current_group))

    if len(fields_to_pack) == 0:
      # Nothing to pack.
      return

    for (type, fields) in fields_to_pack:
      max_start_bit = max([f.start_bit for f in fields])
      min_end_bit = min([f.end_bit for f in fields])

      packed_field_width = max_start_bit - min_end_bit + 1

      if (packed_field_width > type.BitWidth()):
        self.AddError(the_struct,
                      'Unable to pack fields %s. '
                      'Fields are %d bits, type is %d bits.' % (
            utils.ReadableList([f.name for f in fields]),
            packed_field_width,
            type.BitWidth()))

      new_field_name = fields[0].name + "_to_" + LastNonReservedName(fields)
      new_field = Field(new_field_name, type, flit_number,
                        max_start_bit, min_end_bit)
      new_field.line_number = fields[0].line_number

      non_reserved_fields = [f.name for f in fields if not f.IsReserved()]
      bitfield_name_str = utils.ReadableList(non_reserved_fields)
      bitfield_layout_str = ''
      for f in fields:
        bitfield_layout_str += '      %d:%d: %s\n' % (f.start_bit - min_end_bit,
                                                      f.end_bit - min_end_bit,
                                                      f.name)
        new_field.body_comment = "Combines bitfields %s.\n%s" % (bitfield_name_str,
                                                                bitfield_layout_str)

      # Replace first field to be removed with new field, and delete rest.
      for i, f in enumerate(the_struct.fields):
        if f == fields[0]:
          new_field.packed_fields.append(f)
          the_struct.fields[i] = new_field
          break
      for f in fields[1:]:
        new_field.packed_fields.append(f)
        the_struct.fields.remove(f)


  def PackStruct(self, the_struct):
    # Get rid of old struct fields, and use macros on flit-sized
    # fields to access.
    new_fields = []
    flit_field_map = self.FieldsToStartFlits(the_struct)

    for flit, fields_in_flit in flit_field_map.iteritems():
      self.PackFlit(the_struct, flit, fields_in_flit)

  def FieldsToStartFlits(self, struct):
    # Return a map of (flit, fields) for all fields in the structure.
    flit_field_map = {}
    for field in struct.fields:
      item = flit_field_map.get(field.StartFlit(), [])
      item.append(field)
      flit_field_map[field.StartFlit()] = item
    return flit_field_map

# Enums used to indicate the kind of object being processed.
# Used on the stack.
DocBuilderStateStruct = 1
DocBuilderStateUnion = 2
DocBuilderTopLevel = 3
DocBuilderStateEnum = 4


class DocBuilder:
  # Parses a generated header document and creates the internal data structure
  # describing the file.

  def __init__(self):
    # Create a DocBuilder.
    # current_document is the top level object.
    self.current_document = Document()
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

  def AddError(self, msg):
    if self.current_document.filename:
      location = '%s:%d: ' % (self.current_document.filename, self.current_line)
    else:
      location = '%d: ' % self.current_line
    self.errors.append(location + msg)

  def ParseStructStart(self, line):
    # Handle a STRUCT directive opening a new structure.
    # Returns created structure.
    (state, current_object) = self.stack[len(self.stack)-1]
    terms = line.split(' ')

    if len(terms) == 3:
      name = terms[1]
      variable = terms[2]
    elif len(terms) == 2:
      name = terms[1]
      variable = None
    else:
      self.AddError('couldn\'t parse "%s"' % line)
      current_object = None

    name = utils.RemoveWhitespace(name)
    variable = utils.RemoveWhitespace(variable)

    current_struct = Struct(name, variable)
    current_struct.line_number = self.current_line

    if len(self.current_comment) > 0:
      current_struct.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((DocBuilderStateStruct, current_struct))
    current_object.structs.append(current_struct)

  def ParseEnumStart(self, line):
    # Handle an ENUM directive opening a new enum.
    state, current_object = self.stack[len(self.stack)-1]
    _, name = line.split(' ')
    name = utils.RemoveWhitespace(name)
    current_enum = Enum(name)
    current_enum.line_number = self.current_line

    if len(self.current_comment) > 0:
      current_enum.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((DocBuilderStateEnum, current_enum))
    self.current_document.enums.append(current_enum)

  def ParseEnumLine(self, line):
    # Parse the line describing a new enum variable.
    # This regexp matches:
    # Foo = 1 Abitrary following comment
    match = re.match('(\w+)\s*=\s*(\w+)\s*(.*)', line)
    if match is None:
      self.AddError('Invalid enum line: "%s"' % line)
      return None

    var = match.group(1)
    # TODO(bowdidge): Test valid C identifier.
    value_str = match.group(2)
    value = utils.ParseInt(value_str)
    if value is None:
      self.AddError('Invalid enum value for %s: "%s"' % (value_str, var))
      return None
    # Parse a line describing an enum variable.
    # TODO(bowdidge): Remember whether value was hex or decimal for better printing.
    new_enum = EnumVariable(var, value)
    new_enum.line_number = self.current_line

    if len(self.current_comment) > 0:
      new_enum.body_comment = self.current_comment
    self.current_comment = ''

    if match.group(3):
        new_enum.key_comment = utils.StripComment(match.group(3))
    return new_enum

  def ParseLine(self, line):
    """Parse a single line of a gen file that wasn't the start or end of container.

    Use the state on top of the stack to decide what to do.
    """
    (state, current_object) = self.stack[len(self.stack)-1]
    if line.startswith('//'):
      self.current_comment += utils.StripComment(line)
    elif state == DocBuilderTopLevel:
      return
    elif state == DocBuilderStateEnum:
      enum = self.ParseEnumLine(line)
      if enum is not None:
        current_object.variables.append(enum)
    else:
      field = self.ParseFieldLine(line)
      if field is not None:
        current_object.fields.append(field)

  def ParseEnd(self, line):
    # Handle an END directive.
    (state, current_object) = self.stack[len(self.stack)-1]

    if self.flit_crossing_field:
      self.AddError('Field spec for "%s" too short: expected %d bits, got %d' %
                    (self.flit_crossing_field.name,
                     self.flit_crossing_field.type.BitWidth(),
                     self.flit_crossing_field.type.BitWidth() - self.bits_remaining))

    if len(self.current_comment) > 0:
      current_object.tail_comment = self.current_comment
    self.current_comment = ''
    self.stack.pop()

  def ParseUnionStart(self, line):
    # Handle a UNION directive opening a new union.
    (state, current_object) = self.stack[len(self.stack)-1]
    union_args = line.split(' ')
    if len(union_args) != 3:
      self.AddError('Malformed union declaration: %s\n' % line)
      return
    (_, name, variable) = union_args
    name = utils.RemoveWhitespace(name)
    variable = utils.RemoveWhitespace(variable)
    current_union = Union(name, variable)
    current_union.line_number = self.current_line
    if len(self.current_comment) > 0:
      current_union.body_comment = self.current_comment
    self.current_comment = ''
    self.stack.append((DocBuilderStateUnion, current_union))
    current_object.unions.append(current_union)

  def ParseMultiFlitFieldLine(self, line):
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
    self.flit_crossing_field.end_flit = flit
    self.flit_crossing_field.end_bit = end_bit

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




  def ParseFieldLine(self, line):
    """Parse a single line describing a field.

     Struct line is one of the following

    Defines field
    flit start_bit:end_bit type name /* comment */
    flit single_bit type name /* comment */

    Defines continuation of multi-flit field.
    flit start_bit:end_bit ...
    """

    # Try parsing as continuation of previous field.
    if self.ParseMultiFlitFieldLine(line):
      return

    match = re.match('(\w+\s+(\w+:\w+|\w+))\s+(\w+)\s+(\w+)(\[[0-9]+\]|)\s*(.*)', line)

    if match is None:
        # Flag error, or treat as comment.
        self.AddError('Invalid field line: "%s"' % line)
        return None

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

    result = utils.ParseBitSpec(flit_bit_spec_str)

    if not result:
      self.AddError('Invalid bit pattern: "%s"' % flit_bit_spec_str)
      return None

    (flit, start_bit, end_bit) = result

    if start_bit > 63:
      self.AddError('Field "%s" has start bit "%d" too large for 8 byte flit.' % (
          name, start_bit))
      return None

    type = None
    if is_array:
      type = Type(type_name, array_size)
    else:
      type = Type(type_name)

    if start_bit < end_bit:
      self.AddError('Start bit %d greater than end bit %d in field %s' %
                    (start_bit, end_bit, name))

    new_field = Field(name, type, flit, start_bit, end_bit)
    new_field.line_number = self.current_line

    expected_width = type.BitWidth()
    actual_width = new_field.BitWidth()


    if is_array and end_bit == 0 and actual_width < expected_width:
      # Field may stretch across flits.
      self.flit_crossing_field = new_field
      self.bits_remaining = expected_width - actual_width
      self.bits_consumed = actual_width

    if key_comment == '':
      key_comment = None
    else:
      key_comment = utils.StripComment(key_comment)
    new_field.key_comment = key_comment

    if len(self.current_comment) > 0:
      new_field.body_comment = self.current_comment
    self.current_comment = ''

    type_width = new_field.type.BitWidth()
    var_width = new_field.BitWidth()
    if var_width < type_width and new_field.type.IsArray() and new_field.end_bit != 0:
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
    return new_field

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
  sys.stderr.write('-p: pack fields into 8 byte flits, and create accessor macros\n')
  sys.stderr.write('-g code: generate header file to stdout (default)\n')
  sys.stderr.write('-g html: generate HTML description of header\n')
  sys.stderr.write('-o filename_base: send output to named file\n')
  sys.stderr.write('                  for code generation, appends correct extension.\n')

def GenerateFile(should_pack, output_style, output_base,
                 input_stream, input_filename):
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

  if should_pack:
    p = Packer()
    errors = p.VisitDocument(doc)
    if len(errors) > 0:
      for error in errors:
        sys.stderr.write(warning + '\n')

  helper = codegen.HelperGenerator()
  helper.VisitDocument(doc)

  if output_style is OutputStyleHTML:
    html_generator = HTMLGenerator()
    code = html_generator.VisitDocument(doc)
    if output_base:
      f = open(output_base + '.html', 'w')
      f.write(code)
      f.close()
    else:
      return code
  elif output_style is OutputStyleHeader:
    code_generator = codegen.CodeGenerator(output_base)
    code_generator.output_file = output_base
    (header, source) = code_generator.VisitDocument(doc)

    if output_base:
      f = open(output_base + '.h', 'w')
      f.write(header)
      f.close()
      f = open(output_base + '.c', 'w')
      f.write(source)
      f.close()
    else:
      return '/* Header file */\n' +  header + '/* Source file */\n' + source
    return None

OutputStyleHeader = 1
OutputStyleHTML = 2

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'tpg:o:', ['help', 'output='])
  except getopt.GetoptError as err:
    print str(err)
    Usage()
    sys.exit(2)

  should_pack = False
  output_style = OutputStyleHeader
  output_base = None

  for o, a in opts:
    if o == '-p':
      should_pack = True
    elif o in ('-h', '--help'):
      Usage()
      sys.exit(2)
    elif o in ('-o', '--output'):
      output_base = a
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

  if len(args) == 0:
      sys.stderr.write('No genfile named.\n')
      sys.exit(2)

  if len(args) > 1:
      print('Can only process one gen file at a time.')
      sys.exit(2)

  input_stream = open(args[0], 'r')
  out = GenerateFile(should_pack, output_style, output_base,
                     input_stream, args[0])
  input_stream.close()
  if out:
    print out

if __name__ == '__main__':
  main()
