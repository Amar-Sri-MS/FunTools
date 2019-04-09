/*
 *  ebpf_kern.h
 *
 *  Created by Hariharan Thantry on 2019-02-20
 *
 *  Copyright © 2019 Fungible Inc. All rights reserved.
 */

/*
 * This header file contains the definitions for runtime args
 * The same layout must be used by any host for the respective
 * kernels being attached.
 * This utility file needs to be copied over to FunOS
 */

#pragma once
typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
typedef unsigned long long uint64_t;

typedef unsigned long long k_01_arg;

struct k_02_arg {
	uint64_t a;
	uint32_t b;
	uint32_t c;
};
struct k_03_arg {
	uint32_t *arr;
	uint32_t a_len;
};
struct k_04_arg {
	int a;
	int b;
	int c;
};

struct k_05_arg {
    uint64_t data;
    uint64_t data_end;
    uint64_t data_meta;
    uint32_t ingress_ifindex;
    uint32_t rx_queue_index;
};
