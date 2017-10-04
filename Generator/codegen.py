#!/usr/bin/python
#
# Code related to generating C headers and sources.
#
# Robert Bowdidge, June 22, 2017
# Copyright Fungible Inc. 2017.

import os

import generator
import parser
import utils

# TODO(bowdidge): Remove CodeGenerator after switching HTML generation to
# templates.
class CodeGenerator:
  """Generates helper functions for manipulating structures."""
  def __init__(self, options):
    self.generate_json = 'json' in options

  def VisitDocument(self, doc):
    for struct in doc.Structs():
      self.VisitStruct(struct)
    for enum in doc.Enums():
      self.VisitEnum(enum)

  def VisitEnum(self, enum):
    # Pretty print an enum declaration.  Returns enum as string.
    decl = 'extern const char *%s_names[];\n\n' % enum.name.lower()
    defn = 'const char *%s_names[] = {\n' % enum.name.lower()
    next_value = 0
    for enum_variable in enum.variables:
      current_value = enum_variable.value
      while (next_value < current_value):
        defn += '\t"undefined",  /* 0x%x */\n' % next_value
        next_value += 1
      defn += '\t"%s",  /* 0x%x */\n' % (enum_variable.name,
                                            enum_variable.value)
      next_value = current_value + 1
    defn += '};\n'

    fun = parser.Function(decl, defn,
                          'Human-readable strings for enum values in %s.' %
                          enum.name)
    enum.functions.append(fun)

  def InitializerName(self, struct_name):
      """Returns name for the structure initialization function."""
      return struct_name + "_init"

  def JSONInitializerName(self, struct_name):
      """Returns name for the structure initialization function."""
      return struct_name + "_json_init"

  def GenerateMacrosForPackedField(self, the_struct, field):
    """Creates macros to access all the bit fields we removed.
    the_struct: structure containing the fields that was removed.
    field: field combining the contents of the former fields.
    """
    min_end_bit = min([f.EndBit() for f in field.packed_fields])

    for old_field in field.packed_fields:
      # No point in creating macros for fields that shouldn't be accessed.
      if old_field.is_reserved:
        continue

      packed_type_name = field.Type().TypeName()
      ident = utils.AsUppercaseMacro('%s_%s' % (the_struct.name,
                                                         old_field.name))
      shift_name = '%s_S' % ident
      shift = '#define %s %s' % (shift_name, old_field.EndBit() - min_end_bit)
      mask_name = '%s_M' % ident
      mask = '#define %s %s' % (mask_name, old_field.mask)
      value_name = '%s_P' % ident
      value = '#define %s(x) (((%s) x) << %s)' % (value_name, packed_type_name,
                                                  shift_name)
      get_name = '%s_G' % ident
      get = '#define %s(x) (((x) >> %s) & %s)' % (get_name, shift_name, mask_name)
      zero_name = '%s_Z' % ident
      zero = '#define %s (~(((%s) %s) << %s))' % (zero_name, packed_type_name,
                                                     mask_name, shift_name)

      
      value_comment = 'Shifts value to place in packed field "%s" in "%s.%s".' % (
        old_field.name, the_struct.name, field.name)

      get_comment = 'Returns value for packed field %s in "%s.%s".' % (
        old_field.name, the_struct.name, field.name)

      offset_comment = 'Offset of field "%s" in packed field "%s.%s"' % (
        old_field.name, the_struct.name, field.name)

      mask_comment = 'Mask to extract field "%s" from packed field "%s.%s"' % (
        old_field.name, the_struct.name, field.name)

      zero_comment = 'Zero out field "%s" in packed field "%s.%s".' % (
        old_field.name, the_struct.name, field.name)

      the_struct.macros.append(parser.Macro(shift_name, shift, offset_comment))
      the_struct.macros.append(parser.Macro(mask_name, mask, mask_comment))
      the_struct.macros.append(parser.Macro(value_name, value, value_comment))
      the_struct.macros.append(parser.Macro(get_name, get, get_comment))
      the_struct.macros.append(parser.Macro(zero_name, zero, zero_comment))

  def GenerateInitializer(self, the_struct, field, accessor_prefix):
    """Returns a C statement initializing the named variable.

    Assumes that variables with the same name as the field contain initial
    values.
    The variable set should be the packed field; the variables providing the
    values are unpacked.
    """
    if len(field.packed_fields) == 0:
        return '\ts->%s%s = %s;' % (accessor_prefix, field.name, field.name)

    packed_inits = []
    for packed_field in field.packed_fields:
      if packed_field.is_reserved:
        continue
      ident = utils.AsUppercaseMacro('%s_%s' % (the_struct.name,
                                                         packed_field.name))
      packed_inits.append('%s_P(%s)' % (ident, packed_field.name))
    return '\ts->%s%s = %s;' % (accessor_prefix, field.name,
                                ' | '.join(packed_inits))

  def GenerateInitRoutine(self, the_struct, struct_in_union):
    """Generate an initialization function for the named structure.
    If struct_in_union is not None and represents a structure inside
    a union in the_struct, then the initializer created is for that
    version of the structure.

    The function takes all non-reserved scalar fields as arguments, test
    that any bitfields are valid, and sets the fields of the referenced
    structure.

    Arguments:
      the_struct (Struct) is the structure owning the init routine, used to
      find all its fields.

      struct_in_union indicates the init should be customized to include
      fields only in the union.

    Returns:
      (declaration string, definition string) pair.

    Arguments to the Init function are unpacked fields, values set in the
    field are packed.
    """
    # All non-packed fields.  Will become arguments.
    all_fields = []

    # List of arguments to the function.
    arg_list = []

    # List of statements validating size of inputs.
    validates = []

    # List of statements initializing fields of structure.
    inits = []

    # All C code to validate field inputs.
    validate_block = ''

    function_name = self.InitializerName(the_struct.name)
    if struct_in_union:
      function_name = self.InitializerName(struct_in_union.name)

    # First argument is always a pointer to the structure being initialized.
    arg_list.append('struct %s *s' % the_struct.name)

    # Pass in all non-packed fields.
    for field in the_struct.FieldsBeforePacking():
      if not field.is_reserved and field.type.IsScalar():
        all_fields.append(field)

    accessor_prefix = ''
    struct_field = None
    if struct_in_union:
      (accessor_prefix, struct_field) = (
        the_struct.MatchingStructInUnionField(struct_in_union))

      for field in struct_in_union.FieldsBeforePacking():
        if not field.is_reserved and field.type.IsScalar():
          all_fields.append(field)

    for field in all_fields:
      arg_list.append('%s %s' % (field.type.DeclarationType(), field.name))

      if field.SmallerThanType():
        max_value = 1 << field.BitWidth()
        validates.append('\tassert(%s < 0x%x);' % (field.name, max_value))

    # Initialize each packed field.

    for field in the_struct.fields:
      if field.is_reserved or not field.type.IsScalar():
        continue
      inits.append(self.GenerateInitializer(the_struct, field, ''))

    if struct_in_union:
      for field in struct_in_union.fields:
        if field.is_reserved or not field.type.IsScalar():
          continue
        inits.append(self.GenerateInitializer(struct_in_union, field, 
                                              accessor_prefix))

    validate_block = '\n'.join(validates)
    if validate_block:
      validate_block += '\n'
      
    comment = 'Initializes the %s structure.' % the_struct.name
    if struct_in_union:
      comment = ('Initializes the %s structure assuming the %s union should '
                 'be filled in.' % (the_struct.name, struct_in_union.name))

    comment += '\n\nArguments:\n'
    comment += '  s: pointer to structure to be initialized.\n'
    for field in all_fields:
      comment += '  %s: Initial value for field %s\n' % (field.name,
                                                         field.name)
    init_declaration = 'extern void %s(%s);\n' % (function_name,
                                                  ', '.join(arg_list))

    init_definition = 'void %s(%s) {\n%s%s\n}\n' % (function_name,
                                                    ', '.join(arg_list),
                                                    validate_block,
                                                    '\n'.join(inits))
    return parser.Function(init_declaration, init_definition,
                           comment)

  def GenerateJSONInitializer(self, the_struct, the_field, accessor_prefix):
    json_accessor = 'int_value'
    init = ''
    init += '\tstruct fun_json *%s_j = fun_json_lookup(j, "%s");\n' % (
      the_field.name, the_field.name)
    init += '\tif (%s_j == NULL) {\n\t\treturn false;\n\t}\n' % (
      the_field.name)
    init += '\t%s %s = %s_j->%s;\n' % (the_field.type.DeclarationType(),
                                       the_field.name, the_field.name,
                                       json_accessor)
    return init


  def GenerateJSONInitRoutine(self, function_name, struct_name,
                              accessor_prefix, the_struct):
    """Generate function to initialize structure from JSON."""
    arg_list = []
    arg_list.append('struct fun_json *j')
    arg_list.append('struct %s *s' % struct_name)
    inits = []
    for field in the_struct.init_fields():
      inits.append(self.GenerateJSONInitializer(the_struct, field,
                                                accessor_prefix))

    init_fields = ['s']
    init_fields += the_struct.init_fields()

    final_init = '\t%s(%s);\n' % (self.InitializerName(the_struct.name),
                                  ', '.join(init_fields))
    declaration_comment = (
      'Initializes %s structure from JSON representation.\n'
      ' Returns false if initialization failed.\n'
      'Caller responsible for determining correct init function.\n'
      % struct_name)
    init_declaration = 'extern bool %s(%s);\n' %  (
      function_name, ', '.join(arg_list))

    init_definition = 'bool %s(%s) {\n' % (function_name, ', '.join(arg_list))
    init_definition += '%s\n' % '\n'.join(inits)
    init_definition += '%s\n' % final_init
    init_definition += '\treturn true;\n'
    init_definition += '}\n'

    return parser.Function(init_declaration, init_definition,
                           declaration_comment)

  def GenerateHelpersForStruct(self, the_struct):
    """Generates helper functions for the provided structure."""
    initializer_name = self.InitializerName(the_struct.name)
    func = self.GenerateInitRoutine(the_struct, None)
    the_struct.functions.append(func)

    if self.generate_json:
      json_initializer_name = self.JSONInitializerName(the_struct.name)
      json_func = self.GenerateJSONInitRoutine(
        json_initializer_name, the_struct.name, '', the_struct)
      the_struct.functions.append(json_func)

  def VisitField(self, the_struct, the_field):
    if len(the_field.packed_fields) > 0:
      self.GenerateMacrosForPackedField(the_struct, the_field)

  def VisitStruct(self, the_struct):
    """Creates accessor functions related to this structure.

    For each structure, we want an Init/constructor for initializing
    variables easily.
    """
    unions = []
    for field in the_struct.fields:
      if not field.type.IsScalar() and not field.type.IsArray():
         if field.type.base_type.node.is_union:
          unions.append((field.name, field.type.base_type.node))

    if not unions and not the_struct.inline:
      self.GenerateHelpersForStruct(the_struct)

    # TODO(bowdidge): Redo this code for deciding which constructors to create.
    for (union_var, union) in unions:
      structs_in_union = []
      for union_field in union.fields:
        if not union_field.type.IsScalar():
          structs_in_union.append((union_field.name,
                                   union_field.type.base_type.node))

      for (struct_var, struct_in_union) in structs_in_union:
        # Generate constructor for each option.
        function_name = self.InitializerName(struct_in_union.name)
        accessor_prefix = '%s.%s.' % (union_var, struct_var)
        func = self.GenerateInitRoutine(the_struct, struct_in_union)
        the_struct.functions.append(func)

        if self.generate_json:
          json_function_name = self.JSONInitializerName(struct_in_union.name)
          json_func = self.GenerateJSONInitRoutine(json_function_name,
                                                   the_struct.name,
                                                   accessor_prefix,
                                                   struct_in_union)
          the_struct.functions.append(json_func)

        for field in struct_in_union.fields:
          self.VisitField(struct_in_union, field)

    for field in the_struct.fields:
      self.VisitField(the_struct, field)
