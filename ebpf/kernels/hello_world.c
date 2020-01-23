// Trace printing example
  
#include "../bpf_helpers.h"

// Socket Filter program
SEC("socket_filter")
int probe_printer(void *unused) {
  bpf_trace_printk("Hello, ", 0);         
  bpf_trace_printk("World!\\n", 0);
  return SOCKET_FILTER_ALLOW;
}

char _license[] SEC("license") = "MIT";