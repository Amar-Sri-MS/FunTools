#!/usr/bin/python

# generator.py
# Generator takes descriptions of structures describing device commands
# and automatically generates header files, documentation, and other
# products from the description.
#
# Generator can also pack structures with many small fields into
# single fields accessed via macros.  By explicitly providing accessor
# macros, we can avoid cases where compiled code may be inefficient.
#
# Robert Bowdidge August 8, 2016.
# Copyright Fungible Inc. 2016.

import fileinput
import getopt
import hashlib
import os
import subprocess
import sys

import codegen
import htmlgen
import parser
import utils

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template


def CommonPrefix(name_list):
  """Returns the longest prefix (followed by underbar) of all names.
  Returns None if no longest prefix.
  """
  if len(name_list) < 2:
    return None

  first_name = name_list[0]
  if not '_' in first_name:
    return None

  prefix = name_list[0].split('_')[0]
  for name in name_list[1:]:
    if not name.startswith(prefix + '_'):
      return None
  return prefix

def FirstNonReservedName(field_list):
  """Returns name of first field that is not a reserved field.
  Returns None if no such field exists.
  """
  first_name = None
  for field in field_list:
    if not field.is_reserved:
      return field.name
  return None

def LastNonReservedName(field_list):
  """Returns name of last field that is not a reserved field.
  Returns None if no such field exists.
  """
  last_name = None
  for field in field_list:
    if not field.is_reserved:
      last_name = field.name
  return last_name

def ChoosePackedFieldName(fields):
  """Chooses the name for a packed field base on the fields in that field."""
  not_reserved_names = [f.name for f in fields if not f.is_reserved]
  common_prefix = CommonPrefix(not_reserved_names)

  if common_prefix:
    return common_prefix + '_pack'

  first_name = FirstNonReservedName(fields)
  last_name = LastNonReservedName(fields)
  # No fields.
  if first_name is None and last_name is None:
    return "empty_pack"

  # One field.
  if first_name == last_name:
    return first_name + '_pack'

  return first_name + "_to_" + last_name


class Pass:
  def __init__(self):
    self.current_document = None
    self.errors = []

  def AddError(self, node, msg):
    if node.filename:
      location = '%s:%d: ' % (node.filename, node.line_number)
    else:
      location = '%d: ' % node.line_number
    self.errors.append(location + msg)

  def VisitDocument(self, doc):
    # Pack all structures in the named documents.
    self.doc = doc
    for struct in doc.Structs():
      self.VisitStruct(struct)
    return self.errors

  def VisitStruct(self, struct):
    pass

  def VisitEnum(self, enum):
    pass

  def VisitFlagset(self, enum):
    pass


class Splitter(Pass):
  """Splits fields crossing flit boundaries into separate fields."""
  def __init__(self):
    Pass.__init__(self)

  def VisitStruct(self, struct):
    for f in struct.fields:
      if f.StartFlit() != f.EndFlit():
        # TODO(bowdidge): Implement splitter.
        self.AddError(f, "TODO: split field %s" % f.name)

class Packer(Pass):
  """ Searches all structures for bitfields that can be combined.

  We generally don't trust compilers to do a good job on accessing
  bitfields, especially for registers.  By convention, we'd prefer to
  combine those accesses into explicit shifts and masks so we know
  what our code is doing.

  This pass runs through all structures, and looks for adjacent
  bitfields with identical types.  These bitfields are replaced with
  a single field declaration; macros are then added for accessing
  the contents of the field.
  """
  def __init__(self):
    Pass.__init__(self)

  def VisitStruct(self, the_struct):
    # Gather fields by flit, then create macros for each.
    # Should make sure that adjacent fields are same types.
    if not the_struct.is_union:
      self.PackStruct(the_struct)

  def ChoosePackGroups(self, the_fields):
    """Identify and group fields in a flit that deserve to be packed.
    Returns array of proposed packed variables, with each group being
    a tuple of (type, [fields to pack in variable) in that group.
    """
    # Contiguous fields to pack.  When we reach the end of a set of fields to be packed togther,
    # we move them to fields_to_pack.
    fields_to_pack = []

    # Current group of fields to be packed together.
    current_group = []

    # Common type for all in current group of fields to be packed together.
    current_type = None
    # total bits of space used by current_group
    bits_occupied = 0

    for field in the_fields:

      # End the previous group of packed fields if the current field
      # can be a field on its own, if the current field does not match the group's
      # field, or if the packed field is already full (or too full).
      # Code outside checks for packed fields too large for the type.
      if (field.type.BitWidth() == field.BitWidth() or
          current_type != field.type or
          bits_occupied >= field.type.BitWidth()):
        fields_to_pack.append((current_type, current_group))
        current_group = []
        current_type = None
        bits_occupied = 0

      current_group.append(field)
      if (len(current_group) == 1):
        current_type = field.type
      bits_occupied += field.BitWidth()

    fields_to_pack.append((current_type, current_group))

    # Return only the groups that had more than one field in them.
    return [pack_group for pack_group in fields_to_pack if len(pack_group[1]) > 1]

  def PackFlit(self, the_struct, flit_number, the_fields):
    """Replaces contiguous sets of bitfields with macros to access.
    the_struct: structure containing fields to be packed.
    flit_number: which flit of the structure is handled this time.
    the_fields: list of fields in this flit.
    """
    # All fields to pack. List of tuples of (type, [fields to pack])
    fields_to_pack = []

    fields_to_pack = self.ChoosePackGroups(the_fields)

    if len(fields_to_pack) == 0:
      # Nothing to pack.
      return
    for (type, fields) in fields_to_pack:
      packed_field_width = 0
      min_start_offset = min([f.StartOffset() for f in fields])
      for f in fields:
        packed_field_width += f.BitWidth()

      if (packed_field_width > type.BitWidth()):
        self.AddError(the_struct,
                      'Width of packed bit-field containing %s (%d bits) exceeds width of its type (%d bits). '% (
            utils.ReadableList([f.name for f in fields]),
            packed_field_width,
            type.BitWidth()))

      new_field_name = ChoosePackedFieldName(fields)
      new_field = parser.Field(new_field_name, type, min_start_offset,
                               packed_field_width)
      new_field.line_number = fields[0].line_number

      non_reserved_fields = [f.name for f in fields if not f.is_reserved]
      bitfield_name_str = utils.ReadableList(non_reserved_fields)
      bitfield_layout_str = ''

      min_end_bit = min([f.EndBit() for f in fields])
      for f in fields:
        # TODO(bowdidge): Fix.
        bitfield_layout_str += '      %d:%d: %s\n' % (f.StartBit() - min_end_bit,
                                                      f.EndBit() - min_end_bit,
                                                      f.name)
        new_field.body_comment = "Combines bitfields %s.\n%s" % (bitfield_name_str,
                                                                bitfield_layout_str)

      # Replace first field to be removed with new field, and delete rest.
      for i, f in enumerate(the_struct.fields):
        if f == fields[0]:
          new_field.packed_fields.append(f)
          the_struct.fields[i] = new_field
          new_field.parent_struct = the_struct
          f.packed_field = new_field
          break
      for f in fields[1:]:
        new_field.packed_fields.append(f)
        f.packed_field = new_field
        the_struct.fields.remove(f)


  def PackStruct(self, the_struct):
    # Get rid of old struct fields, and use macros on flit-sized
    # fields to access.
    new_fields = []
    flit_field_map = the_struct.FlitFieldMap()

    for flit, fields_in_flit in flit_field_map.iteritems():
      self.PackFlit(the_struct, flit, fields_in_flit)


def Usage():
  sys.stderr.write('generator.py: usage: [-p] [-g [code, html] [-o file]\n')
  sys.stderr.write('-c options: change codegen options.\n')
  sys.stderr.write('-g code: generate header file to stdout (default)\n')
  sys.stderr.write('-g html: generate HTML description of header\n')
  sys.stderr.write('-o filename_base: send output to named file\n')
  sys.stderr.write('                  for code generation, appends correct extension.\n')
  sys.stderr.write('Codegen options include:\n')
  sys.stderr.write('  pack: combine multiple bitfields into a single:\n')
  sys.stderr.write('        field, and create accessor macros.\n')
  sys.stderr.write('  json: generate routines for initializing a structure\n')
  sys.stderr.write('        from a JSON representation.')
  sys.stderr.write('  cpacked: use __attribute__((packed)) on all structures\n')
  sys.stderr.write('        to allow fields to be at non-natural alignments.\n')
                   
  sys.stderr.write('Example: -c json,nopack enables json, and disables packing.\n')

def ReformatCode(source):
  """Rewrites the source to match Linux coding style.

  Tries several tools to see what's available.
  """
  # We prefer clang-format because it reformats source code much nicer,
  # and because it does a better job of removing blank lines.
  out = ReformatCodeWithClangFormat(source)
  if out:
    return out

  out = ReformatCodeWithIndent(source)
  if out:
    return out

  # If no indent tool is available, just provide the un-formatted code.
  return source


def ReformatCodeWithIndent(source):
  """Reformats provided source with GNU indent.

  Returns None if indent not found.
  """
  possible_indent_binaries = ['/usr/bin/indent']

  indent_path = None
  for bin in possible_indent_binaries:
    if os.path.isfile(bin):
      indent_path = bin
      break

  if not indent_path:
    return None

  args = [indent_path, '-sob', '-nfc1', '-nfcb', '-nbad', '-bap',
          '-nbc', '-br', '-brs', '-c33', '-cd33', '-ncdb', '-ce', '-ci4',
          '-cli0', '-d0', '-i8', '-ip0', '-l80', '-lp', '-npcs', '-npsl',
          # Don't format comments, get rid of extra blank lines.
          # Don't add whitespace in the middle of declarations.
          '-nsc', '-sob', '-di0']

  p = subprocess.Popen(args,
                       stdout=subprocess.PIPE,
                       stdin=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       bufsize=1)
  # indent requires line feed after last line.
  out = p.communicate(source + '\n')

  # If there was an indent fail
  if (p.returncode != 0):
    print "%s returned error %d, ignoring output" % (indent_path, p.returncode)
    return None

  return out[0]

def ReformatCodeWithClangFormat(source):
  """Reformats provided source with clang-format.

  Returns None if indent not found.
  """
  possible_indent_binaries = ['/usr/bin/clang-format',
                              '/usr/local/bin/clang-format']

  indent_path = None
  for bin in possible_indent_binaries:
    if os.path.isfile(bin):
      indent_path = bin
      break

  if not indent_path:
    return None

  args = [indent_path,
          '-style={BasedOnStyle: LLVM, IndentWidth: 8, UseTab: Always, '
          'BreakBeforeBraces: Linux, MaxEmptyLinesToKeep: 1, '
          'ColumnLimit: 80}']

  p = subprocess.Popen(args,
                       stdout=subprocess.PIPE,
                       stdin=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       bufsize=1)
  # Make sure there's a line feed after last line.
  out = p.communicate(source + '\n')
  # If there was an indent fail
  if (p.returncode != 0):
    print "%s returned error %d, ignoring output" % (indent_path, p.returncode)
    return None

  return out[0]

# Incremented whenever the generator's algorithm changes in ways that
# would affect output.
GENERATOR_VERSION = 0

def FileHash(filename):
  """Returns an integer representing the contents of the file.

  Value will be unique for different contents, and will also be unique
  if generator version changes.
  """
  try:
    f = open(filename)
  except Exception as err:
    # No file?  Probably testing or stdin.
    return GENERATOR_VERSION
  readFile = f.read()
  f.close()
  hash_as_int = int(hashlib.md5(readFile).hexdigest(), 16)
  return (hash_as_int & 0xfffffff) + GENERATOR_VERSION

def GenerateFromTemplate(doc, template_filename, generator_file, output_base,
                         extra_vars):
  """Creates source file and header for parsed gen file from templates.
  doc: reference to parsed gen file.
  template_filename: the file containing the template to render.
  generator_file: name of the .gen file, used for identifying origins in code.
  output_base: prefix to use on output file
  extra_vars: array of additional variables to set in template.
  """
  this_dir = os.path.dirname(os.path.abspath(__file__))

  env = Environment(loader=FileSystemLoader(this_dir))
  env.lstrip_blocks = True
  env.trim_blocks = True

  # Filters - to do more complex transformations.
  # Filers for strings and names.
  env.filters['as_macro'] = utils.AsUppercaseMacro
  env.filters['as_html'] = utils.AsHTMLComment
  env.filters['as_line'] = utils.AsLine
  env.filters['as_lower'] = utils.AsLower
  env.filters['as_comment'] = utils.AsComment

  # Filters for numbers.
  env.filters['as_hex'] = lambda num: "0x%x" % num

  # Filters for declarations.
  env.filters['as_definition'] = lambda decl : decl.DefinitionString()
  env.filters['as_declaration'] = lambda decl : decl.DeclarationString()
  env.filters['as_cast'] = lambda type : type.CastString()

  if output_base:
    output_base = os.path.basename(output_base)
  else:
    output_base = 'foo_gen'

  gen_file_version_hash = FileHash(generator_file)

  jinja_docs = {
    'gen_file' : os.path.basename(generator_file),
    'output_base' : output_base,
    'original_filename' : generator_file,
    'enums': doc.Enums(),
    'flagsets': doc.Flagsets(),
    'structs' : [x for x in doc.Structs() if not x.is_union],
    'declarations': doc.Declarations(),
    'extra_vars': extra_vars,
    'gen_file_version_hash': gen_file_version_hash
    }

  for var in extra_vars:
    jinja_docs[var] = True

  template = env.get_template(template_filename)
  return template.render(jinja_docs, env=env)

def PrintErrors(error_list):
  """Prints the list of errors to stderr."""
  for e in error_list:
    sys.stderr.write("%s\n" % e)


def WriteFile(filename, contents):
  """Writes generated code to a specified file."""
  f = open(filename, 'w')
  f.write(contents)
  f.close()


# TODO(bowdidge): Create options dictionary to replace all these arguments.
def GenerateFile(output_style, output_base, input_stream, input_filename,
                 options):
  """Generate header or HTML based on options.

  Returns (generated source for output, errors).
  Generated source may be "" if output_base specified output should go to a file.
  """
  # Process a single .gen file and create the appropriate header/docs.
  doc = None
  errors = None

  if input_filename.endswith('.gen') or input_filename.endswith('.pgen'):
    gen_parser = parser.GenParser()
    errors = gen_parser.Parse(input_filename, input_stream)
    doc = gen_parser.current_document
  elif input_filename.endswith('.yaml'):
    yaml_parser = parser.YAMLParser()
    errors = yaml_parser.Parse(input_filename)
    doc = yaml_parser.current_document
  else:
    error = 'Expected input filename to end in .gen or .yaml, got %s.' % (
        input_filename)
    error += 'Rename file to match input file format.'
    return (None, [error])

  if errors:
    return (None, errors)

  c = parser.Checker()
  c.VisitDocument(doc)
  if len(c.errors) != 0:
    return (None, c.errors)

  if 'pack' in options:
    p = Packer()
    errors = p.VisitDocument(doc)
    if errors:
      return (None, errors)

  if 'split' in options:
    s = Splitter()
    errors = s.VisitDocument(doc)
    import pdb
    pdb.set_trace()
    if errors:
      return (None, errors)

  # Convert list of extra codegen features into variables named
  #  generate_{{codegen-style}} that will be in the template.
  extra_vars = ['generate_' + o for o in options]
  if output_style is OutputStyleHTML:
    html_generator = htmlgen.HTMLGenerator()
    codegen.CodeGenerator(options)
    source = html_generator.VisitDocument(doc)
    if output_base:
      WriteFile(output_base + '.html', source)
      return (None, [])
    else:
      return (source, [])

  elif output_style is OutputStyleValidation:
    # TODO(bowdidge): Compile and run the code too.
    source = GenerateFromTemplate(doc, 'validate.tmpl', input_filename,
                                  output_base, extra_vars)
    if output_base:
      WriteFile(output_base + '.validate.c', source)
      return ('', [])
    return (source, [])

  elif output_style is OutputStyleKernel:
    header = GenerateFromTemplate(doc, 'kernel.tmpl', input_filename,
                                  output_base, extra_vars)
    if not header:
      return (None, ["Problems generating output from template."])
    header = ReformatCode(header)
    if output_base:
      WriteFile(output_base + '.h', header)
      return ("", [])
    else:
      return (header, [])
      

  elif output_style is OutputStyleHeader:
    header = GenerateFromTemplate(doc, 'header.tmpl', input_filename,
                                  output_base, extra_vars)
    source = GenerateFromTemplate(doc, 'source.tmpl', input_filename,
                                  output_base, extra_vars)

    if not header or not source:
      return (None, ["Problems generating output from templates."])

    header = ReformatCode(header)
    source = ReformatCode(source)

    if output_base:
      WriteFile(output_base + '.h', header)
      WriteFile(output_base + '.c', source)
      return ("", [])

    out = '/* Header file */\n' +  header + '/* Source file */\n' + source
    return (out, [])

# Output styles supported by generator.

# Output in the FunHCI format with C structures.
OutputStyleHeader = 1
# Output HTML documentation for FunHCI structures.
OutputStyleHTML = 2
# Output validation code for FunHCI structure sizes.
OutputStyleValidation = 3
# Output kernel-style shift macros for hardware structures.
OutputStyleKernel = 4


def SetFromArgs(key, codegen_args, default_value):
  """Returns whether setting 'key' should be set based on provided args.
  key is a name for a codegen setting.
  codegen_args is an array of arguments provided by the user which can
  include either name (to set the value) or noname (to not set the value).
  default_value names the value for the key if it is not in codegen_args.
  """

  if key in codegen_args:
    return True
  if 'no' + key in codegen_args:
    return False
  return default_value

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'tc:g:o:',
                               ['help', 'output=', 'codegen='])
  except getopt.GetoptError as err:
    print str(err)
    Usage()
    sys.exit(2)

  output_style = OutputStyleHeader
  output_base = None
  codegen_args = []

  for o, a in opts:
    if o in ('-h', '--help'):
      Usage()
      sys.exit(2)
    elif o in ('-o', '--output'):
      output_base = a
    elif o in ('-c', '--codegen'):
      codegen_args = a.split(',')
    elif o == '-g':
      if a == 'code':
        output_style = OutputStyleHeader
      elif a == 'html':
        output_style = OutputStyleHTML
      elif a == 'validate':
        output_style = OutputStyleValidation
      elif a == 'kernel':
        output_style = OutputStyleKernel
      else:
        sys.stderr.write('Unknown output style "%s"' % a)
        sys.exit(2)
    else:
      assert False, 'Unhandled option %s' % o

  codegen_pack = SetFromArgs('pack', codegen_args, False)
  codegen_split = SetFromArgs('split', codegen_args, False)
  codegen_json = SetFromArgs('json', codegen_args, False)
  codegen_swap = SetFromArgs('swap', codegen_args, False)
  codegen_cpacked = SetFromArgs('cpacked', codegen_args, False)

  codegen_options = []

  if codegen_pack:
    codegen_options.append('pack')
  if codegen_split:
    codegen_options.append('split')
  if codegen_json:
    codegen_options.append('json')
  if codegen_swap:
    codegen_options.append('swap')
  if codegen_cpacked:
    codegen_options.append('cpacked')

  if (codegen_swap and not codegen_pack):
    print('WARNING - swapping will not work correctly on '
          'unpacked bitfields.')

  if len(args) == 0:
      sys.stderr.write('No genfile named.\n')
      sys.exit(2)

  if len(args) > 1:
      print('Can only process one gen file at a time.')
      sys.exit(2)

  input_stream = open(args[0], 'r')

  (out, errors) = GenerateFile(output_style, output_base, input_stream, args[0],
                               codegen_options)

  if errors:
    PrintErrors(errors)
    # Enable hard errors when fun_hci is clean.
    sys.exit(1)

  if out:
    print out

if __name__ == '__main__':
  main()
