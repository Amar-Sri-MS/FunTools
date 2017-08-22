#!/usr/bin/python
#
# Code related to generating C headers and sources.
#
# Robert Bowdidge, June 22, 2017
# Copyright Fungible Inc. 2017.

import os

import generator
import utils

class CodePrinter:
  # Pretty-prints a parsed structure description into C headers.
  # The generated code should match the Linux coding style.

  def __init__(self, output_file_base, generate_json):
    self.indent = 0
    # Prefix of files to create.
    self.output_file_base = output_file_base
    self.generate_json = generate_json

  def Indent(self):
    """Generates indenting spaces needed for current level of code."""
    return '\t' * self.indent

  def PrintIndent(self, str):
    """Prints the provided (possibly multi-line) string with uniform indenting."""
    result = ''
    for l in str.split('\n'):
      result += self.Indent() + l + '\n'
    return result.rstrip('\n \t')

  def IncrementIndent(self):
    """Add another level of indenting to everything printed."""
    self.indent += 1

  def DecrementIndent(self):
    """Remove a level of indenting from everything printed."""
    self.indent -= 1

  def VisitDocument(self, doc):
    """Pretty-print a document.  Returns code as (header, source)."""
    indent = 0
    # stdlib.h is needed for type names.
    hdr_out = ''
    src_out = ''

    hdr_out += ("""
// Header created by generator.py
// Do not change this file;
// change the gen file "%s" instead.

""") % doc.filename

    src_out += ("""
// Header created by generator.py
// Do not change this file;
// change the gen file "%s" instead.

#ifdef __KERNEL__
/* For Linux kernel */
#define assert(x)

#include <linux/types.h>

#else

/* For FunOS and CC-Linux. */
#include <stdint.h>
#include <assert.h>

#endif // __KERNEL__

""") % doc.filename

    if self.output_file_base:
      header_file = os.path.basename(self.output_file_base) + '.h'
      src_out += '#include "%s"\n\n' % (header_file)

      include_guard_name = utils.AsGuardName(header_file)
      hdr_out += '#ifndef %s\n' % include_guard_name
      hdr_out += '#define %s\n' % include_guard_name

    if self.generate_json:
      hdr_out += '#include <utils/threaded/fun_json.h>\n\n'

    hdr_out += '\n'

    for enum in doc.enums:
      (hdr, src) = self.VisitEnum(enum)
      hdr_out += hdr
      src_out += src

    for flagset in doc.flagsets:
      (hdr, src) = self.VisitFlagSet(flagset)
      hdr_out += hdr
      src_out += src

    hdr_out += '\n'

    for struct in doc.structs:
      if not struct.inline:
        (hdr, src) = self.VisitStruct(struct)
        hdr_out += hdr
        src_out += src

    hdr_out += '\n'

    if self.output_file_base is not None:
      hdr_out += '#endif // %s' % include_guard_name
    return (hdr_out, src_out)

  def VisitEnum(self, enum):
    # Pretty print an enum declaration.  Returns enum as string.
    src_out = ''
    hdr_out = 'enum %s {\n' % enum.name
    self.IncrementIndent()
    for enum_variable in enum.variables:
      hdr_out += self.VisitEnumVariable(enum_variable)
    if enum.tail_comment:
      hdr_out += self.PrintIndent(utils.AsComment(enum.tail_comment)) + '\n'
    hdr_out += '};\n\n'
    self.DecrementIndent()

    for func in enum.functions:
      hdr_out += utils.AsComment(func.body_comment) + '\n'
      hdr_out += func.declaration + '\n\n'
      src_out += func.definition + '\n\n'
    
    return (hdr_out, src_out)

  def VisitFlagSet(self, flagset):
    # Pretty-print a flagset declaration.  Returns flag set as string.
    # For flags, we define const ints for each value, and a *_names array
    # that provides a string value for each power of two.
    src_out = ''
    hdr_out = ''

    hdr_out += '/* Declarations for flag set %s */\n' % flagset.name
    if flagset.key_comment:
      hdr_out += utils.AsComment(flagset.key_comment) + '\n'
    if flagset.body_comment:
      hdr_out += utils.AsComment(flagset.body_comment) + '\n'

    for var in flagset.variables:
      if var.body_comment:
        hdr_out += utils.AsComment(var.body_comment) + '\n'
      key_comment = ''
      if var.key_comment:
        key_comment = '  /* ' + var.key_comment + ' */'
      hdr_out += 'static const int %s = 0x%x;%s\n' % (var.name,
                                                      var.value,
                                                      key_comment)
    hdr_out += '\n'

    max_bits = utils.MaxBit(flagset.MaxValue())
    hdr_out += '/* String names for all power-of-two flags in %s. */\n' % flagset.name
    hdr_out += 'extern const char *%s_names[%d];' % (flagset.name, max_bits)
    src_out += 'const char *%s_names[%d] = {\n' % (flagset.name, max_bits)

    for i in range(0, utils.MaxBit(flagset.MaxValue())):
      next_value = 1 << i
      found = False
      for var in flagset.variables:
        if next_value == var.value:
          src_out += '\t"%s",  /* 0x%x */ \n' % (var.name, var.value)
          found = True
          break
      if not found:
        src_out += '\t"0x%x",  /* 0x%x, not defined with flag. */ \n' % (next_value, next_value)

    src_out += '};\n'

    hdr_out += '\n'
    src_out += '\n'

    return (hdr_out, src_out)

  def VisitEnumVariable(self, enum_variable):
    """Pretty-print a structure or union field declaration.  Returns string."""
    hdr_out = ''
    if enum_variable.body_comment != None:
      hdr_out += self.PrintIndent(utils.AsComment(enum_variable.body_comment)) + '\n'
    hdr_out = self.Indent() + '%s = 0x%x,' % (enum_variable.name, enum_variable.value)
    if enum_variable.key_comment != None:
      hdr_out += ' ' + utils.AsComment(enum_variable.key_comment)
    hdr_out += '\n'
    return hdr_out

  def VisitStructRaw(self, the_struct):
    """Generate a structure without the semicolon.

    This routine lets us have one way to print inline and standalone structs.
    """
    hdr_out = ''
    src_out = ''
    if the_struct.key_comment:
      hdr_out += self.PrintIndent(utils.AsComment(the_struct.key_comment)) + '\n'

    if the_struct.body_comment:
      hdr_out += self.PrintIndent(utils.AsComment(the_struct.body_comment)) + '\n'

    hdr_out += self.Indent() + the_struct.Tag() + ' %s {\n' % the_struct.name

    flit_for_last_field = 0
    for field in the_struct.fields:
      # Add blank line between flits.
      if field.StartFlit() != flit_for_last_field:
        hdr_out += '\n'

      self.IncrementIndent()
      hdr_out += self.VisitField(field)
      self.DecrementIndent()

      flit_for_last_field = field.StartFlit()

    if the_struct.tail_comment:
      self.IncrementIndent()
      hdr_out += self.PrintIndent(utils.AsComment(the_struct.tail_comment)) + '\n'
      self.DecrementIndent()

    hdr_out += self.Indent() + '}'
    return hdr_out

  def VisitStruct(self, the_struct):
    """Pretty-print a structure declaration.  Returns string."""
    hdr_out = ''
    src_out = ''

    hdr_out += self.VisitStructRaw(the_struct)

    var_str = ''
    hdr_out += ';\n'

    for s in [the_struct] + the_struct.NestedStructs():
      for macro in s.macros:
        if macro.body_comment:
          hdr_out += utils.AsComment(macro.body_comment) + '\n'
        hdr_out += macro.body + '\n\n'

    for function in the_struct.functions:
      hdr_out += utils.AsComment(function.body_comment) + '\n'
      hdr_out += function.declaration + '\n'
      src_out += function.definition + '\n'

    return (hdr_out, src_out)

  def VisitField(self, field):
    """Pretty-print a field in a structure or union.  Returns string."""
    hdr_out = ''
    field_type = field.Type()
    type_name = field_type.DeclarationName();

    if field_type.IsRecord():
      struct = field_type.base_type.node
      if struct.inline:
        type_name = self.VisitStructRaw(struct)

    if field.generator_comment is not None:
      hdr_out += self.PrintIndent(utils.AsComment(field.generator_comment)) + '\n'

    if field.body_comment is not None:
      # TODO(bowdidge): Break long comment.
      hdr_out += self.PrintIndent(utils.AsComment(field.body_comment)) + '\n'

    key_comment = ''
    if field.key_comment is not None:
      key_comment = ' ' + utils.AsComment(field.key_comment)

    if field.type.IsArray():
      hdr_out += self.Indent() + '%s %s[%d];%s\n' % (type_name,
                                                     field.name,
                                                     field.type.ArraySize(),
                                                     key_comment)
    else:
      var_width = field.BitWidth()
      type_width = field.type.BitWidth()

      var_bits = ''
      if field.type.IsScalar() and type_width != var_width:
        var_bits = ':%d' % var_width
      hdr_out += self.Indent() + '%s %s%s;%s\n' % (type_name,
                                                   field.name, var_bits,
                                                   key_comment)

    return hdr_out

class CodeGenerator:
  """Generates helper functions for manipulating structures."""
  def __init__(self, generate_json):
    self.generate_json = generate_json

  def VisitDocument(self, doc):
    for struct in doc.structs:
      self.VisitStruct(struct)
    for enum in doc.enums:
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

    fun = generator.Function(
      decl, defn,
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
      if old_field.IsReserved():
        continue

      ident = utils.AsUppercaseMacro('%s_%s' % (the_struct.name,
                                                         old_field.name))
      shift_name = '%s_S' % ident
      shift = '#define %s %s' % (shift_name, old_field.EndBit() - min_end_bit)
      mask_name = '%s_M' % ident
      mask = '#define %s %s' % (mask_name, old_field.Mask())
      value_name = '%s_P' % ident
      value = '#define %s(x) ((x) << %s)' % (value_name, shift_name)
      get_name = '%s_G' % ident
      get = '#define %s(x) (((x) >> %s) & %s)' % (get_name, shift_name, mask_name)

      
      value_comment = 'Shifts value to place in packed field %s in %s.%s.' % (
        old_field.name, the_struct.name, field.name)

      get_comment = 'Returns value for packed field %s in %s.%s.' % (
        old_field.name, the_struct.name, field.name)

      offset_comment = 'Offset of field %s in packed field %s.%s' % (
        old_field.name, the_struct.name, field.name)

      mask_comment = 'Mask to extract field %s from packed field %s.%s' % (
        old_field.name, the_struct.name, field.name)

      the_struct.macros.append(generator.Macro(shift_name, shift, offset_comment))
      the_struct.macros.append(generator.Macro(mask_name, mask, mask_comment))
      the_struct.macros.append(generator.Macro(value_name, value, value_comment))
      the_struct.macros.append(generator.Macro(get_name, get, get_comment))

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
      if packed_field.IsReserved():
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
    for field in the_struct.AllFields():
      if not field.IsReserved() and field.type.IsScalar():
        all_fields.append(field)

    accessor_prefix = ''
    struct_field = None
    if struct_in_union:
      (accessor_prefix, struct_field) = (
        the_struct.MatchingStructInUnionField(struct_in_union))

      for field in struct_in_union.AllFields():
        if not field.IsReserved() and field.type.IsScalar():
          all_fields.append(field)

    for field in all_fields:
      arg_list.append('%s %s' % (field.type.DeclarationType(), field.name))

      if field.SmallerThanType():
        max_value = 1 << field.BitWidth()
        validates.append('\tassert(%s < 0x%x);' % (field.name, max_value))

    # Initialize each packed field.

    for field in the_struct.fields:
      if field.IsReserved() or not field.type.IsScalar():
        continue
      inits.append(self.GenerateInitializer(the_struct, field, ''))

    if struct_in_union:
      for field in struct_in_union.fields:
        if field.IsReserved() or not field.type.IsScalar():
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

    init_declaration = 'extern void %s(%s);\n' % (function_name,
                                                  ', '.join(arg_list))

    init_definition = 'void %s(%s) {\n%s%s\n}\n' % (function_name,
                                                    ', '.join(arg_list),
                                                    validate_block,
                                                    '\n'.join(inits))
    return generator.Function(init_declaration, init_definition,
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
    for field in the_struct.AllFields():
      if field.IsReserved() or not field.type.IsScalar():
        continue
      inits.append(self.GenerateJSONInitializer(the_struct, field,
                                                accessor_prefix))

    init_fields = ['s']
    init_fields += [f.name for f in the_struct.AllFields()
                    if f.type.IsScalar() and not f.IsReserved()]

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

    return generator.Function(init_declaration, init_definition,
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
