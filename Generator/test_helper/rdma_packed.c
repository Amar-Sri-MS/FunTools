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
#include <inttypes.h>
#include <stdlib.h>
#include <stdio.h>
#include <stddef.h> // offsetof
#include <strings.h> // bzero.

#import "rdma_packed_gen.h"

// TODO(bowdidge): Switch to gtest.
#define ASSERT_SIZE(var, bytes, varStr)					\
  if (sizeof(var) != (bytes)) {						\
    fprintf(stderr, "FAIL: %s structure expected to be %" PRIu64 " bytes, got %" PRIu64 "\n", \
	    varStr, (uint64_t) (bytes), (uint64_t) sizeof(var));		\
  } else {								\
    fprintf(stderr, "PASS: %s\n", varStr);				\
  }    

#define ASSERT_OFFSET(var, field, offset, varStr)			\
  if (offsetof(var, field) !=offset) {					\
    fprintf(stderr, "FAIL: %s structure expected to be %" PRIu64 " bytes, got %" PRIu64 "\n", \
	    varStr, (uint64_t) offset, (uint64_t) offsetof(var, field)); \
    exit(1);								\
  } else {								\
    fprintf(stderr, "PASS: %s\n", varStr);				\
  }    

#define ASSERT_EQUAL(expected_value, gotten_value, msg)			\
  if ((expected_value) != (gotten_value)) {				\
    fprintf(stderr, "FAIL: %s: Expected %" PRIu64 ", got %" PRIu64 "\n", \
	    msg, (uint64_t) (expected_value), (uint64_t) (gotten_value)); \
    exit(1);								\
  } else {								\
    fprintf(stderr, "PASS: %s\n", msg);					\
  }

#define ASSERT_TRUE(gotten_value, msg)			\
  if (!(gotten_value)) {				\
    fprintf(stderr, "FAIL: %s: Expression not true.\n",	\
	    msg);					\
    exit(1);						\
  } else {						\
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
  const char* expected_bytes = "01234567890123";

  // Initialize with garbage.
  fragPtr->u1.inline_cmd.opcode_to_inlineByteCount = 0xff;

  // Initialize opcode.
  uint8_t value =  GATHER_LIST_INLINE_FRAGMENT_OPCODE_P(GATHER_LIST_INLINE_FRAGMENT_OPCODE_M) 
    | GATHER_LIST_INLINE_FRAGMENT_SOURCE_P(GATHER_LIST_INLINE_FRAGMENT_SOURCE_M)
    | GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_P(GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_M);
  strcpy((char*)fragPtr->u1.inline_cmd.bytes, expected_bytes);

   printf("value is %d\n", value);
  fragPtr->u1.inline_cmd.opcode_to_inlineByteCount &= ~value;

  ASSERT_EQUAL(0, fragPtr->u1.inline_cmd.opcode_to_inlineByteCount,
	     "field not initialized.");

  // Set all fields to non-zero values, and make sure they read out ok.
  fragPtr->u1.inline_cmd.opcode_to_inlineByteCount |=
    GATHER_LIST_INLINE_FRAGMENT_OPCODE_P(OPCODE_SCATTER) |
    GATHER_LIST_INLINE_FRAGMENT_SOURCE_P(source) |
    GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_P(byte_count);


  ASSERT_EQUAL(0xab, fragPtr->u1.inline_cmd.opcode_to_inlineByteCount,
	     "raw value not correct.");

  ASSERT_EQUAL(OPCODE_SCATTER,
	     GATHER_LIST_INLINE_FRAGMENT_OPCODE_G(fragPtr->u1.inline_cmd.opcode_to_inlineByteCount),
	     "Opcode read doesn't return expected value.");

  ASSERT_EQUAL(source,
	     GATHER_LIST_INLINE_FRAGMENT_SOURCE_G(fragPtr->u1.inline_cmd.opcode_to_inlineByteCount),
	     "source read doesn't return expected value.");

  ASSERT_EQUAL(byte_count,
	     GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_G(fragPtr->u1.inline_cmd.opcode_to_inlineByteCount),
	     "inline byte count read doesn't return expected value.");

  printf("'%s' vs '%s'\n", expected_bytes, (const char *) fragPtr->u1.inline_cmd.bytes);
  ASSERT_TRUE(0 == strncmp(expected_bytes, (const char *) fragPtr->u1.inline_cmd.bytes, 14),
	      "check bytes");

  // Change single value.
  // Clear.
  fragPtr->u1.inline_cmd.opcode_to_inlineByteCount &= 
    ~GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_P(GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_M);
  fragPtr->u1.inline_cmd.opcode_to_inlineByteCount |= GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_P(7);

  ASSERT_EQUAL(7,
	       GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_G(fragPtr->u1.inline_cmd.opcode_to_inlineByteCount),
	       "Change single value returned wrong value.");

  // Test initialization.
  int expected_source = 2;
  int expected_byte_count = 14;

  struct GatherListFragmentHeader hdr;
  strcpy((char*) hdr.u1.inline_cmd.bytes, expected_bytes);

  GatherListInlineFragment_init(&hdr, OPCODE_SCATTER, expected_source,
				expected_byte_count);

  ASSERT_EQUAL(OPCODE_SCATTER, 
	       GATHER_LIST_INLINE_FRAGMENT_OPCODE_G(hdr.u1.inline_cmd.opcode_to_inlineByteCount),
	       "opcode not initialized correctly.");
  ASSERT_EQUAL(expected_source,
	       GATHER_LIST_INLINE_FRAGMENT_SOURCE_G(hdr.u1.inline_cmd.opcode_to_inlineByteCount), 
	       "source not initialized correctly.");
  ASSERT_EQUAL(expected_byte_count,
	       GATHER_LIST_INLINE_FRAGMENT_INLINE_BYTE_COUNT_G(hdr.u1.inline_cmd.opcode_to_inlineByteCount),
	       "inlineByteCount not initialized correctly.");
  ASSERT_TRUE(0 == strncmp(expected_bytes, (const char *) hdr.u1.inline_cmd.bytes, 14),
	       "bytes not initialized correctly");
}

