# CSR Peek/Poke Infrastructure

## Summary

This is a tool that provides the following features:
    * Grab the most recent CSR definitions
    * Slurp them in and generate C++ files
    * Create a library out of these files that can then be integrated into other 
      upstream tools to Peek/Poke CSR registers

## How to use

The presrcibed way to use this infrastructure is through the top level make file.
The make commands **must** be executed in the following order

### Basic install

    $ make

Installs the python objects necessary to perform the next steps

### Get configurations (these are the stuff to munch on)

    $ make cfg_pull

Pulls in the necessary CSR files for the rest of the infrastructure to chew on.
This step may need to be preceded by distclean IF new CSR bits need to be pulled in.


### Generate all the files necessary for the library
    
    $ make cfg

### Finally, create the library

    $ make libcsr 

Creates the library (archive) under csr-rt. Other tools can be written both as frontend and backend
to use this tool. Frontend could be tools like dpcsh, and backend could be socket/RPC/JTAG to write these values to the chip.

An example of how to use this library is provided in csr-rt/test/prog.cpp

