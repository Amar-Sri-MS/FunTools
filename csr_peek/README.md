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

### Get raw files (these are the stuff to munch on)

    $ make cfg_pull

Pulls in the necessary CSR files for the rest of the infrastructure to chew on.
This step may need to be preceded by distclean IF new CSR bits need to be pulled in.


### Generate all the files necessary for the library

    $ make cfg

### Create the library

    $ make libcsr


Creates the library (archive) under csr-rt. Other tools can be written both as frontend and backend
to use this tool. Frontend could be tools like dpcsh, and backend could be socket/RPC/JTAG to write these values to the chip.

### Create the csrsh (frontend)

    $ make csrsh
Creates the csrshell executable under csr-rt/frontends/csrsh. csrsh is a debug shell that utilizes the library to provide a command line interface to set/get/examine values on the F1 chip for CSR registers.

## Cleanup

### Basic cleanup

    $ make clean

Cleans up everything, except the C++ generated files & the CSR definitions that have been pulled in

### Clean everything

    $ make distclean

Cleans up the whole distribution, including generated files. Usually, this is needed if CSR defintions have changed.

## Example Program

A simple example of how to use this library is provided in csr-rt/test/prog.cpp


Note: This only writes to a dumb backend (screen). For this library to be useful, it has to be linked against
other backends.

## Example frontend

See description of csrsh before



