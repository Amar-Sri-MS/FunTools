/*
 * Unit tests for DDR unsharding.
 *
 * Copyright Fungible Inc. 2019.  All rights reserved.
 */

#include <inttypes.h>
#include <stdbool.h>
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

#define EXPECT_EQ_OFFSET(x, y) {EXPECT_EQ((x).offset, (y).offset); EXPECT_EQ((x).file_shard, (y).file_shard);}

TEST(AddressToOffset, ShardsMapToSameOffset)
{
	// TODO(bowdidge): Switch to GUnit or another existing framework.
	struct offset_pair expected;
	EXPECT_EQ_OFFSET(make_offset(0, 0x21d96240),
		  ddr_address_to_offset(0x76584900));
	EXPECT_EQ_OFFSET(make_offset(2, 0x21d96240),
		     ddr_address_to_offset(0x76584940));
	EXPECT_EQ_OFFSET(make_offset(1, 0x21d96240),
		     ddr_address_to_offset(0x76584980));
	EXPECT_EQ_OFFSET(make_offset(3, 0x21d96240),
		     ddr_address_to_offset(0x765849c0));
}

TEST(AddressToOffset, AdjacentAddressMapToDifferentOffsets)
{
	// Adjacent addresses in the same shard map to wildly different
	// addresses because of scattering across high bits.
	EXPECT_EQ_OFFSET(make_offset(0, 0x11d96280),
		     ddr_address_to_offset(0x76584a00));
	EXPECT_EQ_OFFSET(make_offset(0, 0x31d962c0),
		     ddr_address_to_offset(0x76584b00));
	EXPECT_EQ_OFFSET(make_offset(0, 0x81d96300),
		     ddr_address_to_offset(0x76584c00));
	EXPECT_EQ_OFFSET(make_offset(0, 0xa1d96340),
		     ddr_address_to_offset(0x76584d00));
	EXPECT_EQ_OFFSET(make_offset(0, 0x91d96380),
		     ddr_address_to_offset(0x76584e00));
	EXPECT_EQ_OFFSET(make_offset(0, 0xb1d963c0),
		     ddr_address_to_offset(0x76584f00));
}

TEST(DecodeLine, Simple)
{
	char buf[8];

	// decode_lines returns in little-endian format so value is written
	// in correct byte order on write.
	// NEXT is invalid, but lets us check cursor advanced.
	char buf1[] = ("0f12345678\n"
		       "01109abcde\n"
		       "9999999999\n"
		       "9999999999\n"); // Cursor should adv here.
	const char *buf_ptr = buf1;
	EXPECT_EQ(0xefcdab0978563412,
		  ddr_decode_lines(&buf_ptr));
	// Make sure advanced to next line.
	EXPECT_EQ(buf_ptr[0], '9');

	// & is invalid, but lets us check cursor moved ahead.
	char buf2[] = ("0700010203\n"
		       "0000405060\n"
		       "FFFFFFFFFF\n"
		       "FFFFFFFFFF\n");

	buf_ptr = buf2;
	EXPECT_EQ(0x0706050403020100,
		  ddr_decode_lines(&buf_ptr));
	// Make sure advanced to next line.
	EXPECT_EQ(buf_ptr[0], 'F');
}

int main(int argc, char* argv[]) {
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
