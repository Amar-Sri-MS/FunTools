/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#ifndef _INC_SMBUS_HDR_
#define _INC_SMBUS_HDR_

#include <stdint.h>
#include "auto_conf.h"

#define SMBUS_SLAVE_ADDR	0x1a

struct smbus_hdr_stc {
        uint8_t opcode:1, dst_addr:7;
        uint8_t type;
        uint8_t len;
        uint8_t rdwr:1, src_addr:7;

} __attribute__((packed));

extern struct mctp_ops_stc smbus_ops;

#endif /* _INC_PCIE_VDM_HDR_ */
