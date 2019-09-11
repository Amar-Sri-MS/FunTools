/*
*  k_06.c
*
*  Created by Hariharan Thantry on 2019-04-08
*
*  Copyright © 2019 Fungible Inc. All rights reserved.
*  This kernel implements an L2 learning switch.
*  The return value provides an indication on whether
*  the packet should be flooded, or switched directly to an output port
*  learned earlier. Demonstrates the usage of a map
*/

#include "../bpf_helpers.h"

#define FLOOD -1

BPF_MAP_DEF(inports) = {
    .map_type = BPF_MAP_TYPE_HASH,
    .key_size = 6,
    .value_size = sizeof(__u32),
    .max_entries = 256,
};
BPF_MAP_ADD(inports);

SEC("xdp")
int l2_learn(struct k_05_arg *arg)
{
	__u8 *pkt = (__u8 *) arg->data;
	struct ethhdr *eth = (struct ethhdr *)(pkt);
	int out_port = FLOOD;

/*
* Update the ingress port associated with the packet
*/
	if ((eth->h_source[0] & 1) == 0) {
		bpf_map_update_elem(&inports,
				    eth->h_source, &(arg->ingress_ifindex), 0);

	}
	if (eth->h_dest[0] & 1) {
		return out_port;

	}

	if (bpf_map_lookup_elem(&inports, eth->h_dest, &out_port) == -1) {
// If no entry was found flood
		return FLOOD;
	}
	return out_port;
}
