#!/usr/bin/python
#
# Code related to generating C headers and sources.
#
# Robert Bowdidge, June 22, 2017
# Copyright Fungible Inc. 2017.

import os

import utils

class CodeGenerator:
  # Pretty-prints a parsed structure description into C headers.
  # The generated code should match the Linux coding style.

  def __init__(self, output_file_base):
    self.indent = 0
    # Prefix of files to create.
    self.output_file_base = output_file_base

  def Indent(self):
    """Generates indenting spaces needed for current level of code."""
    return '\t' * self.indent

  def PrintIndent(self, str):
    """Prints the provided (possibly multi-lne) string with uniform indenting."""
    result = ''
    for l in str.split('\n'):
      result += self.Indent() + l + '\n'
    return result.rstrip('\n \t')

  def IncrementIndent(self):
    self.indent += 1

  def DecrementIndent(self):
    self.indent -= 1

  def VisitDocument(self, doc):
    # Pretty-print a document.  Returns code as (header, source).
    indent = 0
    # stdlib.h is needed for type names.
    hdr_out = ''
    src_out = ''

    hdr_out += '// Header created by generator.py\n'
    hdr_out += '// Do not change this file;\n'
    hdr_out += '// change the gen file "%s" instead.\n\n' % doc.filename

    src_out += '// Header created by generator.py\n'
    src_out += '// Do not change this file;\n'
    src_out += '// change the gen file "%s" instead.\n\n' % doc.filename
    src_out += '\n'
    src_out += '#include <assert.h>\n'
    if self.output_file_base:
      header_file = os.path.basename(self.output_file_base) + '.h'
      src_out += '#include "%s"\n\n' % (header_file)

      include_guard_name = utils.AsGuardName(header_file)
      hdr_out += '#ifndef %s\n' % include_guard_name
      hdr_out += '#define %s\n' % include_guard_name
    hdr_out += '#include "stdlib.h"\n\n'
    for enum in doc.enums:
        (hdr, src) = self.VisitEnum(enum)
        hdr_out += hdr
        src_out += src
    for struct in doc.structs:
        (hdr, src) = self.VisitStruct(struct)
        hdr_out += hdr
        src_out += src

    for macro in doc.macros:
      hdr_out += macro + '\n'

    for decl in doc.declarations:
        hdr_out += decl + '\n'

    for definition in doc.definitions:
        src_out += definition + '\n'
 
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

    hdr_out += '/* Human-readable strings for enum values in %s. */\n' % enum.name
    hdr_out += 'extern const char *%s_names[%d];\n\n' % (enum.name.lower(),
                                                         len(enum.variables));

    src_out += 'const char *%s_names[%d] = {\n' % (enum.name.lower(),
                                                   len(enum.variables))
    for enum_variable in enum.variables:
      src_out += '\t"%s",  /* 0x%x */\n' % (enum_variable.name,
                                            enum_variable.value)
    src_out += '};\n'
    return (hdr_out, src_out)

  def VisitEnumVariable(self, enum_variable):
    # Pretty-print a structure or union field declaration.  Returns string.
    hdr_out = ''
    if enum_variable.body_comment != None:
      hdr_out += self.PrintIndent(utils.AsComment(enum_variable.body_comment)) + '\n'
    hdr_out = self.Indent() + '%s = 0x%x,' % (enum_variable.name, enum_variable.value)
    if enum_variable.key_comment != None:
      hdr_out += ' ' + utils.AsComment(enum_variable.key_comment)
    hdr_out += '\n'
    return hdr_out

  def VisitStruct(self, the_struct):
    # Pretty-print a structure declaration.  Returns string.
    hdr_out = ''
    src_out = ''
    if the_struct.key_comment:
      hdr_out += self.PrintIndent(utils.AsComment(the_struct.key_comment)) + '\n'
    if the_struct.body_comment:
      hdr_out += self.PrintIndent(utils.AsComment(the_struct.body_comment)) + '\n'
    hdr_out += self.Indent() + the_struct.Tag() + ' %s {\n' % the_struct.name
    lastFlit = 0
    self.IncrementIndent()
    for field in the_struct.fields:
      # Add blank line between flits.
      if field.StartFlit() != lastFlit:
        hdr_out += '\n'
      hdr_out += self.VisitField(field)
      lastFlit = field.StartFlit()

    for struct in the_struct.structs:
      (hdr, src) = self.VisitStruct(struct)
      hdr_out += hdr
      src_out += src

    if the_struct.tail_comment:
      hdr_out += self.PrintIndent(utils.AsComment(the_struct.tail_comment)) + '\n'
    self.DecrementIndent()
    tag_str = ''
    if len(the_struct.variable) > 0:
      tag_str = ' %s' % the_struct.variable
    hdr_out += self.Indent() + '}%s;\n' % tag_str

    return (hdr_out, src_out)

  def VisitField(self, field):
    # Pretty-print a field in a structure or union.  Returns string.
    hdr_out = ''

    if field.generator_comment is not None:
      hdr_out += self.PrintIndent(utils.AsComment(field.generator_comment)) + '\n'
    if field.body_comment is not None:
      # TODO(bowdidge): Break long comment.
      hdr_out += self.PrintIndent(utils.AsComment(field.body_comment)) + '\n'
    key_comment = ''
    if field.key_comment is not None:
      key_comment = ' ' + utils.AsComment(field.key_comment)
     
    var_bits = ''
    var_width = field.BitWidth()
    type_width = field.type.BitWidth()

    if field.type.IsScalar() and type_width != var_width:
      var_bits = ':%d' % var_width
    if field.type.IsArray():
      hdr_out += self.Indent() + '%s %s[%d];%s\n' % (field.type.BaseName(),
                                                           field.name,
                                                           field.type.ArraySize(),
                                                           key_comment)
    else:
      hdr_out += self.Indent() + '%s %s%s;%s\n' % (field.type.DeclarationName(),
                                                         field.name, var_bits,
                                                         key_comment)
    
    return hdr_out

class HelperGenerator:
  """Generates helper functions for manipulating structures."""
  def __init__(self):
    self.current_document = None

  def VisitDocument(self, doc):
    self.current_document = doc
    for struct in doc.structs:
      self.VisitStruct(struct)

  def InitializerName(self, struct_name):
      """Returns name for the structure initialization function."""
      return struct_name + "_init"

  def GenerateMacrosForPackedField(self, struct, field):
    """Creates macros to access all the bit fields we removed.
    struct: structure containing the fields that was removed.
    field: field combining the contents of the former fields.
    """
    min_end_bit = min([f.EndBit() for f in field.packed_fields])

    for old_field in field.packed_fields:
      # No point in creating macros for fields that shouldn't be accessed.
      if old_field.IsReserved():
        continue

      ident = 'FUN_' + utils.AsUppercaseMacro('%s_%s' % (struct.name, 
                                                         old_field.name))
      shift = '#define %s_S %s' % (ident, old_field.EndBit() - min_end_bit)
      mask = '#define %s_M %s' % (ident, old_field.Mask())
      value = '#define %s_P(x) ((x) << %s_S)' % (ident, ident)
      get = '#define %s_G(x) (((x) >> %s_S) & %s_M)' % (ident, ident, ident)

      struct.macros.append(
        '// For accessing "%s" field in %s.%s' % (
          old_field.name, struct.name, field.name))
      self.current_document.macros.append(shift)
      self.current_document.macros.append(mask)
      self.current_document.macros.append(value)
      self.current_document.macros.append(get)

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
      ident = 'FUN_' + utils.AsUppercaseMacro('%s_%s' % (the_struct.name, 
                                                         packed_field.name))
      packed_inits.append('%s_P(%s)' % (ident, packed_field.name))
    return '\ts->%s%s = %s;' % (accessor_prefix, field.name,
                                ' | '.join(packed_inits))

  def GenerateInitRoutine(self, function_name, struct_name, 
                          accessor_prefix, the_struct):
    """Generate an initialization function for the named structure.

    The function takes all non reserved fields as arguments, test
    that any bitfields are valid, and sets the fields of the referenced
    structure.

    Arguments:
      function_name (string) is the preferred name for the init function itself.
      struct_name (string) is the name to use for the structure type.
      accessor_prefix is a bit of code to insert between the pointer token and
        field name token to access the field.  It is used to add the name of union
        fields.
      the_struct (Struct) is the structure owning the init routine, used to find
        all its fields.
     
    Returns:
      (declaration, definition) pair.
    
    Arguments to the Init function are unpacked fields, values set in the 
    field are packed.
    """
    # List of arguments to the function.
    arg_list = []
    # List of statements validating size of inputs.
    validates = []
    # List of statements initializing fields of structure.
    inits = []
    # All C code to validate field inputs.
    validate_block = ''

    # First argument is always a pointer to the structure being initialized.
    arg_list.append('struct %s* s' % struct_name)

    for field in the_struct.AllFields():
      if field.IsReserved() or not field.type.IsScalar():
        continue

      arg_list.append('%s %s' % (field.type.DeclarationType(), field.name))

      if field.SmallerThanType():
        max_value = 1 << field.BitWidth()
        validates.append('\tassert(%s < 0x%x);' % (field.name, max_value))

    if len(arg_list) == 1:
      # If no arguments other than structure, don't bother.
      return ('', '')

    for field in the_struct.fields:
      if field.IsReserved() or not field.type.IsScalar():
        continue

      inits.append(self.GenerateInitializer(the_struct, field, accessor_prefix))

    validate_block = '\n'.join(validates)

    init_declaration = 'extern void %s(%s);\n' % (function_name,
                                                  ', '.join(arg_list))
      
    init_definition = 'void %s(%s) {\n%s%s\n\n}' % (function_name,
                                                    ', '.join(arg_list),
                                                    validate_block,
                                                    '\n'.join(inits))
    return (init_declaration, init_definition)

  def GenerateHelpersForStruct(self, the_struct):
    """Generates helper functions for the provided structure."""
    (decl, defn) = self.GenerateInitRoutine(self.InitializerName(the_struct.name),
                                            the_struct.name, '', the_struct)
    self.current_document.declarations.append(decl)
    self.current_document.definitions.append(defn)
 

  def VisitField(self, the_struct, the_field):
    if len(the_field.packed_fields) > 0:
      self.GenerateMacrosForPackedField(the_struct, the_field)
    
  def VisitStruct(self, the_struct):
    """Creates accessor functions related to this structure.

    For each structure, we want an Init/constructor for initializing
    variables easily.
    """
    has_unions = [True for s in the_struct.structs if s.is_union]

    if not has_unions:
      self.GenerateHelpersForStruct(the_struct)

    # TODO(bowdidge): Redo this code for deciding which constructors to create.
    for union in the_struct.structs:
      if union.is_union:
        for struct in union.structs:
          # Generate constructor for each option.
          function_name = self.InitializerName(the_struct.name + "_" + struct.name)
          struct_name = the_struct.name
          accessor_prefix = '%s.%s.' % (union.variable, struct.variable)
          (decl, defn) = self.GenerateInitRoutine(function_name, struct_name, 
                                                  accessor_prefix,
                                                  struct)
          self.current_document.declarations.append(decl)
          self.current_document.definitions.append(defn)

          # Hack.  Don't recursively visit the structure; instead
          # just visit fields to generate pack macros.
          for field in struct.fields:
            self.VisitField(struct, field)
 
    for field in the_struct.fields:
      self.VisitField(the_struct, field)
    
    for struct in the_struct.structs:
      if not struct.is_union:
        self.VisitStruct(struct)
