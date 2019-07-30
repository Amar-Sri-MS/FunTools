/*
 *  dpcsh_nvme.h
 *
 *  Created by Aneesh Pachilangottil on 2019-04-11.
 *  Copyright © 2019 Fungible. All rights reserved.
 */

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <fcntl.h>

#ifdef __linux__
#include<sys/ioctl.h>
#include<linux/nvme_ioctl.h>
#include <dirent.h>
#endif //__linux__

#include "dpcsh_nvme.h"
#include <utils/threaded/fun_malloc_threaded.h>

/* DPC over NVMe will work only in Linux */
#ifdef __linux__
static bool _read_from_nvme_helper(struct dpcsock *sock, uint8_t *buffer, uint32_t *data_len, uint32_t *remaining, uint32_t offset, uint32_t timeout)
{
        bool retVal = false;
        memset(buffer, 0, NVME_ADMIN_CMD_DATA_LEN);
        struct nvme_admin_cmd cmd = {
                .opcode = NVME_VS_API_RECV,
                .nsid = 0,
                .addr = (__u64)(uintptr_t)(buffer),
                .data_len = NVME_ADMIN_CMD_DATA_LEN,
                .cdw2 = NVME_DPC_CMD_HNDLR_SELECTION,
                .cdw3 = offset,
		.timeout_ms = timeout
        };
        int ret = ioctl(sock->fd, NVME_IOCTL_ADMIN_CMD, &cmd);
        if(ret == 0) {
                if((*data_len) == 0) {
                        struct nvme_vs_api_hdr *hdr = (struct nvme_vs_api_hdr *)buffer;
                        (*data_len) = le32toh(hdr->data_len);
                        (*remaining) = sizeof(struct nvme_vs_api_hdr) + (*data_len);
                }
                (*remaining) -= MIN(*remaining, NVME_ADMIN_CMD_DATA_LEN);
                retVal = true;
        }
        else {
                printf("NVME_IOCTL_ADMIN_CMD %x failed %d\n",NVME_VS_API_RECV,ret);
        }
        return retVal;
}
// Returns true if the nvme device is a Fungible DPU
static bool is_fungible_dpu(char *devname)
{
        bool retVal = false;
        // Run identify controller and check if the device is a DPU
        int fd;
        fd = open(devname, O_RDWR);
        if(fd) {
                        char data[NVME_ADMIN_CMD_DATA_LEN];
                        memset(data, 0, NVME_ADMIN_CMD_DATA_LEN);
                        struct nvme_admin_cmd cmd = {
                                .opcode = NVME_IDENTIFY_COMMAND_OPCODE, // Identify command
                                .nsid = 0,
                                .addr = (__u64)(uintptr_t)data,
                                .data_len = NVME_ADMIN_CMD_DATA_LEN,
                                .cdw10 = 1  // 1 indicate that we need to get information about controller; not a namespace
                                            // Refer NVME spec for more details
                        };

                        int ret;
                        ret= ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd);
                        if(ret == 0) {
                                uint16_t *vidptr = (uint16_t*)(data);
                                uint16_t vid = le16toh(*vidptr);
                                if(vid == FUNGIBLE_DPU_VID) {
                                        retVal = true;
                                }
                        }
        }
        return retVal;
}
#endif //__linux__

/* Execute vendor specific admin command for writing data to NVMe device */
/* DPC over NVMe will work only in Linux */
/* In macOS, always returns false */
bool _write_to_nvme(struct fun_json *json, struct dpcsock *sock)
{
    bool ok = false;
#ifdef __linux__
	uint8_t *addr = malloc(NVME_ADMIN_CMD_DATA_LEN);
	if(addr) {
		memset(addr, 0, NVME_ADMIN_CMD_DATA_LEN);

		// Convert to binary JSON
		size_t allocated_size;
		struct fun_ptr_and_size pas = fun_json_serialize(json, &allocated_size);

		if(pas.size <= NVME_ADMIN_CMD_DATA_LEN - sizeof(struct nvme_vs_api_hdr)) {
			// Build header
			struct nvme_vs_api_hdr *hdr = (struct nvme_vs_api_hdr *)addr;
			hdr->data_len = pas.size; // Setting data_len to length of binary JSON

			// Copy binary JSON
			memcpy((hdr + 1), pas.ptr, pas.size);

			struct nvme_admin_cmd cmd = {
				.opcode = NVME_VS_API_SEND,
				.nsid = 0,
				.addr = (__u64)(uintptr_t)addr,
				.data_len = NVME_ADMIN_CMD_DATA_LEN,
				.cdw2 = NVME_DPC_CMD_HNDLR_SELECTION,
				.cdw3 = pas.size,
				.timeout_ms = sock->cmd_timeout
			};
			int ret = ioctl(sock->fd, NVME_IOCTL_ADMIN_CMD, &cmd);

			if(ret == 0) {
				ok = true;
				sock->nvme_write_done = true;
			}
			else {
				printf("NVME_IOCTL_ADMIN_CMD %x failed %d\n",NVME_VS_API_SEND,ret);
			}
		}
		else {
			printf("Input is bigger than maximum supported size (%zu)\n", NVME_ADMIN_CMD_DATA_LEN - sizeof(struct nvme_vs_api_hdr));
		}

		fun_free_threaded(pas.ptr, allocated_size);
		free(addr);
	}
#endif //__linux__
    return ok;
}

/* Execute vendor specific admin command for reading data from NVMe device */
/* DPC over NVMe will work only in Linux */
/* In macOS, always returns NULL */
struct fun_json* _read_from_nvme(struct dpcsock *sock)
{
	struct fun_json *json = NULL;
#ifdef __linux__
	if(sock->nvme_write_done) {
		uint8_t *addr = malloc(NVME_DPC_MAX_RESPONSE_LEN);
		if(addr) {
			uint32_t remaining = 0;
			uint32_t offset = 0;
			uint32_t data_len = 0;
			bool readSuccess = false;

			do {
				readSuccess = _read_from_nvme_helper(sock, addr + offset, &data_len, &remaining, offset, sock->cmd_timeout);
				offset += NVME_ADMIN_CMD_DATA_LEN;
			} while(readSuccess && (remaining > 0));

			if(readSuccess) {
				json = _buffer2json((uint8_t *)(addr + sizeof(struct nvme_vs_api_hdr)), data_len);
			}
			free(addr);
		}
		sock->nvme_write_done = false;
	}
#endif //__linux__
    return json;
}

/* DPC over NVMe will work only in Linux */
/* In macOS, always returns false */
/* Check if DPU is visible as an NVMe Controller */
/* Retrieve device name if found */
bool find_nvme_dpu_device(char *devname, size_t size)
{
        bool retVal = false;
#ifdef __linux__
        DIR *d;
        struct dirent *dir;
        d = opendir("/dev");
        if (d)
        {
            while ((dir = readdir(d)) != NULL)
            {
                if(strstr(dir->d_name, "nvme") != NULL) {
                    snprintf(devname, size, "/dev/%s", dir->d_name);
                    if(is_fungible_dpu(devname)) {
			retVal = true;
			break;
                    }
                }
            }
            closedir(d);
        }
#endif // __linux__
        return retVal;
}

