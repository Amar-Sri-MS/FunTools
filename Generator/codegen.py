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

  def IndentString(self):
    # Generates indenting spaces needed for current level of code.
    return '\t' * self.indent

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
    hdr_out += '// Do not change this file; '
    hdr_out += 'change the gen file "%s" instead.\n\n' % doc.filename

    src_out += '// Header created by generator.py\n'
    src_out += '// Do not change this file; '
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
        hdr_out += self.VisitEnum(enum)
    for struct in doc.structs:
        (hdr, src) = self.VisitStruct(struct)
        hdr_out += hdr
        src_out += src

    for macro in doc.macros:
      hdr_out += macro + '\n'
    if self.output_file_base is not None:
      hdr_out += '#endif // %s' % include_guard_name
    return (hdr_out, src_out)

  def VisitEnum(self, enum):
    # Pretty print an enum declaration.  Returns enum as string.
    hdr_out = 'enum %s {\n' % enum.name
    self.IncrementIndent()
    for enum_variable in enum.variables:
        hdr_out += self.VisitEnumVariable(enum_variable)
    hdr_out += '};\n\n'
    self.DecrementIndent()
    return hdr_out

  def VisitEnumVariable(self, enum_variable):
    # Pretty-print a structure or union field declaration.  Returns string.
    hdr_out = ''
    if enum_variable.body_comment != None:
      hdr_out += self.IndentString() + ' /* %s */\n' % enum_variable.body_comment
    hdr_out = self.IndentString() + '%s = %s,' % (enum_variable.name, enum_variable.value)
    if enum_variable.key_comment != None:
      hdr_out += self.IndentString() + ' /* %s */' % enum_variable.key_comment
    hdr_out += '\n'
    return hdr_out

  def VisitUnion(self, union):
    # Pretty-print a union declaration.  Returns string.
    hdr_out = ''
    src_out = ''
    if union.key_comment:
      hdr_out += self.IndentString() + '/* %s */\n' % union.key_comment    
    if union.body_comment:
      hdr_out += self.IndentString() + '/* %s */\n' % union.body_comment
    hdr_out += self.IndentString() + 'union %s {\n' % union.name
    for struct in union.structs:
        (hdr, src) = self.VisitStruct(struct)
        hdr_out += hdr
        src_out += src
    variable_str = ''
    if union.variable is not None:
      variable_str = ' ' + union.variable
    hdr_out += self.IndentString() + '}%s;\n' % variable_str
    return (hdr_out, src_out)
 
  def VisitStruct(self, struct):
    # Pretty-print a structure declaration.  Returns string.
    hdr_out = '\n'
    src_out = ''
    if struct.key_comment:
      hdr_out += self.IndentString() + '/* %s */\n' % struct.key_comment    
    if struct.body_comment:
      hdr_out += self.IndentString() + '/* %s */\n' % struct.body_comment
    hdr_out += self.IndentString() + 'struct %s {\n' % struct.name
    lastFlit = 0
    self.IncrementIndent()
    for field in struct.fields:
      if field.flit != lastFlit:
        hdr_out += '\n'
      hdr_out += self.VisitField(field)
      lastFlit = field.flit
    self.DecrementIndent()

    self.IncrementIndent()
    for union in struct.unions:
      (hdr, src) = self.VisitUnion(union)
      hdr_out += hdr
      src_out += src
    self.DecrementIndent()
    tag_str = ''
    if len(struct.variable) > 0:
      tag_str = ' %s' % struct.variable
    hdr_out += self.IndentString() + '}%s;\n\n' % tag_str

    for decl in struct.declarations:
        hdr_out += decl + '\n'

    for definition in struct.definitions:
        src_out += definition + '\n'
 
    return (hdr_out, src_out)

  def VisitField(self, field):
    # Pretty-print a field in a structure or union.  Returns string.
    hdr_out = ''

    if field.generator_comment is not None:
      hdr_out += self.IndentString() + '/* %s */\n' % field.generator_comment
    if field.body_comment is not None:
      # TODO(bowdidge): Break long comment.
      hdr_out += self.IndentString() + '/* %s */\n' % field.body_comment
    key_comment = ''
    if field.key_comment is not None:
      key_comment = ' // %s' % field.key_comment
     
    var_bits = ''
    var_width = field.start_bit - field.end_bit + 1
    type_width = field.type.BitWidth()

    if type_width != var_width:
      var_bits = ':%d' % var_width
    hdr_out += self.IndentString() 
    if field.type.IsArray():
      hdr_out += self.IndentString() + '%s %s[%d];%s\n' % (field.type.BaseName(),
                                                           field.name,
                                                           field.type.ArraySize(),
                                                           key_comment)
    else:
      hdr_out += self.IndentString() + '%s %s%s;%s\n' % (field.type.BaseName(),
                                                         field.name, var_bits,
                                                         key_comment)
    
    return hdr_out

class HelperGenerator:
  def __init__(self):
    self.current_document = None

  def VisitDocument(self, doc):
    self.current_document = doc
    for struct in doc.structs:
      self.VisitStruct(struct)

  def InitializerName(self, struct_name):
      """Returns name for the structure initialization function."""
      return struct_name + "_init"

  def GenerateInitializer(self, the_struct, field, accessor_prefix):
    """Returns a C statement initializing the named variable.

    Assumes that variables with the same name as the field contain initial
    values.
    The variable set should be the packed field; the variables providing the
    values are unpacked.
    """
    if len(field.packed_fields) == 0:
        return '  s->%s%s = %s;' % (accessor_prefix, field.name, field.name)

    packed_inits = []
    for packed_field in field.packed_fields:
      if packed_field.IsReserved():
        continue
      ident = 'FUN_' + utils.AsUppercaseMacro('%s_%s' % (the_struct.name, 
                                                         packed_field.name))
      packed_inits.append('%s_P(%s)' % (ident, packed_field.name))
    return '  s->%s%s = %s;' % (accessor_prefix, field.name,
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
    # All validates, wrapped in a #ifdef DEBUG (or empty if no checks to be done.)
    validate_block = ''

    # First argument is always a pointer to the structure being initialized.
    arg_list.append('struct %s* s' % struct_name)

    for field in the_struct.AllFields():
      if field.IsReserved():
        continue

      arg_list.append('%s %s' % (field.type.DeclarationType(), field.name))

      if field.SmallerThanType():
        max_value = 1 << field.Size()
        validates.append('  assert(%s < 0x%x);' % (field.name, max_value))

    for field in the_struct.fields:
      if field.IsReserved():
        continue
      inits.append(self.GenerateInitializer(the_struct, field, accessor_prefix))

    if len(validates) > 0:
      validate_block = '#ifdef DEBUG\n%s\n#endif\n\n' % '\n'.join(validates)

    init_declaration = 'extern void %s(%s);\n' % (function_name,
                                                  ', '.join(arg_list))
      
    init_definition = 'void %s(%s) {\n%s%s\n\n}' % (function_name,
                                                    ', '.join(arg_list),
                                                    validate_block,
                                                    '\n'.join(inits))
    return (init_declaration, init_definition)

  def VisitStruct(self, the_struct):
    """Creates accessor functions related to this structure.

    For each structure, we want an Init/constructor for initializing
    variables easily.
    """
    if len(the_struct.unions) == 0:
      (decl, defn) = self.GenerateInitRoutine(
          self.InitializerName(the_struct.name),
          the_struct.name, '', the_struct)
      the_struct.declarations.append(decl)
      the_struct.definitions.append(defn)
    else:
      # TODO(bowdidge): Create init routines for structures containing
      # unions.
      if len(the_struct.unions) == 1:
        union = the_struct.unions[0]
        for substruct in union.structs:
          function_name = self.InitializerName(substruct.name)
          struct_name = the_struct.name
          accessor_prefix = '%s.%s.' % (union.variable, substruct.variable)
          (decl, defn) = self.GenerateInitRoutine(function_name, struct_name, 
                                                  accessor_prefix,
                                                  substruct)
          the_struct.declarations.append(decl)
          the_struct.definitions.append(defn)
