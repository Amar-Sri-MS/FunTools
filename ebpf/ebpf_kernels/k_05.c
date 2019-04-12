/*
*  k_05.c
*
*  Created by Hariharan Thantry on 2019-04-08
*
*  Copyright © 2019 Fungible Inc. All rights reserved.
*
*/

#include "ebpf_kern_args.h"

typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
typedef unsigned long long uint64_t;
typedef uint32_t tcp_seq;
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

struct ethhdr {
	uint8_t dmac[6];
	uint8_t smac[6];
	uint16_t eth_p;
} __attribute__ ((packed));

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
} __attribute__ ((packed));

/*
* TCP header, as per RFC 793, September, 1981
*/
struct tcphdr {
	uint16_t th_sport;	/* source port */
	uint16_t th_dport;	/* destination port */

	tcp_seq th_seq;		/* sequence number */
	tcp_seq th_ack;		/* acknowledgment number */

#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
	uint8_t th_x2:4,	/* (unused) */
	 th_off:4;		/* data offset */
#else
	uint8_t th_off:4,	/* data offset */
	 th_x2:4;		/* (unused) */
#endif				/* BYTE_ORDER */
	uint8_t th_flags;	/* pkt control flags */

	uint16_t th_win;	/* window */
	uint16_t th_sum;	/* checksum */
	uint16_t th_urp;	/* urgent pointer */
} __attribute__ ((packed));

/*
* This kernel should drop a packet that has
* ethType = 0x800, IPv4 protocol + TCP + sport = 1234
*/

int drop(struct k_05_arg *arg)
{
	uint8_t *pkt = (uint8_t *) arg->data;
	struct ethhdr *ethhdr = (struct ethhdr *)(pkt);

	if (bpf_ntohs(ethhdr->eth_p) != 0x800) {
		return 0;
	}
	struct iphdr *iphdr = (struct iphdr *)((uint8_t *) ethhdr +
					       sizeof(*ethhdr));

	if (iphdr->ip_p != 6) {
		return 0;
	}
	struct tcphdr *t_hdr = (struct tcphdr *)((uint8_t *) iphdr +
						 sizeof(*iphdr));

	if (bpf_ntohs(t_hdr->th_sport) == 1234) {
		return 1;
	}
	return 0;
}
