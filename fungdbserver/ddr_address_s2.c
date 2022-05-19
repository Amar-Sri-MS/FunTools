/*
 * Code specific to decoding dumps of DDR memory for S2 on Palladium.
 *
 * Copyright Fungible Inc. 2022. All rights reserved.
 *
 * Dumps fed into and extracted out of Palladium are arranged
 * according to the internal layout of addresses for the emulated memory;
 * data is sharded, and data isn't necessarily in address order because of
 * some odd mappings.
 *
 * As best I understand, the actual layout of lines is a mix of our own
 * hardware decisions for the MUD block and what's supported by the memory
 * model from IP.
 *
 * For more information, see:
 * split_hex_ddr_s2_rdimm_with_protium_support.pl: Fungible-created utility
 * for dumping.
 * Cadence docs on DDR IP.
 * MUD block description (for channels, spray, etc.) are in places like
 *     Tech > S1 > Specifications > MU > S1 MUD Spec.doc
 *
 * Helpful hint: Use "od -A x -t x1" to dump out in character order, or
 * just use hexdump -C.
 *
 * Helpful hint: remember that your x86 is little endian, and the S2 is
 * big-endian.
 */

#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include "ddr_address.h"

/* Calculate the reduced XOR for the value.
 *
 * Returns 1 if x has an even number of bits, and 0 otherwise.
 */
static uint64_t reduced_xor64(uint64_t x)
{
	x = (x>>32) ^ x;
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
	 * For S2, each two lines represents 8 bytes of data.
	 * The approach is simpler than S1:
	 * ??aabbccdd
	 * ??eeffgghh
	 * where aa, bb, cc, dd, ee, ff, gg, hh isa two digit hex byte and
	 * ?? is the checksum.
	 *
	 * Each two lines represents 8 bytes of data.
	 *
	 * Each 16 lines represents 64 bytes of data for one line of
	 * memory for a single channel.
	 */
	const char *ptr = *cursor_ptr;
	assert(ptr[LINELEN-1] == '\n');
	assert(ptr[LINELEN * 2-1] == '\n');

	uint64_t value = (decode_char(ptr[2]) << 4 |
			  decode_char(ptr[3]) << 0 |
			  decode_char(ptr[4]) << 12 |
			  decode_char(ptr[5]) << 8 |
			  decode_char(ptr[6]) << 20 |
			  decode_char(ptr[7]) << 16 |
			  decode_char(ptr[8]) << 28 |
			  decode_char(ptr[9]) << 24 |
			  decode_char(ptr[13]) << 36 |
			  decode_char(ptr[14]) << 32 |
			  decode_char(ptr[15]) << 44 |
			  decode_char(ptr[16]) << 40 |
			  decode_char(ptr[17]) << 52 |
			  decode_char(ptr[18]) << 48 |
			  decode_char(ptr[19]) << 60 |
			  decode_char(ptr[20]) << 56);

	*cursor_ptr += LINELEN * 2;
	return value;
}

/* Constants specific to S2_DDR conversion.
 * Don't know what these are?  Check out the MUD Spec, talk with a
 * hardware design engineer, or (preferred) stick your fingers in your ears
 * and say "la la la la" very loudly.
 */

// Whether requests are sprayed across ... um.
bool S2_DDR_SPRAY = true;

// Whether (I guess) memory is in a 128 byte mode where a different
// address bit is used to choose which shard contains which bytes.
// Currently default.
bool S2_DDR_128B = true;

// Bits used internally to select QSYS line (queue?) and bank selector.
// Bit positions are relative to an address line, not an address.
const int S2_DDR_QSYS_SEL = 28;
const int S2_DDR_BA0_SEL = 9;
const int S2_DDR_BA1_SEL = 10;
const int S2_DDR_BA2_SEL = 6;
const int S2_DDR_BA3_SEL = 7;
const int S2_DDR_BA4_SEL = 8;

// Mask out the bank selector bits from internal layout of an address line.
const uint64_t S2_DDR_QADDR_MASK = (~((1 << S2_DDR_BA0_SEL) |
				      (1 << S2_DDR_BA1_SEL) |
				      (1 << S2_DDR_BA2_SEL) |
				      (1 << S2_DDR_BA3_SEL) |
				      (1 << S2_DDR_BA4_SEL) |
				      (1 << S2_DDR_QSYS_SEL)));

// Masks for bits used to convert mangled addresses into the bank ids.
// "Those who know don't tell; those who tell don't know."
const uint64_t S2_DDR_QN1_MASK = 0x1084210;
const uint64_t S2_DDR_QN2_MASK = 0x2108420;
const uint64_t S2_DDR_QN3_MASK = 0x0210849;
const uint64_t S2_DDR_QN4_MASK = 0x4421082;
const uint64_t S2_DDR_QN5_MASK = 0x0842104;
const uint64_t S2_DDR_QN6_MASK = 0x0;
const uint64_t S2_DDR_QN7_MASK = 0x0;

// It's a mask.  Quite obvious, really.
const uint64_t S2_DDR_QSN_MASK = 0x17FFFFFF;

/* Converts memory address in DDR to channel and offset where bytes will
 * be found.
 *
 * This function is intended for S2 DDR dumps.
 *
 * Offset must be aligned to 64 byte boundaries.
 *
 * Taken directly from split_hex_ddr_s2_rdimm_with_protium_support.pl.
 */
struct offset_pair ddr_address_to_offset(uint64_t address) {
	// This was the "protium" option, though Palladium uses the
	// Protium option.  Palladium memory is sharded into channels
	// and insts but not slices.
	int num_slices = 1;

	assert((address & 0x3f) == 0);

	// Memory line of interest.
	uint64_t addr_line = address >> 6;
	// Which half of memory this is in.  This is part of the value
	// determining which file to go to, but isn't the only contributor
	// deciding how the bytes are... er... sharded.
	uint8_t shard;

	// addr_line removing the bit indicating the shard.
	// bits 7-37 for 64 byte mode or bits 6 and 8-38 for 128 byte.
	uint64_t shard_line;

	if (S2_DDR_SPRAY) {
		if (S2_DDR_128B) {
			// 128 byte mode uses bit 7 for determining shard..
			shard = (addr_line>>1) & 1;
			shard_line = (addr_line & 0x3ffffffc) >> 1 | (addr_line & 1);
		} else {
			// 64 bit mode uses bit 6 for spray.
			shard = addr_line & 1;
			shard_line = (addr_line & 0x3ffffffe) >> 1;
		}
	} else {
		shard = (addr_line >> 29) & 1;
		shard_line = addr_line & 0x1fffffff;
	}

	uint64_t qsys_mask = 1 << S2_DDR_QSYS_SEL;
	uint64_t line_prehash = ((shard_line & ~qsys_mask) >> 1) |
		((shard_line & 1) << S2_DDR_QSYS_SEL);
	uint64_t line_hashed = line_prehash & S2_DDR_QADDR_MASK;

	line_hashed |= ((reduced_xor64(line_prehash & S2_DDR_QN1_MASK)&1)
			<< S2_DDR_BA0_SEL);
	line_hashed |= ((reduced_xor64(line_prehash & S2_DDR_QN2_MASK)&1)
			<< S2_DDR_BA1_SEL);
	line_hashed |= ((reduced_xor64(line_prehash & S2_DDR_QN3_MASK) &1)
			<< S2_DDR_BA2_SEL);
	line_hashed |= ((reduced_xor64(line_prehash & S2_DDR_QN4_MASK) &1)
			<< S2_DDR_BA3_SEL);
	line_hashed |= ((reduced_xor64(line_prehash & S2_DDR_QN5_MASK) &1)
			<< S2_DDR_BA4_SEL);
	line_hashed |= ((reduced_xor64(line_prehash & S2_DDR_QSN_MASK) &1)
			<< S2_DDR_QSYS_SEL);

	// Which of the various banks and other special bits are set.
	uint64_t col = (line_hashed & 0x3f) << 6;
	uint8_t ba0 = (line_hashed >> S2_DDR_BA0_SEL) & 1;
	uint8_t ba1 = (line_hashed >> S2_DDR_BA1_SEL) & 1;
	uint8_t ba2 = (line_hashed >> S2_DDR_BA2_SEL) & 1;
	uint8_t ba3 = (line_hashed >> S2_DDR_BA3_SEL) & 1;
	uint8_t ba4 = (line_hashed >> S2_DDR_BA4_SEL) & 1;
	uint8_t qsys = (line_hashed >> S2_DDR_QSYS_SEL) & 1;

	uint64_t bank = (ba1 << 1) | ba0;
	uint64_t bank_group = (ba4 << 2) | (ba3 << 1) | ba2;

	// Starts at 11 because 0-5 is col, 6-10 is BAx.
	uint64_t row =(line_hashed >> 11) & 0xffff;
	uint64_t inst = (bank_group >> 2) & 1;

	struct offset_pair result;

	// Identify which file in all eight funos-s2-emu.64big.chx.insty.slice
	// files should be read for these 64 bytes.
	//
	// 4 bit: bit 6 or 7 of address.
	// 2 bit: qsys bit
	// 1 bit: bank_group: whether ba4 is set, I think.
	result.file_shard = (shard << 2) | (qsys << 1) | inst;

	// Calculate the channel address - the position of the bytes
	// in the binary data from one file.
	// 28-31: bank-group
	// 26-27: bank
	// 10-26: row
	// 6-11 - col
	// 0-5 - 64 byte byte offset. (Always 0 here.)
	result.offset = (((bank_group&3) << 30) |
			 // bank is 2 bits.
			 (bank << 28) |
			 // 12-28
			 (row << 12) |
			 //6-11
			 col);

	if ((result.offset & 0x3f) != 0) {
		printf("Result offset should be 0x40 aligned but 0x%" PRIx64 "\n",
		       result.offset);
		exit(1);
	}

	return result;
}

/* Returns structure describing how the DDR file is sharded. */
struct sharding_info ddr_shard_info(void) {
	struct sharding_info ddr_info;

	// 32 GB, split 8 ways so 4 GB per shard.
	ddr_info.memory_size = 0x800000000;
	ddr_info.num_channels = 4;
	ddr_info.num_inst = 2;
	ddr_info.extension = "%s.ch%d.inst%d.slice";

	// 64 bytes in one file, then look to the next file for the next bytes.
	ddr_info.stride_size = 64;

	ddr_info.channel_order = (uint16_t*)
		malloc(sizeof(uint16_t) *
		       ddr_info.num_channels * ddr_info.num_inst);
	// Each line moves in reasonable order through the list of files.
	ddr_info.channel_order[0] = 0;
	ddr_info.channel_order[1] = 1;
	ddr_info.channel_order[2] = 2;
	ddr_info.channel_order[3] = 3;
	ddr_info.channel_order[4] = 4;
	ddr_info.channel_order[5] = 5;
	ddr_info.channel_order[6] = 6;
	ddr_info.channel_order[7] = 7;

	ddr_info.addr_to_shard = &ddr_address_to_offset;

	// Expected file size for each shard/channel.
	// LINE_LEN characters per 4 bytes.
	// slice file is memory size * lines / word * 1 word / 8 bytes /
	// (num_channels * num_files) shards.
	int num_files = ddr_info.num_channels * ddr_info.num_inst;

	ddr_info.expected_file_size = (LINELEN * ddr_info.memory_size /
				       (num_files * 4));

	// 8 bytes over two lines.
	// This is just habit - the S1 required reading pairs of lines because
	// the first and second lines had different formats.
	ddr_info.file_read_chunk = 2 * LINELEN;

	return ddr_info;
}
