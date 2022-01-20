#!/usr/bin/python2.7
# htmlgen.py
# HTMLGenerator takes a DocBuilder describing various machine data structures,
# and generates documentation for these.

import parser
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
    """Returns an array of arrays of (field name, field width, struct_group)

    struct_group is a number from 0 up that is the same for fields from
    the same structure, and is used for similar background colors for
    fields from the same structure.

    Each top-level array represents a flit and the fields in the flit.
    """
    fields = []
    rows = []
    current_row = []
    next_color = 0
    bytes_remaining = 64

    # Field wrapping to next row.
    lingering_field = None
    # Number of bits in lingering field.
    lingering_field_width = 0
    
    fields = list(struct.fields)
    field_groups = 1
    field_group = {}
    for f in fields:
      field_group[f] = 0

    while len(fields) > 0 or lingering_field_width > 0:
      if lingering_field_width > 0:
        if bytes_remaining > lingering_field_width:
          current_row.append((lingering_field, lingering_field_width,
                              field_group[lingering_field]))
          bytes_remaining -= lingering_field_width
          lingering_field_width = 0
        else:
          current_row.append((lingering_field, bytes_remaining,
                              field_group[lingering_field]))
          lingering_field_width = lingering_field_width - bytes_remaining
          bytes_remaining = 0
      else:
        next_field = fields.pop(0)
        if union_map:
          next_field = ReplaceField(next_field, union_map)

        if next_field.type.IsRecord():
          struct = next_field.type.base_type.node
          fields = list(struct.fields) + fields
          field_groups += 1
          for f in struct.fields:
            field_group[f] = field_groups
            
        elif next_field.type.IsScalar() or next_field.type.IsArray():
          if bytes_remaining >= next_field.BitWidth():
            current_row.append((next_field, next_field.BitWidth(), 
                                field_group[next_field]))
            bytes_remaining -= next_field.BitWidth()
          else:
            current_row.append((next_field, bytes_remaining,
                                field_group[next_field]))
            lingering_field = next_field
            lingering_field_width = next_field.BitWidth() - bytes_remaining
            bytes_remaining = 0

      if bytes_remaining == 0:
        rows.append(current_row)
        current_row = []
        bytes_remaining = 64
    if current_row:
      rows.append(current_row)
    return rows        

  def BarWidth(self, bits):
    """Returns width of field bar in pixels."""
    # 1000 is width of bitmap.  Subtract 2 for luck.
    return (1000 * bits / 64) - 2

  def DrawFields(self, flit, row):
    """Draws a row representing a single flit."""
    out = ''
    out += '  <div class="bitRow">\n'
    out += '    <div class="rowTitle">Flit %d</div>\n' % flit
    width_sum = 0
    for (field, width, field_group_num) in row:
      class_name = 'bar field field-group-%d' % field_group_num
      if field.is_reserved:
        class_name += ' reserved'
      out += '    <div class="%s" style="width: %dpx">%s</div>\n' % ( 
        class_name, self.BarWidth(width), field.name)
      width_sum += width
    if width_sum < 64:
      out += '  <div class="bar field" style="width: %dpx">&nbsp;</div>\n' % self.BarWidth(64 - width_sum)
    
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


  def MakeIndex(self, doc):
    """Generate list of all structs in file in a form acceptable
    at the top of the documentation.
    ."""
    out = ''
    if not doc.Structs():
      return ''

    out += '<h2>Structures</h2>\n'
    out += '<ul>'
    for struct in doc.Structs():
      out += '<li><a href="#%s">%s</a>' % (struct.name, struct.name)
      if struct.key_comment:
        out += ':' + utils.AsHTMLComment(struct.key_comment)
      out += '</li>\n'
    out += '</ul>\n'
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
  height: 40px;  
  border: 1px solid black;
}

.field-group-0 {
  background-color: #f0ffff;
}

.field-group-1 {
  background-color: #f0f0ff;
}

.field-group-2 {
  background-color: #f0fff0;
}

.field-group-3 {
  background-color: #f0f0ff;
}

.field-group-4 {
  background-color: #fff0f0;
}

.field-group-5 {
  background-color: #f0f0f0;
}

dd {
  padding-bottom:20px;
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
  /* Force a width so the bit lines don't wrap. */
  width: 1000px;
}

.bitfieldTable {
  text-align: center;
  border: solid 1px black;
}

/* Color reserved fields slightly lighter in bitmap. */
.reserved {
  opacity: 0.5;
}
""")

    out = '<!-- Documentation created by generator.py.\n'
    out += '     Do not change this file; '
    out += 'change the gen file "%s" instead. -->\n' % doc.filename
    out += '<html>\n<head>\n'
    out += '<style>\n%s</style>\n' % css
    out += '</head>\n<body>\n'
    out += 'Documentation for structures defined in ' + doc.filename + '.<p>\n'

    out += self.MakeIndex(doc)

    for d in doc.Declarations():
      if d.is_enum:
        out += self.VisitEnum(d)
      elif d.is_flagset:
        out += self.VisitFlagset(d)
      elif d.is_const:
        out += self.VisitConst(d)
      elif d.is_struct:
        if not d.inline:
          out += self.VisitStruct(d)
      else:
        print('Unexpected declaration %s found in list of top level declarations in document.' % d.name)
    out += '</body></html>'
    return out

  def VisitEnumVariable(self, enum_variable):
    # Generates HTML Documentation for a specific enum variable.
    out = '<dt><code>%s = %d</code></dt>\n' % (enum_variable.name,
                                               enum_variable.value)
    out += '<dd>\n'
    if enum_variable.key_comment:
        out += utils.AsHTMLComment(enum_variable.key_comment) + '\n'
    if enum_variable.key_comment and enum_variable.body_comment:
        out += '<br>\n'
    if enum_variable.body_comment:
        out += utils.AsHTMLComment(enum_variable.body_comment) + '\n'
    out += '</dd>\n'
    return out

  def VisitEnum(self, enum):
    """Generates HTML documentation for a specific enum type."""
    out = ''
    out += '<h3>%s: enum declaration</h3>\n' % enum.name
    if enum.key_comment:
      out += '<p><b>%s</b></p>\n' % utils.AsHTMLComment(enum.key_comment)
    if enum.body_comment:
      out += '<p>%s</p>\n' % utils.AsHTMLComment(enum.body_comment)
    out += '<b>Values</b><br>\n'
    out += '<dl>\n'
    for enum_variable in enum.variables:
      out += self.VisitEnumVariable(enum_variable)
    out += '</dl>\n'
    if enum.tail_comment:
        out += '<p>%s</p>' % utils.AsHTMLComment(enum.tail_comment)
    return out

  def VisitFlagset(self, flagset):
    """Generates HTML documentation for set of bitfield flags."""
    out = ''
    out += '<h3>%s: flagset</h3>\n' % flagset.name
    if flagset.key_comment:
      out += '<p><b>%s</b></p>\n' % utils.AsHTMLComment(flagset.key_comment)
    if flagset.body_comment:
      out += '<p>%s</p>\n' % utils.AsHTMLComment(flagset.body_comment)
    out += '<b>Possible values</b><br>\n'
    out += '<table class="bitfieldTable">\n'
    out += '<tr><th>Name</th><th>Value</th><th>Bit pattern</th></tr>\n'
    for var in flagset.variables:
      max_bits = utils.MaxBit(flagset.max_value)
      bit_pattern = ' '.join(utils.BitPatternString(var.value, max_bits))
      
      out += '<tr><td>%s</td><td>0x%08x</td><td>%s</td></tr>\n' % (var.name, var.value, bit_pattern)
    out += '</table>'
    return out

  def VisitConst(self, const):
    """Generates HTML documentation for set of constants."""
    out = ''
    out += '<h3>%s: constants</h3>\n' % const.name
    if const.key_comment:
      out += '<p><b>%s</b></p>\n' % utils.AsHTMLComment(const.key_comment)
    if const.body_comment:
      out += '<p>%s</p>\n' % utils.AsHTMLComment(const.body_comment)
    out += '<p><b>Constants</b></p>\n'
    for var in const.variables:
      out += '<p><b>%s</b>: 0x%x' % (var.name, var.value)
      if var.key_comment:
        out += ': ' + utils.AsHTMLComment(var.key_comment)
      out += '</p>\n'
      if var.body_comment:
        out += '<p>%s</p>\n' % var.body_comment

    return out

  def VisitRecordField(self, field, level, union_map):
    """Draws a struct as rows in a containing structure.
    
    struct is the """
    out = '<tr>\n'

    comment = ''
    if field.key_comment:
      comment += utils.AsHTMLComment(field.key_comment) + '<br>'
    if field.body_comment:
      comment += '<p>%s</p>/' % utils.AsHTMLComment(field.body_comment)

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
    struct = field.type.base_type.node
    if not struct.inline:
      out += '  <td>%s <a href="#%s">%s</a></td>\n' % (
        indent,
        struct.Name(),
        field.Type().ParameterTypeName(False, False))
    else:
      out += '  <td>%s%s</td>\n' % (
        indent, field.Type().ParameterTypeName(False, False))
    out += '  <td>%s</td>\n' % field.name
    out += '  <td>%s</td>\n' % utils.AsHTMLComment(comment)
    out += '</tr>\n'

    if not struct.inline:
      return out

    for f in field.subfields:
      if union_map:
        f = ReplaceField(f, union_map)
      if f.type.IsRecord():
        out += self.VisitRecordField(f, level + 2, union_map)
      else:
        out += self.VisitField(f, level + 1, union_map)
    return out

  def VisitStruct(self, struct):
    out = ''

    union_inside = struct.ContainsUnion()
    if not union_inside:
      return self.VisitStructInternal(struct, struct.name, {})

    out += '<h1>Structures Derived From %s</h1>\n' % struct.name
    out += '<p>\n'
    out += '%s contains %d unions, each defining a different message:\n' % (
      struct.name, len(union_inside.fields))
    out += utils.ReadableList([f.name for f in union_inside.fields])
    out += '.\n'
    out += '</p>\n'
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
    out += '<h3>%s: structure</h3>\n' % name
    if struct.key_comment:
      out += '<p><b>%s</b></p>\n' % utils.AsHTMLComment(struct.key_comment)
    if struct.body_comment:
      out += '<p>%s</p>\n' % utils.AsHTMLComment(struct.body_comment)

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
        out += self.VisitRecordField(field, 0, union_map)
      else:
        out += self.VisitField(field, 0, union_map)

    # Tail comment comes after everything else.
    if struct.tail_comment:
      out += '<tr>\n'
      out += '  <td class="description" colspan="5">\n'
      out += '  <center>%s</center>\n' % (
        utils.AsHTMLComment(struct.tail_comment))
      out += '  </td>\n'
      out += '</tr>\n'
    out += "</table>\n"

    out += '<h4>Helper functions for %s</h4>\n' % name
    out += '<dl>\n'
    for function in struct.functions:
      out += '  <dt>\n    <code>%s</code>\n  </dt>\n' % function.declaration
      out += '  <dd>\n    %s\n  </dd>\n' % (
        utils.AsHTMLComment(function.body_comment))
    out += '</dl>\n'

    out += '<h4>Helper macros for %s</h4>\n' % name
    out += '<dl>\n'
    for macro in struct.macros:
        out += '  <dt>\n    <code>%s</code>\n  </dt>\n' % (macro.name)
        out += '  <dd>\n    <code>%s</code>\n' % macro.body
        if macro.body_comment:
          out += '   <br>%s\n' % utils.AsHTMLComment(macro.body_comment)
        out += '  </dd>\n'
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
                                                 field.type.ParameterTypeName(False, False),
                                                 field.name)

    out += '<td class="description">\n'
    if field.key_comment:
      out += field.key_comment + '<br>'
    if field.body_comment:
        out += '<p>%s</p>/' % (field.body_comment)
    out += '</td>\n'
    out += '</tr>\n'
    return out
