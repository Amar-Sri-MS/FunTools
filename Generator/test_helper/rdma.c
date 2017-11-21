/**
 * Tests that header generated by generator.py script correctly parses code
 * and correctly aligned fields.
 *
 * This test requires the rdma.gen file as input to generator.py.
 *
 * Robert Bowdidge, August 8, 2016.
 * Copyright Fungible Inc. 2016.
 */

#include <inttypes.h>
#include <stddef.h> // offsetof
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h> // bzero.

#include "rdma_gen.h"

#include "test_macros.h"

void PrintFragment(struct GatherListFragmentHeader *hdr) {
  uint64_t* ptr = (uint64_t*) hdr;
  printf("0-7   0x%" PRIx64 "\n", ptr[0]);
  printf("8-15  0x%" PRIx64 "\n", ptr[1]);
  printf("\n");
}

int main(int argc, char** argv) {
  struct WorkUnit wu;
  struct GatherListFragmentHeader frag;
  struct GatherListFragmentHeader *fragPtr = malloc(sizeof(struct GatherListFragmentHeader));

  bzero(fragPtr, sizeof(struct GatherListFragmentHeader));
  printf("WorkUnit: 0x%" PRIx64" bytes\n", sizeof(wu));
  printf("GatherListFragmentHeader: 0x%" PRIx64 " bytes\n", sizeof(frag));

  ASSERT_SIZE(wu, 32, "wu");
  
  ASSERT_SIZE(frag, 16, "frag");

  PrintFragment(fragPtr);
  printf("Set gather opcode, and set byte count to 15\n");
  fragPtr->opcode = OPCODE_GATHER;
  fragPtr->u1.inline_cmd.inlineByteCount = 15;
  PrintFragment(fragPtr);

  strcpy((char*)fragPtr->u1.inline_cmd.bytes, "01234567890123");
  PrintFragment(fragPtr);
}

