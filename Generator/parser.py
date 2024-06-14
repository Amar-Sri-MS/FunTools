#
# Code for parsing generator files.
#
# Copyright Fungible Inc. 2017.

import os
import random
import re
import string
import sys
import utils

# Fake value for width of field, used when we can't define the value
# correctly on creation.
FAKE_WIDTH = 8675309

class BaseType:
  """Represents a base type name without qualifications.

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

    # True if type is a scalar that specifies an explicit endianness.
    # Values of endian-explicit types should not be byte-swapped.
    self.has_endianness = node is None and name in builtin_endian_type_widths

  def PrintFormat(self):
    """Returns format string for printf appropriate for the value.

    Undefined for non-POD types.
    """
    if self.node:
      return 'PrintFormat undefined for non-integer values.'
    if self.bit_width > 32:
      return 'llu'
    return 'u'

  def Name(self):
    """Returns the name of the type."""
    return self.name

  def BitWidth(self):
    """Returns the width of the base type itself."""
    return self.bit_width

  def IsScalar(self):
      """Returns True for scalar types, False for structs/unions."""
      return self.node is None

  def Alignment(self):
    """Returns expected alignment of objects of this type in bits.

    Default alignment isn't defined by C; it's a property of the compiler.
    The Generator thinks about alignment because a field matching the
    alignment and size of the specified type can be represented as a
    native field in that structure, while an unaligned or differently-sized
    type must be manipulated via bit shifting in a larger container.
    """
    if self.node is not None:
      # Generally, compilers want to place fields at the alignment of the largest field.
      if len(self.node.fields) == 0:
        return 0
      return max([f.type.Alignment() for f in self.node.fields])
    # Assume remaining fields are aligned at same as bit size.
    return self.bit_width

  def IsSameBaseType(self, other):
    if other is None:
      print('Comparing base type against None')
      return False

    if self.name != other.name:
       return False

    if self.bit_width != other.bit_width:
        return False
    if self.node or other.node:
      if self.node.name != other.node.name:
          return False
    return True


# Types that specify a specific endianness.
# These types are used to mark fields that should be kept in their
# preferred byte-order.
# Available both in Linux and FunOS.
builtin_endian_type_widths = {
  '__le16': 16,
  '__le32': 32,
  '__le64': 64,
  '__be16': 16,
  '__be32': 32,
  '__be64': 64
}

# Width of all known types.  Structures are added to this
# dictionary during execution.
# Only these types are allowed in gen files.
builtin_type_widths = {
  # width of type in bits.
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
  'int64_t' : 64,
  'uint128_t': 128,
}

# In Linux mode, only these unsigned fixed-width type names are allowed.
# They will be replaced with the __le* / __be* / __u* types.
builtin_linux_type_widths = {
  'uint8_t': 8,
  'uint16_t': 16,
  'uint32_t': 32,
  'uint64_t': 64
}

# Type names to use on Linux when endianness is unspecified.
# Used for function arguments.
# Endian-specific type names will remain unchanged.
no_endian_map = {
  'uint8_t' : '__u8',
  'uint16_t' : '__u16',
  'uint32_t' : '__u32',
  'uint64_t' : '__u64'
}

# Type names to use for DPUs that may have either endianness at Linux codegen time.
linux_any_endian_map = {
  'uint8_t' : '__u8',
  'uint16_t' : '__dpu16',
  'uint32_t' : '__dpu32',
  'uint64_t' : '__dpu64'
}

# Type names to use for DPUs that may have native endianness at FunOS codegen time.
dpu_no_endian_map = {
  'uint8_t' : 'uint8_t',
  'uint16_t' : 'uint16_t',
  'uint32_t' : 'uint32_t',
  'uint64_t' : 'uint64_t'
}

# Type names to use in Linux for BE DPUs
linux_be_endian_map = {
  'uint8_t' : '__u8',
  'uint16_t' : '__be16',
  'uint32_t' : '__be32',
  'uint64_t' : '__be64'
}

# Type names to use in FunOS for BE DPUs
dpu_be_endian_map = {
  'uint16_t' : '__be16',
  'uint32_t' : '__be32',
  'uint64_t' : '__be64'
}

# Type names to use in Linux for LE DPUs
linux_le_endian_map = {
  'uint8_t' : '__u8',
  'uint16_t' : '__le16',
  'uint32_t' : '__le32',
  'uint64_t' : '__le64'
}

# Type names to use in FunOS for LE DPUs
dpu_le_endian_map = {
  'uint16_t' : '__le16',
  'uint32_t' : '__le32',
  'uint64_t' : '__le64'
}

dpu_endian_map = None

def SetDPUEndianMap(dpu_endianness, linux_type):
    """Based on the targeted DPU endianness select the endianness map."""
    global dpu_endian_map

    if dpu_endianness == 'Any':
        if linux_type:
          dpu_endian_map = linux_any_endian_map
        else:
          dpu_endian_map = dpu_no_endian_map
    elif dpu_endianness == 'BE':
        if linux_type:
          dpu_endian_map = linux_be_endian_map
        else:
          dpu_endian_map = dpu_be_endian_map
    elif dpu_endianness == 'LE':
        if linux_type:
          dpu_endian_map = linux_le_endian_map
        else:
          dpu_endian_map = dpu_le_endian_map
    else:
        raise ValueError('unknown DPU endianness %s' % dpu_endianness)


def NoStraddle(width, offset, bound):
  """Returns true if a field at (offset, offset+width) doesn't cross
  a boundary at bound intervals.

  Used for determining appropriate types for fields not aligned on obvious
  boundaries.
  """
  return offset // bound == (offset + width - 1) // bound


def DefaultTypeForWidth(width, offset):
  """Chooses a default type for a field based on the width and current offset.

  The offset is used to bump the field to a larger type if it is not
  aligned correctly.
  """
  # TODO(bowdidge): Currently, field packing requires all fields
  # that would be packed together must share the same type.  We should
  # either make sure the chosen type allows packing, or change how we decide
  # whether to pack fields.
  if width <= 8 and NoStraddle(width, offset, 8):
    return TypeForName('uint8_t')
  elif width <= 16 and NoStraddle(width, offset, 16):
    return TypeForName('uint16_t')
  elif width <= 32 and NoStraddle(width, offset, 32):
    return TypeForName('uint32_t')
  elif width <= 64 and NoStraddle(width, offset, 64):
    return TypeForName('uint64_t')
  elif width <= 128 and NoStraddle(width, offset, 128):
    return TypeForName('uint128_t')
  elif width % 8 == 0:
    # Not quite correct- can't align array at less than 8 bit boundary.
    return ArrayTypeForName('unsigned char', width // 8)
  else:
    return TypeForName('uint64_t')

def DefaultTypeMap(linux_type=False):
  """Returns the default type map to use for the given header file.

  The type map allows us to replace standard C types (uint64_t, uint32_t, ...)
  with system-specific types.

  linux_type is true if the header wants to generate Linux kernel's fixed
  size types. (__u16, ...)

  """
  if linux_type:
    type_map = dict(builtin_linux_type_widths)
  else:
    type_map = dict(builtin_type_widths)
  type_map.update(builtin_endian_type_widths)
  return type_map


def BaseTypeForName(name, linux_type=False):
  """Returns a BaseType for the builtin type with the provided name.

  If linux_type is true, then substitute Linux type names for appropriate
  C unsigned types.
  """
  type_map = DefaultTypeMap(linux_type)

  if name not in type_map:
    return None

  return BaseType(name, type_map[name])


def TypeForName(name, linux_type=False):
  """Returns a type for the builtin type with the provided name.

  If linux_type is true, substitute linux types.
  """
  base_type = BaseTypeForName(name, linux_type)
  if base_type is None:
    return None

  return Type(base_type)


def ArrayTypeForName(name, element_count, linux_type=False):
  """Returns a type for an array of the given base type and element count.

  name is the string name of the type name.
  element_count is the size of the array.
  linux_type is true if the type should be one of the Linux types.
  """
  base_type = BaseTypeForName(name, linux_type)
  if base_type is None:
    return None

  return Type(base_type, element_count)


def RecordTypeForStruct(the_struct):
  """Returns a type for a field that would hold a single struct."""
  base_type = BaseType(the_struct.name, 0, the_struct)
  return Type(base_type)


def RecordArrayTypeForStruct(the_struct, element_count):
  """Returns a type for a field that would hold an array of structs."""
  base_type = BaseType(the_struct.name, 0, the_struct)
  return Type(base_type, element_count)


class Type:
  """Represents C type for a field."""

  def __init__(self, base_type, array_size=None):
    self.base_type = base_type
    # Number of elements in the array.
    self.array_size = None
    # Size of the total object in bits.
    self.bit_width = 0
    # True if type represents an array type.
    self.is_array = False
    # True for scalar types
    self.scalar = False

    if array_size is not None:
      self.is_array = True
      self.array_size = array_size

    if self.is_array:
      self.alignment = base_type.Alignment()
      self.bit_width = base_type.BitWidth() * array_size
    elif self.IsRecord():
      # Correct?
      self.alignment = base_type.Alignment()
      self.bit_width = base_type.BitWidth()
    else:
      self.scalar = True
      self.alignment = base_type.Alignment()
      # Integer types generally align to size - 8 bit values
      # aligning to bytes, 16 bit to nibble, 32 bits to 32 bits, etc.
      # TODO(bowdidge): Revisit and match ABIs.
      self.bit_width = self.alignment

  def CastString(self, linux_type=False, dpu_endian=False):
    """Returns a string casting something to this type.
    Used in templates with {{x.type|as_cast}}
    """
    return '(%s)' % self.ParameterTypeName(linux_type, dpu_endian)

  def IsNoSwap(self):
      """Returns true if type has endianness and shouldn't be swapped."""
      # TODO(bowdidge): If we supported pointers, this would get interesting.
      return self.base_type.has_endianness

  def IsArray(self):
    """Returns true if the type is an array type."""
    return self.is_array

  def IsRecord(self):
    """Returns true if the type contains other fields (union or struct)

    Records can still be arrays too.
    """
    return self.base_type.node is not None

  def IsUnion(self):
    return self.base_type.node is not None and self.base_type.node.is_union

  def IsScalar(self):
    """Returns true if the type is a scalar, builtin type."""
    # TODO(bowdidge): Should uint128_t count as scalar or not?
    return self.scalar

  def IsSwappable(self):
      """Returns True if the type is subject to byte-swapping.
      This is the case for scalar multi-byte fields that do not specify
      their endianness.
      """
      return self.bit_width > 8 and self.IsScalar() and not self.IsNoSwap()

  def BaseName(self):
    """Returns base type name without array and other modifiers."""
    return self.base_type.Name()

  def DeclarationName(self, linux_type=False, dpu_endian=False, force_be=False):
    """Returns a string for the declaration.

    If linux_type is true, use Linux's preferred type names.
    If dpu_endian is False, use an endian-agnostic type, i.e., host-endian.
    If dpu_endian is True, use a DPU-endian type.
    """
    if self.base_type.node:
      return self.base_type.node.Tag() + ' ' + self.base_type.name

    if self.IsNoSwap():
      # Already have an endianness?  Use the existing type name.
      return self.base_type.name
    elif force_be is True:
      if linux_type is True:
        return linux_be_endian_map[self.base_type.name]
      elif self.base_type.name in dpu_be_endian_map:
        return dpu_be_endian_map[self.base_type.name]
    elif dpu_endian is False:
      if linux_type is True:
        return no_endian_map[self.base_type.name]
      else:
        return self.base_type.name
    elif dpu_endian is True:
      if self.base_type.name in dpu_endian_map:
        return dpu_endian_map[self.base_type.name]
    elif linux_type:
      raise ValueError('bad dpu_endian value %s' % (dpu_endian  ))

    return self.base_type.Name()

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

  def ParameterTypeName(self, linux_type=False, endian=True):
    """Returns type name as function parameter type."""
    if self.is_array:
      if self.array_size == 0 and linux_type:
        return '%s[]' % self.DeclarationName(linux_type, endian)
      else:
        return '%s[%d]' % (self.DeclarationName(linux_type, endian),
                           self.array_size)
    else:
      return self.DeclarationName(linux_type, endian)

  def Alignment(self):
    """Returns natural alignment for the type in bits."""
    if self.alignment == 0:
      return utils.FLIT_SIZE // 8
    return self.alignment

  def BitWidth(self):
    """Returns width of type in bits."""
    return self.bit_width

  def IsSameType(self, other_type):
    """Returns True if other_type is same exact type as this."""
    if other_type is None:
      print('Invalid comparison against null type')
      return False

    if not self.base_type.IsSameBaseType(other_type.base_type):
        return False
    if self.is_array != other_type.is_array:
      return False
    if self.is_array:
      return self.array_size == other_type.array_size
    return True

  def __str__(self):
    if self.is_array:
      return '<Type: %s[%d]>' % (self.base_type.Name(), self.array_size)
    else:
      return '<Type: %s>' % (self.base_type.Name())


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
    self.filename = None
    self.line_number = 0

    self.is_enum = False
    self.is_flagset = False
    self.is_const = False
    self.is_struct = False
    self.is_function = False
    self.is_macro = False
    self.is_field = False

  def DefinitionString(self, linux=False):
    """Returns a text string that is a valid declaration.
    For structures, this prints all the fields in the struct.
    """
    return '/* DefinitionString unimplemented for %s. */' % self

  def DeclarationString(self, linux_type=False, dpu_endian=False):
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
    self.is_macro = True

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
    self.is_function = True


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

  # When name mangling is enabled names are modified by applying a lambda.
  mangle_func = lambda self, x: x

  # whether to only mangle structs marked "_MANGLE"
  minmangle: bool = False


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
    self.mangled_name = self.mangle_func(name)
    # String name of the C type, or a generic type for signed-ness.
    self.type = type

    # True if the field doesn't actually represent a specific bit pattern.
    # Used for variable length arrays.
    self.no_offset = False

    # Bit offset from top of first word.
    self.offset_start = offset_start
    # Width of field in bits, or None if field doesn't have an offset.
    self.bit_width = bit_width

    # True if the field the same width as the type.
    self.is_natural_width = False
    if self.type.IsRecord():
      self.is_natural_width = True
    else:
      self.is_natural_width = self.type.bit_width == self.bit_width

    # Does this field need to be swapped when converting from a different
    # endian processor? Yes, if it isn't a bitfield and its type has the
    # requirement.
    self.swappable = type is not None and type.IsSwappable() and self.is_natural_width

    # Minimum and maximum value allowed in the field.
    # TODO(bowdidge): Handle signed types.
    self.min_value = 0
    self.max_value = 0
    self.mask = '/* undefined */'

    # Fixed value, if field is always set to the same value.
    # Value is a string - either an integer value or an enum value.
    # Set fixed value in key comment of form 'fixed_value: xxx'
    self.fixed_value = None

    if self.bit_width >= 0:
      self.max_value = (1 << self.bit_width) - 1
      self.mask = '0x%x' % ((1 << self.bit_width) - 1)

    self.crosses_flit = False
    # Fields that have been packed in this field.
    self.packed_fields = []
    # True if field was explicitly defined to be less than its natural size.
    self.is_bitfield = self.is_natural_width

    # True if field appears to be a reserved field that doesn't need to be
    # initialized or manipulated.
    self.is_reserved = (name.startswith('reserved') or
                        name.startswith('rsvd') or
                        name.startswith('unused'))

    # Endianness of the field, if it's a fixed endianness.
    self.endian = None
    type_name = type.TypeName() if type is not None else ''
    if type_name.startswith('__le'):
      self.endian = type_name[2:]
    elif type_name.startswith('__be'):
      self.endian = type_name[2:]

    # Fields for a composite object such as a struct or union.
    self.subfields = []
    self.is_field = True
    # None if a top-level field, or the packed field holding this field.
    self.packed_field = None
    self.parent_struct = None

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

  @classmethod
  def SetMangling(cls, func):
    # lambdas on classes weirdly demand a self argument whereas
    # lambdas on instances do not.
    cls.mangle_func = lambda self, x: func(x)

  @classmethod
  def SetMinMangle(cls, minmangle):
    cls.minmangle = minmangle

  def fields_to_set(self):
    """Returns a list of packed fields (fields actually holding multiple
    other fields).

    This method determines which fields get packed accessors.
    """
    return [x for x in self.packed_fields if not x.is_reserved]
  
  def IsAlwaysMangled(self):
    """Returns True if the field is part of a structure whose members'
    names are mangled, forcing use of accessors.
    """
    # walk the tree to find if a parent is marked for mangle
    p = self.parent_struct
    while p is not None:
      if p.always_mangle:
        return True

      p = p.parent_struct

    return False

  def IsAlwaysBe(self):
    """Returns True if the field is part of a structure whose multi-byte members
    are always BE.
    """
    # walk the tree to find if a parent is marked for BE
    p = self.parent_struct
    while p is not None:
      if p.always_be:
        return True

      p = p.parent_struct

    return False

  def Name(self):
    return self.name

  def MangledName(self):
    # single-byte fields are not mangled, neither are non-swappable (explicit endian) reserved fields.
    if (self.is_reserved or self.type.is_array) and (not self.swappable or (self.type.bit_width == 8 and self.is_natural_width)):
      return self.name

    if self.minmangle and not self.IsAlwaysMangled():
        # use an unmangled name
        return self.name
    else:
      # mangle all the names (or none if not mangling)
      return self.mangled_name

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
    return self.StartOffset() // utils.FLIT_SIZE

  def EndFlit(self):
    """Returns the flit in the container holding the end of this field."""
    if self.no_offset:
      return None
    return (self.StartOffset() + self.BitWidth() - 1) // utils.FLIT_SIZE

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
      return self.EndBit() % utils.FLIT_SIZE
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

  def DeclarationString(self, linux_type=False, dpu_endian=False):
    """Returns a string representing the declaration for variable to set field."""
    if self.type.IsRecord() and self.type.base_type.node.inline:
      return '%s {\n} %s;' % (self.type.DeclarationName(linux_type,
                                                        dpu_endian),
                                 self.name)

    if self.type.IsArray():
      if self.type.array_size == 0 and linux_type:
        return '%s %s[]' % (self.type.DeclarationName(linux_type, dpu_endian))
      else:
        return "%s %s[%d]" % (self.type.DeclarationName(linux_type,
                                                        dpu_endian),
                              self.name,
                              self.type.array_size)

    return "%s %s" % (self.type.ParameterTypeName(linux_type,
                                                  dpu_endian), self.name)

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
        new_subfield = Field(proto_field.Name(), proto_field.Type(), 0, 0)
      else:
        new_subfield = Field(proto_field.Name(), proto_field.Type(),
                             self.StartOffset() + proto_field.StartOffset(),
                             proto_field.BitWidth())
      # TODO(bowdidge): Consider an explicit copy method.
      new_subfield.key_comment = proto_field.key_comment
      new_subfield.body_comment = proto_field.body_comment
      new_subfield.tail_comment = proto_field.tail_comment
      new_subfield.generator_comment = proto_field.generator_comment
      new_subfield.filename = proto_field.filename
      new_subfield.line_number = proto_field.line_number
      new_subfield.crosses_flit = proto_field.crosses_flit
      new_subfield.is_bitfield = proto_field.is_bitfield
      new_subfield.no_offset = proto_field.no_offset


      self.subfields.append(new_subfield)
      if proto_field.type.IsRecord():
        new_subfield.CreateSubfields()


  def DefinitionString(self, linux_type=False, dpu_endian=False, mangled=True):
    """Pretty-print a field in a structure or union.  Returns string."""
    str = ''
    field_type = self.Type()

    # Only use big-endian types in structures that are always mangled if minmangle is set.
    type_name = field_type.DeclarationName(linux_type, dpu_endian, self.IsAlwaysBe())

    name = self.MangledName() if mangled and not field_type.IsRecord() else self.name

    if field_type.IsRecord():
      struct = field_type.base_type.node
      if struct.inline:
        type_name = struct.DefinitionString(linux_type, dpu_endian)

    if self.generator_comment is not None:
      str += utils.AsComment(self.generator_comment) + '\n'

    if self.body_comment is not None:
      # TODO(bowdidge): Break long comment.
      str += utils.AsComment(self.body_comment) + '\n'

    key_comment = ''
    if self.key_comment is not None:
      key_comment = ' ' + utils.AsComment(self.key_comment)

    if self.type.IsArray():
      if self.type.ArraySize() == 0:
        str += '%s %s[];%s\n' % (type_name,
                                 name,
                                 key_comment)
      else:
        str += '%s %s[%d];%s\n' % (type_name,
                                   name,
                                   self.type.ArraySize(),
                                   key_comment)
    else:
      var_width = self.BitWidth()
      type_width = self.type.BitWidth()

      var_bits = ''
      if self.type.IsScalar() and type_width != var_width:
        var_bits = ':%d' % var_width
      str += '%s %s%s;%s\n' % (type_name, name, var_bits, key_comment)

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
     self.is_enum_variable = True

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
    self.is_enum = True
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
    """Width of an enum is the number of bits needed for all values."""
    return utils.MaxBit(self.last_value)

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
    self.is_flagset = True
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


class Const(Declaration):
  # Representation of an Const declaration indicating a group of related
  # constant declarations.  The individual variables will be instantiated
  # as separate global variables.  The declaration name should only appear
  # in comments.

  def __init__(self, name):
    # Create an Const declaration.
    # name is a string.
    # variables holds the EnumVariables associated with the enum.
    Declaration.__init__(self)
    self.name = name
    self.variables = []
    self.is_const = True
    # Any integer value is legal.
    self.max_value = sys.maxsize

  def AddVariable(self, var):
    """Adds a new flagset variable to the flagset."""
    self.variables.append(var)

  def Name(self):
    return self.name

  def BitWidth(self):
    return 0

  def VariablesWithNames(self):
    """Returns set of variables in this container."""
    return self.variables

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
    # TODO(bowdidge): Change fields to all start at 0, rather than matching
    # how they appeared in the gen file.
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
    self.is_struct = True
    self.always_mangle = False
    self.always_be = False

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

  def HasFieldWithName(self, name):
    """Returns true if there's already a field with that name in struct."""
    for f in self.fields:
      if f.Name() == name:
        return True
    return False

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
      if field.type.IsUnion():
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
      start_offset = min([f.StartOffset() for f in fields_with_offsets])
      end_offset = max([f.EndOffset() for f in fields_with_offsets])
      return end_offset - start_offset + 1

    # The first field won't start at zero.  Check the struct's start
    # offset to understand the real zero point.
    first_field = fields_with_offsets[0]
    last_field = fields_with_offsets[-1]
    start_offset = first_field.StartOffset()
    end_offset = last_field.EndOffset()
    return end_offset - start_offset + 1

  def StartOffset(self):
    """Returns beginning offset for structure."""
    if not self.fields:
      return 0

    # StartOffset is None for zero dimension arrays.
    min_offsets = [f.StartOffset() for f in self.fields
                   if f.StartOffset() is not None]
    if min_offsets:
      return min(min_offsets)
    return 0

  def EndOffset(self):
    """Returns furthest bit range for struct.

    Ignores variable length fields.
    """
    if not self.fields:
      return 0

    return max([f.EndOffset() for f in self.fields
                if f.EndOffset() is not None])

  def StartFlit(self):
    """Returns the flit in the container holding the start of this field."""
    if no_offset:
        return 0
    return self.StartOffset() // utils.FLIT_SIZE

  def EndFlit(self):
    """Returns the flit in the container holding the end of this field."""
    if no_offset:
        return 0
    return (self.StartOffset() + self.BitWidth() - 1) // utils.FLIT_SIZE


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

  def DefinitionString(self, linux_type=False, dpu_endian=False):
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

      str += utils.Indent(field.DefinitionString(linux_type, dpu_endian), 2)

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

  def sub_fields(self):
    """Returns set of fields in structure that are other structures."""
    return [x for x in self.fields if x.type.IsRecord() and not
            x.type.IsArray()]



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
    return [d for d in self.declarations_raw if d.is_struct]

  def StructWithName(self, name):
    """Returns the structure with the requested name."""
    for d in self.declarations_raw:
      if d.is_struct and d.name == name:
        return d
    return None

  def Enums(self):
    return [d for d in self.declarations_raw if d.is_enum]

  def EnumWithName(self, name):
    """Returns the enum with the requested name,"""
    for d in self.declarations_raw:
      if d.is_enum and d.name == name:
        return d
    return None

  def Flagsets(self):
    return [d for d in self.declarations_raw if d.is_flagset]

  def Consts(self):
    return [d for d in self.declarations_raw if d.is_const]

  def AddStruct(self, s):
    self.declarations_raw.append(s)

  def AddEnum(self, e):
    self.declarations_raw.append(e)

  def AddFlagSet(self, f):
    self.declarations_raw.append(f)

  def AddConst(self, c):
    self.declarations_raw.append(c)

  def __str__(self):
    return('<Document>')


class Checker:
  """Check alignment, location, etc of the defined structures."""

  def __init__(self):
    # Errors noted.
    self.errors = []
    self.current_document = None

  def AddError(self, node, msg):
    if node.filename:
      location = '%s:%d: ' % (node.filename, node.line_number)
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
      self.VisitField(field)

      if field != the_struct.fields[-1]:
        if field.IsNoOffset():
          self.AddError(field, 'field "%s" is an array of zero size, but is not the last field.')


    fields_with_offsets = [f for f in the_struct.fields if not f.IsNoOffset()]

    if len(fields_with_offsets) == 0:
      return

    last_start_offset = fields_with_offsets[0].StartOffset() - 1
    last_end_offset = fields_with_offsets[0].StartOffset() - 1

    if the_struct.is_union:
      if len(fields_with_offsets) > 1:
        # Check all items in the union have the same start bit.
        for i in range(1, len(fields_with_offsets)):
          prev_field = fields_with_offsets[i-1]
          field = fields_with_offsets[i]
          if (prev_field.StartFlit() != field.StartFlit() or
              prev_field.StartBit() != field.StartBit()):
            self.AddError(field, 'Field "%s" in union does not '
                          'match start bit of previous field "%s": '
                          'flit %d bit %d vs flit %d bit %d' % (
                field.name, prev_field.name,
                field.StartFlit(), field.StartBit(),
                prev_field.StartFlit(), prev_field.StartBit()))

    # Check each field is adjacent to the previous.
    for field in fields_with_offsets:
      start_offset = field.StartOffset()
      end_offset = field.EndOffset()

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
    if the_field.SmallerThanType() and the_field.type.IsNoSwap():
      self.AddError(the_field,
                    'field with endian-specific type %s '
                    'cannot be a bitfield' % the_field.type.BaseName())


# Enums used to indicate the kind of object being processed.
# Used on the stack.
GenParserStateStruct = 1
GenParserTopLevel = 3
GenParserStateEnum = 4
GenParserStateFlagSet = 5
GenParserStateConst = 6


class GenParser:
  # Parses a generated header document and creates the internal data structure
  # describing the file.

  def __init__(self, linux_type=False, dpu_endianness = 'Any', mangle_fields = "", mangle_suffix = "x", minmangle = False):
    # Create a GenParser.
    # current_document is the top level object.
    self.current_document = Document()
    # stack is a list of (state, object) pairs showing all objects
    # currently being parsed.  New containers (enum, struct, union) are put in the
    # last object.
    self.stack = [(GenParserTopLevel, self.current_document)]
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

    if mangle_fields == "mangle":
      Field.SetMangling(lambda name: name + '_' + mangle_suffix)
    elif mangle_fields == "flexmangle":
      Field.SetMangling(lambda name: f"_MANGLE({name})")
    else:
      Field.SetMangling(lambda name: name)

    Field.SetMinMangle(minmangle)

    self.base_types = {}
    type_map = DefaultTypeMap(linux_type)
    for name in type_map:
      self.base_types[name] = BaseType(name, type_map[name])

    SetDPUEndianMap(dpu_endianness, linux_type)

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
    if state not in [GenParserTopLevel, GenParserStateStruct]:
      self.AddError('Struct starting in inappropriate context')

      return None

    # Struct syntax is STRUCT struct-identifier var-name comment
    match = re.match('STRUCT(_MANGLED)?\s+(\w+)(\s+\w+|)(\s*.*)$', line)

    if not match:
      self.AddError('Invalid STRUCT line: "%s"' % line)
      return None

    mangled = match.group(1) == "_MANGLED"
    identifier = match.group(2)
    variable_name = match.group(3)
    key_comment = match.group(4)
    variable_name = utils.RemoveWhitespace(variable_name)

    if not utils.IsValidCIdentifier(identifier):
      self.AddError(
        'struct name "%s" is not a valid identifier name.' % identifier)

    if variable_name and not utils.IsValidCIdentifier(variable_name):
      self.AddError(
        'variable "%s" is not a valid identifier name.' % variable_name)

    # TODO(bowdidge): Complain about nested structures without a field
    # name.
    if (state == GenParserStateStruct and variable_name and
        containing_object.HasFieldWithName(variable_name)):
      self.AddError(
        'Field with name "%s" already exists in struct "%s"' % (
          variable_name, containing_object.Name()))
      return True

    current_struct = Struct(identifier, False)
    current_struct.filename = self.current_document.filename
    current_struct.line_number = self.current_line
    current_struct.key_comment = self.StripKeyComment(key_comment)
    current_struct.always_mangle = mangled
    current_struct.always_be = mangled and Field.minmangle

    if len(self.current_comment) > 0:
      current_struct.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((GenParserStateStruct, current_struct))

    self.current_document.AddStruct(current_struct)

    # Add the struct to the symbol table.  We don't know
    self.base_types[identifier] = BaseType(identifier, FAKE_WIDTH,
                                           current_struct)

    if state != GenParserTopLevel:
      new_field = Field(variable_name, self.MakeType(identifier), 0, 0)
      new_field.filename = self.current_document.filename
      new_field.line_number = self.current_line

      containing_object.AddField(new_field)
      current_struct.inline = True
      current_struct.parent_struct = containing_object

      # inherit parent mangling
      if (containing_object.always_mangle):
        current_struct.always_mangle = True

      # inherit parent endianness
      if (containing_object.always_be):
        current_struct.always_be = True

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

    current_enum = Enum(name)
    current_enum.filename = self.current_document.filename
    current_enum.line_number = self.current_line
    current_enum.key_comment = self.StripKeyComment(key_comment)

    if len(self.current_comment) > 0:
      current_enum.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((GenParserStateEnum, current_enum))
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
    current_flags = FlagSet(name)
    current_flags.filename = self.current_document.filename
    current_flags.line_number = self.current_line
    current_flags.key_comment = self.StripKeyComment(key_comment)

    if len(self.current_comment) > 0:
      current_flags.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((GenParserStateFlagSet, current_flags))
    self.current_document.AddFlagSet(current_flags)

  def ParseConstStart(self, line):
    # Handle a CONST directive defining a set of global constants.
    state, containing_struct = self.stack[len(self.stack)-1]
    match = re.match('CONST\s+(\w+)(.*)$', line)
    if match is None:
      self.AddError('Invalid const start line: "%s"' % line)
      return

    name = match.group(1)
    key_comment = match.group(2)

    if not utils.IsValidCIdentifier(name):
      self.AddError('"%s" is not a valid identifier name.' % name)

    name = utils.RemoveWhitespace(name)
    current_const = Const(name)
    current_const.filename = self.current_document.filename
    current_const.line_number = self.current_line
    current_const.key_comment = self.StripKeyComment(key_comment)

    if len(self.current_comment) > 0:
      current_const.body_comment = self.current_comment
    self.current_comment = ''

    self.stack.append((GenParserStateConst, current_const))
    self.current_document.AddConst(current_const)


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
    # TODO(bowdidge): Remember whether value was hex or decimal
    # for better printing.
    new_enum = EnumVariable(var, value)
    new_enum.filename = self.current_document.filename
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
    elif state == GenParserTopLevel:
      return
    elif state in [GenParserStateEnum, GenParserStateFlagSet,
                   GenParserStateConst]:
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

    if not isinstance(current_object, Struct):
      return

    if self.flit_crossing_field:
      self.AddError('Field spec for "%s" too short: expected %d bits, got %d' %
                    (self.flit_crossing_field.name,
                     self.flit_crossing_field.type.BitWidth(),
                     self.flit_crossing_field.type.BitWidth() - self.bits_remaining))

    self.base_types[current_object.Name()].bit_width = current_object.BitWidth()

    self.current_comment = ''

    if state != GenParserTopLevel:
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

    if (state == GenParserStateStruct and variable and
        containing_object.HasFieldWithName(variable)):
      self.AddError(
        'Field with name "%s" already exists in struct "%s"' % (
          variable, containing_object.Name()))
      return True

    current_union = Struct(name, True)
    current_union.filename = self.current_document.filename
    current_union.line_number = self.current_line
    if len(self.current_comment) > 0:
      current_union.body_comment = self.current_comment
    self.current_comment = ''
    self.stack.append((GenParserStateStruct, current_union))
    self.current_document.AddStruct(current_union)

    self.base_types[identifier] = BaseType(identifier, FAKE_WIDTH,
                                           current_union)
    if state != GenParserTopLevel:
      # Inline union.  Define the field.
      new_field = Field(variable, self.MakeType(identifier), 0, 0)
      new_field.current_filename = self.current_document.filename
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
      return Type(base_type, array_size)
    else:
      return Type(base_type)


  def ParseFieldLine(self, line, containing_struct):
    """Parses a likely line describing a field in a structure or union.

    Returns true if the line appears to be a field description.

    Logs any errors when parsing the line.

    A struct line is one of the following

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
        print("Eek, thought %s was a number, but didn't parse!\n" % (
            match.group(5)))
    key_comment = match.group(6)

    if containing_struct.is_union:
      self.AddError('Field "%s" not allowed at location: '
                    'fields cannot occur directly in a union. '
                    'Wrap each in a struct.' % name)
      return True

    if not utils.IsValidCIdentifier(name):
      self.AddError(
        'field name "%s" is not a valid identifier name.' % name)
      return True

    if containing_struct.HasFieldWithName(name):
      self.AddError(
        'Field with name "%s" already exists in struct "%s"' % (
          name, containing_struct.Name()))
      return True

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

    if start_bit < end_bit:
      self.AddError('Start bit %d greater than end bit %d in field %s' %
                    (start_bit, end_bit, name))

    start_offset = flit * 64 + (utils.FLIT_SIZE - start_bit - 1)
    end_offset = flit * 64 + (utils.FLIT_SIZE - end_bit - 1)
    bit_size = end_offset - start_offset + 1
    new_field = Field(name, type, start_offset, bit_size)
    new_field.filename = self.current_document.filename
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

    if key_comment and key_comment.lstrip().startswith('fixed_value:'):
      new_field.fixed_value = key_comment[12:]
      key_comment = ''

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
      elif line.startswith('CONST'):
        self.ParseConstStart(line)
      elif line.startswith('END'):
        self.ParseEnd(line)
      else:
        self.ParseLine(line)
      self.current_line += 1

    if len(self.stack) != 1:
      (last_state, last_object) = self.stack[-1]
      self.AddError('END missing at end of file. "%s" is still open.' %
                    last_object.name)

    if len(self.errors) > 0:
      return self.errors
    return None

