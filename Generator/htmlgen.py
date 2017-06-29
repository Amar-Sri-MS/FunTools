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

  def VisitUnionInStruct(self, union):
    """Draws a union as rows in a containing structure."""
    out = '<tr>\n'

    comment = ""
    if union.key_comment:
      comment = union.key_comment

    out += '  <td class="structBits" colspan="2">0:63-%d:0</td>\n' % (
      union.Flits() - 1)
    out += '  <td>union %s</td>\n' % union.name
    out += '  <td>%s</td>\n' % union.variable
    out += '  <td>%s</td>\n' % comment
    out += '</tr>\n'

    for s in union.structs:
      out += '<tr>\n'
      out += '  <td class="structBits" colspan="2">0:63 - %d:%d</td>\n' % (
        s.Flits() - 1, 0)
      out += '  <td></td>\n'
      out += '  <td>%s</td>\n' % s.name
      out += '  <td>%s</td>\n' % s.key_comment
      out += '</tr>\n'
    return out

  def VisitStruct(self, struct):
    # Generates HTML documentation for a specific structure.
    out = ''
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
    # TODO(bowdidge): Fields and unions should be displayed in order
    # of index.
    for field in struct.fields:
      out += self.VisitField(field)
    for union in struct.unions:
      out += self.VisitUnionInStruct(union)

    # Tail comment comes after everything else.
    if struct.tail_comment:
      out += '<tr>\n'
      out += '  <td class="description" colspan="5">\n'
      out += '  <center>%s</center>\n' % struct.tail_comment
      out += '  </td>\n'
      out += '</tr>\n'
    out += "</table>\n"

    for union in struct.unions:
      for s in union.structs:
        out += self.VisitStruct(s)

    return out

  def VisitField(self, field, note=''):
    """Generates HTML documentation for a specific field."""
    if len(field.packed_fields) != 0:
      out = ''
      for packed_field in field.packed_fields:
        out += self.VisitField(packed_field,
                               'In packed field %s.' % field.name)
      return out

    # Draw a solid line at start of each flit to visually separate flits.
    solid = ''
    if field.StartBit()== 63:
      solid = 'border-top: solid 1px'
    elif field.crosses_flit:
      solid = 'border-bottom: solid 1px'
    out = ''
    out += '<tr style="%s">\n' % solid
    if field.crosses_flit:
      out += '  <td class="structBits" colspan=2>%d:%d-%d:%d</td>\n' % (
        field.StartFlit(), field.StartBit(), field.EndFlit(), field.EndBit())
      out += '  <td>%s</td>\n  <td>%s</td>\n' % (field.type.DeclarationType(),
                                                 field.name)
    else:
      out += '  <td class="structBits">%d</td>\n' % field.StartFlit()
      out += '  <td class="structBits">%d-%d</td>\n' % (field.StartBit(), 
                                                        field.EndBit())
      out += '  <td>%s</td>\n  <td>%s</td>\n' % (field.type.DeclarationType(),
                                                 field.name)

    out += '<td class="description">\n'
    if field.key_comment:
      out += field.key_comment + '<br>'
    if note:
      out += '<i>' + note + '</i><br>'
    if field.body_comment:
        out += '<p>%s</p>/' % (field.body_comment)
    out += '</td>\n'
    out += '</tr>\n'
    return out
