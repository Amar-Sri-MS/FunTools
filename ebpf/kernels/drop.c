/*
*  k_05.c
*
*  Created by Hariharan Thantry on 2019-04-08
*
*  Copyright © 2019 Fungible Inc. All rights reserved.
*
*/

#include "../bpf_helpers.h"

/*
* This kernel should drop a packet that has
* ethType = 0x800, IPv4 protocol + TCP + sport = 1234
*
*/

SEC("xdp")
int drop(struct k_05_arg *arg)
{
	uint8_t *pkt = (uint8_t *) arg->data;
	struct ethhdr *ethhdr = (struct ethhdr *)(pkt);

	if (bpf_ntohs(ethhdr->h_proto) != 0x800) {
		return 0;
	}
	struct iphdr *iphdr = (struct iphdr *)((uint8_t *) ethhdr +
					       sizeof(*ethhdr));

	if (iphdr->protocol != 6) {
		return 0;
	}
	struct tcphdr *t_hdr = (struct tcphdr *)((uint8_t *) iphdr +
						 sizeof(*iphdr));

	if (bpf_ntohs(t_hdr->source) == 1234) {
		return 1;
	}
	return 0;
}
