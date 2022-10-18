/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#ifndef _INC_PCIE_VDM_HDR_
#define _INC_PCIE_VDM_HDR_

#include <stdint.h>
#include "mctp.h"

#define PCIE_ROUTE_TO_RC	0	
#define PCIE_ROUTE_BY_ID	2
#define PCIE_BC_FROM_RC		3

#define DWORD(n)		((n) >> 2)

#define MCTP_MSG_CODE		0x7f
#define MCTP_VENDOR_ID		0x1ab4

struct pcie_vdm_hdr_stc {
	uint32_t cookie;
#ifndef ARCH_BIG_ENDIAN
	uint32_t type:5, fmt:2, t2:1, t8:4, tc:3, t9:1, len:10, r_at:2, attr:2, ep:1, td:1;
        uint32_t req_id:16, tag:8, msg_code:8;
	//uint32_t tag:8, msg_code:8, req_id:16;
        uint32_t trgt_id:16, vendor_id:16;
	//uint32_t vendor_id:16, trgt_id:16;
#else
        uint32_t t2:1, fmt:2, type:5, t9:1, tc:3, t8:4, td:1, ep:1, attr:2, r_at:2, len:10;
        uint32_t req_id:16, tag:8, msg_code:8;
        uint32_t trgt_id:16, vendor_id:16;
#endif
        uint8_t data[0];
};

#define FUNGIBLE_PCIE_BUS_ID(n)         ((n & 0x000000ff))
#define FUNGIBLE_PCIE_FUN_ID(n)         ((n & 0x0000ff00) >> 8)
struct pcie_vdm_rec_data {
	uint16_t vendor_id;
	uint16_t trgt_id;
	uint32_t cookie;
	uint16_t bus_owner_id;
};

extern struct mctp_ops_stc pcie_vdm_ops;

#endif /* _INC_PCIE_VDM_HDR_ */
