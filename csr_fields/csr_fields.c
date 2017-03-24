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

#define ID __FILE__, __LINE__
#define NREGS (5)

struct read_test {
	const char *fname;
	unsigned int line;
	
	unsigned reg_padded_size;
	unsigned reg_size;
	unsigned fld_size;
	unsigned fld_pos;
	uint64_t in_reg[NREGS];
	uint64_t out_fld[NREGS];
};

struct write_test {
	const char *fname;
	unsigned int line;

	unsigned reg_padded_size;
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
	{ ID, 64, 64, 64, 0, { 0x0123456789abcdef }, { 0x0123456789abcdef } },
	{ ID, 64, 64, 64, 0, { 0x0 }, { 0x0 } },
	{ ID, 64, 64, 64, 0, { -1ull }, { -1ull } },

	/* partials in full-width with zeros -- low, top, middle */
	{ ID, 64, 64,  8, 0, { 0x0123456789abcdef }, { 0xef } },
	{ ID, 64, 64, 16, 0, { 0x0123456789abcdef }, { 0xcdef } },
	{ ID, 64, 64, 32, 0, { 0x0123456789abcdef }, { 0x89abcdef } },
	
	{ ID, 64, 64,  8, 28, { 0x0123456789abcdef }, { 0x78 } },
	{ ID, 64, 64, 16, 24, { 0x0123456789abcdef }, { 0x6789 } },
	{ ID, 64, 64, 32, 16, { 0x0123456789abcdef }, { 0x456789ab } },

	{ ID, 64, 64,  8, 56, { 0x0123456789abcdef }, { 0x01 } },
	{ ID, 64, 64, 16, 48, { 0x0123456789abcdef }, { 0x0123 } },
	{ ID, 64, 64, 32, 32, { 0x0123456789abcdef }, { 0x01234567 } },

	/* short register widths with junk in lower bits */
	{ ID, 64, 32,  8, 32, { 0x0123456789abcdef }, { 0x67 } },
	{ ID, 64, 32, 16, 32, { 0x0123456789abcdef }, { 0x4567 } },
	
	{ ID, 64, 32,  8, 44, { 0x0123456789abcdef }, { 0x34 } },
	{ ID, 64, 32, 16, 40, { 0x0123456789abcdef }, { 0x2345 } },

	{ ID, 64, 32,  8, 56, { 0x0123456789abcdef }, { 0x01 } },
	{ ID, 64, 32, 16, 48, { 0x0123456789abcdef }, { 0x0123 } },

	/* two word -> one word tests, no straddle */
	{ ID, 128, 128,  64,  0, { 2, 1 }, { 1 } },
	{ ID, 128, 128,  64, 64, { 2, 1 }, { 2 } },

	/* same as single, but in second word */
	
	/* full width field in a single register */
	{ ID, 128, 128, 64, 64+0, { 0x0123456789abcdef, 0 }, { 0x0123456789abcdef } },
	{ ID, 128, 128, 64, 64+0, { 0x0, 1 }, { 0x0 } },
	{ ID, 128, 128, 64, 64+0, { -1ull, 0 }, { -1ull } },

	/* partials in full-width with zeros -- low, top, middle */
	{ ID, 128, 128,  8, 64+0, { 0x0123456789abcdef, 0 }, { 0xef } },
	{ ID, 128, 128, 16, 64+0, { 0x0123456789abcdef, 0 }, { 0xcdef } },
	{ ID, 128, 128, 32, 64+0, { 0x0123456789abcdef, 0 }, { 0x89abcdef } },
	
	{ ID, 128, 128,  8, 64+28, { 0x0123456789abcdef, 0 }, { 0x78 } },
	{ ID, 128, 128, 16, 64+24, { 0x0123456789abcdef, 0 }, { 0x6789 } },
	{ ID, 128, 128, 32, 64+16, { 0x0123456789abcdef, 0 }, { 0x456789ab } },

	{ ID, 128, 128,  8, 64+56, { 0x0123456789abcdef, 0 }, { 0x01 } },
	{ ID, 128, 128, 16, 64+48, { 0x0123456789abcdef, 0 }, { 0x0123 } },
	{ ID, 128, 128, 32, 64+32, { 0x0123456789abcdef, 0 }, { 0x01234567 } },

	/* short register widths with junk in lower bits */
	{ ID, 128, 96,  8, 64+0, { 0x0123456789abcdef, 0 }, { 0xef } },
	{ ID, 128, 96, 16, 64+0, { 0x0123456789abcdef, 0 }, { 0xcdef } },
	
	{ ID, 128, 96,  8, 64+12, { 0x0123456789abcdef, 0 }, { 0xbc } },
	{ ID, 128, 96, 16, 64+ 8, { 0x0123456789abcdef, 0 }, { 0xabcd } },

	{ ID, 128, 96,  8, 64+24, { 0x0123456789abcdef, 0 }, { 0x89 } },
	{ ID, 128, 96, 16, 64+16, { 0x0123456789abcdef, 0 }, { 0x89ab } },
	
	/* two word -> one word tests, straddle */
	{ ID, 128, 128, 64, 32, { 0xf7e6d5c4b3a29180, 0x0123456789abcdef }, { 0xb3a2918001234567 } },
	{ ID, 128, 128, 32, 56, { 0xf7e6d5c4b3a29180, 0x0123456789abcdef }, { 0xa2918001 } },
	{ ID, 128, 128, 32, 48, { 0xf7e6d5c4b3a29180, 0x0123456789abcdef }, { 0x91800123 } },
	{ ID, 128, 128, 32, 40, { 0xf7e6d5c4b3a29180, 0x0123456789abcdef }, { 0x80012345 } },

	/* three word -> two word test, well aligned */
	{ ID, 192, 192, 128,  0, { 1, 2, 3 }, { 2, 3 } },
	{ ID, 192, 192, 128, 64, { 1, 2, 3 }, { 1, 2 } },

	/* three word -> two word, badly aligned */
	{ ID, 192, 192, 128, 32, { 0x0001020304050607, 0x1011121314151617, 0x08090a0b0c0d0e0f }, { 0x0405060710111213, 0x1415161708090a0b } },

	/* three word -> three word test, well aligned */
	{ ID, 192, 192, 192, 0, { 1, 2, 3 }, { 1, 2, 3 } },

/* otto generated */
#define AUTO_READ
#include "auto-generated.c"
#undef AUTO_READ
};

#define NREADTESTS (sizeof(read_tests) / sizeof(*read_tests))

struct write_test write_tests[] = {
	/* full width field in a single register */
	{ ID, 64, 64, 64, 0, { 0 }, { 0x0123456789abcdef }, { 0x0123456789abcdef } },
	{ ID, 64, 64, 64, 0, { ~0ull }, { 0x0 }, { 0x0 } },
	{ ID, 64, 64, 64, 0, {  0ull }, { ~0ull }, { ~0ull } },

	/* partials in full-width with zeros -- low, top, middle */
	{ ID, 64, 64,  8, 0, { 0 }, { 0x0123456789abcdef }, { 0xef } },
	{ ID, 64, 64, 16, 0, { 0 }, { 0x0123456789abcdef }, { 0xcdef } },
	{ ID, 64, 64, 32, 0, { 0 }, { 0x0123456789abcdef }, { 0x89abcdef } },
	
	{ ID, 64, 64,  8, 28, { 0 }, { 0x0123456789abcdef }, { 0xef0000000 } },
	{ ID, 64, 64, 16, 24, { 0 }, { 0x0123456789abcdef }, { 0xcdef000000 } },
	{ ID, 64, 64, 32, 16, { 0 }, { 0x0123456789abcdef }, { 0x89abcdef0000 } },

	{ ID, 64, 64,  8, 56, { 0 }, { 0x0123456789abcdef }, { 0xef00000000000000 } },
	{ ID, 64, 64, 16, 48, { 0 }, { 0x0123456789abcdef }, { 0xcdef000000000000 } },
	{ ID, 64, 64, 32, 32, { 0 }, { 0x0123456789abcdef }, { 0x89abcdef00000000 } },

	/* short register widths with junk in upper bits */
	{ ID, 64, 32,  8, 0, { 0 }, { 0x0123456789abcdef }, { 0xef } },
	{ ID, 64, 32, 16, 0, { 0 }, { 0x0123456789abcdef }, { 0xcdef } },
	      
	{ ID, 64, 32,  8, 12, { 0 }, { 0x0123456789abcdef }, { 0xef000 } },
	{ ID, 64, 32, 16,  8, { 0 }, { 0x0123456789abcdef }, { 0xcdef00 } },
	      
	{ ID, 64, 32,  8, 24, { 0 }, { 0x0123456789abcdef }, { 0xef000000 } },
	{ ID, 64, 32, 16, 16, { 0 }, { 0x0123456789abcdef }, { 0xcdef0000 } },

	/* update a full word in a two-word array */
	{ ID, 128, 128, 64,  0, { 1, 2 }, { 3 }, { 1, 3 } },
	{ ID, 128, 128, 64, 64, { 1, 2 }, { 3 }, { 3, 2 } },

	/* two word -> one word tests, straddle */
	{ ID, 128, 128, 64, 32, { 0, 0 }, { 0x0123456789abcdef }, { 0x01234567, 0x89abcdef00000000 } },
	{ ID, 128, 128, 32, 56, { 0, 0 }, { 0x0123456789abcdef }, { 0x89abcd, 0xef00000000000000 } },
	{ ID, 128, 128, 32, 48, { 0, 0 }, { 0x0123456789abcdef }, { 0x89ab, 0xcdef000000000000 } },
	
	/* update a full word in a three-word register */
	{ ID, 192, 192,  64,   0, { 1, 2, 3 }, { 4 }, { 1, 2, 4 } },
	{ ID, 192, 192,  64,  64, { 1, 2, 3 }, { 4 }, { 1, 4, 3 } },
	{ ID, 192, 192,  64, 128, { 1, 2, 3 }, { 4 }, { 4, 2, 3 } },

	/* update two aligned words in a three-word register */
	{ ID, 192, 192,  128,  0, { 1, 2, 3 }, { 4, 5 }, { 1, 4, 5 } },
	{ ID, 192, 192,  128, 64, { 1, 2, 3 }, { 4, 5 }, { 4, 5, 3 } },

	/* two word update to three word register, badly aligned */
	{ ID, 192, 192, 128, 32, {0, 0, 0}, { 0x0001020304050607, 0x08090a0b0c0d0e0f }, { 0x00010203, 0x0405060708090a0b, 0x0c0d0e0f00000000 } },
	{ ID, 192, 192, 128, 32, {~0ULL, ~0ULL, ~0ULL}, { 0x0001020304050607, 0x08090a0b0c0d0e0f }, { 0xffffffff00010203, 0x0405060708090a0b, 0x0c0d0e0fffffffff } },

	/* update three words in a three-word register */
	{ ID, 192, 192,  192, 0, { 1, 2, 3 }, { 4, 5, 6 }, { 4, 5, 6 } },

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
		printf("read test %d @ %s:%d\n", i,
		       read_tests[i].fname, read_tests[i].line);
		memset(out, 0, sizeof(out)); // clean the output array
		csr_fld_read(read_tests[i].reg_padded_size,
			     read_tests[i].reg_size,
		             read_tests[i].fld_size,
		             read_tests[i].fld_pos,
		             &read_tests[i].in_reg[0], &out[0]);

		for (r = 0; r < NREGS; r++) {
			if (out[r] != read_tests[i].out_fld[r]) {
				printf("read test %d failed @ %s:%d. reg %d expected 0x%llx, got 0x%llx\n",
				       i, read_tests[i].fname,
				       read_tests[i].line, r,
				       read_tests[i].out_fld[r], out[r]);
				fails++;
				break;
			}
		}
	}

	printf("running %lu write tests...\n", NWRITETESTS);

	for (i = 0; i < NWRITETESTS; i++) {
		printf("write test %d @ %s:%d\n", i,
			write_tests[i].fname, write_tests[i].line);

		/* copy the value we want */
		memcpy(out, write_tests[i].in_reg, sizeof(out));

		/* update it */
		csr_fld_write(write_tests[i].reg_padded_size,
			      write_tests[i].reg_size,
		              write_tests[i].fld_size,
		              write_tests[i].fld_pos,
		              &out[0], &write_tests[i].in_fld[0]);

		/* validate it */
		for (r = 0; r < NREGS; r++) {
			if (out[r] != write_tests[i].out_reg[r]) {
				printf("write test %d failed @ %s:%d. reg %d expected 0x%llx, got 0x%llx\n",
				       i, write_tests[i].fname,
				       write_tests[i].line, r,
				       write_tests[i].out_reg[r], out[r]);
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
