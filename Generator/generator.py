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
  def visitField(self, field):
    pass
  def visitStruct(self, struct):
    pass
  def visitUnion(self, union):
    pass
  def visitEnum(self, enum):
    pass
  def visitEnumVariable(self, enumVariable):
    pass
  def visitComment(self, comment):
    pass
  def visitDocument(self, document):
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


class Field(Node):
  # Representation of a field in a structure or union.

  def __init__(self, name, type, flit, start_bit, end_bit):
    Node.__init__(self)
    # name of the field declaration.
    self.name = name
    # String name of the C type, or a generic type for signed-ness.
    self.type = type
    # Integer representing the 8 byte "flit" that the field belongs to.
    self.flit = flit
    # Highest bit holding the contents of the field.
    self.start_bit = start_bit
    # Lowest order bit holding the contents of the field.
    self.end_bit = end_bit
    # Fields that have been packed in this field.
    self.packed_fields = []

  def __str__(self):
    return('<Field: name=%s, type=%s, flit=%d, bits=%d:%d>' %
           (self.name, self.type, self.flit, self.start_bit, self.end_bit))
  
  def Size(self): 
    # Returns the number of bits in the field.
    return (self.start_bit - self.end_bit + 1)

  def Mask(self):
    # Returns a hexadecimal number that can be used as a mask in the flit.
    return '0x%x' %  ((1 << self.Size()) - 1)

  def SmallerThanType(self):
    return self.Size() < self.type.BitWidth()

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

  def bytes(self):
    """Returns the total number of bytes for the union object."""
    return max([s.bytes() for s in self.structs])

  def flits(self):
    """Returns the total number of flits (words) in the union object."""
    return max([s.flits() for s in self.structs])

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

  def flits(self):
    return max([field.flit for field in self.fields])

  def bytes(self):
    """Returns the number of bytes in the structure."""
    if len(self.fields) == 0:
      return 0
    return (max([field.flit for field in self.fields]) + 1) * 8


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
    # All macros declared in the file in string form.
    self.macros = []
    
    # Original filename containing the specifications.
    self.filename = None

  def __str__(self):
    return('<Document>')

  def addMacro(self, macroStr):
    # Record a macro to output.
    self.macros.append(macroStr)


class HTMLGenerator(Visitor):

  def visitDocument(self, doc):
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
      out += self.visitEnum(enum)
    for struct in doc.structs:
      out += self.visitStruct(struct)
    for macro in doc.macros:
      pass
    out += '</body></html>'
    return out

  def visitEnumVariable(self, enumVariable):
    # Generates HTML Documentation for a specific enum variable.
    return '<li> <b>%s</b> = %s' % (enumVariable.name, enumVariable.value)

  def visitEnum(self, enum):
    # Generates HTML documentation for a specific enum type.
    out = ''
    out += '<h3>enum %s</h3>\n' % enum.name
    if enum.key_comment:
      out += '<p>%s</p>\n' % enum.key_comment
    if enum.body_comment:
      out += '<p>%s</p>\n' % enum.body_comment
    out += '<b>Values</b><br>\n'
    out += '<ul>\n'
    for enumVariable in enum.variables:
      out += self.visitEnumVariable(enumVariable)
    out += '</ul>\n'
    return out

  def visitUnionInStruct(self, union):
    """Draws a union as rows in a containing structure."""
    out = '<tr>\n'

    flit_str = "0"
    if union.flits() > 1:
      flit_str = "0 ... %d" % (union.flits() -1)

    comment = ""
    if union.key_comment:
      comment = union.key_comment

    out += '  <td class="structBits"h>%s</td>\n' % flit_str
    out += '  <td class="structBits">%d-0</td>\n' % (union.bytes() * 8 - 1)
    out += '  <td>union %s</td>\n' % union.name
    out += '  <td>%s</td>\n' % union.variable
    out += '  <td>%s</td>\n' % comment
    out += '</tr>\n'

    for s in union.structs:
      out += '<tr>\n'
      out += '  <td class="structBits">0..%d</td>\n' % (s.flits() - 1)
      out += '  <td class="structBits">%d-0</td>\n' % (s.bytes() * 8 - 1)
      out += '  <td></td>\n'
      out += '  <td>%s</td>\n' % s.name
      out += '  <td>%s</td>\n' % s.key_comment
      out += '</tr>\n'
    return out

  def visitStruct(self, struct):
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
      out += self.visitField(field)
    if struct.tail_comment:
      out += '<tr>\n'
      out += '  <td class="description" colspan="5">\n'
      out += '  <center>%s</center>\n' % struct.tail_comment
      out += '  </td>\n'
      out += '</tr>\n'
    for union in struct.unions:
      out += self.visitUnionInStruct(union)
    out += "</table>\n"

    for union in struct.unions:
      for s in union.structs:
        out += self.visitStruct(s)

    return out

  def visitField(self, field, note=''):
    """Generates HTML documentation for a specific field."""
    if len(field.packed_fields) != 0:
      out = ''
      for packed_field in field.packed_fields:
        out += self.visitField(packed_field, 
                               'In packed field %s.' % field.name)
      return out

    # Draw a solid line at start of each flit to visually separate flits.
    solid = ''
    if field.start_bit == 63:
      solid = 'border-top: solid 1px'
    out = ''
    out += '<tr style="%s">\n' % solid
    out += '  <td class="structBits">%d</td>\n' % field.flit
    out += '  <td class="structBits">%d-%d</td>\n' % (field.start_bit, field.end_bit)
    if field.type.IsArray():
      out += '  <td>%s[%d]</td>\n  <td>%s</td>\n' % (
        field.type, field.type.ArraySize(), field.name)
    else:
      out += '  <td>%s</td>\n  <td>%s</td>\n' % (field.type, field.name)
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
    # Warnings noted.
    self.warnings = []
    self.current_document = None

  def visitDocument(self, the_doc):
    for struct in the_doc.structs:
      self.visitStruct(struct)

  def visitStruct(self, the_struct):
    last_type = None
    last_flit = None
    last_start_bit = 0
    last_end_bit = 0
    last_field_name = None

    # Iterate through the fields from 0 to make sure LSB is aligned
    # correctly.
    for field in reversed(the_struct.fields):
      if last_type is None:
        last_type = field.type
      elif last_type != field.type:
        # If the type of the variables changes, make sure the current offset would
        # allow the provided alignment.
        # TODO(bowdidge): Assumes type width = type alignment.
        if (field.end_bit % field.type.Alignment() != 0):

          self.warnings.append(
            'In structure %s, type won\'t allow alignment: "%s %s" at bit %d' %
            (the_struct.name, field.type, field.name, field.end_bit))

      if last_flit == field.flit:
        # Note that fields are visited in reverse order - smallest to largest.
        if (last_start_bit >= field.start_bit or 
            last_end_bit >= field.end_bit):
          self.warnings.append('*** field "%s" and "%s" not in bit order' % (
              field.name, last_field_name))
        elif field.end_bit <= last_start_bit:
          self.warnings.append('*** field "%s" overlaps field "%s"' % (
              field.name, last_field_name))
        elif last_start_bit != field.end_bit - 1:
          self.warnings.append('*** unexpected space between field "%s" and "%s"' % (
              field.name, last_field_name))
              
      last_flit = field.flit
      last_start_bit = field.start_bit
      last_end_bit = field.end_bit
      last_field_name = field.name

    for struct in the_struct.structs:
      # Check adjacent structures match up with bit patterns.
      self.visitStruct(struct)

  def visitUnion(self, the_union):
    for struct in the_union.structs:
      self.visitStruct(struct)

  def visitField(self, the_field):
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

  def visitDocument(self, doc):
    # Pack all structures in the named documents.
    self.doc = doc
    for struct in doc.structs:
      self.visitStruct(struct)

  def visitStruct(self, the_struct):
    # Gather fields by flit, then create macros for each.
    # Should make sure that adjacent fields are same types.
    for struct in the_struct.structs:
      self.visitStruct(struct)
    for union in the_struct.unions:
      self.visitUnion(union)
    self.packStruct(the_struct)

  def visitUnion(self, the_union):
    # Handle packing fields in union.
    # TODO(bowdidge): Union fields start the packing all over again, so if the 
    # common bit is not a full word, then need to copy fields over.
    for struct in the_union.structs:
      self.visitStruct(struct)


  def packFlit(self, the_struct, flit_number, the_fields):
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
      if field.type != current_type or field.type.IsArray():
        if len(current_group) > 1:
          fields_to_pack.append((current_type, current_group))
        current_group = []
        current_type = None

      if (field.type.BitWidth() != field.Size() and
          (current_type == None or field.type == current_type)):
        current_type = field.type
        current_group.append(field)

    if len(current_group) > 1:
      # No need to pack if only one item in set of things to pack.
      fields_to_pack.append((current_type, current_group))

    if len(fields_to_pack) == 0:
      # Nothing to pack.
      return

    for (type, fields) in fields_to_pack:
      max_start_bit = max([f.start_bit for f in fields])
      min_end_bit = min([f.end_bit for f in fields])
      new_field_name = fields[0].name + "_to_" + LastNonReservedName(fields)
      new_field = Field(new_field_name, type, flit_number,
                        max_start_bit, min_end_bit)
      
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

      self.createMacros(the_struct, new_field, fields)
        

  def packStruct(self, the_struct):
    # Get rid of old struct fields, and use macros on flit-sized 
    # fields to access.
    new_fields = []
    flit_field_map = self.fieldsToFlits(the_struct)

    for flit, fields_in_flit in flit_field_map.iteritems():
      self.packFlit(the_struct, flit, fields_in_flit)

  def fieldsToFlits(self, struct):
    # Return a map of (flit, fields) for all fields in the structure.
    flit_field_map = {}
    for field in struct.fields:
      item = flit_field_map.get(field.flit, [])
      item.append(field)
      flit_field_map[field.flit] = item
    return flit_field_map

  def createMacros(self, struct, new_field, combined_fields):
    """Creates macros to access all the bit fields we removed.
    struct: structure containing the fields that was removed.
    new_field: field combining the contents of the former fields.
    combined_fields: fields that were removed.
    """
    min_end_bit = min([f.end_bit for f in combined_fields])

    for old_field in combined_fields:
      # No point in creating macros for fields that shouldn't be accessed.
      if old_field.name == "reserved":
        continue

      ident = utils.AsUppercaseMacro('FUN%s_%s' % (struct.name, old_field.name))
      shift = '#define %s_S %s' % (ident, old_field.end_bit - min_end_bit)
      mask = '#define %s_M %s' % (ident, old_field.Mask())
      value = '#define %s_P(x) ((x) << %s_S)' % (ident, ident)
      get = '#define %s_G(x) (((x) >> %s_S) & %s_M)' % (ident, ident, ident)

      self.doc.addMacro(
          '// For accessing "%s" field in %s.%s' % (
          old_field.name, struct.name, new_field.name))
      self.doc.addMacro(shift)
      self.doc.addMacro(mask)
      self.doc.addMacro(value)
      self.doc.addMacro(get)
      self.doc.addMacro('\n')

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
    # currently being parsed.  New fields or structures are put in the
    # last object.
    self.stack = [(DocBuilderTopLevel, self.current_document)]
    # strings describing any errors encountered during parsing.
    self.errors = []
    # strings describing any odd but non-fatal problems.
    self.warnings = []
    # Comment being formed for next object.
    self.current_comment = ''

  def parseStructStart(self, line):
    # Handle a STRUCT directive opening a new structure.
    # Returns created structure.
    state, current_object = self.stack[len(self.stack)-1]
    terms = line.split(' ')

    if len(terms) == 3:
      name = terms[1]
      variable = terms[2]
    elif len(terms) == 2:
      name = terms[1]
      variable = None
    else:
      self.errors.append('couldn\'t parse "%s"' % line)
      current_object = None

    name = utils.RemoveWhitespace(name)
    variable = utils.RemoveWhitespace(variable)

    current_struct = Struct(name, variable)

    if len(self.current_comment) > 0:
      current_struct.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((DocBuilderStateStruct, current_struct))
    current_object.structs.append(current_struct)

  def parseEnumStart(self, line):
    # Handle an ENUM directive opening a new enum.
    state, current_object = self.stack[len(self.stack)-1]
    _, name = line.split(' ')
    name = utils.RemoveWhitespace(name)
    current_enum = Enum(name)

    if len(self.current_comment) > 0:
      current_enum.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((DocBuilderStateEnum, current_enum))
    self.current_document.enums.append(current_enum)

  def parseEnumLine(self, line):
    # Parse the line describing a new enum variable.
    # This regexp matches:
    # Foo = 1 Abitrary following comment 
    match = re.match('(\w+)\s*=\s*(\w+)\s*(.*)', line)
    if match is None:
      self.errors.append('Invalid enum line: "%s"' % line)
      return None

    var = match.group(1)
    # TODO(bowdidge): Test valid C identifier.
    value_str = match.group(2)
    value = utils.ParseInt(value_str)
    if value is None:
      self.errors.append('Invalid enum value for %s: "%s"' % (value_str, var))
      return None
    # Parse a line describing an enum variable.
    # TODO(bowdidge): Remember whether value was hex or decimal for better printing.
    new_enum = EnumVariable(var, value)

    if len(self.current_comment) > 0:
      new_enum.body_comment = self.current_comment
    self.current_comment = ''

    if match.group(3):
        new_enum.key_comment = utils.StripComment(match.group(3))
    return new_enum
 
  def parseLine(self, line):
    # Handle a line.  Use the state on top of the stack to decide what to do.
    state,current_object = self.stack[len(self.stack)-1]
    if line.startswith('//'):
      self.current_comment += utils.StripComment(line)
    elif state == DocBuilderTopLevel:
      return
    elif state == DocBuilderStateEnum:
      enum = self.parseEnumLine(line)
      if enum is not None:
        current_object.variables.append(enum)
    else:
      field = self.parseFieldLine(line)
      if field is not None:
        current_object.fields.append(field)

  def parseEnd(self, line):
    # Handle an END directive.
    state,current_object = self.stack[len(self.stack)-1]
    if len(self.current_comment) > 0:
      current_object.tail_comment = self.current_comment
    self.current_comment = ''
    self.stack.pop()

  def parseUnionStart(self, line):
    # Handle a UNION directive opening a new union.
    state,current_object = self.stack[len(self.stack)-1]
    _, name, variable = line.split(' ')
    name = utils.RemoveWhitespace(name)
    variable = utils.RemoveWhitespace(variable)
    current_union = Union(name, variable)
    if len(self.current_comment) > 0:
      current_union.body_comment = self.current_comment
    self.current_comment = ''
    self.stack.append((DocBuilderStateUnion, current_union))
    current_object.unions.append(current_union)

  def parseFieldLine(self, line):
    # Handle a line describing a field in a structure.
    # Struct line is:
    # flit start_bit:end_bit type name /* comment */
    match = re.match('(\w+)\s+(\w+:\w+|\w+)\s+(\w+)\s+(\w+)(\[[0-9]+\]|)\s*(.*)', line)

    if match is None:
        # Flag error, or treat as comment.
        self.errors.append('Invalid field line: "%s"' % line)
        return None

    is_array = False
    array_size = 1

    flit_str = match.group(1)
    bit_spec = match.group(2)
    type_name = match.group(3)
    name = match.group(4)
    if len(match.group(5)) != 0: 
      is_array = True
      array_size = utils.ParseInt(match.group(5).lstrip('[').rstrip(']'))
      if array_size is None:
        print("Eek, thought %s was a number, but didn't parse!\n" % match.group(5))
    key_comment = match.group(6)

    start_bit_str = None
    end_bit_str = None

    if ':' in bit_spec:
      bits_match = re.match('(\w+):(\w+)', bit_spec)
      if bits_match is None:
        self.errors.append('Invalid bit pattern: "%s"' % bits)
        return None
      start_bit_str = bits_match.group(1)
      end_bit_str = bits_match.group(2)
    else:
      # Assume single bit.
      start_bit_str = bit_spec
      end_bit_str = bit_spec
        
    flit = utils.ParseInt(flit_str)
    if flit is None:
      self.errors.append('Invalid flit "%s"' % flit_str)
      return None

    start_bit = utils.ParseInt(start_bit_str)
    if start_bit is None:
      self.errors.append('Invalid start bit "%s"' % start_bit_str)
      return None

    end_bit = utils.ParseInt(end_bit_str)
    if end_bit is None:
      self.errors.append('Invalid end bit "%s"' % end_bit_str)
      return None

    if start_bit > 63:
      self.errors.append('Field "%s" has start bit "%d" too large for 8 byte flit.' % (
          name, start_bit))
      return None
 
    type = None
    if is_array:
      type = Type(type_name, array_size)
    else:
      type = Type(type_name)

    if start_bit < end_bit:
      self.errors.append('Start bit %d greater than end bit %d in field %s' % 
                         (start_bit, end_bit, name))

    expected_width = type.BitWidth()

    actual_width = start_bit - end_bit + 1
    if is_array:
      if actual_width != expected_width:
        self.errors.append('Field "%s" needed %d bytes to hold %s[%d], got %d.' %
                         (name, expected_width, type, array_size,
                          actual_width))


    elif actual_width > expected_width:
      self.errors.append('Type "%s" too small to hold %d bits for field "%s".' % 
                         (type, actual_width, name))
      return None

    if key_comment == '':
      key_comment = None
    else:
      key_comment = utils.StripComment(key_comment)

    new_field = Field(name, type, flit, start_bit, end_bit)

    new_field.key_comment = key_comment

    if len(self.current_comment) > 0:
      new_field.body_comment = self.current_comment
    self.current_comment = ''
    
    type_width = new_field.type.BitWidth()
    var_width = new_field.start_bit - new_field.end_bit + 1
    if var_width < type_width:
      self.warnings.append('*** field "%s" doesn\'t fill field' % new_field.name)
    elif var_width > type_width:
      warning = '*** %s larger than field type %s' % (new_field.name, new_field.type)
      self.warnings.append(warning)
    return new_field

  def parsePlainLine(self, line):
    # TODO(bowdidge): Save test in order for printing as comments.
    return

  def parse(self, the_file):
    # Begin parsing a generated file provided as text.  Returns errors if any, or None.
    line_count = 0
    for line in the_file:
      # Remove whitespace to allow for meaningful indenting.
      line = line.lstrip(' ')
      line_count += 1
      if line.startswith('STRUCT'):
        self.parseStructStart(line)
      elif line.startswith('UNION'):
        self.parseUnionStart(line)
      elif line.startswith('ENUM'):
        self.parseEnumStart(line)
      elif line.startswith('END'):
        self.parseEnd(line)
      else:
        self.parseLine(line)
    if len(self.errors) > 0:
      return self.errors
    return None

def usage():
  sys.stderr.write('generator.py: usage: [-p] [-g [code, html] [-o file]\n')
  sys.stderr.write('-p: pack fields into 8 byte flits, and create accessor macros\n')
  sys.stderr.write('-g code: generate header file to stdout (default)\n')
  sys.stderr.write('-g html: generate HTML description of header\n')
  sys.stderr.write('-o filename_base: send output to named file\n')
  sys.stderr.write('                  for code generation, appends correct extension.\n')

def generateFile(should_pack, output_style, output_base,
                 input_stream, input_filename):
  # Process a single .gen file and create the appropriate header/docs.
  doc_builder = DocBuilder()

  errors = doc_builder.parse(input_stream)

  if errors is not None:
    for error in errors:
      print(error)
    sys.exit(1)

  doc = doc_builder.current_document
  doc.filename = input_filename

  c = Checker()
  c.visitDocument(doc)
  if len(c.warnings) != 0:
    for warning in c.warnings:
      sys.stderr.write('Warning: %s\n' % warning)
 
  if should_pack:
    p = Packer()
    p.visitDocument(doc)

  helper = codegen.HelperGenerator()
  helper.visitDocument(doc)

  if output_style is OutputStyleHTML:
    html_generator = HTMLGenerator()
    code = html_generator.visitDocument(doc)
    if output_base:
      f = open(output_base + '.html', 'w')
      f.write(code)
      f.close()
    else:
      return code
  elif output_style is OutputStyleHeader:
    code_generator = codegen.CodeGenerator(output_base)
    code_generator.output_file = output_base
    (header, source) = code_generator.visitDocument(doc)

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
    usage()
    sys.exit(2)
  
  should_pack = False
  output_style = OutputStyleHeader
  output_base = None

  for o, a in opts:
    if o == '-p':
      should_pack = True
    elif o in ('-h', '--help'):
      usage()
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
  out = generateFile(should_pack, output_style, output_base,
                     input_stream, args[0])
  input_stream.close()
  if out:
    print out              

if __name__ == '__main__':
  main()
