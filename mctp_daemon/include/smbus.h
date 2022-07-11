/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#ifndef _INC_SMBUS_HDR_
#define _INC_SMBUS_HDR_

#include <stdint.h>
#include "auto_conf.h"

#define smbus_err(fmt, arg...)  log("SMBUS: ERROR - "fmt, ##arg)

#define SMBUS_SLAVE_ADDR	0x1a

struct smbus_hdr_stc {
#ifndef ARCH_BIG_ENDIAN
        uint8_t opcode:1, dst_addr:7;
        uint8_t type;
        uint8_t len;
        uint8_t rdwr:1, src_addr:7;
#else
        uint8_t dst_addr:7, opcode:1;
        uint8_t type;
        uint8_t len;
        uint8_t src_addr:7, rdwr:1;
#endif
	uint8_t data[0];
} __attribute__((packed));

struct smbus_priv_data_stc {
        uint8_t slv_addr;
        uint8_t src_addr;
};

extern struct mctp_ops_stc smbus_ops;

#endif /* _INC_PCIE_VDM_HDR_ */
