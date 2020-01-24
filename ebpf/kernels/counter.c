// This is generic conter probe
#include "../bpf_helpers.h"

// eBPF map for the counter
BPF_MAP_DEF(counter) = {
    .map_type = BPF_MAP_TYPE_PERCPU_ARRAY,
    .key_size = sizeof(__u32),
    .value_size = sizeof(__u64),
    .max_entries = 1,
};
BPF_MAP_ADD(counter);


SEC("probe")
void generic_counter(void) {
  __u32 idx = 0;
  __u64 *value = bpf_map_lookup_elem(&counter, &idx);
  if (value) {
      *value += 1;
  }
}

char _license[] SEC("license") = "GPLv2";