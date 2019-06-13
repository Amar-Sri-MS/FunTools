/*
 * ebpf_include.h
 * Copyright (C) 2019 thantry <thantry@lubu>
 *
 * Distributed under terms of the MIT license.
 */

#ifndef EBPF_INCLUDE_H
#define EBPF_INCLUDE_H


#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <stdint.h>

#include "ebpf_functions.h"

/*
* Portable code based on the target
* being compiled for
*/

#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
#define _bpf_ntohs(x)    __builtin_bswap16(x)
#define _bpf_htons(x)    __builtin_bswap16(x)
#define _bpf_constant_ntohs(x)    __constant_swab16(x)
#define _bpf_constant_htons(x)    __constant_swab16(x)
#elif __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define _bpf_ntohs(x)		(x)
#define _bpf_htons(x)		(x)
#define _bpf_constant_ntohs(x) (x)
#define _bpf_constant_htons(x) (x)
#else
#error "Compiler does not have __BYTE_ORDER__?!"
#endif

#define bpf_htons(x)                            \
(__builtin_constant_p(x) ?              \
_bpf_constant_htons(x) : _bpf_htons(x))

#define bpf_ntohs(x)                            \
(__builtin_constant_p(x) ?              \
_bpf_constant_ntohs(x) : _bpf_ntohs(x))



#define SEC(NAME) __attribute__((section(NAME), used))


struct bpf_map_def {
    unsigned int type;
    unsigned int key_size;
    unsigned int value_size;
    unsigned int max_entries;
    unsigned int map_flags;

};




#endif /* !EBPF_INCLUDE_H */
