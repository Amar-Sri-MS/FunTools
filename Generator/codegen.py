#!/usr/bin/python
#
# Code related to generating C headers and sources.
#
# Robert Bowdidge, June 22, 2017
# Copyright Fungible Inc. 2017.

class CodeGenerator:
  # Pretty-prints a parsed structure description into C headers.
  # The generated code should match the Linux coding style.

  def __init__(self, output_file):
    self.indent = 0
    # Name of file to create.
    self.output_file = output_file

  def indentString(self):
    # Generates indenting spaces needed for current level of code.
    return '\t' * self.indent

  def incrementIndent(self):
    self.indent += 1

  def decrementIndent(self):
    self.indent -= 1

  def visitDocument(self, doc):
    # Pretty-print a document.  Returns header as string.
    indent = 0
    # stdlib.h is needed for type names.
    out = ""
    out += '// Header created by generator.py\n'
    out += '// Do not change this file; '
    out += 'change the gen file "%s" instead.\n\n' % doc.filename
    if self.output_file is not None:
      include_guard_name = guardName(self.output_file)
      out += '#ifndef %s\n' % include_guard_name
      out += '#define %s 1\n\n' % include_guard_name
    out += '#import "stdlib.h"\n\n'
    for enum in doc.enums:
      out += self.visitEnum(enum)
    for struct in doc.structs:
      out += self.visitStruct(struct)

    for macro in doc.macros:
      out += macro + '\n'
    if self.output_file is not None:
      out += '#endif // %s' % include_guard_name
    return out

  def visitEnum(self, enum):
    # Pretty print an enum declaration.  Returns enum as string.
    out = 'enum %s {\n' % enum.name
    self.incrementIndent()
    for enum_variable in enum.variables:
        out += self.visitEnumVariable(enum_variable)
    out += '};\n'
    self.decrementIndent()
    return out

  def visitEnumVariable(self, enum_variable):
    # Pretty-print a structure or union field declaration.  Returns string.
    out = ''
    if enum_variable.body_comment != None:
      out += self.indentString() + ' /* %s */\n' % enum_variable.body_comment
    out = self.indentString() + '%s = %s,' % (enum_variable.name, enum_variable.value)
    if enum_variable.key_comment != None:
      out += ' /* %s */' % enum_variable.key_comment
    out += '\n'
    return out

  def visitUnion(self, union):
    # Pretty-print a union declaration.  Returns string.
    out = ''
    if union.key_comment:
      out += self.indentString() + '/* %s */\n' % union.key_comment    
    if union.body_comment:
      out += self.indentString() + '/* %s */\n' % union.body_comment
    out += self.indentString() + 'union %s {\n' % union.name
    for struct in union.structs:
      out += self.visitStruct(struct)
    variable_str = ''
    if union.variable is not None:
      variable_str = ' ' + union.variable
    out += self.indentString() + '}%s;\n' % variable_str
    return out
 
  def visitStruct(self, struct):
    # Pretty-print a structure declaration.  Returns string.
    out = '\n'
    if struct.key_comment:
      out += self.indentString() + '/* %s */\n' % struct.key_comment    
    if struct.body_comment:
      out += self.indentString() + '/* %s */\n' % struct.body_comment
    out += self.indentString() + 'struct %s {\n' % struct.name
    lastFlit = 0
    self.incrementIndent()
    for field in struct.fields:
      if field.flit != lastFlit:
        out += '\n'
      out += self.visitField(field)
      lastFlit = field.flit
    self.decrementIndent()

    self.incrementIndent()
    for union in struct.unions:
      out += self.visitUnion(union)
    self.decrementIndent()
    tag_str = ''
    if len(struct.variable) > 0:
      tag_str = ' %s' % struct.variable
    out += self.indentString() + '}%s;\n' % tag_str
    return out

  def visitField(self, field):
    # Pretty-print a field in a structure or union.  Returns string.
    out = ''

    if field.generator_comment is not None:
      out += self.indentString() + '/* %s */\n' % field.generator_comment
    if field.body_comment is not None:
      # TODO(bowdidge): Break long comment.
      out += self.indentString() + '/* %s */\n' % field.body_comment
    key_comment = ''
    if field.key_comment is not None:
      key_comment = ' // %s' % field.key_comment
     
    var_bits = ''
    var_width = field.start_bit - field.end_bit + 1
    type_width = field.type.BitWidth()

    if type_width != var_width:
      var_bits = ':%d' % var_width
    out += self.indentString() 
    if field.type.IsArray():
      out += '%s %s[%d];%s\n' % (field.type.BaseName(), field.name,
                                 field.type.ArraySize(), key_comment)
    else:
      out += '%s %s%s;%s\n' % (field.type.BaseName(), field.name, var_bits,
                               key_comment)
    
    return out
