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
import htmlgen
import utils

# Default size of a word.  Input is specified in flits and bit offsets.
FLIT_SIZE = 64

# Fake value for width of field, used when we can't define the value
# correctly on creation.
FAKE_WIDTH = 8675309

def BitFlitString(offset):
  """Returns a human-readable string describing the offset as flit/bit."""
  return '%d:%d' % (offset / FLIT_SIZE, 63 - offset % FLIT_SIZE)

class BaseType:
  """Represents a the base type name without qualifications.
  
  The base type only contains a scalar type, struct, or union.
  Arrays, const, etc. would be represented in the Type class.
  """
  def __init__(self, name, bit_width=0, node=None):
    # Short name used in file.
    self.name = name
    # Number of bits.
    self.bit_width = bit_width
    # Parsed struct or union, or None if built-in.
    self.node = node

  def Name(self):
    """Returns the name of the type."""
    return self.name

  def BitWidth(self):
    """Returns the width of the base type itself."""
    return self.bit_width

  def __cmp__(self, other):
    if other is None:
      return -1

    if self.name != other.name:
      if self.name < other.name:
        return -1
      else:
        return 1
    if self.bit_width != other.bit_width:
      if self.bit_width < other.bit_width:
        return -1
      else:
        return 1
    if self.node or other.node:
      if self.node.name != other.node.name:
        if self.node.name < other.node.name:
          return -1
        else:
          return 1
    return 0
  

# Width of all known types.  Structures are added to this
# dictionary during execution.
builtin_type_widths = {
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

def BaseTypeForName(name):
  """Returns a BaseType for the builtin type with the provided name."""
  if name not in builtin_type_widths:
    sys.stderr.write('Invalid name in BaseTypeForName.')
  return BaseType(name, builtin_type_widths[name])

def TypeForName(name):
  """Returns a type for the builtin type with the provided name."""
  if name not in builtin_type_widths:
    sys.stderr.write('Invalid name in BaseTypeForName.')
  return Type(BaseType(name, builtin_type_widths[name]))

def ArrayTypeForName(name, element_count):
  """Returns a type for the builtin type with the provided name and size."""
  if name not in builtin_type_widths:
    sys.stderr.write('Invalid name in BaseTypeForName.')
  return Type(BaseType(name, builtin_type_widths[name]), element_count)

  
class Type:
  """Represents C type for a field."""

  def __init__(self, base_type, array_size=None):
    self.base_type = base_type
    # Number of elements in the array.
    self.array_size = 0
    # Size of the total object in bits.
    self.bit_width = 0
    # True if type represents an array type.
    self.is_array = False

    if array_size is not None:
      self.is_array = True
      self.array_size = array_size
    else:
      self.is_array = False
      self.array_size = None

    self.alignment = base_type.BitWidth()

    if self.is_array:
      self.bit_width = self.alignment * array_size
    else:
      self.bit_width = self.alignment

  def IsArray(self):
    """Returns true if the type is an array type."""
    return self.is_array

  def IsRecord(self):
    """Returns true if the type contains other fields (union or struct)

    Records can still be arrays too.
    """
    return self.base_type.node is not None

  def IsScalar(self):
    """Returns true if the type is a scalar, builtin type."""
    # TODO(bowdidge): Should uint128_t count as scalar or not?
    if self.is_array:
      return False
    if self.base_type.node:
      return False
    return True

  def BaseName(self):
    """Returns base type name without array and other modifiers."""
    return self.base_type.Name()

  def DeclarationName(self):
    if self.base_type.node:
      return "struct " + self.base_type.name
    return self.base_type.name

  def ArraySize(self):
    """Returns the size of an array.  Throws exception if not an array type."""
    if not self.is_array:
      raise ValueError('Not array')
    return self.array_size

  def TypeName(self):
    """Returns type name."""
    if self.is_array:
      return "%s[%d]" % (self.base_type.Name(), self.array_size)
    else:
      return self.base_type.Name()

  def DeclarationType(self):
    """Returns type name as function parameter type."""
    if self.is_array:
      return '%s[%d]' % (self.base_type.name, self.array_size)
    elif self.base_type.node:
      return 'struct %s' % self.base_type.name
    else:
      return self.base_type.Name()

  def Alignment(self):
    """Returns natural alignment for the type in bits."""
    if self.alignment == 0:
      return FLIT_SIZE / 8
    return self.alignment

  def BitWidth(self):
    """Returns width of type in bits."""
    return self.bit_width

  def __cmp__(self, other_type):
    if other_type is None:
      return -1

    if self.base_type != other_type.base_type:
      if self.base_type < other_type.base_type:
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
      return '<Type: %s[%d]>' % (self.base_type.Name(), self.array_size)
    else:
      return '<Type: %s>' % (self.base_type.Name())


class Visitor:
  # Visitor abstract class for walking the specification tree.
  def VisitField(self, field):
    pass
  def VisitStruct(self, struct):
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


class Field(Node):
  # Representation of a field in a structure or union.
  #
  # Within the field, bit positions are relative to the high bit of the
  # first flit; 0 is the high bit of the first flit, 63 is the low bit of
  # the first flit, etc.  This choice makes math about packing easier.
  # For the human descriptions (both input and output), bits are ordered
  # in the opposite fashio with 63 as the high bit of the flit.
  # The StartOffset and EndOffset use the high bit = 0 system;
  # the StartBit and EndBit use high bit = 63.

  def __init__(self, name, type, offset_start, bit_width):
    Node.__init__(self)
    # name of the field declaration.
    self.name = name
    # String name of the C type, or a generic type for signed-ness.
    self.type = type

    # True if the field doesn't actually represent a specific bit pattern.
    # Used for variable length arrays.
    self.no_offset = False

    # Bit offset from top of first word.
    self.offset_start = offset_start
    self.bit_width = bit_width

    self.crosses_flit = False
    # Fields that have been packed in this field.
    self.packed_fields = []
    # True if field was explicitly defined to be less than its natural size.
    self.is_bitfield = False

    # Fields for a composite object such as a struct or union.
    self.subfields = []

  def __str__(self):
    if self.StartFlit() == self.EndFlit():
      return('<Field: name=%s, type=%s, flit=%d, bits=%d:%d>' %
             (self.name, self.type, self.StartFlit(),
              self.StartBit(), self.EndBit()))
    else:
      return('<Field: name=%s, type=%s, start: flit=%d, bit=%d, '
             'end: flit=%d, bit=%d>' % (self.name, self.type,
                                        self.StartFlit(), self.StartBit(),

                                        self.EndFlit(), self.EndBit()))

  def Name(self):
    return self.name

  def Type(self):
    return self.type

  def ExtendSize(self, amount):
    """Increases the size of the field.  Used for ... notation."""
    self.bit_width += amount

  def StartOffset(self):
    """Returns the offset of the field from the top of the container."""
    if self.no_offset:
      return None
    return self.offset_start

  def EndOffset(self):
    """Returns the bottom offset of the field from the top of the container."""
    if self.no_offset:
      return None
    return self.offset_start + self.bit_width - 1

  def StartFlit(self):
    """Returns the flit in the container holding the start of this field."""
    if self.no_offset:
      return None
    return self.StartOffset() / FLIT_SIZE

  def EndFlit(self):
    """Returns the flit in the container holding the end of this field."""
    if self.no_offset:
      return None
    return (self.StartOffset() + self.BitWidth() - 1) / FLIT_SIZE

  def StartBit(self):
    """Returns the bit offset in the start flit.

    0 is the bottom of the flit.
    """
    if self.no_offset:
      return None
    return FLIT_SIZE - (self.StartOffset() - (self.StartFlit() * FLIT_SIZE)) - 1

  def EndBit(self):
    """Returns the bit offset in the end flit.

    0 is the bottom of the flit.
    """
    if self.no_offset:
      return None
    return FLIT_SIZE - (self.EndOffset() - (self.EndFlit() * FLIT_SIZE)) - 1

  def BitWidth(self):
    # Returns the number of bits in the field.
    if self.no_offset:
      return 0
    return self.bit_width

  def Mask(self):
    # Returns a hexadecimal number that can be used as a mask in the flit.
    return '0x%x' %  ((1 << self.bit_width) - 1)

  def SmallerThanType(self):
    return self.bit_width < self.type.BitWidth()

  def IsNoOffset(self):
    return self.no_offset

  def IsReserved(self):
    """True if the field is a placeholder that doesn't need to be initialized."""
    return (self.name.startswith('reserved') or self.name.startswith('rsvd')
            or self.no_offset)

  def CreateSubfields(self):
    """Inserts sub-fields into this field based on the its type.

    For fields that are structures, this code walks the tree of structures
    and creates new sub-fields in this field from the fields of the prototype
    structure.  It sets the offset and size to match the prototype.
    """
    if not self.type.base_type.node:
      return

    for proto_field in self.type.base_type.node.fields:
      if proto_field.no_offset:
        new_subfield = Field(proto_field.Name(), proto_field.Type(), None, None)
      else:
        new_subfield = Field(proto_field.Name(), proto_field.Type(),
                             self.StartOffset() + proto_field.StartOffset(),
                             proto_field.BitWidth())
      # TODO(bowdidge): Consider an explicit copy method.
      new_subfield.key_comment = proto_field.key_comment
      new_subfield.body_comment = proto_field.body_comment
      new_subfield.tail_comment = proto_field.tail_comment
      new_subfield.generator_comment = proto_field.generator_comment
      new_subfield.line_number = proto_field.line_number
      new_subfield.crosses_flit = proto_field.crosses_flit
      new_subfield.is_bitfield = proto_field.is_bitfield
      new_subfield.no_offset = proto_field.no_offset


      self.subfields.append(new_subfield)
      if proto_field.type.IsRecord():
        new_subfield.CreateSubfields()
        

class EnumVariable(Node):
  # Representation of an enum variable in an enum declaration.

  def __init__(self, name, value):
     # Create an EnumVariable.
     Node.__init__(self)
     # name is a string.
     self.name = name
     # value is an integer value for the variable.
     self.value = value

  def __str__(self):
     return('<EnumVariable: %s = 0x%x>' % self.name, self.value)


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

  def Name(self):
    return self.name

  def BitWidth(self):
    return 0

  def __str__(self):
    return('<Enum %s:\n  %s\n>\n' % (self.name, self.variables))


class FlagSet(Node):
  # Representation of an flags declaration.  FlagSet are like enums,
  # but the values are expected to represent bitmasks, and the values
  # are generated as ints rather than as an enum.

  def __init__(self, name):
    # Create an FlagSet declaration.
    # name is a string.
    # variables holds the EnumVariables associated with the enum.
    Node.__init__(self)
    self.name = name
    self.variables = []

  def Name(self):
    return self.name

  def BitWidth(self):
    return 0

  def MaxValue(self):
    max_value = 0
    for var in self.variables:
      if var.value > max_value:
        max_value = var.value
    return max_value

  def __str__(self):
    return('<FlagSet %s:\n  %s\n>\n' % (self.name, self.variables))


class Struct(Node):
  # Representation of a structure.

  def __init__(self, name, is_union):
    """Create a struct declaration.

    if is_union is true, then this is a union rather than a structure.
    """
    Node.__init__(self)
    # name is a string representing the name of the struct.
    self.name = name

    # fields is the list of fields in the struct.
    self.fields = []

    # True if this struct actually represents a union.
    self.is_union = is_union

    # True if the struct or union should be drawn inline where it's
    # used.  The inline flag is usually set depending on whether the
    # struct was defined inline in the gen file, or on its own.
    self.inline = False

  def Name(self):
    return self.name

  def Tag(self):
    """Returns the correct token to use when generating a declaration."""
    if self.is_union:
      return 'union'
    return 'struct'

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
    return('<Struct %s, isUnion: %d fields: %s>\n' %
           (self.name, self.is_union, self.fields))

  def BitWidth(self):
    """Returns the width in bits of the contents of this struct."""

    fields_with_offsets = [f for f in self.fields if not f.IsNoOffset()]

    if len(fields_with_offsets) == 0:
      return 0

    if self.is_union:
      return max([f.BitWidth() for f in fields_with_offsets])

    last_field = fields_with_offsets[-1]
    end_offset = last_field.EndOffset()
    return end_offset + 1

  def StartOffset(self):
    """Returns beginning offset for structure."""
    if not self.fields:
      return 0

    return min([f.StartOffset() for f in self.fields])

  def Flits(self):
    """Returns the number of flits this structure would occupy.

    Assumes the struct is aligned at the top of a flit.
    """
    if len(self.fields) == 0:
      return 0
    return max([field.EndFlit() for field in self.fields]) + 1

  def Bytes(self):
    """Returns the number of bytes in the structure."""
    if len(self.fields) == 0:
      return 0

    return max([(f.EndFlit() + 1) * 8 for f in self.fields])

  def FlitFieldMap(self):
    # Return a map of (flit, fields) for all fields in the structure.
    flit_field_map = {}
    fields_with_offsets = [f for f in self.fields if not f.IsNoOffset()]

    for field in fields_with_offsets:
      item = flit_field_map.get(field.StartFlit(), [])
      item.append(field)
      flit_field_map[field.StartFlit()] = item
    return flit_field_map

class Document(Node):
  # Representation of an entire generated header specification.
  def __init__(self):
    Node.__init__(self)
    # structs is all the structures defined in the document.
    self.structs = []

    # All enums declared in the file.
    self.enums = []

    # All flag sets declared in the file.
    self.flagsets = []

    # Source code for function declarations.
    self.declarations = []

    # Source code for function definitions.
    self.definitions = []

    # Original filename containing the specifications.
    self.filename = None

  def __str__(self):
    return('<Document>')

  def AddMacro(self, macro_str):
    # Record a macro to output.
    self.macros.append(macro_str)



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
              last_field_name, BitFlitString(last_end_offset),
              field.name, BitFlitString(start_offset)))
          
        elif start_offset != last_end_offset + 1:
          self.AddError(field, 'unexpected space between field "%s" and "%s".  '
                        '("%s" ends at %s, "%s" begins at %s)'
                        % (last_field_name, field.name,
                           last_field_name, BitFlitString(last_end_offset),
                           field.name, BitFlitString(start_offset)))

      last_start_offset = field.StartOffset()
      last_end_offset = field.EndOffset()
      last_field_name = field.name

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
    if not the_struct.is_union:
      self.PackStruct(the_struct)

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
      packed_field_width = 0
      min_start_bit = min([f.StartBit() for f in fields])
      for f in fields:
        packed_field_width += f.BitWidth()

      if (packed_field_width > type.BitWidth()):
        self.AddError(the_struct,
                      'Unable to pack fields %s. '
                      'Fields are %d bits, type is %d bits.' % (
            utils.ReadableList([f.name for f in fields]),
            packed_field_width,
            type.BitWidth()))

      new_field_name = fields[0].name + "_to_" + LastNonReservedName(fields)
      new_field = Field(new_field_name, type, min_start_bit, packed_field_width)
      new_field.line_number = fields[0].line_number

      non_reserved_fields = [f.name for f in fields if not f.IsReserved()]
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
          break
      for f in fields[1:]:
        new_field.packed_fields.append(f)
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

    self.base_types = {}
    for name in builtin_type_widths:
      self.base_types[name] = BaseType(name, builtin_type_widths[name])

  def AddError(self, msg):
    if self.current_document.filename:
      location = '%s:%d: ' % (self.current_document.filename, self.current_line)
    else:
      location = '%d: ' % self.current_line
    self.errors.append(location + msg)

  def ParseStructStart(self, line):
    # Handle a STRUCT directive opening a new structure.
    # Returns created structure.
    (state, current_object) = self.stack[-1]
    # Struct syntax is STRUCT struct-identifier var-name comment
    match = re.match('STRUCT\s+(\w+)(\s+\w+|)(\s*.*)$', line)

    if not match:
      self.AddError('Invalid STRUCT line: "%s" % lne')
      return None

    identifier = match.group(1)
    variable_name = match.group(2)
    key_comment = match.group(3)
    variable_name = utils.RemoveWhitespace(variable_name)

    current_struct = Struct(identifier, False)
    current_struct.line_number = self.current_line
    current_struct.key_comment = self.StripKeyComment(key_comment)

    if len(self.current_comment) > 0:
      current_struct.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((DocBuilderStateStruct, current_struct))

    self.current_document.structs.append(current_struct)

    # Add the struct to the symbol table.  We don't know
    self.base_types[identifier] = BaseType(identifier, FAKE_WIDTH, current_struct)

    if state != DocBuilderTopLevel:
      new_field = Field(variable_name, self.MakeType(identifier), 0, 0)
      new_field.line_number = self.current_line

      current_object.fields.append(new_field)
      current_struct.inline = True

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
    current_enum = Enum(name)
    current_enum.line_number = self.current_line
    current_enum.key_comment = self.StripKeyComment(key_comment)

    if len(self.current_comment) > 0:
      current_enum.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((DocBuilderStateEnum, current_enum))
    self.current_document.enums.append(current_enum)

  def ParseFlagSetStart(self, line):
    # Handle an FLAGS directive opening a new type represeting bit flags.
    state, containing_struct = self.stack[len(self.stack)-1]
    match = re.match('FLAGS\s+(\w+)(.*)$', line)
    if match is None:
      self.AddError('Invalid flags start line: "%s"' % line)
      return

    name = match.group(1)
    key_comment = match.group(2)

    name = utils.RemoveWhitespace(name)
    current_flags = FlagSet(name)
    current_flags.line_number = self.current_line
    current_flags.key_comment = self.StripKeyComment(key_comment)

    if len(self.current_comment) > 0:
      current_flags.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((DocBuilderStateFlagSet, current_flags))
    self.current_document.flagsets.append(current_flags)

  def ParseEnumLine(self, line):
    # Parse the line describing a new enum variable.
    # This regexp matches:
    # Foo = 1 Abitrary following comment
    match = re.match('(\w+)\s*=\s*(\w+)\s*(.*)$', line)
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
        new_enum.key_comment = self.StripKeyComment(match.group(3))
    return new_enum

  def ParseLine(self, line):
    """Parse a single line of a gen file that wasn't the start or end of container.

    Use the state on top of the stack to decide what to do.
    """
    (state, containing_struct) = self.stack[len(self.stack)-1]
    if line.startswith('//'):
      self.current_comment += self.StripKeyComment(line)
    elif state == DocBuilderTopLevel:
      return
    elif state == DocBuilderStateEnum or state == DocBuilderStateFlagSet:
      enum = self.ParseEnumLine(line)
      if enum is not None:
        containing_struct.variables.append(enum)
    else:
      # Try parsing as continuation of previous field
      if (not self.ParseMultiFlitFieldLine(line, containing_struct) and 
          not self.ParseFieldLine(line, containing_struct)):
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

    if not isinstance(current_object, Struct):
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
    current_union = Struct(name, True)
    current_union.line_number = self.current_line
    if len(self.current_comment) > 0:
      current_union.body_comment = self.current_comment
    self.current_comment = ''
    self.stack.append((DocBuilderStateStruct, current_union))
    self.current_document.structs.append(current_union)

    self.base_types[identifier] = BaseType(identifier, FAKE_WIDTH, current_union)
    if state != DocBuilderTopLevel:
      # Inline union.  Define the field.
      new_field = Field(variable, self.MakeType(identifier), 0, 0)
      new_field.line_number = self.current_line
      containing_object.fields.append(new_field)
      current_union.inline = True

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
      return Type(base_type, array_size)
    else:
      return Type(base_type)


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

      zero_array = Field(name, type, -1, -1)
      zero_array.no_offset = True
      zero_array.key_comment = key_comment
      zero_array.body_comment = body_comment
      containing_struct.fields.append(zero_array)
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

    start_offset = flit * 64 + (FLIT_SIZE - start_bit - 1)
    end_offset = flit * 64 + (FLIT_SIZE - end_bit - 1)
    bit_size = end_offset - start_offset + 1
    new_field = Field(name, type, start_offset, bit_size)
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
    containing_struct.fields.append(new_field)
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
        sys.stderr.write(error + '\n')

  helper = codegen.HelperGenerator()
  helper.VisitDocument(doc)

  if output_style is OutputStyleHTML:
    html_generator = htmlgen.HTMLGenerator()
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
