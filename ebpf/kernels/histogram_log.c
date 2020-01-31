// This is generic conter probe
#include "../bpf_helpers.h"

BPF_HISTOGRAM(hist);

SEC("prehook")
void generic_histogram(size_t value) {
  bpf_histogram_log_inc(&hist, value);
}

char _license[] SEC("license") = "GPLv2";