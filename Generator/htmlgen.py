#!/usr/bin/python

# htmlgen.py
# HTMLGenerator takes a DocBuilder describing various machine data structures,
# and generates documentation for these.

class HTMLGenerator:

  def VisitDocument(self, doc):
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
      out += self.VisitEnum(enum)
    for struct in doc.structs:
      if not struct.inline:
        out += self.VisitStruct(struct)
    for macro in doc.macros:
     pass
    out += '</body></html>'
    return out

  def VisitEnumVariable(self, enum_variable):
    # Generates HTML Documentation for a specific enum variable.
    out = '<dt>%s = %d</dt>\n' % (enum_variable.name, enum_variable.value)
    out += '<dd>\n'
    if enum_variable.key_comment:
        out += enum_variable.key_comment
    if enum_variable.key_comment and enum_variable.body_comment:
        out += '<br>'
    if enum_variable.body_comment:
        out += enum_variable.body_comment
    out += '</dd>\n'
    return out

  def VisitEnum(self, enum):
    # Generates HTML documentation for a specific enum type.
    out = ''
    out += '<h3>enum %s</h3>\n' % enum.name
    if enum.key_comment:
      out += '<p>%s</p>\n' % enum.key_comment
    if enum.body_comment:
      out += '<p>%s</p>\n' % enum.body_comment
    out += '<b>Values</b><br>\n'
    out += '<dl>\n'
    for enum_variable in enum.variables:
      out += self.VisitEnumVariable(enum_variable)
    out += '</dl>\n'
    if enum.tail_comment:
        out += '<p>%s</p>' % enum.tail_comment
    return out

  def VisitRecordField(self, field, struct, level):
    """Draws a struct as rows in a containing structure.
    
    struct is the """
    out = '<tr>\n'

    comment = ""
    if struct.key_comment:
      comment = struct.key_comment

    if field.StartFlit() != field.EndFlit():
      out += '  <td class="structBits" colspan=2>%d:%d-%d:%d</td>\n' % (
        field.StartFlit(), field.StartBit(), field.EndFlit(), field.EndBit())
    else:
      out += '  <td class="structBits">%d</td>\n' % field.StartFlit()
      out += '  <td class="structBits">%d-%d</td>\n' % (field.StartBit(), 
                                                        field.EndBit())
    indent = '&nbsp;' * level
    if not struct.inline:
      out += '  <td>%s%s <a href="#%s">%s</a></td>\n' % (indent, struct.Tag(), 
                                                        struct.Name(),
                                                        struct.Name())
    else:
      out += '  <td>%s%s %s</td>\n' % (indent, struct.Tag(), struct.Name())
    out += '  <td>%s</td>\n' % field.name
    out += '  <td>%s</td>\n' % comment
    out += '</tr>\n'

    if not struct.inline:
      return out

    for f in field.subfields:
      if f.type.IsRecord():
        out += self.VisitRecordField(f, f.type.base_type.node, level + 2)
      else:
        out += self.VisitField(f, level + 1)
    return out

  def VisitStruct(self, struct):
    # Generates HTML documentation for a specific structure.
    out = ''
    out += '<a name="%s"></a>' % struct.name
    out += '<h3>struct %s:</h3>\n' % struct.name
    if struct.key_comment:
      out += '<p>%s</p>\n' % struct.key_comment
    out += '<p>%s</p>\n' % struct.body_comment
    out += '<table class="structTable">\n'
    out += '<tr>\n'
    out += '  <th class="structBits">Flit</th>\n'
    out += '  <th class="structBits">Bits</th>\n'
    out += '  <th>Type</th>'
    out += '  <th>Name</th><th>Description</th></tr>\n'
    # TODO(bowdidge): Fields and nested structures or unions should be
    # displayed in order of index.
    for field in struct.fields:
      if field.type.IsRecord():
        out += self.VisitRecordField(field, field.type.base_type.node, 0)
      else:
        out += self.VisitField(field, 0)

    # Tail comment comes after everything else.
    if struct.tail_comment:
      out += '<tr>\n'
      out += '  <td class="description" colspan="5">\n'
      out += '  <center>%s</center>\n' % struct.tail_comment
      out += '  </td>\n'
      out += '</tr>\n'
    out += "</table>\n"

    return out

  def VisitField(self, field, level):
    """Generates HTML documentation for a specific field."""
    if len(field.packed_fields) != 0:
      out = ''
      for packed_field in field.packed_fields:
        out += self.VisitField(packed_field, level + 1)
      return out

    # Draw a solid line at start of each flit to visually separate flits.
    solid = ''
    if field.StartBit()== 63:
      solid = 'border-top: solid 1px'
    elif field.crosses_flit:
      solid = 'border-bottom: solid 1px'
    out = ''

    indent = '&nbsp;' * level

    out += '<tr style="%s">\n' % solid
    if field.crosses_flit:
      out += '  <td class="structBits" colspan=2>%d:%d-%d:%d</td>\n' % (
        field.StartFlit(), field.StartBit(), field.EndFlit(), field.EndBit())
    elif field.no_offset:
      out += '  <td class="structBits" colspan=2></td>\n'
    else:
      out += '  <td class="structBits">%d</td>\n' % field.StartFlit()
      out += '  <td class="structBits">%d-%d</td>\n' % (field.StartBit(), 
                                                        field.EndBit())
    out += '  <td>%s%s</td>\n  <td>%s</td>\n' % (indent,
                                                 field.type.DeclarationType(),
                                                 field.name)

    out += '<td class="description">\n'
    if field.key_comment:
      out += field.key_comment + '<br>'
    if field.body_comment:
        out += '<p>%s</p>/' % (field.body_comment)
    out += '</td>\n'
    out += '</tr>\n'
    return out
