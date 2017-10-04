#!/usr/bin/python
#
# Code for parsing generator files.
#
# Copyright Fungible Inc. 2017.

import utils

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

def RecordTypeForStruct(the_struct):
  """Returns a type for a field that would hold a single struct."""
  base_type = BaseType(the_struct.name, 0, the_struct)
  return Type(base_type)

def RecordArrayTypeForStruct(the_struct, element_count):
  """Returns a type for a field that would hold a single struct."""
  base_type = BaseType(the_struct.name, 0, the_struct)
  return Type(base_type, element_count)
  

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
      return utils.FLIT_SIZE / 8
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


UnknownKind = 0
# Declarations in input.
StructKind = 1
EnumKind = 2
FlagSetKind = 3

MacroKind = 4
FunctionKind = 5
FieldKind = 6
EnumVariableKind = 5


class Declaration:
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

    # All macros related to this Declaration in string form.
    self.macros = []

    # Source code for functions related to this Declaration.
    # List of Function objects.
    self.functions = []

    # Location where Declaration appeared in source.
    self.line_number = 0

    self.declarationKind = UnknownKind

  def MacroWithName(self, name):
    """Returns a specific macro attached to this declaration."""
    for macro in self.macros:
      if macro.name == name:
        return macro
    return None
 

class Macro(Declaration):
  """Representation of a generated macro.
  Code generator should fill in comments for documentation.
  """
  def __init__(self, name, body, comment):
    Declaration.__init__(self)
    self.name = name
    self.body = body
    self.body_comment = comment
    self.declaration_kind = MacroKind

class Function(Declaration):
  """Representation of a generated function.
  Code generator should fill in comments for documentation.
  """
  def __init__(self, decl, defn, comment):
    Declaration.__init__(self)
    # Forward declaration of function.
    self.declaration = decl
    # Full function definition with body.
    self.definition = defn
    self.body_comment = comment
    self.declaration_kind = FunctionKind
    
class Field(Declaration):
  # Representation of a field in a structure or union.
  #
  # Within the field, bit positions are relative to the high bit of the
  # first flit; 0 is the high bit of the first flit, 63 is the low bit of
  # the first flit, etc.  This choice makes math about packing easier.
  # For the human descriptions (both input and output), bits are ordered
  # in the opposite fashion with 63 as the high bit of the flit.
  # The StartOffset and EndOffset use the high bit = 0 system;
  # the StartBit and EndBit use high bit = 63.

  def __init__(self, name, type, offset_start, bit_width):
    """Creates a new field in a struct.

    name: name of the field.
    type: Type object describing the type of the field.
    offset_start: offset of the field in the structure, starting at 0.
    bit_width: width of field in bits, or -1 if an array of undefined length.
    """
    Declaration.__init__(self)
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

    # True if field needs to be swapped when converting from a different
    # ended processor.  Irrelevant for packed fields.
    self.swappable = type is not None and type.bit_width > 8

    # True if field appears to be a reserved field that doesn't need to be
    # initialized or manipulated.
    self.is_reserved = (name.startswith('reserved') or
                        name.startswith('rsvd') or
                        name.startswith('unused'))

    # Fields for a composite object such as a struct or union.
    self.subfields = []
    self.declaration_kind = FieldKind

  def __str__(self):
    if self.no_offset:
      return('<Field: name=%s, type=%s, no offset>' %
             (self.name, self.type))
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
    """Returns the bottom offset of the field from the top of the
    container.
    """
    if self.no_offset:
      return None
    return self.offset_start + self.bit_width - 1

  def StartFlit(self):
    """Returns the flit in the container holding the start of this field."""
    if self.no_offset:
      return None
    return self.StartOffset() / utils.FLIT_SIZE

  def EndFlit(self):
    """Returns the flit in the container holding the end of this field."""
    if self.no_offset:
      return None
    return (self.StartOffset() + self.BitWidth() - 1) / utils.FLIT_SIZE

  def StartBit(self):
    """Returns the bit offset in the start flit.

    0 is the bottom of the flit.
    """
    if self.no_offset:
      return None
    return utils.FLIT_SIZE - (self.StartOffset() -
                              (self.StartFlit() * utils.FLIT_SIZE)) - 1

  def EndBit(self):
    """Returns the bit offset in the end flit.

    0 is the bottom of the flit.
    """
    if self.no_offset:
      return None
    return utils.FLIT_SIZE - (self.EndOffset() -
                              (self.EndFlit() * utils.FLIT_SIZE)) - 1

  def BitWidth(self):
    # Returns the number of bits in the field.
    if self.no_offset:
      return 0
    return self.bit_width

  def Mask(self):
    # Returns a hexadecimal number that can be used as a mask in the flit.
    return '0x%x' %  ((1 << self.bit_width) - 1)

  def SmallerThanType(self):
    """Returns true if the field does not fully fill its type.
    Used for identifying packed fields.
    """
    # TODO(bowdidge): Create separate packed flag for packed fields?
    return self.bit_width < self.type.BitWidth()

  def IsNoOffset(self):
    return self.no_offset

  def CreateSubfields(self):
    """Inserts sub-fields into this field based on the its type.

    For fields that are structures, this code walks the tree of structures
    and creates new sub-fields in this field from the fields of the prototype
    structure.  It sets the offset and size to match the prototype.
    """
    if not self.type.IsRecord():
      # Doesn't have subfields to create.
      return

    if self.type.IsArray() and self.type.ArraySize() == 0:
      # Subfields shouldn't be created because we can't know their
      # positions.
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


class EnumVariable(Declaration):
  # Representation of an enum variable in an enum declaration.

  def __init__(self, name, value):
     # Create an EnumVariable.
     Declaration.__init__(self)
     # name is a string.
     self.name = name
     # value is an integer value for the variable.
     self.value = value
     self.declaration_kind = EnumVariableKind

  def __str__(self):
     return('<EnumVariable: %s = 0x%x>' % self.name, self.value)


class Enum(Declaration):
  # Representation of an enum declaration.

  def __init__(self, name):
    # Create an Enum declaration.
    # name is a string.
    # variables holds the EnumVariables associated with the enum.
    # Multiple enum variables may hold the same value.
    Declaration.__init__(self)
    self.name = name
    self.variables = []
    self.declaration_kind = EnumKind

  def Name(self):
    return self.name

  def BitWidth(self):
    return 0

  def __str__(self):
    return('<Enum %s:\n  %s\n>\n' % (self.name, self.variables))


class FlagSet(Declaration):
  # Representation of an flags declaration.  FlagSet are like enums,
  # but the values are expected to represent bitmasks, and the values
  # are generated as ints rather than as an enum.

  def __init__(self, name):
    # Create an FlagSet declaration.
    # name is a string.
    # variables holds the EnumVariables associated with the enum.
    Declaration.__init__(self)
    self.name = name
    self.variables = []
    self.declaration_kind = FlagSetKind

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


class Struct(Declaration):
  # Representation of a structure.

  def __init__(self, name, is_union):
    """Create a struct declaration.

    if is_union is true, then this is a union rather than a structure.
    """
    Declaration.__init__(self)
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
    self.declaration_kind = StructKind

  def Name(self):
    return self.name

  def Tag(self):
    """Returns the correct token to use when generating a declaration."""
    if self.is_union:
      return 'union'
    return 'struct'

  def NestedStructs(self):
    result = []
    for field in self.fields:
      if field.type.IsRecord():
        struct = field.type.base_type.node
        if struct.inline:
          result.append(struct)
          result += struct.NestedStructs()
    return result

  def MatchingStructInUnionField(self, struct_in_union):
    """Returns (accessor expr, field) for an instance of a structure
    of the provided type inside a union inside the current structure.
    """
    for field in self.AllFields():
      if field.type.IsRecord() and field.type.base_type.node.is_union:
        union = field.type.base_type.node
        for union_field in union.AllFields():
          if (union_field.type.IsRecord() and
              union_field.type.base_type.node == struct_in_union):
            return (field.name + '.' + union_field.name + '.', union_field)
    return ('', None)

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
    """Return a map of (flit, fields) for all fields in the structure."""
    flit_field_map = {}
    fields_with_offsets = [f for f in self.fields if not f.IsNoOffset()]

    for field in fields_with_offsets:
      item = flit_field_map.get(field.StartFlit(), [])
      item.append(field)
      flit_field_map[field.StartFlit()] = item
    return flit_field_map

  def ContainsUnion(self):
    """Returns union in this struct, or None if no unions exist."""
    if self.is_union:
      return self

    for f in self.fields:
      if f.type.IsRecord():
        struct = f.type.base_type.node
        the_union = struct.ContainsUnion()
        if the_union:
          return the_union
    return None


class Document:
  # Representation of an entire generated header specification.
  def __init__(self):
    # All structures, enums, and flagsets defined in file.
    self.declarations_raw = []


    # Original filename containing the specifications.
    self.filename = None

  def Declarations(self):
    return self.declarations_raw

  def Structs(self):
    return [d for d in self.declarations_raw if d.declaration_kind == StructKind]

  def Enums(self):
    return [d for d in self.declarations_raw if d.declaration_kind == EnumKind]

  def Flagsets(self):
    return [d for d in self.declarations_raw if d.declaration_kind == FlagSetKind]

  def AddStruct(self, s):
    self.declarations_raw.append(s)

  def AddEnum(self, e):
    self.declarations_raw.append(e)

  def AddFlagSet(self, f):
    self.declarations_raw.append(f)

  def __str__(self):
    return('<Document>')


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
