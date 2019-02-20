# Ebpf kernels (for testing)

## Pre-requisites

Requires llvm and its frontend clang. At least version 6.0.0
Has been tested on Ubuntu 18.04
```
$sudo apt-get update; 
$sudo apt-get install clang-6.0
```

## Conventions

Please follow convention to name the kernels as
```
k_01.c
k_02.c
```

Please have only one function per file. If using functions to construct the injected bytecode, 
please use [inlining attribute](https://gcc.gnu.org/onlinedocs/gcc/Inline.html) for all called functions.

Please follow standard conventions for defining args, please only use one arg per function (for now).
Please declare all args in the provided header file. It is copied over to FunOS on make install so that
it can be used directly in tests.

## Compiling

`make` generates (by default) ebpf bytecode for the BPF VM.
`make install` installs this to the checked out FunOS repo tests. Modify ebpf_test under tests appropriately.
`make clean` removes everything (except already installed stuff in FunOS)
