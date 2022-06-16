/* Interfaces for unsharding code.
 *
 * Copyright Fungible Inc. 2019.  All rights reserved.
 */

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Return value for calculating offset in sharded dump where
 * memory location would be found.
 */
struct offset_pair {
	// Offset *in decoded bytes* for location.
	uint64_t offset;
	// Ordinal of shard containing memory location.
	uint8_t file_shard;
};

/* Description of how input files are sharded for a memory model.
 * This struct should describe features generically enough so we can
 * use the same code for unsharding while only adjusting these lines.
 */
struct sharding_info {
	// Total number of bytes in final hex dump.
	uint64_t memory_size;

	// Expected file size for each shard.
	// Incorrect sizes cause us to fail immediately.
	uint64_t expected_file_size;

	// Files from ddr dumps are of form funos-s%d-emu.64big.ch%d or
	// funos-s%d-emu.64big.ch%dinst%d.slice.
	// Number of different shard files.
	uint16_t num_channels;

	// Number of instances.  If 1, then assume the filename doesn't
	// mention the inst number.
	uint16_t num_inst;

	// Array of channel numbers in order that channel files
	// should be read.
	// There are num_channels * num_inst entries.
	uint16_t *channel_order;

	// Number of contiguous bytes in a dump file.
	// Based on size of memory lines in memory.
	size_t stride_size;

	// File extension with substitutions for channel/part.
	const char *extension;

	// Function for calculating address to shard mapping.
	struct offset_pair (*addr_to_shard)(uint64_t address);

	/* How many bytes needed to decode 8 bytes. Used for
	 * efficient reading of input text file.
	 */
	uint16_t file_read_chunk;
};

/* Returns offset, shard_file for specified address. */
struct offset_pair ddr_address_to_offset(uint64_t address);

/* Returns implementation details for S1 DDR sharded dumps. */
struct sharding_info ddr_shard_info(void);

/* Parse two lines of output into 8 bytes.
 * Values in current machine's endianness so writing binaries right will
 * shove data out in correct order.
 *
 * cursor_ptr points to start of text buffer, and updates after each read.
 */
uint64_t ddr_decode_lines(const char **cursor_ptr);

// Number of bytes returned on each ddr_decode_lines call.
#define BYTES_PER_LINE 8

#ifdef __cplusplus
};
#endif
