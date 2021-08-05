#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <inttypes.h>
#include <linux/nvme_ioctl.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <time.h>
#include <string.h>
#include <stdbool.h> 
#include <assert.h>
#include <unistd.h>
#include <linux/fs.h>
#include <uuid/uuid.h>
#include <errno.h>

// macro functions
#define MIN(a,b) (((a)<(b))?(a):(b))
#define MAX(a,b) (((a)>(b))?(a):(b))
#define BITMAP_ALIGN(_val, _boundary)\
	(__typeof__(_val))(((unsigned long)(_val) +\
	(_boundary) - 1) & ~((_boundary) - 1))
#define ONE_GB_IN_BYTES (1073741824ULL)
#define ONE_GB_IN_BLOCKS(blksz) (ONE_GB_IN_BYTES / blksz)
#define IS_SNAPPING_GB_BOUNDRY(slba, nlb, blksz) ({\
	bool is_spanning = false;\
	if ((slba / ONE_GB_IN_BLOCKS(blksz)) !=\
		((slba + nlb - 1) / ONE_GB_IN_BLOCKS(blksz))) {\
		is_spanning = true;\
	}\
	is_spanning;\
})
#define BLOCK_COUNT_ROUND_DOWN(slba, nlb, blksz) ({\
	uint16_t _nlb = nlb;\
	_nlb -= ((slba + nlb) % ONE_GB_IN_BLOCKS(blksz));\
	_nlb;\
})

// constants
#define MAX_PATH 				(256)
#define BUF_SIZE 				(4096)
#define UUID_LEN 				(16)
#define MAX_QUERY_BLOCK_COUNT 	(512)
#define BITS_PER_BYTE 			(8)
#define BITS_PER_RECORD 		(64)

// NVMe opcodes
#define OPCODE_VS_CHANGED_BLOCKS 			(0xc6)
#define OPCODE_VS_GET_NS_BLKHDR				(0xc7)
#define OPCODE_IDENTIFY 					(0x06)
#define IDENTIFY_RESP_NS_SIZE_OFFSET		(0x0)
#define OPCODE_VS_GET_NS_BLKHDR_BS_MASK		(0xff)

// enum for various log messages
enum log_type {
	INFO,
	ERROR,
	VERBOSE
};

// enum for output format options
enum change_block_format{
	FORMAT_BLOCK_LIST,
	FORMAT_RANGE_LIST
};

struct params {
	int nsid; 							// namespace id of the nvme namespace device
	int block_size; 					// internal block size in bytes of the nvme device
	int ns_block_size; 					// block size seen by nvme client
	uint64_t nlb; 						// number of blocks in the diff request
	uint64_t slba; 						// starting block of the diff request
	uint64_t ns_size; 					// size of nvme namespace in blocks
	enum change_block_format format; 	// output format
	uuid_t snap_id; 					// uuid of the snapshot volume namespace
	char dev_path[MAX_PATH]; 			// device path of nvme device
	char snap_uuid1[UUID_STR_LEN]; 		// uuid string of snapshot1 in diff request
	char snap_uuid2[UUID_STR_LEN]; 		// uuid string of snapshot2 in diff request
	char file_path[MAX_PATH]; 			// file path of output JSON file
	FILE *log_fp;						// handle to tool's diagnostic log file
	bool verbose;						// enable verbose logging
};

struct params g_params = {};

// ******************* logging functions *******************
void LOG_INIT()
{
	g_params.log_fp = fopen("./snap_diff.log", "a");
}

void LOG(enum log_type type, char *format, ...)
{
	time_t t = time(NULL);
	char *time_str = asctime(localtime(&t));
	time_str[strlen(time_str)-1] = 0;

	if (g_params.log_fp != NULL) {
		switch(type) {
			case INFO:
				fprintf (g_params.log_fp, "[%s] INFO: ", time_str);
			break;
			case ERROR:
				fprintf (g_params.log_fp, "[%s] ERROR: ", time_str);
			break;
			case VERBOSE:
				if (!g_params.verbose) {
					return;
				}
				fprintf (g_params.log_fp, "[%s] VERBOSE: ", time_str);
				break;
			default:
				break;
		}
		va_list args;
		va_start (args, format);
		vfprintf (g_params.log_fp, format, args);
		va_end (args);
	}
}

void LOG_UNINIT()
{
	if (g_params.log_fp != NULL) {
		fclose(g_params.log_fp);
	}
}

//******************* parsing and help functions *******************
void print_usage()
{
	printf("snap_diff -d:<device_path> -t:<snap_uuid> -f:<file_path> [-s:<starting_block> -l:<count_of_blocks> -r -v -h]\n");
	printf("-d:<device_path> Required. NVMe device path to which change block tracking query is sent\n");
	printf("-t:<snap_uuid> Required. UUID of target snapshot for comparison/diff\n");
	printf("-f:<file_path> Required. Path of file to write JSON diff\n");
	printf("-s:<starting_block> Optional. LBA of volume from which diff is generated. Default is 0.\n");
	printf("-l:<number_of_blocks> Optional. Number of blocks from starting_block for which diff is generated. Default count is till last block.\n");
	printf("-r Generate the output in range format. Default is block format\n");
	printf("-v Enable verbose logging\n");
	printf("-h Print usage\n");
	printf("Examples:\n");
	printf("1. Generate sample.json in range format for all blocks of the device.\n");
	printf("\tsnap_diff -d:/dev/nvme0n1 -t:5e611fd0-50f8-43a9-9296-e9c921a4df1e -f:sample.json -r\n");
	printf("2. Generate sample.json in block format starting from LBA 1024 ending at LBA 2047.\n");
	printf("\tsnap_diff -d:/dev/nvme0n1 -t:5e611fd0-50f8-43a9-9296-e9c921a4df1e -s:1024 -l:1024 -f:sample.json\n");
}

void parse_params(int cnt, char* params[])
{
	int i = 1;
	while (i < cnt) {
		if (strncasecmp(params[i], "-d:", strlen("-d:")) == 0) {
			strncpy(g_params.dev_path, params[i]+strlen("-d:"), MAX_PATH);
		} else if (strncasecmp(params[i], "-t:", strlen("-t:")) == 0) {
			strncpy(g_params.snap_uuid1, params[i]+strlen("-t:"), UUID_STR_LEN);
		} else if (strncasecmp(params[i], "-f:", strlen("-f:")) == 0) {
			strncpy(g_params.file_path, params[i]+strlen("-f:"), MAX_PATH);
		} else if (strncasecmp(params[i], "-s:", strlen("-s:")) == 0) {
			g_params.slba = atoll(params[i]+strlen("-s:"));
		} else if (strncasecmp(params[i], "-l:", strlen("-l:")) == 0) {
			g_params.nlb = atoll(params[i]+strlen("-l:"));
		} else if (strcasecmp(params[i], "-r") == 0) {
			g_params.format = FORMAT_RANGE_LIST;
		} else if (strcasecmp(params[i], "-v") == 0) {
			g_params.verbose = true;
		} else if (strcasecmp(params[i], "-h") == 0) {
			print_usage();
			exit(0);
		} else {
			LOG(ERROR, "Invalid parameter %s\n", params[i]);
			exit(1);
		}
		i++;
	}
}

bool validate_params()
{
	if (strlen(g_params.dev_path) == 0 ||
		strlen(g_params.snap_uuid1) == 0 ||
		strlen(g_params.file_path) == 0) {
		LOG(ERROR, "Required parameter(s) missing. Run with -h option to see required parameter list.\n");
		return false;
	}
	if (g_params.slba < 0 || g_params.nlb < 0) {
		LOG(ERROR, "Invalid parameter. -l/-s can't be negative.\n");
		return false;
	}
	if (uuid_parse(g_params.snap_uuid1, g_params.snap_id)) {
		LOG(ERROR, "Invalid snapshot uuid.\n");
		return false;
	}
	uuid_unparse_lower(g_params.snap_id, g_params.snap_uuid1);
	return true;
}

// ******************* JSON file writer functions *******************
void write_header(FILE *fp)
{
	fprintf(fp, "{\n");
	fprintf(fp, "\t\"version\": \"1.0\",\n");
	fprintf(fp, "\t\"format\": \"block_format\",\n");
	fprintf(fp, "\t\"snap1\": \"%s\",\n", g_params.snap_uuid1);
	fprintf(fp, "\t\"snap2\": \"%s\",\n", g_params.snap_uuid2);
	fprintf(fp, "\t\"start\": \"%"PRIu64"\",\n", g_params.slba);
	fprintf(fp, "\t\"length\": \"%"PRIu64"\",\n", g_params.nlb);
	fprintf(fp, "\t\"block_size\": \"%d\",\n", g_params.block_size);
	fprintf(fp, "\t\"%s\": [", g_params.format == FORMAT_BLOCK_LIST ? "block_list": "range_list");
}

void write_block_record(FILE *fp, char *delim, uint64_t slba)
{
	fprintf(fp, "%s%"PRIu64, delim, slba);
}

void write_range_record(FILE *fp, char *delim, uint64_t slba, uint64_t nlb)
{
	fprintf(fp, "%s{\"start\":%"PRIu64", \"length\":%"PRIu64"}", delim, slba, nlb);
}

void write_footer(FILE *fp)
{
	fprintf(fp, "]\n}\n");
	fflush(fp);
}

// ******************* device query functions *******************
int query_device_details(int dd, int nsid)
{
	uint64_t *ns_size;
	int ret = 0, multiplier = 0;
	struct nvme_admin_cmd cmd = {};
	char buf[BUF_SIZE] = {};

	do {
		cmd.opcode = OPCODE_IDENTIFY;
		cmd.nsid = nsid;
		cmd.addr = (uint64_t)buf;
		cmd.data_len = BUF_SIZE;

		ret = ioctl(dd, NVME_IOCTL_ADMIN_CMD, &cmd);
		if(ret != 0) {
			LOG(ERROR, "NVMe admin command %x failed with error %d\n", OPCODE_IDENTIFY, ret);
			break;
		}

		ns_size = (uint64_t *) buf + IDENTIFY_RESP_NS_SIZE_OFFSET;
		g_params.ns_size = le64toh(*ns_size);
		uuid_unparse_lower(buf+104, g_params.snap_uuid2);

		if (!uuid_compare(g_params.snap_uuid1, g_params.snap_uuid2)) {
			LOG(ERROR, "No changes. Source and destination for diff are same %s\n",
				g_params.snap_uuid1);
			ret = 1;
			break;
		}

		cmd.opcode = OPCODE_VS_GET_NS_BLKHDR;
		cmd.nsid = nsid;
		cmd.addr = 0;
		cmd.data_len = 0;
		cmd.result = 0;

		ret = ioctl(dd, NVME_IOCTL_ADMIN_CMD, &cmd);
		if(ret != 0) {
			LOG(ERROR, "NVMe admin command %x failed with error %d\n", OPCODE_VS_GET_NS_BLKHDR, ret);
			break;
		}

		g_params.block_size = 1 << (le32toh(cmd.result) & OPCODE_VS_GET_NS_BLKHDR_BS_MASK);
		if (g_params.block_size > g_params.ns_block_size) {
			if (g_params.block_size % g_params.ns_block_size) {
				LOG(ERROR, "Incompatible block size. internal block size %u, namespace block size %u\n",
					g_params.block_size, g_params.ns_block_size);
				ret = 1;
				break;
			}
			multiplier = g_params.block_size / g_params.ns_block_size;
			if (g_params.ns_size % multiplier) {
				LOG(ERROR, "Incompatible block size %u and namespace size %"PRIu64"\n",
					g_params.block_size, g_params.ns_size);
				ret = 1;
				break;
			}
			g_params.ns_size /= multiplier;
		}
	} while (0);

	return ret;
}

int query_device()
{
	int dd = 0, ret = 0;
	struct nvme_admin_cmd cmd = {};

	do {
		dd = open(g_params.dev_path, O_RDWR);
		if(dd == 0) {
			LOG(ERROR, "Device %s open failed with error %d\n", g_params.dev_path, errno);
			ret = 1;
			break;
		}

		g_params.nsid = ioctl(dd, NVME_IOCTL_ID);
		if (g_params.nsid < 0) {
			LOG(ERROR, "Nsid query on device %s failed with error %d\n", g_params.dev_path, errno);
			ret = 1;
			break;
		}

		ret = ioctl(dd, BLKSSZGET, &g_params.ns_block_size);
		if (ret < 0) {
			LOG(ERROR, "Block size query on device %s failed with error %d\n", g_params.dev_path, errno);
			break;
		}

		if (query_device_details(dd, g_params.nsid)) {
			ret = 1;
			break;
		}

		if (g_params.nlb == 0) {
			g_params.nlb = g_params.ns_size - g_params.slba;
			LOG(VERBOSE, "-l not specified. Using %"PRIu64, g_params.nlb);
		}

		if ((g_params.slba + g_params.nlb) > g_params.ns_size) {
			LOG(ERROR, "Blocks out of range. s=%"PRIu64" l="PRIu64" ns size=%"PRIu64"\n",
				g_params.slba, g_params.nlb, g_params.ns_size);
			ret = 1;
			break;
		}
	} while (0);

	if (dd != 0) {
		close(dd);
	}
	return ret;
}

// ******************* snapshot diff generator function *******************
int get_snap_diff()
{
	char *delim = "";
	FILE *fp = NULL;
	uint16_t nlb = 0;
	int dd = 0, ret = 0, cnt = 0;
	uint64_t *b = NULL;
	char *data = NULL; 
	uint64_t range = 0, rslba = g_params.slba;
	uint64_t blockid = 0, mask = 0, d = 0;
	uint64_t slba = g_params.slba;
	uint64_t end = g_params.slba + g_params.nlb;
	struct nvme_admin_cmd cmd = {};

	printf("It may take several minutes to complete for large namespace..\n");

	LOG(INFO, "Comparing %s <-> %s Device %s NS ID %d Device Size %"PRIu64"\n",
		g_params.snap_uuid1, g_params.snap_uuid2, g_params.dev_path,
		g_params.nsid, g_params.ns_size);
	LOG(INFO, "Start LBA %"PRIu64" Length %"PRIu64" Block Size %d NS Block Size %d\n",
		g_params.slba, g_params.nlb, g_params.block_size, g_params.ns_block_size);
	LOG(INFO, "Output file %s Format %s\n", g_params.file_path,
		g_params.format == FORMAT_RANGE_LIST ? "RANGE LIST" : "BLOCK LIST");

	do {
		dd = open(g_params.dev_path, O_RDWR);
		if(dd == 0) {
			LOG(ERROR, "Device %s open failed with error %d\n", g_params.dev_path, errno);
			ret = 1;
			break;
		}

		fp = fopen(g_params.file_path, "w+");
		if(fp == NULL) {
			LOG(ERROR, "File %s open failed with error %d\n", g_params.file_path, errno);
			ret = 1;
			break;
		}

		data = (char*)malloc(sizeof(char)*BUF_SIZE);
		if(NULL == data) {
			LOG(ERROR, "Failed to allocate memory\n");
			ret = 1;
			break;
		}

		cmd.opcode = OPCODE_VS_CHANGED_BLOCKS;
		cmd.nsid = g_params.nsid;
		cmd.addr = (uint64_t)data;
		cmd.data_len = BUF_SIZE;
		memcpy(&cmd.cdw12, g_params.snap_id, UUID_LEN);

		write_header(fp);
		while (slba < end) {
			nlb = MIN(MAX_QUERY_BLOCK_COUNT, end - slba);
			if (IS_SNAPPING_GB_BOUNDRY(slba, nlb, g_params.block_size)) {
				nlb = BLOCK_COUNT_ROUND_DOWN(slba, nlb, g_params.block_size);
			}

			// encode slba and nlb into cdw10 and cdw11
			cmd.cdw10 = (uint32_t)(slba & 0xFFFFFFFF);
			cmd.cdw11 = (nlb-1) << 16;
			cmd.cdw11 |= ((slba >> 32) & 0xFFFF);
			memset(data, 0, BUF_SIZE);

			LOG(VERBOSE, "Querying slba=%"PRIu64" nlb=%u\n",
				slba, nlb);

			ret = ioctl(dd, NVME_IOCTL_ADMIN_CMD, &cmd);
			if(ret != 0) {
				LOG(ERROR, "NVMe admin command %x (slba=%"PRIu64" nlb=%u) failed with error %d\n",
					OPCODE_VS_CHANGED_BLOCKS, slba, nlb, ret);
				break;
			}

			//LOG_HEX(VERBOSE, data, BUF_SIZE);

			mask = 0;
			blockid = slba;
			cnt = (BITMAP_ALIGN(nlb, 64) >> 6);
			b = (uint64_t*)data;

			for (int i=cnt-1; i >= 0; i--) {
				d = htobe64(b[i]);
				for(int j=0; j < BITS_PER_RECORD; j++) {
					if (blockid == end) {
						break;
					}
					mask = 1ULL << j;
					if (d & mask) {
						if (g_params.format == FORMAT_BLOCK_LIST) {
							write_block_record(fp, delim, blockid);
							delim = ",";
						} else {
							if (range == 0) {
								rslba = blockid;
							}
							range++;
						}
					} else if (range > 0) {
						write_range_record(fp, delim, rslba, range);
						delim = ",";
						range = 0;
					}
					blockid++;
				}
			}
			slba += nlb;
		}
		if (range > 0) {
			write_range_record(fp, delim, rslba, range);
			range = 0;
		}
		write_footer(fp);
	} while (0);

	if (dd != 0) {
		close(dd);
	}
	if (fp != NULL) {
		fclose(fp);
	}
	if (data != NULL) {
		free(data);
	}
	if (ret != 0) {
		remove(g_params.file_path);
	}
	return ret;
}

// ******************* program entry point *******************
int main(int argc, char* argv[])
{
	int res = 0;

	LOG_INIT();
	LOG(INFO, "Starting snap_diff\n");
	do {
		parse_params(argc, argv);
		if (validate_params() == false) {
			print_usage();
			res = 1;
			break;
		}
		if (query_device() != 0) {
			res = 1;
			break;
		}
		if (get_snap_diff() != 0) {
			res = 1;
			break;
		}
	} while (0);
	LOG(INFO, "Ending snap_diff\n");
	LOG_UNINIT();

	printf("snap_diff %s\n", res == 0 ? "completed" : "failed. See snap_diff.log file for more details.");
	return res;
}
