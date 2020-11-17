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

// TODO:
// 1. Query snap vol uuid
// 2. Query snap vol block count

#define MIN(a,b) (((a)<(b))?(a):(b))
#define MAX(a,b) (((a)>(b))?(a):(b))
#define BITMAP_ALIGN(_val, _boundary)\
	(__typeof__(_val))(((unsigned long)(_val) +\
	(_boundary) - 1) & ~((_boundary) - 1))

#define MAX_PATH (256)
#define BUF_SIZE (4096)
#define OPCODE_CHANGED_BLOCKS (0xc6)
#define UUID_LEN (16)
#define MAX_QUERY_BLOCK_COUNT (512)
#define BITS_PER_BYTE (8)
#define CB_DATA_OFFSET_IN_BYTES (0)
#define BITS_PER_RECORD (64)

enum change_block_format{
	FORMAT_BLOCK_LIST,
	FORMAT_RANGE_LIST
};

struct params {
	char dev_path[MAX_PATH];
	char snap_uuid[UUID_LEN + 1];
	char file_path[MAX_PATH];
	unsigned long long slba;
	unsigned short nlb;
	enum change_block_format format;
	int nsid;
	int block_size;
};

struct params g_params;

void print_usage()
{
	printf("snap_diff -d:<device_path> -t:<snap_uuid> -f:<file_path> -s:<starting_block> -l:<count_of_blocks> [-r -h]\n");
	printf("-d:<device_path> Required. NVMe device path to which change block tracking query is sent\n");
	printf("-t:<snap_uuid> Required. UUID of target snapshot for comparison/diff\n");
	printf("-f:<file_path> Required. Path of file to write JSON diff\n");
	printf("-s:<starting_block> Required. Lba of volume from which diff is generated.\n");
	printf("-l:<count_of_blocks> Required. Block count for which diff is generated.\n");
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
			strncpy(g_params.snap_uuid, params[i]+strlen("-t:"), UUID_LEN);
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
		strlen(g_params.snap_uuid) == 0 ||
		strlen(g_params.file_path) == 0) {
		printf("Error. Required parameter missing.\n");
		return false;
	}
	return true;
}

void write_header(FILE *fp)
{
	fprintf(fp, "{\n");
	fprintf(fp, "\t\"version\": \"1.0\"\n");
	fprintf(fp, "\t\"format\": \"block_format\"\n");
	fprintf(fp, "\t\"snap1\": \"%s\"\n", g_params.snap_uuid);
	fprintf(fp, "\t\"snap2\": \"%s\"\n", g_params.snap_uuid);
	fprintf(fp, "\t\"start\": \"%llu\"\n", g_params.slba);
	fprintf(fp, "\t\"length\": \"%d\"\n", g_params.nlb);
	fprintf(fp, "\t\"block_size\": \"%d\"\n", g_params.block_size);
	fprintf(fp, "\t\"block_list\": [");
}

void write_record(FILE *fp, char delim, unsigned long long slba)
{
	fprintf(fp, "%c %llu", delim, slba);
}

void write_footer(FILE *fp)
{
	fprintf(fp, "]\n}\n");
	fflush(fp);
}

int query_device()
{
	int dd = 0, ret = 0;
	struct nvme_admin_cmd cmd = {};

	dd = open(g_params.dev_path, O_RDWR);
	if(dd == 0) {
		printf("Could not open device file %s\n", g_params.dev_path);
		ret = 1;
		goto done;
	}

	g_params.nsid = ioctl(dd, NVME_IOCTL_ID);
	if (g_params.nsid == -1) {
		printf("Failed to query nsid\n");
		ret = 1;
		goto done;
	}

	ret = ioctl(dd, BLKSSZGET, &g_params.block_size);
	if (ret < 0) {
		printf("Failed to query block size\n");
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
	char delim = '\0';
	FILE *fp = NULL;
	unsigned short nlb = 0;
	int dd = 0, ret = 0, cnt = 0;
	unsigned long long *b = NULL;
	char *data = NULL, *cb_data = NULL; 
	unsigned long long blockid = 0, mask = 0;
	unsigned long long slba = g_params.slba;
	unsigned long long end = g_params.slba + g_params.nlb;
	char uuid2[UUID_LEN] = {};
	struct nvme_admin_cmd cmd = {};

	dd = open(g_params.dev_path, O_RDWR);
	if(dd == 0) {
		printf("Could not open device file %s\n", g_params.dev_path);
		ret = 1;
		goto done;
	}

	fp = fopen(g_params.file_path, "w+");
	if(fp == NULL) {
		printf("Could not open file %s\n", g_params.file_path);
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
	memcpy(&cmd.cdw12, g_params.snap_uuid, UUID_LEN);
    cb_data = data + CB_DATA_OFFSET_IN_BYTES;

	write_header(fp);
	while (slba < end) {
		nlb = MIN(MAX_QUERY_BLOCK_COUNT, end - slba);
		// encode slba and nlb into cdw10 and cdw11
		cmd.cdw10 = (unsigned int)(slba & 0xFFFFFFFF);
		cmd.cdw11 = (nlb-1) << 16;
		cmd.cdw11 |= ((slba >> 32) & 0xFFFF);
		memset(data, 0, BUF_SIZE);

		ret = ioctl(dd, NVME_IOCTL_ADMIN_CMD, &cmd);
		if(0 != ret) {
			printf("Error sending NVMe command %d\n", ret);
			goto done;
		}

		mask = 0;
		blockid = slba;
		cnt = (BITMAP_ALIGN(nlb, 64) >> 6);
		b = (unsigned long long*)data;
        printf("count=%d\n", cnt);
		for (int i=cnt-1; i >= 0; i--) {
			printf("data=%llu\n", b[i]);
			for(int j=0; j < BITS_PER_RECORD; j++) {
				if (blockid == end) {
					break;
				}
				mask = 1ULL << j;
				if (b[i] & mask) {
					write_record(fp, delim, blockid);
					delim = ',';
				}
				blockid++;
			}
		}
		slba += nlb;
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
