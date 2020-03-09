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
#include <utils/threaded/fun_malloc_threaded.h>

/* DPC over NVMe will work only in Linux */
#ifdef __linux__
static bool _read_from_nvme_helper(struct dpcsock *sock, uint8_t *buffer,
				   uint32_t *data_len, uint32_t *remaining,
				   uint32_t offset, uint32_t timeout,
				   uint32_t sess_id, uint32_t seq_num)
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
		.cdw10 = sess_id,
		.cdw11 = seq_num,
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

static void
_process_fwdl(struct fun_json *json, struct dpcsock *sock)
{
	const char *verb = NULL;
	if (!fun_json_lookup_string(json, "verb", &verb) || (!verb)
	    || strcmp(verb, "storage"))
		return;

	struct fun_json *args = fun_json_lookup(json, "arguments");
	struct fun_json *j = fun_json_array_at(args, 0);
	const char *class_str = NULL;
	if (!fun_json_lookup_string(j, "class", &class_str) || (!class_str)
			|| strcmp(class_str, "device"))
		return;
	const char *opcode_str = NULL;
	if (!fun_json_lookup_string(j, "opcode", &opcode_str) || (!opcode_str)
	    || strcmp(opcode_str, "FWDL"))
		return;

	struct fun_json *params = fun_json_lookup(j, "params");
	const char *fwfile_str = NULL;
	if (!params || !fun_json_lookup_string(params, "fwfile", &fwfile_str))
		return;
	int fd = open(fwfile_str, O_RDONLY);
	if(-1 == fd) {
		perror("Failed to open FW image file");
		return;
	}

	struct stat st;
	int retval = stat(fwfile_str, &st);
	if(retval) {
		perror("Failed to read FW image size");
		close(fd);
		return;
	}

	size_t fwfile_size = st.st_size;

	if(fwfile_size == 0) {
		perror("FW image size is 0");
		close(fd);
		return;
	}

	size_t remaining = fwfile_size;
	uint32_t fwfile_key = rand();
	uint32_t offset = 0;
	uint8_t *buffer = malloc(NVME_ADMIN_CMD_DATA_LEN);
	while (remaining) {
		uint32_t to_copy = MIN(NVME_ADMIN_CMD_DATA_LEN, remaining);
		retval = read(fd, buffer, to_copy);
		if (retval != to_copy) {
			printf("%s: Insufficient data read %d(Exp %d)\n", __func__, retval, to_copy);
			break;
		}
		struct nvme_admin_cmd cmd = {
			.opcode = NVME_VS_API_FWDL_START,
			.nsid = 0,
			.addr = (__u64)(uintptr_t)(buffer),
			.data_len = NVME_ADMIN_CMD_DATA_LEN,
			.cdw2 = NVME_DPC_CMD_HNDLR_SELECTION,
			.cdw3 = offset,
			.cdw10 = fwfile_size,
			.cdw11 = fwfile_key,
			.timeout_ms = sock->cmd_timeout
		};
		retval = ioctl(sock->fd, NVME_IOCTL_ADMIN_CMD, &cmd);
		if (retval) {
			printf("NVME_IOCTL_ADMIN_CMD %x failed %d\n",
			       NVME_VS_API_FWDL_START, retval);
			break;
		}

		remaining -= to_copy;
		offset += to_copy;
	}
	if (retval == 0) {
		fun_json_dict_add_int64(params, "fwfile_key", fun_json_no_copy_no_own,
				fwfile_key, true);
	}
	free(buffer);
	// fun_json_printf("new json -> %s\n", json);
	if(fd != -1)
		close(fd);

	return;
}
#endif //__linux__

/* Execute vendor specific admin command for writing data to NVMe device */
/* DPC over NVMe will work only in Linux */
/* In macOS, always returns false */
bool _write_to_nvme(struct fun_json *json, struct dpcsock *sock,
		    uint32_t sess_id, uint32_t seq_num)
{
	bool ok = false;
#ifdef __linux__
	// Copy file to F1 if its FW download request
	_process_fwdl(json, sock);
	uint8_t *addr = malloc(NVME_ADMIN_CMD_DATA_LEN);
	if(addr) {
		memset(addr, 0, NVME_ADMIN_CMD_DATA_LEN);

		// Convert to binary JSON
		size_t allocated_size;
		struct fun_ptr_and_size pas = fun_json_serialize(json,
								 &allocated_size);

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
				.cdw10 = sess_id,
				.cdw11 = seq_num,
				.timeout_ms = sock->cmd_timeout
			};
			int ret = ioctl(sock->fd, NVME_IOCTL_ADMIN_CMD, &cmd);

			if(ret == 0) {
				ok = true;
				sock->nvme_write_done = true;
			}
			else {
				printf("NVME_IOCTL_ADMIN_CMD %x failed %d\n",
				       NVME_VS_API_SEND, ret);
			}
		}
		else {
			printf("Input is bigger than maximum supported size (%zu)\n",
			       NVME_ADMIN_CMD_DATA_LEN - sizeof(struct nvme_vs_api_hdr));
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
struct fun_json* _read_from_nvme(struct dpcsock *sock, uint32_t sess_id,
				 uint32_t seq_num)
{
	struct fun_json *json = NULL;
#ifdef __linux__
	if(sock->nvme_write_done) {
		uint8_t *addr = malloc(NVME_ADMIN_CMD_DATA_LEN);
		uint8_t *data_buf = NULL;
		if(addr) {
			uint32_t remaining = 0;
			uint32_t offset = 0;
			uint32_t data_len = 0;
			bool readSuccess = false;

			readSuccess = _read_from_nvme_helper(sock,
							     addr + offset,
							     &data_len,
							     &remaining,
							     offset,
							     sock->cmd_timeout,
							     sess_id,
							     seq_num);
			offset += NVME_ADMIN_CMD_DATA_LEN;
			if ((sizeof(struct nvme_vs_api_hdr) + data_len) > NVME_DPC_MAX_RESPONSE_LEN) {
				printf("%s:%d: sess %u/%u: Data len = %d",
				       __func__, __LINE__, sess_id, seq_num,
				       data_len);
			}
			if (remaining > 0) {
				data_buf = malloc(sizeof(struct nvme_vs_api_hdr) + data_len);
				if (data_buf) {
					memcpy(data_buf, addr, NVME_ADMIN_CMD_DATA_LEN);
					free(addr);
					addr = data_buf;
					do {
						readSuccess = _read_from_nvme_helper(sock,
										     addr + offset,
										     &data_len,
										     &remaining,
										     offset,
										     sock->cmd_timeout,
										     sess_id,
										     seq_num);
						offset += NVME_ADMIN_CMD_DATA_LEN;
					} while(readSuccess && (remaining > 0));
				} else {
					printf("%s:%d  sess %u/%u Unable to alloc %lu bytes",
					       __func__, __LINE__, sess_id,
					       seq_num,
					       sizeof(struct nvme_vs_api_hdr) + data_len);
					readSuccess = 0;
				}
			}

			if(readSuccess) {
				json = _buffer2json((uint8_t *)(addr + sizeof(struct nvme_vs_api_hdr)),
						    data_len);
			}
			free(addr);
		} else {
			printf("%s:%d sess %u/%u Unable to alloc %d bytes",
			       __func__, __LINE__, sess_id, seq_num,
			       NVME_ADMIN_CMD_DATA_LEN);
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

