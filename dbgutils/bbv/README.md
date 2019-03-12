# BBV utility

This is a utility for performing some amount of static code analysis on any MIPS64 elf binary.
It uses the cross compiler objdump to perform some amount of static code analysis

## Usage
The script currently allows performs histogramming for [basic block](https://en.wikipedia.org/wiki/Basic_block) 
It excludes any basic block exceeding an instruction count of 20.
The script also allows for histogramming for function instruction count.
The make target currently generates the histogram as a png for storage.

The makefile can be modified for any MIPS64 ELF target. It currently works off a locally compiled FunOS-F1 binary

## Prerequisites

Please install pandas, matplotlib and seaborn using pip

## Notes
