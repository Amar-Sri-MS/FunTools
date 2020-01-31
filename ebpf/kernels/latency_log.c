// This is generic conter probe
#include "../bpf_helpers.h"

BPF_HISTOGRAM(hist);


SEC("prehook")
size_t latency_prehook(void) {
  return bpf_ktime_get_ns();
}

SEC("posthook")
void latency_posthook(size_t value) {
  bpf_histogram_log_inc(&hist, bpf_ktime_get_ns() - value);
}

char _license[] SEC("license") = "GPLv2";
