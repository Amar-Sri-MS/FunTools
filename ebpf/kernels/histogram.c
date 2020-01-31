// This is generic histogram probe
// to compile:
// $ clang -I./ -O2 -target mips64r6 -c kernels/histogram.c -v -emit-llvm
// $ llc histogram.bc -filetype=obj

#include "../bpf_helpers.h"

BPF_HISTOGRAM(hist);


SEC("prehook")
void generic_histogram(size_t value) {
  bpf_histogram_inc(&hist, value);
}

char _license[] SEC("license") = "GPLv2";