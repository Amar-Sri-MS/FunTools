# eBPF FunOS client

## Introduction

This section represents the client side of the eBPF framework.
The eBPF client framework is intended to function as a frontend
to the eBPF service offered by FunOS.

The intent is to provide functionality and usability level similar to BCC.

There are `trace points` and `probes` in FunOS. Trace points are limited to
the sites that are defined statically, probes can be attached to any FunOS
function at runtime, you need to have your image compiled with debug information
to be able to get memory location for hooking.

Probe example can be found in `dpc_probe.py`.

## Interacting With Kernels

`bpf_client.py` provides an interface to read and write maps to interact with
hooks that are loaded into FunOS. Check `test_basics.py` to see an example of read-write workflow.

## Using Predefined Kernels

There are kernels for counters and histograms, you may check `dpc_probe.py`
script to see how to use them. If you need to check latency for particular function
all you need to change function name inside of the script.

## Compiling Custom Kernels

To compile a hook targeting BPF architecture please run:
```sh
clang -I./ -O2 -target bpf -c kernels/counter.c -o kernels/counter.elf
```

However, only native code is supported for probing. Compile for MIPS R6 to generate native code.

ELF parsing and hooking are separated to have ability to hook with no dependency on ELF tooling. Use `extract_hook.py` to transform ELF into JSON. Use `function_to_ptr.py` to extract the information about function location in the memory.

Feel free to reach out `renat.idrisov@fungible.com` if you have questions.