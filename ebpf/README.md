# Ebpf client framework

## Introduction

This section represents the client side of the ebpf framework.
The ebpf client framework is intended to function as a frontend
to the ebpf service offered by FunOS.

It is API compatible with libbpf. libbpf is intricately tied to the
linux kernel. Our attempt is to make this interface generic, and
work across all OS environments.

The libbpf repository here is a mirror of the out-of-kernel bpf
repository. We will try to remain compatible with all kernel changes.


