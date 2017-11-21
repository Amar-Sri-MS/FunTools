#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

#include "test_macros.h"

#include "swap_gen.h"

int main(int argc, char **argv) {
	struct SwapReq s;
	uint8_t value_8 = 0xa5;
	uint16_t value_16 = 0x3210;
	uint32_t value_32 = 0x76543210;
	uint64_t value_64 = 0xfedcba9876543210;
	uint8_t value_3 = 0x5;
	uint8_t value_2 = 0x2;
	uint8_t value_1 = 0x1;
	uint16_t fourteen_bit_value = 0x543;

	s.value_64 = __builtin_bswap64(value_64);
	s.value_32 = __builtin_bswap32(value_32);
	s.value_16 = __builtin_bswap16(value_16);

	// Single byte values aren't explicitly swapped.
	s.value_8 = value_8;

	// Bitfields are swapped in containers.
	s.value_pack =
	  SWAP_REQ_VALUE_3_P(value_3) | 
	  SWAP_REQ_VALUE_2_P(value_2) | 
	  SWAP_REQ_VALUE_1_P(value_1);
	  
	s.value_14_pack =
	  __builtin_bswap16(SWAP_REQ_VALUE_14_P(fourteen_bit_value));

	SWAP_REQ_SWAP(s);

	ASSERT_EQUAL(value_64, s.value_64, "");
	ASSERT_EQUAL(value_32, s.value_32, "");
	ASSERT_EQUAL(value_16, s.value_16, "");

	ASSERT_EQUAL(value_8, s.value_8, "");

	ASSERT_EQUAL(value_3,
		     SWAP_REQ_VALUE_3_G(s.value_pack), "");

	ASSERT_EQUAL(value_2,
		     SWAP_REQ_VALUE_2_G(s.value_pack), "");

	ASSERT_EQUAL(value_1,
		     SWAP_REQ_VALUE_1_G(s.value_pack), "");
	ASSERT_EQUAL(value_2,
		     SWAP_REQ_VALUE_2_G(s.value_pack), "");

	ASSERT_EQUAL(value_3,
		     SWAP_REQ_VALUE_3_G(s.value_pack),
		     "");
	ASSERT_EQUAL(fourteen_bit_value,
		     SWAP_REQ_VALUE_14_G(s.value_14_pack),
		     "");
}
