# eBPF FunOS client

## Introduction

This section represents the client side of the eBPF framework.
The eBPF client framework is intended to function as a frontend
to the eBPF service offered by FunOS.

The intent is to provide functionality and usability level similar to BCC.

## Compiling Kernels

```sh
clang -I./ -O2 -target bpf -c kernels/counter.c -o kernels/counter.elf
```
