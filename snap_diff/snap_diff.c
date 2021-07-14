#include <stdio.h>
#include <stdlib.h>
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

// constants
#define MAX_PATH 				(256)
#define BUF_SIZE 				(4096)
#define UUID_LEN 				(16)
#define MAX_QUERY_BLOCK_COUNT 	(512)
#define BITS_PER_BYTE 			(8)
#define BITS_PER_RECORD 		(64)

// NVMe opcodes
#define OPCODE_CHANGED_BLOCKS 	(0xc6)
#define OPCODE_IDENTIFY 		(0x06)

// enum for output format options
enum change_block_format{
	FORMAT_BLOCK_LIST,
	FORMAT_RANGE_LIST
};

struct params {
	int nsid; // namespace id of the nvme namespace device
	int block_size; // block size in bytes of the nve device
	unsigned long long nlb; // number of blocks in the diff request
	unsigned long long slba; // starting block of the diff request
	unsigned long long ns_size; // size of nvme namespace in blocks
	enum change_block_format format; // output format
	uuid_t snap_id; // uuid of the snapshot volume namespace
	char dev_path[MAX_PATH]; // device path of nvme device
	char snap_uuid1[UUID_STR_LEN]; // uuid string of snapshot1 in diff request
	char snap_uuid2[UUID_STR_LEN]; // uuid string of snapshot2 in diff request
	char file_path[MAX_PATH]; // file path of output file
};

struct params g_params = {};

void print_usage()
{
	printf("snap_diff -d:<device_path> -t:<snap_uuid> -f:<file_path> -s:<starting_block> -l:<count_of_blocks> [-r -h]\n");
	printf("-d:<device_path> Required. NVMe device path to which change block tracking query is sent\n");
	printf("-t:<snap_uuid> Required. UUID of target snapshot for comparison/diff\n");
	printf("-f:<file_path> Required. Path of file to write JSON diff\n");
	printf("-s:<starting_block> Optional. Lba of volume from which diff is generated. Default is 0.\n");
	printf("-l:<count_of_blocks> Optional. Block count for which diff is generated. Default is all blocks of the volume.\n");
	printf("-r Generate the output in range format. Default is block format\n");
	printf("-h Print usage\n");
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
		} else if (strcasecmp(params[i], "-h") == 0) {
			print_usage();
			exit(0);
		} else {
			printf("Invalid parameter %s\n", params[i]);
			print_usage();
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
		printf("Error. Required parameter missing.\n");
		print_usage();
		return false;
	}
	if (g_params.slba < 0 || g_params.nlb < 0) {
		printf("Error. Invalid parameter. -l/-s can't be negative.\n");
		print_usage();
		return false;
	}
	if (uuid_parse(g_params.snap_uuid1, g_params.snap_id)) {
		printf("Invalid snapshot uuid.\n");
		return false;
	}
	return true;
}

void write_header(FILE *fp)
{
	fprintf(fp, "{\n");
	fprintf(fp, "\t\"version\": \"1.0\",\n");
	fprintf(fp, "\t\"format\": \"block_format\",\n");
	fprintf(fp, "\t\"snap1\": \"%s\",\n", g_params.snap_uuid1);
	fprintf(fp, "\t\"snap2\": \"%s\",\n", g_params.snap_uuid2);
	fprintf(fp, "\t\"start\": \"%llu\",\n", g_params.slba);
	fprintf(fp, "\t\"length\": \"%llu\",\n", g_params.nlb);
	fprintf(fp, "\t\"block_size\": \"%d\",\n", g_params.block_size);
	fprintf(fp, "\t\"%s\": [", g_params.format == FORMAT_BLOCK_LIST ? "block_list": "range_list");
}

void write_block_record(FILE *fp, char delim, unsigned long long slba)
{
	fprintf(fp, "%c %llu", delim, slba);
}

void write_range_record(FILE *fp, char delim, unsigned long long slba, unsigned long long nlb)
{
	fprintf(fp, "%c {\"start\":%llu, \"length\":%llu}", delim, slba, nlb);
}

void write_footer(FILE *fp)
{
	fprintf(fp, "]\n}\n");
	fflush(fp);
}

int query_device_details(int dd, int nsid)
{
	int ret = 0;
	unsigned short noiob = 0;
	unsigned short *pnoiob;
	unsigned long long *ns_size;
	struct nvme_admin_cmd cmd = {};
	char buf[BUF_SIZE];

	memset(buf, 0, BUF_SIZE);
	cmd.opcode = OPCODE_IDENTIFY;
	cmd.nsid = nsid;
	cmd.addr = (unsigned long long)buf;
	cmd.data_len = BUF_SIZE;

	ret = ioctl(dd, NVME_IOCTL_ADMIN_CMD, &cmd);
	if(ret < 0) {
		printf("NVMe admin command %x failed. Error %d\n", OPCODE_IDENTIFY, errno);
		goto done;
	}

	ns_size = (unsigned long long *) buf;
	g_params.ns_size = le64toh(*ns_size) + 1;
	pnoiob = (unsigned short *) buf + 46;
	noiob = le16toh(*pnoiob);
	if (noiob != 0) {
		g_params.block_size *= noiob;
	}
	uuid_unparse_lower(buf+104, g_params.snap_uuid2);

done:
	return ret;
}

int query_device()
{
	int dd = 0, ret = 0;
	struct nvme_admin_cmd cmd = {};

	dd = open(g_params.dev_path, O_RDWR);
	if(dd == 0) {
		printf("Could not open device file %s. Error %d\n", g_params.dev_path, errno);
		ret = 1;
		goto done;
	}

	g_params.nsid = ioctl(dd, NVME_IOCTL_ID);
	if (g_params.nsid < 0) {
		printf("Failed to query nsid. Erro %d\n", errno);
		ret = 1;
		goto done;
	}

	ret = ioctl(dd, BLKSSZGET, &g_params.block_size);
	if (ret < 0) {
		printf("Failed to query block size. Error %d\n", errno);
		goto done;
	}

	if (query_device_details(dd, g_params.nsid)) {
		printf("Failed to query device details\n");
		ret = 1;
		goto done;
	}

	if (g_params.nlb == 0) {
		g_params.nlb = g_params.ns_size;
	}

	if ((g_params.slba + g_params.nlb) > g_params.ns_size) {
		printf("Invalid parameter. Blocks out of range.\n");
		ret = 1;
		goto done;
	}

done:
	if (dd != 0) {
		close(dd);
	}
	return ret;
}

int get_snap_diff()
{
	char delim = ' ';
	FILE *fp = NULL;
	unsigned short nlb = 0;
	int dd = 0, ret = 0, cnt = 0;
	unsigned long long *b = NULL;
	char *data = NULL; 
	unsigned long long range = 0, rslba = g_params.slba;
	unsigned long long blockid = 0, mask = 0;
	unsigned long long slba = g_params.slba;
	unsigned long long end = g_params.slba + g_params.nlb;
	struct nvme_admin_cmd cmd = {};

	dd = open(g_params.dev_path, O_RDWR);
	if(dd == 0) {
		printf("Could not open device file %s. Error %d\n", g_params.dev_path, errno);
		ret = 1;
		goto done;
	}

	fp = fopen(g_params.file_path, "w+");
	if(fp == NULL) {
		printf("Could not open file %s. Error %d\n", g_params.file_path, errno);
		ret = 1;
		goto done;
	}

	data = (char*)malloc(sizeof(char)*BUF_SIZE);
	if(NULL == data) {
		printf("Unable to allocate memory\n");
		ret = 1;
		goto done;
	}

	cmd.opcode = OPCODE_CHANGED_BLOCKS;
	cmd.nsid = g_params.nsid;
	cmd.addr = (unsigned long long)data;
	cmd.data_len = BUF_SIZE;
	memcpy(&cmd.cdw12, g_params.snap_id, UUID_LEN);

	write_header(fp);
	while (slba < end) {
		nlb = MIN(MAX_QUERY_BLOCK_COUNT, end - slba);
		// encode slba and nlb into cdw10 and cdw11
		cmd.cdw10 = (unsigned int)(slba & 0xFFFFFFFF);
		cmd.cdw11 = (nlb-1) << 16;
		cmd.cdw11 |= ((slba >> 32) & 0xFFFF);
		memset(data, 0, BUF_SIZE);

		ret = ioctl(dd, NVME_IOCTL_ADMIN_CMD, &cmd);
		if(ret < 0) {
			printf("NVMe admin command %x failed. Error %d\n", OPCODE_CHANGED_BLOCKS, errno);
			goto done;
		}

		mask = 0;
		blockid = slba;
		cnt = (BITMAP_ALIGN(nlb, 64) >> 6);
		b = (unsigned long long*)data;
		for (int i=cnt-1; i >= 0; i--) {
			for(int j=0; j < BITS_PER_RECORD; j++) {
				if (blockid == end) {
					break;
				}
				mask = 1ULL << j;
				if (b[i] & mask) {
					if (g_params.format == FORMAT_BLOCK_LIST) {
						write_block_record(fp, delim, blockid);
						delim = ',';
					} else {
						if (range == 0) {
							rslba = blockid;
						}
						range++;
					}
				} else if (range > 0) {
					write_range_record(fp, delim, rslba, range);
					delim = ',';
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
	printf("snap_diff completed\n");

done:
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
		printf("snap_diff failed\n");
	}
	return ret;
}

int main(int argc, char* argv[])
{
	parse_params(argc, argv);
	if (validate_params() == false) {
		print_usage();
		return 1;
	}
	if (query_device() != 0) {
		return 1;
	}
	return get_snap_diff();
}
