/*
 *  dpcsh_nvme.h
 *
 *  Created by Aneesh Pachilangottil on 2019-04-11.
 *  Copyright © 2019 Fungible. All rights reserved.
 */

#pragma once

#include "dpcsh.h"

// DPC over NVMe is needed only in Linux
#ifndef __APPLE__
#include<sys/ioctl.h>
#include<linux/nvme_ioctl.h>
#include <dirent.h>

#define NVME_DEV_NAME   "/dev/nvme0"  /* default nvme device used for sending dpc commands as 
										 NVME vendor specific admin commands */
#define NVME_VS_ADMIN_CMD_DATA_LEN 4096   /* data length for the NVMe vendor specific admin command
											 used for executing DPC command over NVMe admin queue */
#define NVME_DPC_MAX_RESPONSE_LEN 1024 * 1024   /* Maximum response size for dpc command when using DPC over NVMe */

#define NVME_VS_API_SEND	0xc1	/* Vendor specific admin command opcode for host to dpu data transfer */
#define NVME_VS_API_RECV	0xc2	/* Vendor specific admin command opcode for dpu to host data transfer */
#define NVME_DPC_CMD_HNDLR_SELECTION	0x20000	/* 2 in MSB selects dpc_cmd_handler in FunOS */
#define NVME_IDENTIFY_CONTROLLER_OPCODE 0x06 /* opcode for identify controller command */
#define FUNGIBLE_DPU_VID	0x1dad

struct nvme_vs_api_hdr {
	uint8_t version;
	uint8_t rsvd1[7];
	uint32_t data_len;
	uint32_t rsvd2;
};
#endif

extern bool _write_to_nvme(struct fun_json *json, struct dpcsock *sock);
extern struct fun_json* _read_from_nvme(struct dpcsock *sock);
extern bool find_nvme_dpu_device(char *devname);