/*
*  k_05.c
*
*  Created by Hariharan Thantry on 2019-04-08
*
*  Copyright © 2019 Fungible Inc. All rights reserved.
*/
#include "ebpf_kern_args.h"

typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
typedef unsigned long long uint64_t;

struct ethhdr {
	uint8_t dmac[6];
	uint8_t smac[6];
	uint16_t eth_p;
};

struct iphdr {

#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
	uint8_t ip_hl:4,	/* header length */
	 ip_v:4;		/* version */
#else
	uint8_t ip_v:4,		/* version */
	 ip_hl:4;		/* header length */
#endif				/* _BYTE_ORDER__ */
	uint8_t ip_tos;		/* type of service */

	uint16_t ip_len;	/* total length */
	uint16_t ip_id;		/* identification */

	uint16_t ip_off;	/* fragment offset field */
#define IP_RF 0x8000		/* reserved fragment flag */
#define IP_DF 0x4000		/* dont fragment flag */
#define IP_MF 0x2000		/* more fragments flag */
#define IP_OFFMASK 0x1fff	/* mask for fragmenting bits */

	uint8_t ip_ttl;		/* time to live */
	uint8_t ip_p;		/* protocol */
	uint16_t ip_csum;	/* checksum */
	uint32_t ip_src;
	uint32_t ip_dst;
};

struct tcphdr {
	uint16_t sport;
	uint16_t dport;
};

int drop(struct k_05_arg *arg)
{
	uint8_t *pkt = (uint8_t *) arg->data;
	struct ethhdr *ethhdr = (struct ethhdr *)pkt;
	if (ethhdr->eth_p != 0x800) {
		return 0;
	}
	struct iphdr *iphdr = (struct iphdr *)((uint8_t *) ethhdr +
					       sizeof(struct ethhdr));

	if (iphdr->ip_p != 6) {
		return 0;
	}
	struct tcphdr *tcphdr = (struct tcphdr *)((uint8_t *) iphdr +
						  sizeof(struct iphdr));
	if (tcphdr->sport == 1234) {
		return 1;
	}
	return 0;
}
