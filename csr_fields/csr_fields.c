/*
 *  csr_fields.c
 *
 *  Created by Charles Gray on 2016-11-28.
 *  Copyright © 2016 Fungible. All rights reserved.
 */

#include <stdio.h>
#include <stdint.h>
#include <assert.h>
#include <stdlib.h>
#include <string.h>

#include "csr_fields.h"

#define NREGS (5)

struct read_test {
	unsigned reg_size;
	unsigned fld_size;
	unsigned fld_pos;
	uint64_t in_reg[NREGS];
	uint64_t out_fld[NREGS];
};

struct write_test {
	unsigned reg_size;
	unsigned fld_size;
	unsigned fld_pos;
	uint64_t in_reg[NREGS];
	uint64_t in_fld[NREGS];
	uint64_t out_reg[NREGS];
};

struct read_test read_tests[] = {

	/* single register tests */
	
	/* full width field in a single register */
	{ 64, 64, 0, { 0x0123456789abcdef }, { 0x0123456789abcdef } },
	{ 64, 64, 0, { 0x0 }, { 0x0 } },
	{ 64, 64, 0, { -1ull }, { -1ull } },

	/* partials in full-width with zeros -- low, top, middle */
	{ 64,  8, 0, { 0x0123456789abcdef }, { 0xef } },
	{ 64, 16, 0, { 0x0123456789abcdef }, { 0xcdef } },
	{ 64, 32, 0, { 0x0123456789abcdef }, { 0x89abcdef } },
	
	{ 64,  8, 28, { 0x0123456789abcdef }, { 0x78 } },
	{ 64, 16, 24, { 0x0123456789abcdef }, { 0x6789 } },
	{ 64, 32, 16, { 0x0123456789abcdef }, { 0x456789ab } },

	{ 64,  8, 56, { 0x0123456789abcdef }, { 0x01 } },
	{ 64, 16, 48, { 0x0123456789abcdef }, { 0x0123 } },
	{ 64, 32, 32, { 0x0123456789abcdef }, { 0x01234567 } },

	/* short register widths with junk in upper bits */
	{ 32,  8, 0, { 0x0123456789abcdef }, { 0xef } },
	{ 32, 16, 0, { 0x0123456789abcdef }, { 0xcdef } },
	
	{ 32,  8, 12, { 0x0123456789abcdef }, { 0xbc } },
	{ 32, 16,  8, { 0x0123456789abcdef }, { 0xabcd } },

	{ 32,  8, 24, { 0x0123456789abcdef }, { 0x89 } },
	{ 32, 16, 16, { 0x0123456789abcdef }, { 0x89ab } },

	/* two word -> one word tests, no straddle */
	{ 128,  64,  0, { 1, 2 }, { 1 } },
	{ 128,  64, 64, { 1, 2 }, { 2 } },

	/* same as single, but in second word */
	
	/* full width field in a single register */
	{ 128, 64, 64+0, { 0, 0x0123456789abcdef }, { 0x0123456789abcdef } },
	{ 128, 64, 64+0, { 1, 0x0 }, { 0x0 } },
	{ 128, 64, 64+0, { 0, -1ull }, { -1ull } },

	/* partials in full-width with zeros -- low, top, middle */
	{ 128,  8, 64+0, { 0, 0x0123456789abcdef }, { 0xef } },
	{ 128, 16, 64+0, { 0, 0x0123456789abcdef }, { 0xcdef } },
	{ 128, 32, 64+0, { 0, 0x0123456789abcdef }, { 0x89abcdef } },
	
	{ 128,  8, 64+28, { 0, 0x0123456789abcdef }, { 0x78 } },
	{ 128, 16, 64+24, { 0, 0x0123456789abcdef }, { 0x6789 } },
	{ 128, 32, 64+16, { 0, 0x0123456789abcdef }, { 0x456789ab } },

	{ 128,  8, 64+56, { 0, 0x0123456789abcdef }, { 0x01 } },
	{ 128, 16, 64+48, { 0, 0x0123456789abcdef }, { 0x0123 } },
	{ 128, 32, 64+32, { 0, 0x0123456789abcdef }, { 0x01234567 } },

	/* short register widths with junk in upper bits */
	{ 96,  8, 64+0, { 0, 0x0123456789abcdef }, { 0xef } },
	{ 96, 16, 64+0, { 0, 0x0123456789abcdef }, { 0xcdef } },
	
	{ 96,  8, 64+12, { 0, 0x0123456789abcdef }, { 0xbc } },
	{ 96, 16, 64+ 8, { 0, 0x0123456789abcdef }, { 0xabcd } },

	{ 96,  8, 64+24, { 0, 0x0123456789abcdef }, { 0x89 } },
	{ 96, 16, 64+16, { 0, 0x0123456789abcdef }, { 0x89ab } },
	
	/* two word -> one word tests, straddle */
	{ 128, 64, 32, { 0x0123456789abcdef, 0xf7e6d5c4b3a29180 }, { 0xb3a2918001234567 } },
	{ 128, 32, 56, { 0x0123456789abcdef, 0xf7e6d5c4b3a29180 }, { 0xa2918001 } },
	{ 128, 32, 48, { 0x0123456789abcdef, 0xf7e6d5c4b3a29180 }, { 0x91800123 } },
	{ 128, 32, 40, { 0x0123456789abcdef, 0xf7e6d5c4b3a29180 }, { 0x80012345 } },

	/* three word -> two word test, well aligned */
	{ 192, 128,  0, { 1, 2, 3 }, { 1, 2 } },
	{ 192, 128, 64, { 1, 2, 3 }, { 2, 3 } },

	/* three word -> two word, badly aligned */
	{ 192, 128, 32, { 0x0001020304050607, 0x08090a0b0c0d0e0f, 0x1011121314151617 }, { 0xc0d0e0f00010203, 0x1415161708090a0b } },
	
	/* three word -> three word test, well aligned */
	{ 192, 192, 0, { 1, 2, 3 }, { 1, 2, 3 } },

/* otto generated */
#define AUTO_READ
#include "auto-generated.c"
#undef AUTO_READ
};

#define NREADTESTS (sizeof(read_tests) / sizeof(*read_tests))

struct write_test write_tests[] = {
	/* full width field in a single register */
	{ 64, 64, 0, { 0 }, { 0x0123456789abcdef }, { 0x0123456789abcdef } },
	{ 64, 64, 0, { ~0ull }, { 0x0 }, { 0x0 } },
	{ 64, 64, 0, {  0ull }, { ~0ull }, { ~0ull } },

	/* partials in full-width with zeros -- low, top, middle */
	{ 64,  8, 0, { 0 }, { 0x0123456789abcdef }, { 0xef } },
	{ 64, 16, 0, { 0 }, { 0x0123456789abcdef }, { 0xcdef } },
	{ 64, 32, 0, { 0 }, { 0x0123456789abcdef }, { 0x89abcdef } },
	
	{ 64,  8, 28, { 0 }, { 0x0123456789abcdef }, { 0xef0000000 } },
	{ 64, 16, 24, { 0 }, { 0x0123456789abcdef }, { 0xcdef000000 } },
	{ 64, 32, 16, { 0 }, { 0x0123456789abcdef }, { 0x89abcdef0000 } },

	{ 64,  8, 56, { 0 }, { 0x0123456789abcdef }, { 0xef00000000000000 } },
	{ 64, 16, 48, { 0 }, { 0x0123456789abcdef }, { 0xcdef000000000000 } },
	{ 64, 32, 32, { 0 }, { 0x0123456789abcdef }, { 0x89abcdef00000000 } },

	/* short register widths with junk in upper bits */
	{ 32,  8, 0, { 0 }, { 0x0123456789abcdef }, { 0xef } },
	{ 32, 16, 0, { 0 }, { 0x0123456789abcdef }, { 0xcdef } },
	
	{ 32,  8, 12, { 0 }, { 0x0123456789abcdef }, { 0xef000 } },
	{ 32, 16,  8, { 0 }, { 0x0123456789abcdef }, { 0xcdef00 } },

	{ 32,  8, 24, { 0 }, { 0x0123456789abcdef }, { 0xef000000 } },
	{ 32, 16, 16, { 0 }, { 0x0123456789abcdef }, { 0xcdef0000 } },

	/* update a full word in a two-word array */
	{ 128,  64,  0, { 1, 2 }, { 3 }, { 3, 2 } },
	{ 128,  64, 64, { 1, 2 }, { 3 }, { 1, 3 } },

	/* two word -> one word tests, straddle */
	{ 128, 64, 32, { 0, 0 }, { 0x0123456789abcdef }, { 0x89abcdef00000000, 0x01234567 } },
	{ 128, 32, 56, { 0, 0 }, { 0x0123456789abcdef }, { 0xef00000000000000, 0x89abcd } },
	{ 128, 32, 48, { 0, 0 }, { 0x0123456789abcdef }, { 0xcdef000000000000, 0x89ab } },
	
	/* update a full word in a three-word register */
	{ 192,  64,   0, { 1, 2, 3 }, { 4 }, { 4, 2, 3 } },
	{ 192,  64,  64, { 1, 2, 3 }, { 4 }, { 1, 4, 3 } },
	{ 192,  64, 128, { 1, 2, 3 }, { 4 }, { 1, 2, 4 } },

	/* update two aligned words in a three-word register */
	{ 192,  128,  0, { 1, 2, 3 }, { 4, 5 }, { 4, 5, 3 } },
	{ 192,  128, 64, { 1, 2, 3 }, { 4, 5 }, { 1, 4, 5 } },

	/* two word update to three word register, badly aligned */
	{ 192, 128, 32, {0, 0, 0}, { 0x0001020304050607, 0x08090a0b0c0d0e0f }, { 0x0405060700000000, 0x0c0d0e0f00010203, 0x08090a0b } },
	{ 192, 128, 32, {~0ULL, ~0ULL, ~0ULL}, { 0x0001020304050607, 0x08090a0b0c0d0e0f }, { 0x04050607ffffffff, 0x0c0d0e0f00010203, 0xffffffff08090a0b } },

	/* update three words in a three-word register */
	{ 192,  192, 0, { 1, 2, 3 }, { 4, 5, 6 }, { 4, 5, 6 } },

/* otto generated */
#define AUTO_WRITE
#include "auto-generated.c"
#undef AUTO_WRITE

};

#define NWRITETESTS (sizeof(write_tests) / sizeof(*write_tests))
	
int
main(int argc, char *argv[])
{
	int i, r;
	uint64_t out[NREGS];
	int fails = 0;
	
	printf("running %lu read tests...\n", NREADTESTS);

	for (i = 0; i < NREADTESTS; i++) {
		printf("read test %d\n", i);
		memset(out, 0, sizeof(out)); // clean the output array
		csr_fld_read(read_tests[i].reg_size,
		             read_tests[i].fld_size,
		             read_tests[i].fld_pos,
		             &read_tests[i].in_reg[0], &out[0]);

		for (r = 0; r < NREGS; r++) {
			if (out[r] != read_tests[i].out_fld[r]) {
				printf("read test %d failed. reg %d expected 0x%llx, got 0x%llx\n", i, r, read_tests[i].out_fld[r], out[r]);
				fails++;
				break;
			}
		}
	}

	printf("running %lu write tests...\n", NWRITETESTS);

	for (i = 0; i < NWRITETESTS; i++) {
		printf("write test %d\n", i);

		/* copy the value we want */
		memcpy(out, write_tests[i].in_reg, sizeof(out));

		/* update it */
		csr_fld_write(write_tests[i].reg_size,
		              write_tests[i].fld_size,
		              write_tests[i].fld_pos,
		              &out[0], &write_tests[i].in_fld[0]);

		/* validate it */
		for (r = 0; r < NREGS; r++) {
			if (out[r] != write_tests[i].out_reg[r]) {
				printf("write test %d failed. reg %d expected 0x%llx, got 0x%llx\n", i, r, write_tests[i].out_reg[r], out[r]);
				fails++;
				break;
			}
		}
	}

	if (fails == 0)
		printf("all %lu tests passed\n", NREADTESTS + NWRITETESTS);
	else
		printf("%d tests failed\n", fails);

	return 0;
}
