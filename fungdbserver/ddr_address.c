/*
 * Code specific to decoding dumps of DDR memory for S1 on Palladium.
 *
 * Copyright Fungible Inc. 2019. All rights reserved.
 *
 * Dumps fed into Palladium need to be arranged according to the internal
 * layout of addresses which does not necessarily match the addresses from
 * software's point of view.  Dumps are also sharded across multiple files,
 * with each shard file providing a memory line of data in turn.
 *
 * As best I understand, the actual layout of lines is a mix of our own
 * hardware decisions for the MUD block and what's supported by the memory /
 * Cadence's IP.
 *
 * For more information, see:
 * split_hex_ddr_s1_rdimm_4.pl: Fungible-created utility for dumping.
 * Cadence docs on DDR IP.
 * MUD block description (for channels, spray, etc.)
 *     Tech > S1 > Specifications > MU > S1 MUD Spec.doc
 *
 * Helpful hint: Use "od -A x -t x1" to dump out in character order.
 * Helpful hint: remember that your x86 is little endian, and the S1 is
 * big-endian.
 */

#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include <stdlib.h>
#include "ddr_address.h"

/* Calculate the reduced XOR for the value.
 *
 * Returns 1 if x has an even number of bits, and 0 otherwise.
 */
static uint64_t reduced_xor64(uint64_t x)
{
	x = (x>>16) ^ x;
	x = (x>>8)  ^ x;
	x = (x>>4)  ^ x;
	x = (x>>2)  ^ x;
	x = (x>>1)  ^ x;
	x &= 1;

	return x;
}

// 10 characters plus line feed for four bits.
#define LINELEN 11

static const char HEXVALS[256] = {
	['0'] = 0,
	['1'] = 1,
	['2'] = 2,
	['3'] = 3,
	['4'] = 4,
	['5'] = 5,
	['6'] = 6,
	['7'] = 7,
	['8'] = 8,
	['9'] = 9,
	['a'] = 0xa,
	['b'] = 0xb,
	['c'] = 0xc,
	['d'] = 0xd,
	['e'] = 0xe,
	['f'] = 0xf,
	['A'] = 0xa,
	['B'] = 0xb,
	['C'] = 0xc,
	['D'] = 0xd,
	['E'] = 0xe,
	['F'] = 0xf,
};
/* Returns nybble value (0-15) for hex character. */
uint64_t decode_char(char c) {
	if ((c >= '0' && c <= '9') ||
	    (c >= 'A' && c <= 'F') ||
	    (c >= 'a' && c <= 'f')) {
		return (uint64_t) HEXVALS[c];
	}
	printf("Invalid hex character %c\n", c);
	exit(1);
}

/* Read 8 bytes of data from the text file for a DDR dump.
 *
 * ptr: pointer to pointer to text buffer containing data.
 *
 * Returns 8 byte value in native machine's byte order.
 */
uint64_t ddr_decode_lines(const char **cursor_ptr)
{
	/*
	  Each line of input from the dump looks like 5 bytes of hex swizzled.
	  (Peter says they're 36 bits of data per line with 8 bits ECC.)
	  0haabbccdd
	  0??eeffggh
	  where aa, bb, cc, dd, ee, ff, gg, hh isa two digit hex byte and ?? is
	  the checksum.  Checksums are supposedly off right now.)

	  Each two lines represents 8 bytes of data.

	  Each 16 lines represents 64 bytes of data for one line of
	  memory for a single channel.
	*/
	const char *ptr = *cursor_ptr;
	assert(ptr[LINELEN-1] == '\n');
	assert(ptr[LINELEN * 2-1] == '\n');
	char buf[LINELEN * 2];
	strncpy(buf, ptr, LINELEN * 2);
	buf[LINELEN * 2 - 1] = '\0';
	uint64_t value = (decode_char(ptr[2]) << 4 |
			  decode_char(ptr[3]) << 0 |
			  decode_char(ptr[4]) << 12 |
			  decode_char(ptr[5]) << 8 |
			  decode_char(ptr[6]) << 20 |
			  decode_char(ptr[7]) << 16 |
			  decode_char(ptr[8]) << 28 |
			  decode_char(ptr[9]) << 24 |
			  decode_char(ptr[14]) << 36 |
			  decode_char(ptr[15]) << 32 |
			  decode_char(ptr[16]) << 44 |
			  decode_char(ptr[17]) << 40 |
			  decode_char(ptr[18]) << 52 |
			  decode_char(ptr[19]) << 48 |
			  decode_char(ptr[20]) << 60 |
			  decode_char(ptr[1]) << 56);

	*cursor_ptr += LINELEN * 2;
	return value;
}

/* Constants specific to S1_DDR conversion.
 * Don't know what these are?  Check out the MUD Spec, talk with a
 * hardware design engineer, or (preferred) stick your fingers in your ears
 * and say "la la la la" very loudly.
 */

// Whether requests are sp
bool S1_DDR_SPRAY = true;

// Bits used internally to select QSYS line (queue?) and bank selector.
const int S1_DDR_QSYS_SEL = 28;
const int S1_DDR_BA0_SEL = 8;
const int S1_DDR_BA1_SEL = 9;
const int S1_DDR_BA2_SEL = 6;
const int S1_DDR_BA3_SEL = 7;

// Mask out the bank selector bits from internal layout.
#define S1_DDR_QADDR_MASK (~((1 << S1_DDR_BA0_SEL) | (1 << S1_DDR_BA1_SEL) | \
			     (1 << S1_DDR_BA2_SEL) | (1 << S1_DDR_BA3_SEL)))

// Masks for bits used to convert mangled addresses into the bank ids.
// "Those who know don't tell; those who tell don't know."
const int S1_DDR_QN1_MASK = 0x122;
const int S1_DDR_QN2_MASK = 0x211;
const int S1_DDR_QN3_MASK = 0x48;
const int S1_DDR_QN4_MASK = 0x84;

// la la la la la la la I can't hear you!
const uint64_t S1_DDR_QSN_MASK = 0x10000000;
const uint64_t S1_DDR_QSYS_MASK = (1 << S1_DDR_QSYS_SEL);

/* Converts memory address in DDR to channel and offset where bytes will
 * be found.
 *
 * This function is intended for S1 DDR dumps.
 *
 * Offset must be aligned to 64 byte stride for shard.
 */
struct offset_pair ddr_address_to_offset(uint64_t address) {
	// This code was converted verbatim from
	// Memory line of interest.
	assert((address & 0x3f) == 0);
	uint64_t addr_line = address >> 6;
	uint8_t shard;
	uint64_t shard_line;

	if (S1_DDR_SPRAY) {
		shard = addr_line & 1;
		shard_line = (addr_line & 0x3ffffffe) >> 1;
	} else {
		shard = (addr_line >> 29) & 1;
		shard_line = addr_line & 0x1fffffff;
	}

	uint64_t line_prehash = ((shard_line & ~S1_DDR_QSYS_MASK) >> 1) |
		((shard_line & 1) << S1_DDR_QSYS_SEL);
	uint64_t line_hashed = line_prehash & S1_DDR_QADDR_MASK;

	line_hashed |= (reduced_xor64(line_prehash & S1_DDR_QN1_MASK)
			<< S1_DDR_BA0_SEL);
	line_hashed |= (reduced_xor64(line_prehash & S1_DDR_QN2_MASK)
			<< S1_DDR_BA1_SEL);
	line_hashed |= (reduced_xor64(line_prehash & S1_DDR_QN3_MASK)
			<< S1_DDR_BA2_SEL);
	line_hashed |= (reduced_xor64(line_prehash & S1_DDR_QN4_MASK)
			<< S1_DDR_BA3_SEL);
	line_hashed |= (reduced_xor64(line_prehash & S1_DDR_QSN_MASK)
			<< S1_DDR_QSYS_SEL);

	uint64_t col = (line_hashed & 0x3f) << 4;
	uint8_t ba0 = (line_hashed >> S1_DDR_BA0_SEL) & 1;
	uint8_t ba1 = (line_hashed >> S1_DDR_BA1_SEL) & 1;
	uint8_t ba2 = (line_hashed >> S1_DDR_BA2_SEL) & 1;
	uint8_t ba3 = (line_hashed >> S1_DDR_BA3_SEL) & 1;
	uint8_t qsys = (line_hashed >> S1_DDR_QSYS_SEL) & 1;

	uint64_t bank = (ba1 << 1) | ba0;
	uint64_t bank_group = (ba3 << 1) | ba2;

	uint64_t row =(line_hashed >> 10) & 0xffff;

	struct offset_pair result;
	result.file_shard = (shard << 1) | qsys;
	// TODO(bowdidge): Figure out << 2 magic number.
	// We should be shifting by 6 bits to get back to a 64 byte offset
	// and dividing by four for the four shards.
	result.offset = (bank_group << 28 |
			 bank << 26 |
			 row << 10 |
			 col) << 2;

	return result;
}

/* Returns structure describing how the DDR file is sharded. */
struct sharding_info ddr_shard_info(void) {
	struct sharding_info ddr_info;

	ddr_info.memory_size = 0x200000000;
	ddr_info.num_channels = 4;
	ddr_info.extension = "%s.ch%d";

	// 64 bytes in a file, then rotate.
	ddr_info.stride_size = 64;
	ddr_info.channel_order = (uint16_t*) malloc(sizeof(uint16_t) * 4);
	// TODO(bowdidge): Why don't we need to swizzle the order of channels?
	ddr_info.channel_order[0] = 0;
	ddr_info.channel_order[1] = 1;
	ddr_info.channel_order[2] = 2;
	ddr_info.channel_order[3] = 3;

	ddr_info.addr_to_shard = &ddr_address_to_offset;

	// Expected file size should be
	// memory_size_bytes * lines / word * 1 word / 8 bytes * 1/4 shards
	ddr_info.expected_file_size = LINELEN * ddr_info.memory_size / 8;

	// 8 bytes over two lines.
	ddr_info.file_read_chunk = 2 * LINELEN;

	return ddr_info;
}
