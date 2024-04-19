#!/usr/bin/env python3

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

class AlignmentChecker(Pass):
  """Checks all fields in data structures match packing rules."""

  def __init__(self, packed):
    """Creates an alignment checker.

    If packed is false, then the checker assumes alignment will match
    MIPS and x86 ABIs for clang and gcc.

    If packed is true, then the checker assumes alignment must match
    behavior if __attribute__((packed)) is attached to all structures.
    """
    Pass.__init__(self)
    self.packed_attribute = packed

  def IsNaturalWidth(self, field):
    """Returns true if the field represents a non-bitfield."""
    if field.type.IsRecord():
      return True
    return field.type.BitWidth() == field.BitWidth()

  def Alignment(self, field):
    """Returns alignment of field in bits.
    General rules:
    * bitfields are aligned to 1 bit boundaries (as long as grouped
      together.)
    * when the packed attribute is put on the structure, the compiler
      will align to 8 bits.
    * structures and pointers want to align to 32 bit boundaries.
    * plain old data types align to their size.
    * Arrays (both zero dimension and with finite dimension) follow
      the same rules.  Unpacked structures align the array to the alignment
      of the base type, and align to 1 byte boundaries if packed.
    """
    if not self.IsNaturalWidth(field):
      return 1

    if self.packed_attribute:
      return 8

    if field.type.IsRecord():
      return 32

    if field.type.IsArray():
      return field.type.base_type.BitWidth()

    return field.type.BitWidth()

  def VisitStruct(self, struct):
    """Checks whether all fields are correctly aligned."""
    prev_field_was_bitfield = False
    for field in struct.fields:
      is_bitfield = not self.IsNaturalWidth(field)
      reason = ''

      alignment = self.Alignment(field)

      if not prev_field_was_bitfield and is_bitfield:
        alignment = 32
        reason = ' because of switch from non-bitfield to bitfield'

      if prev_field_was_bitfield and not is_bitfield:
        alignment = 32
        reason = ' because of switch from bitfield to non-bitfield'

      # Start offset is None if field is a variable-sized array.
      start_offset = field.StartOffset()
      if start_offset is None:
        start_offset = struct.EndOffset() + 1

      if start_offset % alignment != 0:
        self.AddError(field, 'Field "%s" cannot be placed at location.'
                      'Expected alignment: %d bits%s.  '
                      'Field at bit offset %d.' % (field.Name(), alignment,
                                                   reason,
                                                   start_offset))
      prev_field_was_bitfield = is_bitfield

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
          (not current_type or not current_type.IsSameType(field.type)) or
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
                      'Width of packed bit-field containing %s (%d bits) '
                      'exceeds width of its type (%d bits). '% (
            utils.ReadableList([f.name for f in fields]),
            packed_field_width,
            type.BitWidth()))

      new_field_name = ChoosePackedFieldName(fields)

      if the_struct.HasFieldWithName(new_field_name):
        self.AddError(
          'Can\'t create packed field: '
          'Field with name "%s" already exists in struct "%s"' % (
          new_field_name, the_struct.Name()))
        return

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

    for flit, fields_in_flit in flit_field_map.items():
      self.PackFlit(the_struct, flit, fields_in_flit)


def Usage():
  sys.stderr.write('generator.py: usage: [-d] [-c <options>] [-g [code, html]] [-o file]\n')
  sys.stderr.write('-c options: comma-separated list of codegen options\n')
  sys.stderr.write('-g code: generate header file to stdout (default)\n')
  sys.stderr.write('-g html: generate HTML description of header\n')
  sys.stderr.write('-o filename_base: send output to named file\n')
  sys.stderr.write('                  for code generation, appends correct extension\n')
  sys.stderr.write('-d dump generator\'s runtime dependencies\n')
  sys.stderr.write('\nCodegen options include:\n')
  sys.stderr.write('  pack: combine multiple bitfields into a single field,\n')
  sys.stderr.write('        and create accessor macros.\n')
  sys.stderr.write('  json: generate routines for initializing a structure\n')
  sys.stderr.write('        from a JSON representation.\n')
  sys.stderr.write('  dump: generate routines to dump a hex representation\n')
  sys.stderr.write('        of all structures.\n')
  sys.stderr.write('  cpacked: use __attribute__((packed)) on all structures\n')
  sys.stderr.write('        to allow fields to be at non-natural alignments.\n')
  sys.stderr.write('  swap: emit byte-swapping code\n')
  sys.stderr.write('  linux: generate code suitable for Linux and Windows\n')
  sys.stderr.write('         user- and kernel-space apps and drivers\n')
  sys.stderr.write('  be: generate code only for BE FunOS\n')
  sys.stderr.write('  le: generate code only for LE FunOS\n')
  sys.stderr.write('  init_macros: generate macros rather than inline functions\n')
  sys.stderr.write('               to initialize HCI structures\n')
  sys.stderr.write('  mangle: mangle field names in generated structures\n')

  sys.stderr.write('\nExample: -c json,nopack enables json, and disables packing.\n')

def ReformatCode(source):
  """Rewrites the source to match Linux coding style.

  Tries several tools to see what's available.
  """
  # We prefer AStyle because it reformats source code much nicer,
  # and because it does a better job of removing blank lines.
  out = ReformatCodeWithAStyle(source)
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

  args_wanted = ['-sob', '-nfc1', '-nfcb', '-nbad', '-bap',
          '-nbc', '-br', '-brs', '-c33', '-cd33', '-ncdb', '-ce', '-ci4',
          '-cli0', '-d0', '-i8', '-ip0', '-l79', '-lp', '-npcs', '-npsl',
          # Don't format comments, get rid of extra blank lines.
          # Don't add whitespace in the middle of declarations.
          '-nsc', '-sob', '-di0']

  args = [indent_path]

  with open(os.devnull, 'r+') as dummy:
    for arg in args_wanted:
      if not subprocess.call([indent_path, arg], stdin=dummy, stdout=dummy, stderr=dummy):
        args.append(arg)

  p = subprocess.Popen(args,
                       stdout=subprocess.PIPE,
                       stdin=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
  # indent requires line feed after last line.
  source = source + '\n'
  out = p.communicate(source.encode('utf-8'))

  # If there was an indent fail
  if (p.returncode != 0):
    print("%s returned error %d, ignoring output" % (indent_path, p.returncode))
    return None

  return out[0].decode('utf-8')

def ReformatCodeWithAStyle(source):
  """Reformats provided source with AStyle.

  Returns None if indent not found.
  """
  possible_indent_binaries = ['/usr/bin/astyle',
                              '/usr/local/bin/astyle']

  indent_path = None
  for bin in possible_indent_binaries:
    if os.path.isfile(bin):
      indent_path = bin
      break

  if not indent_path:
    return None

  args = [indent_path,
          '--style=knf', '--delete-empty-lines', '--indent=force-tab=8',
          '--max-code-length=80']

  p = subprocess.Popen(args,
                       stdout=subprocess.PIPE,
                       stdin=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
  # Make sure there's a line feed after last line.
  source = source + '\n'
  out = p.communicate(source.encode('utf-8'))
  # If there was an indent fail
  if (p.returncode != 0):
    print("%s returned error %d, ignoring output" % (indent_path, p.returncode))
    return None

  return out[0].decode('utf-8')

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
  hash_as_int = int(hashlib.md5(readFile.encode('utf-8')).hexdigest(), 16)
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

  # 'linux' in extra variables indicates that we're building a header
  # for Linux.  Use Linux-style declarations.
  linux = 'linux' in extra_vars

  # Building header with byte-swapping when storing to structure.
  swap = 'generate_swap' in extra_vars

  # Don't use endian types by default.  None=plain type, True=big.
  big_endian_types = None
  if linux and swap:
    big_endian_types = True

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
  env.filters['as_definition'] = (
    lambda decl : decl.DefinitionString(linux, big_endian_types))
  env.filters['as_declaration'] = lambda decl :  decl.DeclarationString(linux)
  env.filters['as_cast'] = lambda type : type.CastString(linux)
  env.filters['as_mangled'] = lambda field : field.MangledName()
  env.filters['type_only'] = lambda field : field.type.DeclarationName(linux)

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
  """Writes generated code to a specified file.

  filename: string name of file to send output to.
  contents: bytes containing contents.
  """
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
    use_linux_types = (output_style == OutputStyleLinux)
    mangle_fields = 'mangle' in options
    dpu_endianness = 'Any'
    if 'be' in options:
        dpu_endianness = 'BE'
    elif 'le' in options:
        dpu_endianness = 'LE'
    gen_parser = parser.GenParser(use_linux_types, dpu_endianness, mangle_fields)
    errors = gen_parser.Parse(input_filename, input_stream)
    doc = gen_parser.current_document
  else:
    error = 'Expected input filename to end in .gen, got %s.' % (
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
    p.VisitDocument(doc)
    if len(p.errors) != 0:
      return (None, p.errors)

  # Check alignment of the final fields.
  attr_packed_struct = 'pack' in options
  aligner = AlignmentChecker(attr_packed_struct)
  aligner.VisitDocument(doc)
  if len(aligner.errors) != 0:
    return (None, aligner.errors)

  if 'split' in options:
    s = Splitter()
    s.VisitDocument(doc)
    if len(s.errors) != 0:
      return (None, s.errors)

  # Convert list of extra codegen features into variables named
  #  generate_{{codegen-style}} that will be in the template.
  extra_vars = ['generate_' + o for o in options]
  if output_style is OutputStyleHTML:
    html_generator = htmlgen.HTMLGenerator()
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

  elif output_style is OutputStyleLinux:
    # TODO(bowdidge): Find better way to pass fact that we need Linux types
    # into GenerateFromTemplate - it needs to know that it should generate
    # declarations differently.
    extra_vars.append('linux')
    header = GenerateFromTemplate(doc, 'header-linux.tmpl', input_filename,
                                  output_base, extra_vars)
    source = GenerateFromTemplate(doc, 'source-linux.tmpl', input_filename,
                                  output_base, extra_vars)
    if not header:
      return (None, ["Problems generating output from template."])
    header = ReformatCode(header)
    source = ReformatCode(source)
    if output_base:
      WriteFile(output_base + '.h', header)
      WriteFile(output_base + '.c', source)
      return ("", [])

  elif output_style is OutputStyleWindows:
    extra_vars.append('windows')
    header = GenerateFromTemplate(doc, 'header-windows.tmpl', input_filename,
                                  output_base, extra_vars)
    if not header:
      return (None, ["Problems generating output from template."])
    header = ReformatCode(header)
    if output_base:
      WriteFile(output_base + '.h', header)
      return ("", [])

    else:
      # For testing, combine source and headers.
      return (header + source, [])


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
# Output Linux headers.
OutputStyleLinux = 5
# Output Windows headers.
OutputStyleWindows = 6


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

def ShowDeps(style):
  deps = []
  basepath = os.path.dirname(os.path.realpath(__file__))
  if style == OutputStyleHeader:
    deps.extend(['header.tmpl', 'source.tmpl'])
  elif style == OutputStyleValidation:
    deps.extend(['validate.tmpl'])
  elif style == OutputStyleLinux:
    deps.extend(['header-linux.tmpl', 'source-linux.tmpl'])
  elif style == OutputStyleWindows:
    deps.extend(['header-windows.tmpl'])

  print(' '.join(os.path.join(basepath, f) for f in deps))


def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'hc:g:o:d',
                               ['help', 'output=', 'codegen=', 'deps'])
  except getopt.GetoptError as err:
    print(str(err))
    Usage()
    sys.exit(2)

  output_style = OutputStyleHeader
  output_base = None
  codegen_args = []
  show_deps = False

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
      elif a == 'linux':
        output_style = OutputStyleLinux
      elif a == 'windows':
        output_style = OutputStyleWindows
      else:
        sys.stderr.write('Unknown output style "%s"' % a)
        sys.exit(2)
    elif o in ('-d', '--deps'):
      show_deps = True
    else:
      assert False, 'Unhandled option %s' % o

  if show_deps:
    ShowDeps(output_style)
    sys.exit(0)

  codegen_pack = SetFromArgs('pack', codegen_args, False)
  codegen_split = SetFromArgs('split', codegen_args, False)
  codegen_json = SetFromArgs('json', codegen_args, False)
  codegen_dump = SetFromArgs('dump', codegen_args, False)
  codegen_cpacked = SetFromArgs('cpacked', codegen_args, False)
  codegen_swap = SetFromArgs('swap', codegen_args, False)
  codegen_linux = SetFromArgs('linux', codegen_args, False)
  codegen_be = SetFromArgs('be', codegen_args, False)
  codegen_le = SetFromArgs('le', codegen_args, False)
  codegen_init_macros = SetFromArgs('init_macros', codegen_args, False)
  codegen_mangle = SetFromArgs('mangle', codegen_args, False)

  if codegen_be and codegen_le:
    sys.stderr.write('\'be\' and \'le\' codegen options are mutually exclusive\n')
    sys.exit(2)

  codegen_options = []

  if codegen_pack:
    codegen_options.append('pack')
  if codegen_split:
    codegen_options.append('split')
  if codegen_json:
    codegen_options.append('json')
  if codegen_dump:
    codegen_options.append('dump')
  if codegen_cpacked:
    codegen_options.append('cpacked')
  if codegen_swap:
    codegen_options.append('swap')
  if codegen_be:
    codegen_options.append('be')
  if codegen_le:
    codegen_options.append('le')
  if codegen_init_macros:
    codegen_options.append('init_macros')
  if codegen_mangle:
    codegen_options.append('mangle')

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
    print(out)

if __name__ == '__main__':
  main()
