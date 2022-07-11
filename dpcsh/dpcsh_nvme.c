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

#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>

#include "dpcsh_nvme.h"
#include "dpcsh_log.h"
#include <FunOS/utils/threaded/fun_malloc_threaded.h>

#define READ_RETRY_DELAY_IN_US	(500) // in microsecs
#define RETRY_DELAY_SCALE	(5)

/* DPC over NVMe will work only in Linux */
#ifdef __linux__
static bool _read_from_nvme_helper(struct dpcsock_connection *connection, uint8_t *buffer,
				   uint32_t *data_len, uint32_t *remaining,
				   uint32_t offset, uint32_t timeout)
{
        bool retVal = false;
	bool writeDone = false;
        memset(buffer, 0, NVME_ADMIN_CMD_DATA_LEN);
	int retry_count = 0;
	while (!writeDone) {
		struct nvme_admin_cmd cmd = {
			.opcode = NVME_VS_API_RECV,
			.nsid = 0,
			.addr = (__u64)(uintptr_t)(buffer),
			.data_len = NVME_ADMIN_CMD_DATA_LEN,
			.cdw2 = NVME_DPC_CMD_HNDLR_SELECTION,
			.cdw3 = offset,
			.cdw10 = connection->nvme_session_id,
			.cdw11 = connection->nvme_seq_num,
			.timeout_ms = timeout
		};
		int fd = open(connection->socket->socket_name, O_RDWR);
		if (fd < 0) {
			log_error("%s: Failed to open %s\n", __func__,
			       connection->socket->socket_name);
			break;
		}
		int ret = ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd);
		if(ret == 0) {
			if((*data_len) == 0) {
				struct nvme_vs_api_hdr *hdr = (struct nvme_vs_api_hdr *)buffer;
				if (le16toh(hdr->json_cmd_status) != WRITE_COMPLETE) {
					usleep(READ_RETRY_DELAY_IN_US * ((retry_count/RETRY_DELAY_SCALE) + 1));
					retry_count++;
					close(fd);
					continue;
				}
				(*data_len) = le32toh(hdr->data_len);
				(*remaining) = sizeof(struct nvme_vs_api_hdr) + (*data_len);
			}
			(*remaining) -= MIN(*remaining, NVME_ADMIN_CMD_DATA_LEN);
			retVal = true;
		} else {
			log_error("NVME_IOCTL_ADMIN_CMD %x failed %d\n",NVME_VS_API_RECV,ret);
		}
		close(fd);
		writeDone = true;
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
bool _write_to_nvme(struct fun_ptr_and_size data, struct dpcsock_connection *connection)
{
	bool ok = false;
#ifdef __linux__
	uint8_t *addr = malloc(NVME_ADMIN_CMD_DATA_LEN);
	if(addr) {
		memset(addr, 0, NVME_ADMIN_CMD_DATA_LEN);

		// Convert to binary JSON
		if(data.size <= NVME_ADMIN_CMD_DATA_LEN - sizeof(struct nvme_vs_api_hdr)) {
			// Build header
			struct nvme_vs_api_hdr *hdr = (struct nvme_vs_api_hdr *)addr;
			hdr->data_len = htole32(data.size); // Setting data_len to length of binary JSON
			hdr->version = htole32(DPCSH_NVME_VER);

			// Copy binary JSON
			memcpy((hdr + 1), data.ptr, data.size);

			struct nvme_admin_cmd cmd = {
				.opcode = NVME_VS_API_SEND,
				.nsid = 0,
				.addr = (__u64)(uintptr_t)addr,
				.data_len = NVME_ADMIN_CMD_DATA_LEN,
				.cdw2 = NVME_DPC_CMD_HNDLR_SELECTION,
				.cdw3 = data.size,
				.cdw10 = connection->nvme_session_id,
				.cdw11 = connection->nvme_seq_num,
				.timeout_ms = connection->socket->cmd_timeout
			};
			int fd = open(connection->socket->socket_name, O_RDWR);
			if (fd >= 0) {
				int ret = ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd);

				if(ret == 0) {
					ok = true;
					connection->nvme_write_done = true;
				} else {
					log_error("NVME_IOCTL_ADMIN_CMD %x failed %d\n",
							NVME_VS_API_SEND, ret);
				}
				close(fd);
			} else {
				log_error("%s: Failed to open %s\n", __func__,
				       connection->socket->socket_name);
			}
		} else {
			log_error("Input is bigger than maximum supported size (%zu)\n",
			       NVME_ADMIN_CMD_DATA_LEN - sizeof(struct nvme_vs_api_hdr));
		}
		free(addr);
	}
#endif //__linux__
	return ok;
}

/* Execute vendor specific admin command for reading data from NVMe device */
/* DPC over NVMe will work only in Linux */
/* In macOS, always returns 0 */
uint32_t _read_from_nvme(uint8_t **data, uint8_t **deallocate_ptr, struct dpcsock_connection *connection)
{
	*data = NULL;
	*deallocate_ptr = NULL;
#ifdef __linux__
	if(connection->nvme_write_done) {
		uint8_t *addr = malloc(NVME_ADMIN_CMD_DATA_LEN);
		uint8_t *data_buf = NULL;
		if(addr) {
			uint32_t remaining = 0;
			uint32_t offset = 0;
			uint32_t data_len = 0;
			bool readSuccess = false;

			readSuccess = _read_from_nvme_helper(connection,
							     addr + offset,
							     &data_len,
							     &remaining,
							     offset,
							     connection->socket->cmd_timeout);
			offset += NVME_ADMIN_CMD_DATA_LEN;
			if ((sizeof(struct nvme_vs_api_hdr) + data_len) > NVME_DPC_MAX_RESPONSE_LEN) {
				log_error("%s:%d: sess %u/%u: Data len = %d\n",
				       __func__, __LINE__, connection->nvme_session_id, connection->nvme_seq_num,
				       data_len);
			}
			if (remaining > 0) {
				uint32_t alloc_len = sizeof(struct nvme_vs_api_hdr) + data_len;
				if (alloc_len % NVME_ADMIN_CMD_DATA_LEN)
					alloc_len = ((alloc_len / NVME_ADMIN_CMD_DATA_LEN) + 1) * NVME_ADMIN_CMD_DATA_LEN;
				data_buf = malloc(alloc_len);
				if (data_buf) {
					memcpy(data_buf, addr, NVME_ADMIN_CMD_DATA_LEN);
					free(addr);
					addr = data_buf;
					do {
						readSuccess = _read_from_nvme_helper(connection,
										     addr + offset,
										     &data_len,
										     &remaining,
										     offset,
										     connection->socket->cmd_timeout);
						offset += NVME_ADMIN_CMD_DATA_LEN;
					} while(readSuccess && (remaining > 0));
				} else {
					log_error("%s:%d  sess %u/%u Unable to alloc %u bytes",
					       __func__, __LINE__, connection->nvme_session_id,
					       connection->nvme_seq_num, alloc_len);
					readSuccess = 0;
				}
			}

			if(readSuccess) {
				*data = addr + sizeof(struct nvme_vs_api_hdr);
				*deallocate_ptr = addr;
				connection->nvme_write_done = false;
				return data_len;
			}
			free(addr);
		} else {
			log_error("%s:%d sess %u/%u Unable to alloc %u bytes",
			       __func__, __LINE__, connection->nvme_session_id, connection->nvme_seq_num,
			       NVME_ADMIN_CMD_DATA_LEN);
		}
		connection->nvme_write_done = false;
	}
#endif //__linux__
    return 0;
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

