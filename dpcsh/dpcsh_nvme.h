/*
 *  dpcsh_nvme.h
 *
 *  Created by Aneesh Pachilangottil on 2019-04-11.
 *  Copyright © 2019 Fungible. All rights reserved.
 */

#pragma once

#include "dpcsh.h"

// DPC over NVMe is needed only in Linux
#ifdef __linux__
#define NVME_DEV_NAME   "/dev/nvme0"  /* default nvme device used for sending dpc commands as
										 NVME vendor specific admin commands */
#define NVME_ADMIN_CMD_DATA_LEN 4096   /* data length for the NVMe admin command
											 used for executing DPC command over NVMe admin queue */
#define NVME_DPC_MAX_RESPONSE_LEN 1024 * 1024   /* Maximum response size for dpc command when using DPC over NVMe */

#define NVME_VS_API_SEND	0xc1	/* Vendor specific admin command opcode for host to dpu data transfer */
#define NVME_VS_API_RECV	0xc2	/* Vendor specific admin command opcode for dpu to host data transfer */
#define NVME_VS_API_FWDL_START  0xc5
#define NVME_DPC_CMD_HNDLR_SELECTION	0x20000	/* 2 in MSB selects dpc_cmd_handler in FunOS */
#define NVME_IDENTIFY_COMMAND_OPCODE 0x06 /* opcode for identify controller command */
#define FUNGIBLE_DPU_VID	0x1dad

#define WRITE_IN_PROGRESS 1
#define WRITE_COMPLETE 2

#define DPCSH_NVME_VER_LEGACY		(0)
#define DPCSH_NVME_VER_2020_03_22	(1)
#define DPCSH_NVME_VER		DPCSH_NVME_VER_2020_03_22

struct nvme_vs_api_hdr {
	uint32_t version;
	uint16_t json_cmd_status;
	uint16_t rsvd1;
	uint32_t data_len;
	uint32_t rsvd2;
};
#endif

extern bool _write_to_nvme(struct fun_json *json, struct dpcsock *sock,
			   uint32_t sess_id, uint32_t seq_num);
extern struct fun_json* _read_from_nvme(struct dpcsock *sock, uint32_t sess_id,
					uint32_t saq_num);
extern bool find_nvme_dpu_device(char *devname, size_t namelen);
