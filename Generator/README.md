# generator.py and Data Structure Specification

The Fungible Generator an interface generator used to create
boilerplate functions related to data and control plane requests and
responses sent from the central cluster or host server and the F1.
Generator describes data structures used to communicate between CC-Linux
and F1, or between the F1 and server.

The Generator serves several purposes:
* allows bit-accurate specification of how shared data structures are laid out in memory.
* validates names and types.
* creates valid C structures defining the shared data structures
* packs variables that are bitfields and creates for efficiently accessing fields.
* creates uniform initialization and serialization routines.
* aware of conventions such as reserved fields (for unused variables).
* generation of documentation for messages and sub-structures.

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

The generator's input takes high-level descriptions of data structures
used in interchange.  It creates helper functions to initialize the
data structure, access packed fields with predictable code. It also
produces documentations defining those data structures.  generator.py
is intended for software-only structures.  Hardware specifications
(such as CSR descriptions) should use the existing Perl scripts for
describing hardware registers.

The generator script also transforms the structures in various ways
for efficiency.  The first supported conversion, "packing", avoids
inefficient compiled code by replacing multiple bitfields with a
larger field to fit a full C type.  It defines accessor macros to get
and set from the multiple fields in a single access.

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

Comments for work unit would print:
```
key comment 
body comment
tail comment
```

Use C style comments for single lines ( /* ... */). 
Generator only supports C++-style comments for multi-line comments ( // ... ).

In source code, the form would match the structure - key comment on
the same line as the variable, body comment preceding, tail comment
inside and at the end.

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
for each enum value.

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

## Packed fields

If you pass the -p option to generator.py, it packs contiguous bitfields
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
```


To do:
* Better formatting of comments, and matching line length requirements.
(Running the Generator's output through clang-format or another formatting
tool improves code significantly, but doesn't touch comments.)
* Match Linux coding patterns.
* Linux-style types.
* Explicitly mark which functions represent commands or messages.  Currently,
we assume all top-level structs can be used individually, and require all
generated functions.  Nested structs might not be used individually.
Top level structures holding a union represent a set of related messages,
and should have accessors generated for each item in the union.
* Support enum names and flag names as type names.
* Allow defining a default constant value for a field.  This would be
particularly useful for specifying an opcode in a message.
* Endian-swappers?