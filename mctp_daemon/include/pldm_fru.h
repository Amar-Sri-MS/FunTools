/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#ifndef _INC_PLDM_FRU_HDR_
#define _INC_PLDM_FRU_HDR_

#include <stdint.h>

#define PLDM_FRU_VERSION	0xf1f0f100

struct fru_meta_stc {
        uint32_t size;
        uint32_t records;
        uint8_t *ptr;
};

struct fru_data_stc {
        struct fru_meta_stc meta;
        uint8_t *buf;
        uint32_t size;
};

struct pldm_get_meta_rsp_stc {
        uint8_t ver_maj;
        uint8_t ver_min;
        uint32_t set_max_size;
        uint32_t fru_length;
        uint16_t set_records;
        uint16_t total_records;
        uint8_t data[0];
} __attribute__((packed));

struct pldm_get_rec_req_hdr_stc {
        uint32_t handler;
        uint8_t flags;
} __attribute__((packed));

struct pldm_get_rec_rsp_stc {
        uint32_t next_handler;
        uint8_t flags;
        uint8_t data[0];
} __attribute__((packed));

#define PLDM_FRU_GET_RECORD_METADATA    0x01
#define PLDM_FRU_GET_RECORD_TABLE       0x02
#define PLDM_FRU_SET_RECORD_TABLE       0x03
#define PLDM_FRU_GET_RECORD_BT_OPTION   0x04

#define PLDM_GETFRU_FLAGS_GET_FIRST     1
#define PLDM_GETFRU_FLAGS_GET_NEXT      0

#define PLDM_GETFRU_RSPN_FLAGS_START    1
#define PLDM_GETFRU_RSPN_FLAGS_MIDDLE   2
#define PLDM_GETFRU_RSPN_FLAGS_END      4
#define PLDM_GETFRU_RSPN_FLAGS_SINGLE   5

void get_fru_supported_cmds(uint8_t *cmds);
int pldm_fru_init(void);

#endif /* _INC_PLDM_FRU_HDR_ */
