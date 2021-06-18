# generator.py and Data Structure Specification

The Fungible Generator is an interface generator used to create
boilerplate functions related to data and control plane requests.  The generator
create the data structures used to communicate between CC-Linux
and F1, or between the F1 and server.

The Generator serves several purposes:
* allows bit-accurate specification of how shared data structures are laid out in memory.
* validates names and types.
* creates valid C structures defining the shared data structures
* packs variables that are bitfields and creates macros for efficiently accessing fields.
* creates uniform initialization and serialization macros or functions.
* aware of conventions such as reserved fields (for unused variables).
* generates documentation for messages and sub-structures.

Unlike other interface generators (rpcgen, protocol buffers, Thrift),
the Generator is intended for data structures transferred via shared
memory, efficiently manipulating these data structures, hiding
differences between host systems in C, and avoiding overhead.  Most
other systems are designed for communication over networks,
efficiently marshaling and demarshaling data structures in the
presence of optional fields, and supporting multiple languages
at the expense of a straightforward C mapping and efficient access.

These requests and results are implemented as C data structures copied
via PCI.  Messages can have different sizes, and may contain
variable-length parts.  At the current time, efficient processing in
different languages is not a design goal for Generator.

## Command line

Usage:
```
generator.py [-d] [-g generator-style] [-c codgen-options] [-o output_prefix] description_file
```

* -g specifies the kind of output to generate.  Choices are code (default) or html.  With ```-g code```, the generator creates header and source files based on the data structure description file.  With ```-g linux```, the generator creates a header file suitable for Linux.  With ```-g html```, the generator creates HTML documentation for the data structures.  With ```-g validate```, the generator creates test code to confirm that the size and layout of the data structures matches the specified bit ranges.
* -c specifies the code generation options to use.  This is a comma-separated list of terms.  Valid code generation options are pack, json, cpacked, swap, and dump.  The pack option rewrites the data structures so adjacent bitfields are packed together into native-sized fields for the type, and creates macros to access the field (get, put, zero).  json generates a new initialization function to allow a data structure to be initialized from a JSON description.  json generates routines to encode and decode structures in JSON format on FunOS.  cpacked causes all structures to have __attribute__(packed) appended.  swap generates functions for byte-swapping structures on Linux.
* -o specifies the path prefix to be used for output.  The generator appends .c and .h to this prefix when generating source code, or .html when generating documentation.
* -d specifies that script's dependencies should be printed to stdout.
If set, options other than ```-g``` will be ignored and a space-separated list of internal dependencies will be printed. This can be used to specify generated files' dependencies in make build rules.

Example command line

The following command line generates the source and header for the foo.gen file, and puts the output in /tmp/foo_gen.c and /tmp/foo_gen.h.

```
generator.py -g code -o /tmp/foo_gen foo.gen
```

The following command line packs the bitfields in foo.gen, and generates the JSON initialization:

```
generator.py -g code -c pack,json -o foo_gen /path/to/foo.gen
```

The following command creates the HTML documentation for foo.gen.  Note that the codegen options still need to be specified so that descriptions of the bitfield accessors are created.  The output documentation will be in foo_docs.html.

```
generator.py -g html -c pack,json -o foo_docs /path/to/foo.gen
```

The following command can be used in Makefiles to ensure dependencies are handled as needed:

    GEN_DEPS := $(shell ./generator.py -g code -d)

    /tmp/foo_gen.c /tmp/foo_gen.h: foo.gen generator.py $(GEN_DEPS)
        generator.py -g code -o /tmp/foo_gen foo.gen


## Input File Format

Descriptions of a data structure represent:
* structures (or nested structures)
* unions within structures for describing alternate contents
* field descriptions
* enum declarations for unique constant values.
* flags declarations for a group of constants for a single purpose that
are not types and may be or'd together.
* comments associated with all elements.

generator.py's input format interleaves a bitwise-description of the
data structure with a C language-like description.  The bitwise
description is at the beginning of each line; the C-like description
is on the right hand side.

```
/* Standard work unit format for all messages in F1. */
STRUCT WorkUnit
  /* destinationID is the only field in this. */
  0 7:0 uint8_t destinationID /* comment */
  /* Fourteen more bytes */
END
```

This description contains a structure, a field, and comments associated with
both.

Here, the structure WorkUnit contains a single field called destinationID.
destinationID is stored in the first flit - the first 8 bytes of the structure,
covering bits 7:0 of the first flit.  The field's type is uint8_t.
Note that fields are declared from highest bit to lowest, and bit ranges
for fields are always high:low.  Single bits can also be specified with
a single number.

The generator also supports variable-length arrays at the end of structures.
This is done by specifying a zero-size array at the end without specifying a bit
pattern:

```
STRUCT WorkUnit
  0 32:0 uint32_t count
  _ _:_ uint32 values[0]
END
```

Comments fall into two categories: inline (immediately following a
directive) or block.  Inline comments always apply to the directive on
the same line.  Block comments always apply to the following
directive.  Inline comments are always considered to be a title or
summary description.  Comments at the end of a block are associated
with the enclosing structure, and would either be considered lower
priority.  When rendering comments for documentation:

```
/* Body comment */
STRUCT WorkUnit /* key comment */
  0 0:7 uint8_t foo
  /* tail comment */
END
```

In the generated source code, the form would match the structure - key comment on
the same line as the variable, body comment preceding, tail comment
inside and at the end:
```

/* body comment */
struct WorkUnit {  /* key comment */
  uint8_t foo;
  /* tail comment */
```

In the generator file, only use C style comments for single lines ( /* ... */).
Generator only supports C++-style comments for multi-line comments ( // ... ).



The generator also defines two classes of constants: enums and flags.
Enums represent symbolic names for ordinal values in a variable, such as
names of operations encoded by a number.  Flags represent symbolic names for
bitfield values, such as a collection of bit flags.

Enums are declared like this:

```
/* Math operators. */
ENUM operator
ADD=1  /* Simple addition */
SUBTRACT = 2
MULTIPLY = 3
END
```

Enums are generated as enum types in C code.  The symbolic names and meanings are provided in HTML.
An array of strings called <enum_name>_names contains a table for looking up the symbolic name
for each enum value.  In the generated C header file, a synthetic enum value <enum_name>_max_value
is also generated which can be used for sizing arrays indexed by the enum values.

Flags represent a set of related constants that should be implemented as
separate values rather than an enum.

```
/* Action flags */
FLAGS command
CACHED = 1
DELAYED = 2
COMPLETED = 4
DELAYED_AND_COMPLETED = 6
END
```

In the generated code, flags are represented by const int declarations
and definitions.  The symbolic name, bit pattern, and documentation is
provided in HTML.  An array of strings called <flag_name>_names
contains a table for looking up the symbolic name for each
power-of-two enum value.  Powers of two without a flag defined returns
only the value.  Names are not available for non-power-of-two values.

Enum and flag names will eventually be usable as type names.  However,
support for enum and flag names as a field type currently isn't
implemented; using one of these as a type name will generate an
unknown type error.

## Types

The following type names are allowed in generator files.

unsigned, signed, char, uint8_t, uint16_t, int16_t, short, int,
uint32_t, int32_t, long, float, double, uint64_t, int64_t.

Fields can also have array type:

	  STRUCT Document
	    0 63:32 char creatorCode[4]
	    0 31:0 char fileType[4]
	  END

Array types must provide enough space for all elements.

Fields can also have the type of a previously defined structure.  Structures and unions declared
inline in a containing structure are defined as fields with the provided name:

```
STRUCT Container
  0 63:0 uint64_t value
  STRUCT Contained c
    0 63:0 uint64_t contained_value
  END
END
```

In this case, the following C code is generated:

```
struct Container {
  uint64_t value;
  struct Container {
    uint64_t contained_value;
  } c;
};
```

Structure can also be non-inline:
STRUCT A
  0 63:0 uint64_t arg0
END

STRUCT B
  0 63:0 A arg0_container
  1 63:0 uint64_t arg1;
END

This case would generate the following C code:
```
struct A {
  uint64_t arg0;
};
struct B {
  struct A arg0_container;
  uint64_t arg1;
};
```

Variable-length arrays are permitted at the end of
a top-level structure.  Variable length arrays are specified using the syntax

```
STRUCT Document
  0 63:56 char c
  _ _:_   char additional_values[0]
END
```

It is an error to use a variable length array at any place other than the
end of a structure, or include a structure with a variable-length array
at any place in another structure other than the end.

## Generated Code

For each data structure, the generator creates the following bits of code.

* Each top-level structure is turned into a C structure.  Unions and structs
nested within each top-level structure are also nested into the structure.
Types for each field are based on the defined type; if the field is packed,
then the precise size of each field is specified as a bitfield.

* Each top-level structure gets a setter function for setting the
  values of all non-array fields.  If the top-level structure contains
  a union, then separate setters are created for each union variant.
  Setter functions are not created for structures defined inline inside
  another structure.

Setter functions always have the form "struct_name_init" or
"struct_name_union_name_init".

Setter functions do not fully initialize the structure; arrays and some
other fields may not be initialized.

* For packed fields, macros are created to access the value packed into
the containing field.   Macros created are:

```
field_name_S: number of right shifts to get the final value aligned.
field_name_M: Mask for bits (after shifting)
field_name_G(struct): get value from packed structure.
field_name_P(value): gets value to put into field.  Field should be cleared
  beforehand by inserting the complement of the mask.
field_name_Z(value): Returns a value that can be and'd with a packed field to zero out the field.
```


## Additional Codegen Options

The -c option allows you to specify names of additional codegen passes to perform.
-c pack combines bitfields into a single container field where individual fields are accessed via macros.
-c json generates initialization routines that initialize the structure from JSON.
-c swap treats structures as having a specific endianness in memory, and
swaps values when stored or retrieved.  (Supported only for Linux header
generation.)
-c cpacked adds the __attribute__((packed)) to all structures.

Each option is described in more detail below.

The -c option supports multiple optinos. -c pack,json turns on both bitfield packing and JSON initialization.

## Packed fields

If you pass the '-c pack' option to generator.py, it packs contiguous bitfields
into a single field value, and generates macros to access these fields.
(Packing fields like this ensures that we keep control over how we set the
values - helpful if we want to manipulate registers efficiently.)

Packed fields must have the same base type, must be bitfields (not using all
bits of the type), and must be contiguous in the layout.

Packed field naming is as follows:
* Packed fields can include reserved fields (fields beginning with reserved
or rsvd), but the names of reserved fields aren't used in the packed field
name.
* Packed fields are generally named after the first and last field:
"a_to_z".
* If only one field is in the packed field (after reserved fields are removed),
then the name is "fieldname_pack".
* If all non-reserved fields in a packed field have a similar prefix, then
the packed field name is "prefix_pack".  The prefix must be delimited by
a _, and prefixing does not look at multiple underbars. "pre_a" and "pre_b"
will be combined into a pre_pack field, but "pre_foo_a and pre_foo_b" will
also disregard that pre_foo is a prefix and again name the packed field
"pre_pack".

## JSON

The '-c json' option causes initialization routines to be created that load values from
JSON descriptions.  The JSON initialization routine always looks like:

```
bool struct_name_json_init(struct fun_json *j, struct struct_name *s);
```

## CPACKED

The '-c cpacked' option causes the compiler extension "__attribute__(packed))"
to be added to all structures generated by this tool.  The option allows
fields and sub-structures to be aligned to byte boundaries rather than
using the natural, preferred alignments the compiler prefers to use.
(For example, structures and unions are normally aligned to 4 byte boundaries,
and uint16_t is normally aligned to a 2 byte boundary.)
This option allows specifying structure layouts that would not normally
be permitted by the compiler and may not be legal on processors.

## Future Work
* Better formatting of comments, and matching line length requirements.
(Running the Generator's output through clang-format or another formatting
tool improves code significantly, but doesn't touch comments.)
* Match Linux coding style.
* Linux-style types.
* Explicitly mark which functions represent commands or messages.  Currently,
we assume all top-level structs can be used individually, and require all
generated functions.  Nested structs might not be used individually.
Top level structures holding a union represent a set of related messages,
and should have accessors generated for each item in the union.
* Support enum names and flag names as type names.
* Allow defining a default constant value for a field.  This would be
particularly useful for specifying an opcode in a message.
