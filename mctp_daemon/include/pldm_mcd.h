/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#ifndef _INC_PLDM_MCD_HDR_
#define _INC_PLDM_MCD_HDR_

#include "pldm.h"
#define PLDM_REQ_DATA           2

#define PLDM_MCD_VERSION         0xf1f0f000      /* ver 1.0.0 in BE format */
#define PLDM_PMC_VERSION         0xf1f1f100      /* ver 1.1.1 in BE format */

#define CONFIG_DYNAMIC_CRC_CALC

/* pldm tid struct */
struct pldm_set_tid_req_stc {
    uint8_t tid;
} __attribute__((packed));

struct pldm_get_tid_rspn_stc {
    uint8_t cmp_code;
    uint8_t tid;
} __attribute__((packed));

/* pldm version struct */
struct pldm_get_ver_req_stc {
    uint32_t handle;
    uint8_t flag;
    uint8_t type;
    uint8_t data[0];
} __attribute__((packed));

struct pldm_get_ver_rspn_stc {
    uint8_t cmp_code;
    uint32_t handle;
    uint8_t flag;
    uint8_t data[0];
} __attribute__((packed));

struct pldm_version_stc {
    uint32_t ver;
    uint8_t data[0];
} __attribute__((packed));

/* pldm types */
struct pldm_get_type_req_stc {
    uint8_t type;
    uint32_t ver;
} __attribute__((packed));

struct pldm_get_type_rspn_stc {
    uint8_t cmp_code;
    uint8_t type[7];
} __attribute__((packed));

/* pldm commands */
struct pldm_cmds_req_stc {
    uint8_t type;
    uint32_t ver;
}  __attribute__((packed));

struct pldm_cmds_rspn_stc {
    uint8_t cmp_code;
    uint8_t cmds[32];
} __attribute__((packed));

extern pldm_cmd_hdlr_stct pldm_mcd_cmds[];

#endif /* _INC_PLDM_MCD_HDR_ */
