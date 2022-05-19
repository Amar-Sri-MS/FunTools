/*
 * Unit tests for DDR unsharding.
 *
 * Copyright Fungible Inc. 2022.  All rights reserved.
 */

#include <inttypes.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

#include "ddr_address.h"

#include <gtest/gtest.h>

bool fail = false;

/* Fills in an offset_pair. */
struct offset_pair make_offset(uint8_t shard, uint64_t offset) {
	struct offset_pair p;
	p.file_shard = shard;
	p.offset = offset;
	return p;
}

#define EXPECT_EQ_OFFSET(x, y) {\
		EXPECT_EQ((x).offset, (y).offset);\
		EXPECT_EQ((x).file_shard, (y).file_shard);}

/* Test that all expected offset bits get touched. */
TEST(AddressToOffset, DumpAllAddresses) {
	uint64_t all_bits = 0x3f; // Set bits within line.
	uint64_t expected_bits;
	struct sharding_info shard_info = ddr_shard_info();

	expected_bits = (shard_info.memory_size / (shard_info.num_channels *
						   shard_info.num_inst)) - 1;

	for (uint64_t addr=0; addr < shard_info.memory_size; addr += 0x40) {
		struct offset_pair offset = ddr_address_to_offset(addr);

		all_bits |= offset.offset;
	}

	EXPECT_EQ(expected_bits, all_bits);
}

TEST(AddressToOffset, ShardsMapToSameOffset)
{
	// TODO(bowdidge): Switch to GUnit or another existing framework.
	struct offset_pair expected;
	EXPECT_EQ_OFFSET(make_offset(0, 0x0),
		  ddr_address_to_offset(0x0));
	EXPECT_EQ_OFFSET(make_offset(2, 0x40000040),
		     ddr_address_to_offset(0x100));
	EXPECT_EQ_OFFSET(make_offset(3, 0x100),
		     ddr_address_to_offset(0x400));
	EXPECT_EQ_OFFSET(make_offset(7, 0x80000180),
			 ddr_address_to_offset(0x6c0));

}


TEST(AddressToOffset, AdjacentAddressMapToDifferentOffsets)
{
	// Adjacent addresses in the same shard map to wildly different
	// addresses because of scattering across high bits.
	EXPECT_EQ_OFFSET(make_offset(3, 0x30ecb280),
		     ddr_address_to_offset(0x76584a00));
	EXPECT_EQ_OFFSET(make_offset(1, 0x70ecb2c0),
		     ddr_address_to_offset(0x76584b00));
	EXPECT_EQ_OFFSET(make_offset(2, 0xb0ecb300),
		     ddr_address_to_offset(0x76584c00));
	EXPECT_EQ_OFFSET(make_offset(0, 0xf0ecb340),
		     ddr_address_to_offset(0x76584d00));
	EXPECT_EQ_OFFSET(make_offset(0, 0x30ecb380),
		     ddr_address_to_offset(0x76584e00));
	EXPECT_EQ_OFFSET(make_offset(2, 0x70ecb3c0),
		     ddr_address_to_offset(0x76584f00));
}

TEST(DecodeLine, Simple)
{
	char buf[8];

	// decode_lines returns in little-endian format so value is written
	// in correct byte order on write.
	// NEXT is invalid, but lets us check cursor advanced.
	char buf1[] = ("ff12345678\n"
		       "779abcdef0\n"
		       "9999999999\n"
		       "9999999999\n"); // Cursor should adv here.
	const char *buf_ptr = buf1;
	EXPECT_EQ(0xf0debc9a78563412,
		  ddr_decode_lines(&buf_ptr));
	// Make sure advanced to next line.
	EXPECT_EQ(buf_ptr[0], '9');

	// & is invalid, but lets us check cursor moved ahead.
	char buf2[] = ("0700010203\n"
		       "0000405060\n"
		       "FFFFFFFFFF\n"
		       "FFFFFFFFFF\n");

	buf_ptr = buf2;
	EXPECT_EQ(0x6050400003020100,
		  ddr_decode_lines(&buf_ptr));
	// Make sure advanced to next line.
	EXPECT_EQ(buf_ptr[0], 'F');
}

int main(int argc, char* argv[]) {
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
