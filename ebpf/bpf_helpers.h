// This file was copied from https://github.com/dropbox/goebpf
// License could be found there, it is GPLv2

// Copyright (c) 2019 Dropbox, Inc.
// Full license can be found in the LICENSE file.

// BPF helpers
// Set of defines / prototypes to use from eBPF programs as well as from regular
// linux/mac "cross" compilation.

#ifndef __BPF_HELPERS_H
#define __BPF_HELPERS_H

// Standard types.
// Due to tooons of dependencies in standard linux kernel headers
// Define types explicitly.
typedef unsigned short __u16;  // NOLINT
typedef unsigned char __u8;
typedef unsigned int __u32;
typedef unsigned long long __u64;
typedef int __s32;
typedef unsigned long size_t;
typedef __u32 __be32;
typedef __u16 __be16;

// BPF map types
enum bpf_map_type {
  BPF_MAP_TYPE_UNSPEC = 0,
  BPF_MAP_TYPE_HASH,
  BPF_MAP_TYPE_ARRAY,
  BPF_MAP_TYPE_PROG_ARRAY,
  BPF_MAP_TYPE_PERF_EVENT_ARRAY,
  BPF_MAP_TYPE_PERCPU_HASH,
  BPF_MAP_TYPE_PERCPU_ARRAY,
  BPF_MAP_TYPE_STACK_TRACE,
  BPF_MAP_TYPE_CGROUP_ARRAY,
  BPF_MAP_TYPE_LRU_HASH,
  BPF_MAP_TYPE_LRU_PERCPU_HASH,
  BPF_MAP_TYPE_LPM_TRIE,
  BPF_MAP_TYPE_ARRAY_OF_MAPS,
  BPF_MAP_TYPE_HASH_OF_MAPS,
  BPF_MAP_TYPE_DEVMAP,
  BPF_MAP_TYPE_SOCKMAP,
  BPF_MAP_TYPE_CPUMAP,
  BPF_MAP_TYPE_XSKMAP,
  BPF_MAP_TYPE_SOCKHASH,
  BPF_MAP_TYPE_CGROUP_STORAGE,
  BPF_MAP_TYPE_REUSEPORT_SOCKARRAY,
  BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE,
  BPF_MAP_TYPE_QUEUE,
  BPF_MAP_TYPE_STACK,
  BPF_MAP_TYPE_SK_STORAGE,
};

/* flags for BPF_MAP_UPDATE_ELEM command */
#define BPF_ANY     0 /* create new element or update existing */
#define BPF_NOEXIST 1 /* create new element if it didn't exist */
#define BPF_EXIST   2 /* update existing element */
#define BPF_F_LOCK  4 /* spin_lock-ed map_lookup/map_update */

// A helper structure used by eBPF C program
// to describe map attributes to BPF program loader
struct bpf_map_def {
  __u32 map_type;
  __u32 key_size;
  __u32 value_size;
  __u32 max_entries;
  __u32 map_flags;
  // Array/Hash of maps use case: pointer to inner map template
  void *inner_map_def;
  // Define this to make map system wide ("object pinning")
  // path could be anything, like '/sys/fs/bpf/foo'
  // WARN: You must have BPF filesystem mounted on provided location
  const char *persistent_path;
};

#define BPF_MAP_DEF_SIZE sizeof(struct bpf_map_def)
#define BPF_MAP_OFFSET_PERSISTENT offsetof(struct bpf_map_def, persistent_path)
#define BPF_MAP_OFFSET_INNER_MAP offsetof(struct bpf_map_def, inner_map_def)

// XDP related constants
enum xdp_action {
  XDP_ABORTED = 0,
  XDP_DROP,
  XDP_PASS,
  XDP_TX,
  XDP_REDIRECT,
};

// Socket Filter programs return code
enum socket_filter_action {
  SOCKET_FILTER_DENY = 0,
  SOCKET_FILTER_ALLOW,
};

#define bpf_likely(X) __builtin_expect(!!(X), 1)
#define bpf_unlikely(X) __builtin_expect(!!(X), 0)
#define UNUSED __attribute__((unused))

// In order to cross compile BPF program for BPF / Linux / Mac
// we need to define platform specific things like:
// 1. Custom (non kernel) implementation for bpf_map_* functions
// 2. For BPF we need to put programs into special sections, but, for
//    regular linux target (mostly for tests) we don't.
// 3. BPF does not support function calls, so __always_inline__ is must have.
//    However, for testing it doesn't make sense.
// 4. Debug prints - for BPF it is done by calling helper, for linux just
// regular printf()

// Clang for eBPF missed static_assert declaration because programs are C, not
// CPP
#define static_assert _Static_assert

// Helper macro to place programs, maps, license in
// different sections in ELF file.
#define SEC(NAME) __attribute__((section(NAME), used))

// eBPF does not support functions (yet), so, all functions MUST be inlined.
// Starting from kernel 4.16 it is not required to always inline functions
// since support has been added
#define INLINE __attribute__((__always_inline__))

// XDP metadata - basically data packet
// P.S. for some reason XDP programs uses 32bit pointers
struct xdp_md {
  __u32 data;
  __u32 data_end;
  __u32 data_meta;
};

/* user accessible mirror of in-kernel sk_buff.
 * new fields can only be added to the end of this structure
 */
struct __sk_buff {
  __u32 len;
  __u32 pkt_type;
  __u32 mark;
  __u32 queue_mapping;
  __u32 protocol;
  __u32 vlan_present;
  __u32 vlan_tci;
  __u32 vlan_proto;
  __u32 priority;
  __u32 ingress_ifindex;
  __u32 ifindex;
  __u32 tc_index;
  __u32 cb[5];
  __u32 hash;
  __u32 tc_classid;
  __u32 data;
  __u32 data_end;
  __u32 napi_id;

  /* Accessed by BPF_PROG_TYPE_sk_skb types from here to ... */
  __u32 family;
  __u32 remote_ip4;  /* Stored in network byte order */
  __u32 local_ip4;  /* Stored in network byte order */
  __u32 remote_ip6[4];  /* Stored in network byte order */
  __u32 local_ip6[4];  /* Stored in network byte order */
  __u32 remote_port;  /* Stored in network byte order */
  __u32 local_port;  /* stored in host byte order */
  /* ... here. */

  __u32 data_meta;
};

struct bpf_sock_tuple {
	union {
		struct {
			__be32 saddr;
			__be32 daddr;
			__be16 sport;
			__be16 dport;
		} ipv4;
		struct {
			__be32 saddr[4];
			__be32 daddr[4];
			__be16 sport;
			__be16 dport;
		} ipv6;
	};
};

struct bpf_spin_lock {
	__u32	val;
};

struct bpf_sysctl {
	__u32	write;		/* Sysctl is being read (= 0) or written (= 1).
				 * Allows 1,2,4-byte read, but no write.
				 */
	__u32	file_pos;	/* Sysctl file position to read from, write to.
				 * Allows 1,2,4-byte read an 4-byte write.
				 */
};

#ifdef __BPF__
// BPF helper functions supported on linux kernel 5.2+
// clang-format off
#define __BPF_FUNC_MAPPER(FN)       \
     FN(unspec),                    \
     FN(map_lookup_elem),           \
     FN(map_update_elem),           \
     FN(map_delete_elem),           \
     FN(probe_read),                \
     FN(ktime_get_ns),              \
     FN(trace_printk),              \
     FN(histogram_inc),         \
     FN(histogram_log_inc),     \
     FN(get_prandom_u32),           \
     FN(get_smp_processor_id),      \
     FN(skb_store_bytes),           \
     FN(l3_csum_replace),           \
     FN(l4_csum_replace),           \
     FN(tail_call),                 \
     FN(clone_redirect),            \
     FN(get_current_pid_tgid),      \
     FN(get_current_uid_gid),       \
     FN(get_current_comm),          \
     FN(get_cgroup_classid),        \
     FN(skb_vlan_push),             \
     FN(skb_vlan_pop),              \
     FN(skb_get_tunnel_key),        \
     FN(skb_set_tunnel_key),        \
     FN(perf_event_read),           \
     FN(redirect),                  \
     FN(get_route_realm),           \
     FN(perf_event_output),         \
     FN(skb_load_bytes),            \
     FN(get_stackid),               \
     FN(csum_diff),                 \
     FN(skb_get_tunnel_opt),        \
     FN(skb_set_tunnel_opt),        \
     FN(skb_change_proto),          \
     FN(skb_change_type),           \
     FN(skb_under_cgroup),          \
     FN(get_hash_recalc),           \
     FN(get_current_task),          \
     FN(probe_write_user),          \
     FN(current_task_under_cgroup), \
     FN(skb_change_tail),           \
     FN(skb_pull_data),             \
     FN(csum_update),               \
     FN(set_hash_invalid),          \
     FN(get_numa_node_id),          \
     FN(skb_change_head),           \
     FN(xdp_adjust_head),           \
     FN(probe_read_str),            \
     FN(get_socket_cookie),         \
     FN(get_socket_uid),            \
     FN(set_hash),                  \
     FN(setsockopt),                \
     FN(skb_adjust_room),           \
     FN(redirect_map),              \
     FN(sk_redirect_map),           \
     FN(sock_map_update),           \
     FN(xdp_adjust_meta),           \
     FN(perf_event_read_value),     \
     FN(perf_prog_read_value),      \
     FN(getsockopt),                \
     FN(override_return),           \
     FN(sock_ops_cb_flags_set),     \
     FN(msg_redirect_map),          \
     FN(msg_apply_bytes),           \
     FN(msg_cork_bytes),            \
     FN(msg_pull_data),             \
     FN(bind),                      \
     FN(xdp_adjust_tail),           \
     FN(skb_get_xfrm_state),        \
     FN(get_stack),                 \
     FN(skb_load_bytes_relative),   \
     FN(fib_lookup),                \
     FN(sock_hash_update),          \
     FN(msg_redirect_hash),         \
     FN(sk_redirect_hash),          \
     FN(lwt_push_encap),            \
     FN(lwt_seg6_store_bytes),      \
     FN(lwt_seg6_adjust_srh),       \
     FN(lwt_seg6_action),           \
     FN(rc_repeat),                 \
     FN(rc_keydown),                \
     FN(skb_cgroup_id),             \
     FN(get_current_cgroup_id),     \
     FN(get_local_storage),         \
     FN(sk_select_reuseport),       \
     FN(skb_ancestor_cgroup_id),    \
     FN(sk_lookup_tcp),             \
     FN(sk_lookup_udp),             \
     FN(sk_release),                \
     FN(map_push_elem),             \
     FN(map_pop_elem),              \
     FN(map_peek_elem),             \
     FN(msg_push_data),             \
     FN(msg_pop_data),              \
     FN(rc_pointer_rel),            \
     FN(spin_lock),                 \
     FN(spin_unlock),               \
     FN(sk_fullsock),               \
     FN(tcp_sock),                  \
     FN(skb_ecn_set_ce),            \
     FN(get_listener_sock),         \
     FN(skc_lookup_tcp),            \
     FN(tcp_check_syncookie),       \
     FN(sysctl_get_name),           \
     FN(sysctl_get_current_value),  \
     FN(sysctl_get_new_value),      \
     FN(sysctl_set_new_value),      \
     FN(strtol),                    \
     FN(strtoul),                   \
     FN(sk_storage_get),            \
     FN(sk_storage_delete),         \
     FN(send_signal),

#define __BPF_ENUM_FN(x) BPF_FUNC_ ## x
enum bpf_func_id {
    __BPF_FUNC_MAPPER(__BPF_ENUM_FN)
    __BPF_FUNC_MAX_ID,
};
#undef __BPF_ENUM_FN
// clang-format on

// BPF helper functions - this construction looks complicated, but actually
// it explained to just:
//      static void* bpf_map_lookup_elem(void *map, void *key) = 1
// In other words bpf_map_lookup_elem points to memory address 0x1 - which is
// BPF function number 1.
// More details about helper functions at: http://docs.cilium.io/en/v1.1/bpf/
// Search for "Helper Functions"
// clang-format off

// Lookup bpf map element by key.
// Return: Map value or NULL
static void *(*bpf_map_lookup_elem)(const void *map, const void *key) = (void *)  // NOLINT
    BPF_FUNC_map_lookup_elem;

// Update bpf map element by key to value
// Return: 0 on success or negative error
static int (*bpf_map_update_elem)(const void *map, const void *key,
                                  const void *value, __u64 flags) = (void *)  // NOLINT
    BPF_FUNC_map_update_elem;

// Delete element. Actually applicable on HASH maps
// Return: 0 on success or negative error
static int (*bpf_map_delete_elem)(const void *map, void *key) = (void *)  // NOLINT
    BPF_FUNC_map_delete_elem;

static int (*bpf_probe_read)(void *dst, __u64 size, const void *unsafe_ptr) = (void *) // NOLINT
    BPF_FUNC_probe_read;

static __u64 (*bpf_ktime_get_ns)(void) = (void *) // NOLINT
    BPF_FUNC_ktime_get_ns;

static void (*bpf_histogram_inc)(void *map, __u64 key) = (void *) // NOLINT
    BPF_FUNC_histogram_inc;

static void (*bpf_histogram_log_inc)(void *map, __u64 key) = (void *) // NOLINT
    BPF_FUNC_histogram_log_inc;

static __u32 (*bpf_get_prandom_u32)(void) = (void *) // NOLINT
    BPF_FUNC_get_prandom_u32;

// Like printf() for BPF
// Return: length of buffer written or negative error
static int (*bpf_trace_printk)(const char *fmt, int fmt_size, ...) = (void *)  // NOLINT
    BPF_FUNC_trace_printk;

static int (*bpf_probe_read_str)(void *dst, __u64 size, const void *unsafe_ptr) = (void *) // NOLINT
    BPF_FUNC_probe_read_str;

// Jump into another BPF program
//     prog_array_map: pointer to map which type is BPF_MAP_TYPE_PROG_ARRAY
//     index: 32-bit index inside array that selects specific program to run
// Return: 0 on success or negative error
 static void (*bpf_tail_call)(const void *ctx, void *map, int index) = (void *)  // NOLINT
    BPF_FUNC_tail_call;

static int (*bpf_clone_redirect)(void *ctx, int ifindex, __u32 flags) = (void*) // NOLINT
     BPF_FUNC_clone_redirect;

static __u64 (*bpf_get_smp_processor_id)(void) = (void*) // NOLINT
     BPF_FUNC_get_smp_processor_id;

static __u64 (*bpf_get_current_pid_tgid)(void) = (void*) // NOLINT
     BPF_FUNC_get_current_pid_tgid;

static __u64 (*bpf_get_current_uid_gid)(void) = (void*) // NOLINT
     BPF_FUNC_get_current_uid_gid;

static int (*bpf_get_current_comm)(void *buf, int buf_size) = (void*) // NOLINT
     BPF_FUNC_get_current_comm;

static __u64 (*bpf_get_cgroup_classid)(void *ctx) = (void*) // NOLINT
     BPF_FUNC_get_cgroup_classid;

static __u64 (*bpf_skb_vlan_push)(void *ctx, __u16 proto, __u16 vlan_tci) = (void*) // NOLINT
     BPF_FUNC_skb_vlan_push;

static __u64 (*bpf_skb_vlan_pop)(void *ctx) = (void*) // NOLINT
     BPF_FUNC_skb_vlan_pop;

static int (*bpf_skb_get_tunnel_key)(void *ctx, void *to, __u32 size, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_skb_get_tunnel_key;

static int (*bpf_skb_set_tunnel_key)(void *ctx, void *from, __u32 size, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_skb_set_tunnel_key;

static __u64 (*bpf_perf_event_read)(void *map, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_perf_event_read;

static int (*bpf_redirect)(int ifindex, __u32 flags) = (void*) // NOLINT
     BPF_FUNC_redirect;

static __u32 (*bpf_get_route_realm)(void *ctx) = (void*) // NOLINT
     BPF_FUNC_get_route_realm;

static int (*bpf_perf_event_output)(void *ctx, void *map, __u64 index, void *data, __u32 size) = (void*) // NOLINT
     BPF_FUNC_perf_event_output;

static int (*bpf_skb_load_bytes)(void *ctx, int offset, void *to, __u32 len) = (void*) // NOLINT
     BPF_FUNC_skb_load_bytes;

static int (*bpf_perf_event_read_value)(void *map, __u64 flags, void *buf, __u32 buf_size) = (void*) // NOLINT
     BPF_FUNC_perf_event_read_value;

static int (*bpf_perf_prog_read_value)(void *ctx, void *buf, __u32 buf_size) = (void*) // NOLINT
     BPF_FUNC_perf_prog_read_value;

static int (*bpf_current_task_under_cgroup)(void *map, int index) = (void*) // NOLINT
     BPF_FUNC_current_task_under_cgroup;

static __u32 (*bpf_get_socket_cookie)(void *ctx) = (void*) // NOLINT
     BPF_FUNC_get_socket_cookie;

static __u64 (*bpf_get_socket_uid)(void *ctx) = (void*) // NOLINT
     BPF_FUNC_get_socket_uid;

static int (*bpf_getsockopt)(void *ctx, int level, int optname, void *optval, int optlen) = (void*) // NOLINT
     BPF_FUNC_getsockopt;

static int (*bpf_redirect_map)(void *map, int key, int flags) = (void*) // NOLINT
     BPF_FUNC_redirect_map;

static int (*bpf_set_hash)(void *ctx, __u32 hash) = (void*) // NOLINT
     BPF_FUNC_set_hash;

static int (*bpf_setsockopt)(void *ctx, int level, int optname, void *optval, int optlen) = (void*) // NOLINT
     BPF_FUNC_setsockopt;

static int (*bpf_skb_adjust_room)(void *ctx, int len_diff, __u32 mode, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_skb_adjust_room;

static int (*bpf_skb_under_cgroup)(void *ctx, void *map, int index) = (void*) // NOLINT
     BPF_FUNC_skb_under_cgroup;

static struct bpf_sock *(*bpf_skc_lookup_tcp)(void *ctx, struct bpf_sock_tuple *tuple, int size,
                                              unsigned long long netns_id,
                                              unsigned long long flags) = (void*) // NOLINT
     BPF_FUNC_skc_lookup_tcp;

static int (*bpf_sk_redirect_map)(void *ctx, void *map, int key, int flags) = (void*) // NOLINT
     BPF_FUNC_sk_redirect_map;

static int (*bpf_sock_map_update)(void *map, void *key, void *value, unsigned long long flags) = (void*) // NOLINT
     BPF_FUNC_sock_map_update;

static int (*bpf_strtol)(const char *buf, size_t buf_len, __u64 flags, long *res) = (void*) // NOLINT
     BPF_FUNC_strtol;

static int (*bpf_strtoul)(const char *buf, size_t buf_len, __u64 flags, unsigned long *res) = (void*) // NOLINT
     BPF_FUNC_strtoul;

static int (*bpf_sysctl_get_current_value)(struct bpf_sysctl *ctx, char *buf, size_t buf_len) = (void*) // NOLINT
     BPF_FUNC_sysctl_get_current_value;

static int (*bpf_sysctl_get_name)(struct bpf_sysctl *ctx, char *buf, size_t buf_len, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_sysctl_get_name;

static int (*bpf_sysctl_get_new_value)(struct bpf_sysctl *ctx, char *buf, size_t buf_len) = (void*) // NOLINT
     BPF_FUNC_sysctl_get_new_value;

static int (*bpf_sysctl_set_new_value)(struct bpf_sysctl *ctx, const char *buf, size_t buf_len) = (void*) // NOLINT
     BPF_FUNC_sysctl_set_new_value;

static int (*bpf_tcp_check_syncookie)(struct bpf_sock *sk, void *ip, int ip_len, void *tcp,
                                      int tcp_len) = (void*) // NOLINT
     BPF_FUNC_tcp_check_syncookie;

// Adjust the xdp_md.data_meta by delta
//     ctx: pointer to xdp_md
//     delta: An positive/negative integer to be added to ctx.data_meta
// Return: 0 on success or negative on error
static int (*bpf_xdp_adjust_meta)(void *ctx, int offset) = (void*) // NOLINT
     BPF_FUNC_xdp_adjust_meta;

static int (*bpf_get_stackid)(void *ctx, void *map, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_get_stackid;

static int (*bpf_csum_diff)(void *from, __u64 from_size, void *to, __u64 to_size, __u64 seed) = (void*) // NOLINT
     BPF_FUNC_csum_diff;

static int (*bpf_skb_get_tunnel_opt)(void *ctx, void *md, __u32 size) = (void*) // NOLINT
     BPF_FUNC_skb_get_tunnel_opt;

static int (*bpf_skb_set_tunnel_opt)(void *ctx, void *md, __u32 size) = (void*) // NOLINT
     BPF_FUNC_skb_set_tunnel_opt;

static int (*bpf_skb_change_proto)(void *ctx, __u16 proto, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_skb_change_proto;

static int (*bpf_skb_change_type)(void *ctx, __u32 type) = (void*) // NOLINT
     BPF_FUNC_skb_change_type;

static __u32 (*bpf_get_hash_recalc)(void *ctx) = (void*) // NOLINT
     BPF_FUNC_get_hash_recalc;

static __u64 (*bpf_get_current_task)(void) = (void*) // NOLINT
     BPF_FUNC_get_current_task;

static int (*bpf_probe_write_user)(void *dst, void *src, __u32 size) = (void*) // NOLINT
     BPF_FUNC_probe_write_user;

static int (*bpf_skb_change_tail)(void *ctx, __u32 new_len, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_skb_change_tail;

static int (*bpf_skb_pull_data)(void *ctx, __u32 len) = (void*) // NOLINT
     BPF_FUNC_skb_pull_data;

static int (*bpf_csum_update)(void *ctx, __u16 csum) = (void*) // NOLINT
     BPF_FUNC_csum_update;

static int (*bpf_set_hash_invalid)(void *ctx) = (void*) // NOLINT
     BPF_FUNC_set_hash_invalid;

static int (*bpf_get_numa_node_id)(void) = (void*) // NOLINT
     BPF_FUNC_get_numa_node_id;

static int (*bpf_skb_change_head)(void *ctx, __u32 len, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_skb_change_head;


static int (*bpf_override_return)(void *pt_regs, unsigned long rc) = (void*) // NOLINT
     BPF_FUNC_override_return;

static int (*bpf_sock_ops_cb_flags_set)(void *skops, int flags) = (void*) // NOLINT
     BPF_FUNC_sock_ops_cb_flags_set;

static int (*bpf_msg_redirect_map)(void *msg, void *map, __u32 key, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_msg_redirect_map;

static int (*bpf_msg_apply_bytes)(void *msg, __u32 bytes) = (void*) // NOLINT
     BPF_FUNC_msg_apply_bytes;

static int (*bpf_msg_cork_bytes)(void *msg, __u32 bytes) = (void*) // NOLINT
     BPF_FUNC_msg_cork_bytes;

static int (*bpf_msg_pull_data)(void *msg, __u32 start, __u32 end, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_msg_pull_data;

static int (*bpf_bind)(void *ctx, void *addr, int addr_len) = (void*) // NOLINT
     BPF_FUNC_bind;

static int (*bpf_xdp_adjust_tail)(void *ctx, int offset) = (void*) // NOLINT
     BPF_FUNC_xdp_adjust_tail;

static int (*bpf_skb_get_xfrm_state)(void *ctx, __u32 index, void *xfrm_state, __u32 size, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_skb_get_xfrm_state;

static int (*bpf_get_stack)(void *ctx, void *buf, __u32 size, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_get_stack;

static int (*bpf_skb_load_bytes_relative)(void *ctx, __u32 offset, void *to, __u32 len, __u32 start_header) = (void*) // NOLINT
     BPF_FUNC_skb_load_bytes_relative;

static int (*bpf_fib_lookup)(void *ctx, void *params, int plen, __u32 flags) = (void*) // NOLINT
     BPF_FUNC_fib_lookup;

static int (*bpf_sock_hash_update)(void *ctx, void *map, void *key, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_sock_hash_update;

static int (*bpf_msg_redirect_hash)(void *ctx, void *map, void *key, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_msg_redirect_hash;

static int (*bpf_sk_redirect_hash)(void *ctx, void *map, void *key, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_sk_redirect_hash;

static int (*bpf_lwt_push_encap)(void *skb, __u32 type, void *hdr, __u32 len) = (void*) // NOLINT
     BPF_FUNC_lwt_push_encap;

static int (*bpf_lwt_seg6_store_bytes)(void *ctx, __u32 offset, const void *from, __u32 len) = (void*) // NOLINT
     BPF_FUNC_lwt_seg6_store_bytes;

static int (*bpf_lwt_seg6_adjust_srh)(void *ctx, __u32 offset, __s32 delta) = (void*) // NOLINT
     BPF_FUNC_lwt_seg6_adjust_srh;

static int (*bpf_lwt_seg6_action)(void *ctx, __u32 action, void *param, __u32 param_len) = (void*) // NOLINT
     BPF_FUNC_lwt_seg6_action;

static int (*bpf_rc_keydown)(void *ctx, __u32 protocol, __u64 scancode, __u32 toggle) = (void*) // NOLINT
     BPF_FUNC_rc_keydown;

static int (*bpf_rc_repeat)(void *ctx) = (void*) // NOLINT
     BPF_FUNC_rc_repeat;

static __u64 (*bpf_skb_cgroup_id)(void *skb) = (void*) // NOLINT
     BPF_FUNC_skb_cgroup_id;

static __u64 (*bpf_get_current_cgroup_id)(void) = (void*) // NOLINT
     BPF_FUNC_get_current_cgroup_id;

static __u64 (*bpf_skb_ancestor_cgroup_id)(void *skb, int ancestor_level) = (void*) // NOLINT
     BPF_FUNC_skb_ancestor_cgroup_id;

static void * (*bpf_get_local_storage)(void *map, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_get_local_storage;

static int (*bpf_sk_select_reuseport)(void *reuse, void *map, void *key, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_sk_select_reuseport;

static struct bpf_sock *(*bpf_sk_lookup_tcp)(void *ctx,
                                             struct bpf_sock_tuple *tuple,
                                             int size, unsigned int netns_id,
                                             unsigned long long flags) = (void*) // NOLINT
     BPF_FUNC_sk_lookup_tcp;

static struct bpf_sock *(*bpf_sk_lookup_udp)(void *ctx,
                                             struct bpf_sock_tuple *tuple,
                                             int size, unsigned int netns_id,
                                             unsigned long long flags) = (void*) // NOLINT
     BPF_FUNC_sk_lookup_udp;

static int (*bpf_sk_release)(struct bpf_sock *sk) = (void*) // NOLINT
     BPF_FUNC_sk_release;

static int (*bpf_map_push_elem)(void *map, const void *value, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_map_push_elem;

static int (*bpf_map_pop_elem)(void *map, void *value) = (void*) // NOLINT
     BPF_FUNC_map_pop_elem;

static int (*bpf_map_peek_elem)(void *map, void *value) = (void*) // NOLINT
     BPF_FUNC_map_peek_elem;

static int (*bpf_msg_push_data)(void *skb, __u32 start, __u32 len, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_msg_push_data;

static int (*bpf_msg_pop_data)(void *msg, __u32 start, __u32 pop, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_msg_pop_data;

static int (*bpf_rc_pointer_rel)(void *ctx, __s32 rel_x, __s32 rel_y) = (void*) // NOLINT
     BPF_FUNC_rc_pointer_rel;

static void (*bpf_spin_lock)(struct bpf_spin_lock *lock) = (void*) // NOLINT
     BPF_FUNC_spin_lock;

static void (*bpf_spin_unlock)(struct bpf_spin_lock *lock) = (void*) // NOLINT
     BPF_FUNC_spin_unlock;

static struct bpf_sock *(*bpf_sk_fullsock)(struct bpf_sock *sk) = (void*) // NOLINT
     BPF_FUNC_sk_fullsock;

static struct bpf_tcp_sock *(*bpf_tcp_sock)(struct bpf_sock *sk) = (void*) // NOLINT
     BPF_FUNC_tcp_sock;

static int (*bpf_skb_ecn_set_ce)(void *ctx) = (void*) // NOLINT
     BPF_FUNC_skb_ecn_set_ce;

static struct bpf_sock *(*bpf_get_listener_sock)(struct bpf_sock *sk) = (void*) // NOLINT
     BPF_FUNC_get_listener_sock;

static void *(*bpf_sk_storage_get)(void *map, struct bpf_sock *sk,
                                   void *value, __u64 flags) = (void*) // NOLINT
     BPF_FUNC_sk_storage_get;

static int (*bpf_sk_storage_delete)(void *map, struct bpf_sock *sk) = (void*) // NOLINT
    BPF_FUNC_sk_storage_delete;

static int (*bpf_send_signal)(unsigned sig) = (void *) // NOLINT
    BPF_FUNC_send_signal;

// Adjust the xdp_md.data by delta
//     ctx: pointer to xdp_md
//     delta: An positive/negative integer to be added to ctx.data
// Return: 0 on success or negative on error
static int (*bpf_xdp_adjust_head)(const void *ctx, int delta) = (void *) // NOLINT
    BPF_FUNC_xdp_adjust_head;

// clang-format on

#else
//// JIT ////

// Lookup bpf map element by key.
// Return: Map value or NULL
void *bpf_map_lookup_elem(const void *map, const void *key);

// Update bpf map element by key to value
// Return: 0 on success or negative error
int *bpf_map_update_elem(const void *map, const void *key,
                                  const void *value, __u64 flags);

// Delete element. Actually applicable on HASH maps
// Return: 0 on success or negative error
int *bpf_map_delete_elem(const void *map, void *key);

int *bpf_probe_read(void *dst, __u64 size, const void *unsafe_ptr);

__u64 bpf_ktime_get_ns();

// Like printf() for BPF
// Return: length of buffer written or negative error
int *bpf_trace_printk(const char *fmt, int fmt_size, ...);

// Increase an element in an array defined with bpf_histogram
// a value may be out of bounds, in this case, the last one will be increased
void bpf_histogram_inc(void *map, __u64 key);

// Same as bpf_histogram_inc with additional log(x) before increase
void bpf_histogram_log_inc(void *map, __u64 key);

#endif

///// end of __BPF__ /////

// printk() - kernel trace mechanism, like printf()
// To get trace (debug) messages:
// - Add #define DEBUG into your eBPF program before includes
// - $ sudo cat /sys/kernel/debug/tracing/trace
#ifdef DEBUG
#define bpf_printk(fmt, ...)                                   \
  ({                                                           \
    char ____fmt[] = fmt;                                      \
    bpf_trace_printk(____fmt, sizeof(____fmt), ##__VA_ARGS__); \
  })
#else
#define bpf_printk(fmt, ...)
#endif

// Since BPF programs cannot perform any function calls other than
// those to BPF helpers, common library code needs to be implemented
// as inline functions. In addition, also LLVM provides some built-ins
// that can be used for constant sizes.
#define memset(dest, chr, n) __builtin_memset((dest), (chr), (n))
#define memcpy(dest, src, n) __builtin_memcpy((dest), (src), (n))
#define memmove(dest, src, n) __builtin_memmove((dest), (src), (n))

// Do not allow use printf()
#define printf(fmt, ...) do_not_use_printf_use_bpf_printk

// Macro to define BPF Map
#define BPF_MAP_DEF(name) struct bpf_map_def SEC("maps") name
#define BPF_MAP_ADD(x)

#define BPF_HISTOGRAM(name) struct bpf_map_def SEC("maps") name = {\
    .map_type = BPF_MAP_TYPE_PERCPU_ARRAY,\
    .key_size = sizeof(__u32),\
    .value_size = sizeof(__u64),\
    .max_entries = 64,\
};

// Finally make sure that all types have expected size regardless of platform
static_assert(sizeof(__u8) == 1, "wrong_u8_size");
static_assert(sizeof(__u16) == 2, "wrong_u16_size");
static_assert(sizeof(__u32) == 4, "wrong_u32_size");
static_assert(sizeof(__u64) == 8, "wrong_u64_size");

#endif