#!/usr/bin/python
# htmlgen.py
# HTMLGenerator takes a DocBuilder describing various machine data structures,
# and generates documentation for these.

import utils

def ReplaceField(field, union_map):
  """Returns the actual field to draw for a field and a union map.

  Replaces fields with type of a union key in the union map with the
  field in the union with the same type as the value in the union map.
  Allows descriptions to focus only on a particular alternative.
  """
  for union in union_map.keys():
    substruct = union_map[union]
    if field.type.IsRecord():
      if field.type.base_type.node == union:
        for f in field.subfields:
          if f.type.IsRecord():
            if f.type.base_type.node == substruct:
              return f
  return field


  for f in field.subfields:
    if f.type == replacement_struct:
      return f
  print('ReplaceField: could not find replacement for %s in %s' % (
      union_map[field.type], field))
  return None
  

class HTMLGenerator:

  def Rows(self, struct, union_map):
    """Returns an array of arrays of (field name, field width)

    Each top-level array represents a flit and the fields in the flit.
    """
    fields = []
    rows = []
    current_row = []
    next_color = 0
    bytes_remaining = 64

    # Field wrapping to next row.
    lingering_field_name = None
    # Number of bits in lingering field.
    lingering_field_width = 0
    
    fields = list(struct.fields)

    while len(fields) > 0 or lingering_field_width > 0:
      if lingering_field_width > 0:
        if bytes_remaining > lingering_field_width:
          current_row.append((lingering_field_name, lingering_field_width))
        else:
          current_row.append((lingering_field_name, bytes_remaining))
          lingering_field_width = lingering_field_width - bytes_remaining
      else:
        next_field = fields.pop(0)

        if union_map:
          next_field = ReplaceField(next_field, union_map)

        if next_field.type.IsRecord():
          struct = next_field.type.base_type.node
          fields = list(struct.fields) + fields
        elif next_field.type.IsScalar() or next_field.type.IsArray():
          if bytes_remaining >= next_field.BitWidth():
            current_row.append((next_field.name, next_field.BitWidth()))
            bytes_remaining -= next_field.BitWidth()
        else:
          lingering_field_name = next_field.name
          lingering_field_width = next_field.BitWidth()

      if bytes_remaining == 0:
        rows.append(current_row)
        current_row = []
        bytes_remaining = 64
    return rows        

  def DrawFields(self, flit, row):
    """Draws a row representing a single flit."""
    out = ''
    out += '  <div class="bitRow">\n'
    out += '    <div class="rowTitle">Flit %d</div>\n' % flit
    for (name, width) in row:
      bar_width = (1000 * width / 64) - 2
      out += '    <div class="bar field" style="width: %dpx">%s</div>\n' % ( 
        bar_width, name)
    out += '  </div>\n'
    return out

  def BitmapForStruct(self, struct, union_map):
    out = '<div class="bitmap">\n'
    out += '  <div class="bitRow">\n'
    out += '    <div class="rowTitle"><b>Bits</b></div>\n'
    out += '    <div class="bar keybar" style="width: 123px">63-56</div>\n'
    out += '    <div class="bar keybar" style="width: 123px">55-48</div>\n'
    out += '    <div class="bar keybar" style="width: 123px">47-40</div>\n'
    out += '    <div class="bar keybar" style="width: 123px">39-32</div>\n'
    out += '    <div class="bar keybar" style="width: 123px">31-24</div>\n'
    out += '    <div class="bar keybar" style="width: 123px">23-16</div>\n'
    out += '    <div class="bar keybar" style="width: 123px">15-8</div>\n'
    out += '    <div class="bar keybar" style="width: 123px">7-0</div>\n'
    out += '  </div>\n'

    rows = self.Rows(struct, union_map)
    flit = 0
    for row in rows:
      out += self.DrawFields(flit, row)
      flit += 1
    out += '</div>\n'
    return out


  def VisitDocument(self, doc):
    # Generates all the HTML to document the structures.
    css = ("""
.structTable {
    border: solid 1px black;
    border-collapse: collapse;
}
.structTable td {
        font-family: "Courier"
}
.structTable .description {
        font-family: "Times New Roman"
}
.structBits {
        background: #eeeeee;
        /* TODO(bowdidge): Mess with padding to get left column of both tables same width. */
        width: 85px;

}
.structTable td {
        padding: 10px;
}
.structTable th {
        background: #dddddd;
}

/* Any row of the bitmap. */
.bitRow {
  width: 1200px;
  display: inline-block;
  padding: 0px;
  margin: 0px;
}
/* Title bar of bitmap showing bit ranges. */
.keybar {
  background-color: #f0f0f0;
  height: 40px;
  border: 1px solid gray;
  border-bottom: 1px solid black;
  border-left: 1px  solid black;
  border-right: 1px solid black;
  font-weight: bold;
}

/* Block representing a single non-nested field. */
.field {
  background-color: #f0ffff;
  height: 40px;  
  border: 1px solid black;
}

/* Block representing top line of a nested field listing the
   contained structure. */
.nested {
  height: 25px;
  background-color: #f0f0ff;
  border-left: 1px solid black;
  border-right: 1px solid black;
  border-bottom: 0px solid black
}
/* Block representing lower line of a nested field listing the field. */
.nestedfield {
  background-color: #f0f0ff;
  height: 40px;
  border: 1px solid black;
  border-bottom 2px solid black;
  border-top: 0px solid black
}

/* Generic part of a bar in the bitmap. */
.bar {
 float: left;
  margin: 0px;
  padding: 0px;
  text-align: center;
}
/* Left caption for a row. */
.rowtitle {
  width: 200px;
  height: 40px;
  display: inline-block;
  float: left;
  background-color: #eeeeee;
}
/* Entire bitmap. */
.bitmap {
  margin-bottom: 10px;
}

.bitfieldTable {
  text-align: center;
  border: solid 1px black;
}

""")

    out = '<!-- Documentation created by generator.py.\n'
    out += '     Do not change this file; '
    out += 'change the gen file "%s" instead. -->\n' % doc.filename
    out += '<html>\n<head>\n'
    out += '<style>\n%s</style>\n' % css
    out += '</head>\n<body>\n'
    out += 'Documentation for structures defined in ' + doc.filename + '.<p>\n'
    for enum in doc.enums:
      out += self.VisitEnum(enum)
    for flagset in doc.flagsets:
      out += self.VisitFlagset(flagset)
    for struct in doc.structs:
      if not struct.inline:
        out += self.VisitStruct(struct)
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
    """Generates HTML documentation for a specific enum type."""
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

  def VisitFlagset(self, flagset):
    """Generates HTML documentation for set of variables representing possible bitfield flags."""
    out = ''
    out += '<h3>Flags: %s</h3>\n' % flagset.name
    if flagset.key_comment:
      out += '<p>%s</p>\n' % flagset.key_comment
    if flagset.body_comment:
      out += '<p>%s</p>\n' % flagset.body_comment
    out += '<b>Possible values</b><br>\n'
    out += '<table class="bitfieldTable">\n'
    out += '<tr><th>Name</th><th>Value</th><th>Bit pattern</th></tr>\n'
    for var in flagset.variables:
      max_bits = utils.MaxBit(flagset.MaxValue())
      bit_pattern = ' '.join(utils.BitPatternString(var.value, max_bits))
      
      out += '<tr><td>%s</td><td>0x%08x</td><td>%s</td></tr>\n' % (var.name, var.value, bit_pattern)
    out += '</table>'
    return out

  def VisitRecordField(self, field, struct, level, union_map):
    """Draws a struct as rows in a containing structure.
    
    struct is the """
    out = '<tr>\n'

    comment = ''
    if field.key_comment:
      comment += field.key_comment + '<br>'
    if field.body_comment:
      comment += '<p>%s</p>/' % (field.body_comment)

    if field.IsNoOffset():
      out += '  <td class="structBits" colspan=2></td>\n'
    elif field.StartFlit() != field.EndFlit():
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
      if union_map:
        f = ReplaceField(f, union_map)
      if f.type.IsRecord():
        out += self.VisitRecordField(f, f.type.base_type.node, level + 2,
                                     union_map)
      else:
        out += self.VisitField(f, level + 1, union_map)
    return out

  def VisitStruct(self, struct):
    out = ''
    union_inside = struct.ContainsUnion()
    if not union_inside:
      return self.VisitStructInternal(struct, struct.name, {})

    out += '<h1>Commands Related To %s</h1>\n' % struct.name
    out += '<p>There are several commands here.</p>'
    for f in union_inside.fields:
      if f.type.IsRecord():
        substruct = f.type.base_type.node
        out += self.VisitStructInternal(struct,
                                        substruct.name,
                                        {union_inside: substruct})
    return out

  def VisitStructInternal(self, struct, name, union_map):
    """Generates HTML documentation for a specific structure."""
    out = ''
    out += '<a name="%s"></a>' % name
    out += '<h3>struct %s:</h3>\n' % name
    if struct.key_comment:
      out += '<p>%s</p>\n' % struct.key_comment
    if struct.body_comment:
      out += '<p>%s</p>\n' % struct.body_comment

    out += self.BitmapForStruct(struct, union_map)

    out += '<table class="structTable">\n'
    out += '<tr>\n'
    out += '  <th class="structBits">Flit</th>\n'
    out += '  <th class="structBits">Bits</th>\n'
    out += '  <th>Type</th>'
    out += '  <th>Name</th><th>Description</th></tr>\n'
    # TODO(bowdidge): Fields and nested structures or unions should be
    # displayed in order of index.
    for field in struct.fields:
      if union_map:
        field = ReplaceField(field, union_map)
      if field.type.IsRecord():
        out += self.VisitRecordField(field, field.type.base_type.node, 0,
                                     union_map)
      else:
        out += self.VisitField(field, 0, union_map)

    # Tail comment comes after everything else.
    if struct.tail_comment:
      out += '<tr>\n'
      out += '  <td class="description" colspan="5">\n'
      out += '  <center>%s</center>\n' % struct.tail_comment
      out += '  </td>\n'
      out += '</tr>\n'
    out += "</table>\n"

    out += '<h4>Helper functions for %s</h4>\n' % name
    out += '<dl>\n'
    for function in struct.functions:
      out += '  <dt>\n    <pre>%s</pre>\n  </dt>\n' % function.declaration
      out += '  <dd>\n    %s\n  </dd>\n' % function.body_comment
    out += '</dl>\n'

    out += '<h4>Helper macros for %s</h4>\n' % name
    out += '<dl>\n'
    for macro in struct.macros:
      if len(macro.body_comment) > 0:
        out += '  <dt>\n    <pre>%s</pre>\n  </dt>\n'
        out += '  <dd>\n    %s\n  </dd>\n' % (
          macro.declaration, macro.body_comment)
    out += '</dl>\n'
    return out

  def VisitField(self, field, level, union_map):
    """Generates HTML documentation for a specific field."""
    if len(field.packed_fields) != 0:
      out = ''
      for packed_field in field.packed_fields:
        out += self.VisitField(packed_field, level + 1, union_map)
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
    elif field.IsNoOffset():
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
