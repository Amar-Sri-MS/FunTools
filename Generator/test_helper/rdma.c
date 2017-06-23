/**
 * Tests that header generated by generator.py script correctly parses code
 * and correctly aligned fields.
 *
 * This test requires the rdma.gen file as input to generator.py.
 *
 * Robert Bowdidge, August 8, 2016.
 * Copyright Fungible Inc. 2016.
 */

#import <stdlib.h>
#import <stdio.h>
#import <stddef.h> // offsetof
#include <strings.h> // bzero.

#import "rdma_gen.h"

#define EXPECT_SIZE(var, bytes, varStr)		\
  if (sizeof(var) != bytes) {						\
    fprintf(stderr, "FAIL: %s structure expected to be %d bytes, got %lu\n", \
	    varStr, bytes, sizeof(var)); \
  } else { \
    fprintf(stderr, "PASS\n"); \
  }    

#define EXPECT_OFFSET(var, field, offset, varStr)			\
  if (offsetof(var, field) !=offset) {					\
    fprintf(stderr, "FAIL: %s structure expected to be %d bytes, got %lu\n", \
	    varStr, offset, offsetof(var, field));				\
    exit(1); \
  } else { \
    fprintf(stderr, "PASS\n"); \
  }    

void PrintFragment(struct GatherListFragmentHeader *hdr) {
  uint64_t* ptr = (uint64_t*) hdr;
  printf("0-7   0x%016llx\n", ptr[0]);
  printf("8-15  0x%016llx\n", ptr[1]);
  printf("\n");
}

int main(int argc, char** argv) {
  struct WorkUnit wu;
  struct GatherListFragmentHeader frag;
  struct GatherListFragmentHeader *fragPtr = malloc(sizeof(struct GatherListFragmentHeader));

  bzero(fragPtr, sizeof(struct GatherListFragmentHeader));
  printf("WorkUnit: 0x%lx bytes\n", sizeof(wu));
  printf("GatherListFragmentHeader: 0x%lx bytes\n", sizeof(frag));

  EXPECT_SIZE(wu, 32, "wu");
  
  EXPECT_SIZE(frag, 16, "frag");

  PrintFragment(fragPtr);
  printf("Set gather opcode, and set byte count to 15\n");
  fragPtr->u1.inline_cmd.opcode = OPCODE_GATHER;
  fragPtr->u1.inline_cmd.inlineByteCount = 15;
  PrintFragment(fragPtr);

  printf("Set bytes1\n");
  fragPtr->u1.inline_cmd.bytes1 = 0xba987654321;
  PrintFragment(fragPtr);

  printf("Set bytes2\n");
  fragPtr->u1.inline_cmd.bytes2 = 0xfedcba987654321;
  PrintFragment(fragPtr);
}

