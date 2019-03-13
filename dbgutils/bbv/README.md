# Static code analysis

This is a basic utility for performing histogram on instruction counts on basic blocks on any MIPS64 elf binary.
It uses the cross compiler objdump to perform some amount of static code analysis

## Basic instruction count analysis
The script currently allows performs histogramming for [basic block](https://en.wikipedia.org/wiki/Basic_block) 
The script also allows for histogramming for function instruction count.
The makefile can be modified for any MIPS64 ELF target. It currently works off a locally compiled FunOS-F1 binary

## Prerequisites

Please install pandas, matplotlib and seaborn using pip

## Detailed analysis

More detailed analysis can be performed using NSA released open source tool, [Ghidra](https://www.nsa.gov/resources/everyone/ghidra/)
It can be downloaded from [here](https://ghidra-sre.org/)
Ghidra REQUIRES Oracle's JDK11 at a minumum. Please install from [here](https://jdk.java.net/11/) for your architecture.
Please make sure to set the following two variables JAVA_HOME (path where the JDK is installed), and modify your path to include javac, java under JAVA_HOME.
Once installed, you can perform static analysis for binaries of any architecture (MIPS64be) included.
Running this tool requires a beefy system, so please make sure that you run this on a server.





