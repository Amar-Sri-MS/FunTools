/**
 * Tests that header generated by generator.py script correctly parses code
 * and correctly aligned fields.
 *
 * This test requires the rdma.gen file as input to generator.py.
 *
 * Robert Bowdidge, August 8, 2016.
 * Copyright Fungible Inc. 2016.
 */

#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <stddef.h> // offsetof
#include <strings.h> // bzero.

#import "rdma_packed_gen.h"

#define ASSERT_SIZE(var, bytes, varStr)		\
  if (sizeof(var) != bytes) {						\
    fprintf(stderr, "FAIL: %s structure expected to be %d bytes, got %lu\n", \
	    varStr, bytes, sizeof(var)); \
  } else { \
    fprintf(stderr, "PASS: %s\n", varStr);		\
  }    

#define ASSERT_OFFSET(var, field, offset, varStr)			\
  if (offsetof(var, field) !=offset) {					\
    fprintf(stderr, "FAIL: %s structure expected to be %d bytes, got %lu\n", \
	    varStr, offset, offsetof(var, field));				\
    exit(1); \
  } else { \
    fprintf(stderr, "PASS: %s\n", varStr);		\
  }    

#define ASSERT_EQUAL(expected_value, gotten_value, msg) \
  if (expected_value != gotten_value) { \
    fprintf(stderr, "FAIL: %s: Expected %lld, got %lld\n",\
	    msg, expected_value, gotten_value);	  \
    exit(1); \
  } else {\
    fprintf(stderr, "PASS: %s\n", msg);\
  }

  
int main(int argc, char** argv) {
  struct GatherListFragmentHeader frag;
  struct GatherListFragmentHeader *fragPtr = malloc(sizeof(struct GatherListFragmentHeader));

  bzero(fragPtr, sizeof(struct GatherListFragmentHeader));
  
  ASSERT_SIZE(frag, 16, "frag structure is not expected size.");

  // Set fields to valid, in range values, and make sure values come
  // out unchanged.
  int source = 2;
  int byte_count = 11;
  uint64_t bytes1_value = 0xba9876654321;
  uint64_t bytes2_value = 0xffffffffffffffff;

  // Initialize with garbage.
  fragPtr->u1.inline_cmd.opcode_to_inlineByteCount = 0xff;

  // Initialize opcode.
  uint8_t value =  FUN_GATHER_LIST_INLINE_FRAGMENT_OPCODE_P(FUN_GATHER_LIST_INLINE_FRAGMENT_OPCODE_M) 
    | FUN_GATHER_LIST_INLINE_FRAGMENT_SOURCE_P(FUN_GATHER_LIST_INLINE_FRAGMENT_SOURCE_M)
    | FUN_GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_P(FUN_GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_M);

   printf("value is %d\n", value);
  fragPtr->u1.inline_cmd.opcode_to_inlineByteCount &= ~value;

  ASSERT_EQUAL(0, fragPtr->u1.inline_cmd.opcode_to_inlineByteCount,
	     "field not initialized.");

  // Set all fields to non-zero values, and make sure they read out ok.
  fragPtr->u1.inline_cmd.opcode_to_inlineByteCount |=
    FUN_GATHER_LIST_INLINE_FRAGMENT_OPCODE_P(OPCODE_SCATTER) |
    FUN_GATHER_LIST_INLINE_FRAGMENT_SOURCE_P(source) |
    FUN_GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_P(byte_count);
  fragPtr->u1.inline_cmd.bytes1 = bytes1_value;
  fragPtr->u1.inline_cmd.bytes2 = bytes2_value;


  ASSERT_EQUAL(0xab, fragPtr->u1.inline_cmd.opcode_to_inlineByteCount,
	     "raw value not correct.");

  ASSERT_EQUAL(OPCODE_SCATTER,
	     FUN_GATHER_LIST_INLINE_FRAGMENT_OPCODE_G(fragPtr->u1.inline_cmd.opcode_to_inlineByteCount),
	     "Opcode read doesn't return expected value.");

  ASSERT_EQUAL(source,
	     FUN_GATHER_LIST_INLINE_FRAGMENT_SOURCE_G(fragPtr->u1.inline_cmd.opcode_to_inlineByteCount),
	     "source read doesn't return expected value.");

  ASSERT_EQUAL(byte_count,
	     FUN_GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_G(fragPtr->u1.inline_cmd.opcode_to_inlineByteCount),
	     "inline byte count read doesn't return expected value.");

  ASSERT_EQUAL(bytes1_value, fragPtr->u1.inline_cmd.bytes1,
	      "check bytes1");
  ASSERT_EQUAL(bytes2_value, fragPtr->u1.inline_cmd.bytes2,
	      "check bytes2");

  // Change single value.
  // Clear.
  fragPtr->u1.inline_cmd.opcode_to_inlineByteCount &= 
    ~FUN_GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_P(FUN_GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_M);
  fragPtr->u1.inline_cmd.opcode_to_inlineByteCount |= FUN_GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_P(7);

  ASSERT_EQUAL(7,
	       FUN_GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_G(fragPtr->u1.inline_cmd.opcode_to_inlineByteCount),
	       "Change single value returned wrong value.");

  // Test initialization.
  int expected_source = 2;
  int expected_byte_count = 14;
  uint64_t expected_bytes1 = 0xfefefefefefe;
  uint64_t expected_bytes2 = 0x800000000;

  struct GatherListFragmentHeader hdr;
  GatherListInlineFragment_init(&hdr, OPCODE_SCATTER, expected_source,
				expected_byte_count,
				expected_bytes1, expected_bytes2);

  ASSERT_EQUAL(OPCODE_SCATTER, 
	       FUN_GATHER_LIST_INLINE_FRAGMENT_OPCODE_G(hdr.u1.inline_cmd.opcode_to_inlineByteCount),
	       "opcode not initialized correctly.");
  ASSERT_EQUAL(expected_source,
	       FUN_GATHER_LIST_INLINE_FRAGMENT_SOURCE_G(hdr.u1.inline_cmd.opcode_to_inlineByteCount), 
	       "source not initialized correctly.");
  ASSERT_EQUAL(expected_byte_count,
	       FUN_GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_G(hdr.u1.inline_cmd.opcode_to_inlineByteCount),
	       "inlineByteCount not initialized correctly.");
  ASSERT_EQUAL(expected_bytes1, hdr.u1.inline_cmd.bytes1,
	       "bytes1 not initialized correctly");
  ASSERT_EQUAL(expected_bytes2, hdr.u1.inline_cmd.bytes2,
	       "bytes2 not initialized correctly");
}

