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

  def CastString(self):
    """Returns a string casting something to this type.
    Used in templates with {{x.type|as_cast}}
    """
    return '(%s)' % self.DeclarationType()

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

  def DefinitionString(self):
    """Returns a text string that is a valid declaration.
    For structures, this prints all the fields in the struct.
    """
    return '/* DefinitionString unimplemented for %s. */' % self

  def DeclarationString(self):
    """Returns text string that is valid parameter declaration for decl."""
    return '/* DeclarationString unimplemented for %s. */' % self

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

    # Does this field need to be swapped when converting from a different
    # endian processor?
    self.swappable = type is not None and type.bit_width > 8

    # True if the field doesn't actually represent a specific bit pattern.
    # Used for variable length arrays.
    self.no_offset = False

    # Bit offset from top of first word.
    self.offset_start = offset_start
    self.bit_width = bit_width

    # True if the field the same width as the type.
    self.is_natural_width = False
    if self.type:
      self.is_natural_width = self.type.bit_width == self.bit_width

    # Minimum and maximum value allowed in the field.
    # TODO(bowdidge): Handle signed types.
    self.min_value = 0
    self.max_value = 0
    self.mask = '/* undefined */'

    if self.bit_width >= 0:
      self.max_value = (1 << self.bit_width) - 1
      self.mask = '0x%x' % ((1 << self.bit_width) - 1)

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
    # None if a top-level field, or the packed field holding this field.
    self.packed_field = None
    self.parent_struct = None

    self.is_reserved = (name.startswith('reserved') or 
                        name.startswith('rsvd') or
                        name.startswith('unused'))

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
  def fields_to_set(self):
    """Returns a list of packed fields (fields actually holding multiple
    other fields).

    This method determines which fields get packed accessors.
    """
    return [x for x in self.packed_fields if not x.is_reserved]

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

  def shift(self):
    # TODO(bowdidge): subtract container.
    if not self.packed_field:
      return 0
    min_end_bit = min([f.EndBit() for f in self.packed_field.packed_fields])
    return '%d' % (self.EndBit() - min_end_bit)

  def SmallerThanType(self):
    """Returns true if the field does not fully fill its type.
    Used for identifying packed fields.
    """
    # TODO(bowdidge): Create separate packed flag for packed fields?
    return self.bit_width < self.type.BitWidth()

  def IsNoOffset(self):
    return self.no_offset

  #
  # Helper functions neeeded by templates.
  #

  def init_accessor(self):
    """String to access a field from the likely initial struct argument."""
    if not self.parent_struct or not self.parent_struct.inline:
      return ''
    
    container_base_type = RecordTypeForStruct(self.parent_struct).base_type
    struct_field = self.parent_struct.parent_struct.FieldWithBaseType(container_base_type)

    container_container_base_type = RecordTypeForStruct(self.parent_struct.parent_struct).base_type
    union_field = self.parent_struct.parent_struct.parent_struct.FieldWithBaseType(container_container_base_type)
    return union_field.name + '.' + struct_field.name + '.'

  def IsInitable(self):
    """Returns true if the field should be an argument to an init function,
    or should be initialized in an init function.
    """
    return (not self.is_reserved and not self.type.IsRecord() 
            and not self.type.IsArray())

  def DeclarationString(self):
    """Returns a string representing the declaration for variable to set field."""
    if self.type.IsRecord() and self.type.base_type.node.inline:
      return '%s {\n} %s;' % (self.type.DeclarationName(),
                                 self.name)

    if self.type.IsArray():
      return "%s %s[%d]" % (self.type.DeclarationName(), self.name, self.type.array_size)
    return "%s %s" % (self.type.DeclarationType(), self.name)

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


  def DefinitionString(self):
    """Pretty-print a field in a structure or union.  Returns string."""
    str = ''
    field_type = self.Type()
    type_name = field_type.DeclarationName();

    if field_type.IsRecord():
      struct = field_type.base_type.node
      if struct.inline:
        type_name = struct.DefinitionString()

    if self.generator_comment is not None:
      str += utils.AsComment(self.generator_comment) + '\n'

    if self.body_comment is not None:
      # TODO(bowdidge): Break long comment.
      str += utils.AsComment(self.body_comment) + '\n'

    key_comment = ''
    if self.key_comment is not None:
      key_comment = ' ' + utils.AsComment(self.key_comment)

    if self.type.IsArray():
      str += '%s %s[%d];%s\n' % (type_name,
                                     self.name,
                                     self.type.ArraySize(),
                                     key_comment)
    else:
      var_width = self.BitWidth()
      type_width = self.type.BitWidth()

      var_bits = ''
      if self.type.IsScalar() and type_width != var_width:
        var_bits = ':%d' % var_width
      str += '%s %s%s;%s\n' % (type_name,
                                   self.name, var_bits,
                                   key_comment)

    return str


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
    return('<EnumVariable: %s = 0x%x>' % (self.name, self.value))


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
    self.last_value = 0

  def AddVariable(self, var):
    """Adds a new enum variable to the enum."""
    self.variables.append(var)
    if var.value > self.last_value:
      self.last_value = var.value

  def VariablesWithPlaceholders(self):
    return ''
    
  def Name(self):
    return self.name

  def BitWidth(self):
    return 0

  def NameForValue(self, idx):
    for var in self.variables:
      if var.value == idx:
        return var.name
    return 'undefined'

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
    self.max_value = 0

  def AddVariable(self, var):
    """Adds a new flagset variable to the flagset."""
    self.variables.append(var)
    if var.value > self.max_value:
      self.max_value = var.value

  def Name(self):
    return self.name

  def BitWidth(self):
    return 0

  def VariablesWithNames(self):
    """Returns set of variables which go in power-of-two array."""
    result = []
    for i in range(0, utils.MaxBit(self.max_value)):
      next_value = 1 << i
      found = False
      for var in self.variables:
        if next_value == var.value:
          result.append(var)
          found = True
          break
      if not found:
        fake_var = EnumVariable('undefined', next_value)
        result.append(fake_var)
    return result

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
    if self.is_union:
      self.keyword = 'union'
    else:
      self.keyword = 'struct'

    # True if the struct or union should be drawn inline where it's
    # used.  The inline flag is usually set depending on whether the
    # struct was defined inline in the gen file, or on its own.
    self.inline = False
    self.parent_struct = None
    self.declaration_kind = StructKind

  def FieldWithBaseType(self, base_type):
    """Returns first field with the given type.

    Used for finding structs and unions defined in this struct
    when trying to figure out how to access fields in the nested structures.
    """
    for f in self.fields:
      if f.type.base_type.node:
        if f.type.base_type.node == base_type.node:
          return f
    return None

  def AddField(self, field):
    """Adds a new field to this structure."""
    self.fields.append(field)
    field.parent_struct = self

  def Name(self):
    return self.name

  def Tag(self):
    """Returns the correct token to use when generating a declaration."""
    if self.is_union:
      return 'union'
    return 'struct'

  def MatchingStructInUnionField(self, struct_in_union):
    """Returns (accessor expr, field) for an instance of a structure
    of the provided type inside a union inside the current structure.
    """
    for field in self.FieldsBeforePacking():
      if field.type.IsRecord() and field.type.base_type.node.is_union:
        union = field.type.base_type.node
        for union_field in union.FieldsBeforePacking():
          if (union_field.type.IsRecord() and
              union_field.type.base_type.node == struct_in_union):
            return (field.name + '.' + union_field.name + '.', union_field)
    return ('', None)

  def FieldsBeforePacking(self):
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

  def DeclarationString(self):
    return self.Tag() + ' ' + self.name

  def DefinitionString(self):
    """Generate a structure without the semicolon.

    This routine lets us have one way to print inline and standalone structs.
    """
    str = ''
    if self.key_comment:
      str += utils.AsComment(self.key_comment) + '\n'

    if self.body_comment:
      str += utils.AsComment(self.body_comment) + '\n'

    str += self.Tag() + ' %s {\n' % self.name

    flit_for_last_field = 0
    for field in self.fields:
      # Add blank line between flits.
      if field.StartFlit() != flit_for_last_field:
        str += '\n'

      str += utils.Indent(field.DefinitionString(), 2)

      flit_for_last_field = field.StartFlit()

    if self.tail_comment:
      str += utils.Indent(utils.AsComment(self.tail_comment), 2)

    str += '}'
    return str
  
  #
  # Helpers for templates.
  #

  # When generating code or documentation for structures, we have several
  # different sets of fields that may need to be identified:
  #
  # * fields that represent variables in the struct's generated code.
  #   List in self.fields.
  #
  # * conceptual fields - struct fields before packing.
  #   Get list with self.FieldsBeforePacking()
  #
  # * fields to pass as arguments to an initializer.  May include fields
  #   from an enclosing structure.  May not include fields that can't be
  #   passed easily to a function such as sub-structures or arrays, or
  #   reserved fields.
  #   
  # * fields that need to be initialized in an initializer.  Every field
  #   to be initialized maps to one or more arguments to the initializer.
  #   Ignores arrays, sub-structures, and reserved fields.
  #
  # * fields that will not be initialized in an initializer.  Needed for
  #   printing out what won't be done.
  def init_fields(self):
    """Returns the list of fields that should be set in an init routine.
    
    This should include all packed fields, and may include fields inside
    nested structures.
    """
    arg_list = []
    if self.inline:
      arg_list += [x for x in self.init_struct().fields if x.IsInitable()]
    arg_list += [f for f in self.fields if f.IsInitable()]
    return arg_list
      
  def arg_fields(self):
    """Returns list of fields that should be arguments to an init function.

    May include fields from parent structures if this is an inlined
    structure.  Ignores fields that cannot neatly be passed in an init
    function, such as arrays or nested structures.
    """
    arg_list = []
    
    if self.inline:
      arg_list += [x for x in self.init_struct().FieldsBeforePacking()
                   if x.IsInitable()]
    arg_list += [x for x in self.FieldsBeforePacking() if x.IsInitable()]
    return arg_list

  def non_arg_fields(self):
    """Returns list of fields in the structure that will not be initialized
    in an init routine.

    Used for generating documentation.
    """
    return [x for x in self.FieldsBeforePacking() if not x.IsInitable()]

  def init_struct(self):
    """Returns the type of the self argument when initializing this
    structure.

    If the structure is inlined in another, then the init struct
    container.
    """
    if not self.inline:
      return self

    parent = self.parent_struct

    while parent.keyword == 'union' and parent.parent_struct != None:
      parent = parent.parent_struct
    return parent

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
