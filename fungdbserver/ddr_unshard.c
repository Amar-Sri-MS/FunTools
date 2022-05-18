/*
 * ddr_unshard.c: decode a DDR memory dump for S1 from Palladium.
 *
 * Usage:
 *
 * ddr_unshard outfile path-prefix
 *
 * path_prefix is path and partial name of dump files
 * up to funos-s1-emu.64big where the "ch%d" suffix of the different
 * shards of the dump have been omitted.
 * wh

 * Copyright Fungible Inc. 2019.  All rights reserved.
 */

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <unistd.h>
#include <string.h>
#include <stdbool.h>
#include <inttypes.h>
#include <sys/mman.h>
#include <sys/stat.h>

#include "ddr_address.h"

// True if we should print extra debugging info.
bool debugging = false;

// TODO(bowdidge): Unify with HBM dumping.

// Details on file containing sharded dump data.
struct infile {
	// Name of text hex dump.
	char *name;
	// File descriptor for hex dump.
	int srcfd;
	// Name of temporary file for binary data.
	char *fname;
	// File descriptor for binary data.
	int binfd;
	// Pointer to mmapped contents of binary data.
	uint64_t *map;
	// Size of binary file.
	uint64_t size;
};

// Array of ascii hex dump shards containing memory dump.
// Array is in order of ordinal in file name.
static struct infile *shards;

/*
 * Open the multiple shard files and verify all exist.
 * prefix is the full path (minus the .ch0 extension.)
 *
 * Open files are placed in shards array which should be defined.
 *
 * Exits if any files cannot be found.
 *
 * prefix: full path to dumps without the .ch[0-9] suffix.
 * shard_info: pointer to struct describing sharding arrangement.
 * expected_file_size: predicted size of hex dump files.
 */
void open_shard_files(const char *prefix,
		      struct sharding_info *shard_info)
{
	size_t nlen = strlen(prefix) + strlen(shard_info->extension)+1;
	int i;

	printf("Expecting %d channels, %d inst\n",
	       shard_info->num_channels, shard_info->num_inst);
	for (i = 0; i < shard_info->num_channels; i++) {
		for (int j = 0; j < shard_info->num_inst; j++) {
			/* make a filename and open it */
			uint16_t shard_index = i * shard_info->num_inst + j;
			shards[shard_index].name = malloc(nlen);
			if (shard_info->num_inst <= 1) {
				// Only one substitution - channel number.
				sprintf(shards[shard_index].name,
					shard_info->extension,
					prefix, shard_index);
			} else {
				// Substitute channel number and instance.
				sprintf(shards[shard_index].name,
					shard_info->extension,
					prefix, i, j);
			}
			shards[shard_index].srcfd =
				open(shards[shard_index].name, O_RDONLY);
			if (shards[shard_index].srcfd < 0) {
				printf("failed to open shard %s\n",
				       shards[shard_index].name);
				exit(1);
			}
			struct stat st;

			if (stat(shards[shard_index].name, &st) != 0) {
				perror("stat");
				exit(1);
			}
			printf("file %s is %" PRId64 " bytes\n",
			       shards[shard_index].name, st.st_size);
			if (st.st_size != shard_info->expected_file_size) {
				printf("Expected shard hex file to be %" PRId64
				       " bytes, got % " PRId64 " bytes\n",
				       shard_info->expected_file_size,
				       st.st_size);
				exit(1);
			}
		}
	}
}

/* Cleanup shard data structures before exit. */
void close_shard_files(struct sharding_info *shard_info) {
	int i;

	for (i = 0; i < shard_info->num_channels; i++) {
		free(shards[i].name);
		free(shards[i].fname);

		close(shards[i].srcfd);
	}
}

/*
 * Create binary dump file for output.
 */
static int create_bin_file(const char *outfile)
{
	int fd = -1;

	fd = open(outfile, O_CREAT | O_WRONLY | O_TRUNC, 0644);

	if (fd < 0) {
		printf("failed to open output file %s\n", outfile);
		exit(1);
	}

	return fd;
}

// Number of words to read and write at a time for efficient disk use.
#define CHUNK (16 * 1024)

/* Reads the hex dump data from shard file into a binary file.
 *
 * Reassembling the shards is done by seeking around in the binary file.
 */
static void decode_input(int shard_number, struct sharding_info *shard_info)
{
	uint64_t n;
	uint64_t j;
	bool done = false;
	uint16_t file_read_chunk = shard_info->file_read_chunk;

	uint64_t input_buffer_size = CHUNK * file_read_chunk;
	char *input_buffer = malloc(input_buffer_size);
	uint64_t output_buffer[CHUNK];
	struct infile *f = &shards[shard_number];
	const char *text_cursor;
	uint32_t i;

	/* create a temporary fd for the binary */
	char name[24];
	sprintf(name, "shard_%d", shard_number);
	f->fname = malloc(strlen(name) + 1);
	strcpy(f->fname, name);
	printf("binary in %s\n", f->fname);

	f->binfd = open(name, O_WRONLY|O_CREAT, 0644);
	if (f->binfd < 0) {
		perror("open");
		exit(1);
	}
	/* do the actual decode */
	while (true) {
		/* read in a large number of lines */
		n = read(f->srcfd, input_buffer, input_buffer_size);
		text_cursor = input_buffer;
		if (n == 0) {
			// Out of data - we're at end of file.
			break;
		} else if (n < 0) {
			perror("read");
			exit(1);
		}

		if (n % file_read_chunk) {
			printf("read %" PRIx64 " bytes\n", n);
			printf("failed to read complete lines - "
			       "is %s corrupt?\n", f->fname);
			exit(1);
		}

		uint64_t words_in_buf = n / (file_read_chunk);

		// Read pairs of lines because format of first and second
		// line differ slightly.
		for (i = 0; i < words_in_buf; i++) {
			/* compute the address of the line */
			uint64_t value = ddr_decode_lines(&text_cursor);
			output_buffer[i] = value;
		}

		n = write(f->binfd, output_buffer,
			  words_in_buf * sizeof(*output_buffer));
		if (n <= 0) {
			perror("write");
			exit(1);
		}
		f->size += n;
	}

	/* mmap the file so we can map it in and pick out bits at random. */
	close(f->binfd);
	f->binfd = open(name, O_RDONLY);
	f->map = mmap(NULL, f->size, PROT_READ, MAP_FILE | MAP_PRIVATE,
		      f->binfd, 0);
	if (f->map == MAP_FAILED) {
		perror("mmap: mapping binary shard into memory");
		exit(1);
	}
	printf("Sharded binary file is 0x%" PRIx64 " bytes.\n", f->size);
	close(f->binfd);

	// Unlink the binary version of the shard file so that it
	// doesn't stick around after processing.
	// Comment this out if you want to look at the raw shards.
	unlink(f->fname);

	f->binfd = -1;
	free(input_buffer);
}

/* Sweep through each of the binary shard files copying bits into
 * the output file.
 */
static void decode_inputs(struct sharding_info *shard_info)
{
	int i, j;
	for (i = 0; i < shard_info->num_channels; i++) {
		for (j = 0; j < shard_info->num_inst; j++) {
			uint16_t shard_index = i * shard_info->num_inst + j;
			printf("Converting shard %d to binary.\n",
			       shard_index);
			fflush(stdout);
			decode_input(shard_index, shard_info);
		}
	}
	printf("\n");
}

/*
 * Sweep through memory finding the location of each chunk of data.
 * Pick it out of the file, and write it to the output file.
 */
static void unshard(int dump_fd, struct sharding_info *shard_info)
{
	uint64_t addr = 0;
	struct infile *f = NULL;
	size_t i, c = 0;
	ssize_t n;
	uint16_t file_shard;

	uint16_t max_shard =
		shard_info->num_channels * shard_info->num_inst - 1;

	printf("Unsharding\n");
	for (addr = 0; addr < shard_info->memory_size;
	     addr += shard_info->stride_size) {

		/* compute where next memory line is found in files. */
		struct offset_pair offset_loc =
			shard_info->addr_to_shard(addr);
		if (debugging) {
			printf("addr %" PRIx64" at file %d "
			       "offset %" PRIx64 "\n",
			       addr, offset_loc.file_shard, offset_loc.offset);
		}
		assert(offset_loc.file_shard < max_shard);

		file_shard = shard_info->channel_order[offset_loc.file_shard];

		f = &shards[file_shard];

		// Sanity check that offset is within the size of the shard.
		if (offset_loc.offset >= f->size) {
			printf("offset is 0x%" PRIx64
			       ", but file size was 0x%" PRIx64 "\n",
			       offset_loc.offset, f->size);
			assert(offset_loc.offset < f->size);
		}

		const char *buf = ((const char*) f->map) + offset_loc.offset;
		n = write(dump_fd, buf, shard_info->stride_size);
		if (n != shard_info->stride_size) {
			perror("problems writing dump file");
			exit(1);
		}
	}
}

int main(int argc, char *argv[])
{
	struct sharding_info ddr_info = ddr_shard_info();

	const char *prefix = NULL;
	const char *outfile = NULL;
	uint32_t i;
	int dump_fd = -1;

	if (argc != 3) {
		printf("usage: %s <outfile> <shard-prefix>\n", argv[0]);
		exit(1);
	}

	/* extract the actual output filename & prefix */
	outfile = argv[1];
	prefix = argv[2];

	uint16_t num_shards = ddr_info.num_channels * ddr_info.num_inst;
	shards = malloc(sizeof(struct infile) * num_shards);

	/* open all the files */
	open_shard_files(prefix, &ddr_info);

	/* create the actual output file */
	dump_fd = create_bin_file(outfile);

	/* translate the shard files from text->binary */
	decode_inputs(&ddr_info);

	/* do the actual assembly */
	unshard(dump_fd, &ddr_info);

	close(dump_fd);
	close_shard_files(&ddr_info);

	return 0;
}
