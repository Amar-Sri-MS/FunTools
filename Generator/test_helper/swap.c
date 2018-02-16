#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

#include "test_macros.h"

#define __BIG_ENDIAN 1
#define __LITTLE_ENDIAN 2
#define __DPU_BYTEORDER __BIG_ENDIAN


#define __u8 uint8_t
#define __u16 uint16_t
#define __u32 uint32_t
#define __u64 uint64_t

#define __le16 __u16
#define __le32 __u32
#define __le64 __u64

#define __be16 __u16
#define __be32 __u32
#define __be64 __u64

#define cpu_to_le16(x) (x)
#define cpu_to_le32(x) (x)
#define cpu_to_le64(x) (x)

#define cpu_to_be16(x) (__builtin_bswap16(x))
#define cpu_to_be32(x) (__builtin_bswap32(x))
#define cpu_to_be64(x) (__builtin_bswap64(x))

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
	uint16_t new_fourteen_bit_value = 0x31f7;


	SwapReq_init(&s, value_64, value_32, value_16, value_8,
		     value_3, value_2, value_1, fourteen_bit_value);

	// Need to swap when pulling out manually.
	ASSERT_EQUAL(value_64, __builtin_bswap64(s.value_64), "");
	ASSERT_EQUAL(value_32, __builtin_bswap32(s.value_32), "");
	ASSERT_EQUAL(value_16, __builtin_bswap16(s.value_16), "");

	// 8 bit values not swapped.
	ASSERT_EQUAL(value_8, s.value_8, "");

	// Bitfields automatically swapped.
	ASSERT_EQUAL(fourteen_bit_value,
		     SWAP_REQ_VALUE_14_G(s.value_14_pack), "");

	s.value_14_pack = SWAP_REQ_VALUE_14_P(new_fourteen_bit_value);

	ASSERT_EQUAL(value_3, SWAP_REQ_VALUE_3_G(s.value_pack), "");
	ASSERT_EQUAL(value_2, SWAP_REQ_VALUE_2_G(s.value_pack), "");
	ASSERT_EQUAL(value_1, SWAP_REQ_VALUE_1_G(s.value_pack), "");

	ASSERT_EQUAL(new_fourteen_bit_value,
		     SWAP_REQ_VALUE_14_G(s.value_14_pack), "");
}
