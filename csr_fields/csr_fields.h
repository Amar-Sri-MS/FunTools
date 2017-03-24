/*
 *  csr_fields.h
 *
 *  Created by Charles Gray on 2016-11-29.
 *  Copyright © 2016 Fungible. All rights reserved.
 */

#ifndef __CSR_FIELDS_H__
#define __CSR_FIELDS_H__

// master switch
// #define DEBUG

#ifdef DEBUG
#define DEBUG_READ
#define DEBUG_WRITE
#else
// normal switches
#define DEBUG_READ
// #define DEBUG_WRITE
#endif


/* short bits-per-word macro */
#define BPW (8 * sizeof(uint64_t))

static inline void
csr_fld_write(unsigned reg_padded_size,
	      unsigned reg_size,
              unsigned fld_size,
              unsigned fld_pos,
              uint64_t *out_reg, uint64_t *in_fld)
{
	uint64_t mask;
	unsigned out_idx, out_pos, out_size, out_size_hi, write_upper;
	unsigned in_idx = 0;
	unsigned rem_size = fld_size;

	assert(reg_padded_size >= fld_size + fld_pos);
	assert(reg_padded_size % 64 == 0);
	assert(reg_size <= reg_padded_size);

	/* find the LSB word on the input field */
	assert(fld_size > 0);
	in_idx = (fld_size - 1) / BPW;

	while (rem_size > 0) {
		/* find the LSB word on the output register */
		assert((reg_padded_size - fld_pos - fld_size + rem_size) > 0);
		out_idx = (reg_padded_size - fld_pos - fld_size + rem_size - 1) / BPW;

		/* calculate the base bit position in this word */
		out_pos = fld_pos % BPW;

		/* trim the size for this input word */
		out_size = rem_size;
		write_upper = 0;
		if (out_size + out_pos > BPW) {
			out_size = BPW - out_pos;
			write_upper = 1;
		}
		
		/* calculate a mask */
		if (out_size == BPW)
			mask = ~0ULL;
		else
			mask = (1ULL << out_size) - 1;

#ifdef DEBUG_WRITE
		printf("out_idx: %u, in_idx %u\n", out_idx, in_idx);
		printf("mask: 0x%llx\n", mask);
		printf("fld_size: %u -> %u\n", fld_size, out_size);
#endif
	
		/* copy in the first part of the word, masking out the rest */
		out_reg[out_idx] &= ~(mask << out_pos);
		out_reg[out_idx] |= (in_fld[in_idx] & mask) << out_pos;

		/* determine if we need to read part of the next word */
		if (write_upper) {
			/* need to read the remaining bits in this input word */
			if (BPW < rem_size)
				out_size_hi = BPW - out_size;
			else
				out_size_hi = rem_size - out_size;
			assert(out_size_hi < BPW); /* can't be BPW, would be read above */

			/* construct the mask */
			mask = (1ULL << out_size_hi) - 1;

			/* or in the value */
			assert(out_idx > 0);
			out_reg[out_idx-1] &= ~mask;
			out_reg[out_idx-1] |= (in_fld[in_idx] >> out_size) & mask;
		} else
			out_size_hi = 0;

#ifdef DEBUG_WRITE
		printf("rem_size %u, in_size %u, in_size_hi %u = %u\n",
		       rem_size, out_size, out_size_hi, rem_size -  out_size + out_size_hi);
#endif
		
		/* next output word */
		in_idx--;
		rem_size -= out_size + out_size_hi;
	}
}


static inline void
csr_fld_read(unsigned reg_padded_size,
	     unsigned reg_size,
             unsigned fld_size,
             unsigned fld_pos,
             uint64_t *in_reg, uint64_t *out_fld)
{
	uint64_t mask;
	unsigned in_idx, in_pos, in_size, in_size_hi, read_upper;
	unsigned out_idx = 0;
	unsigned rem_size = fld_size;
	
	assert(reg_padded_size >= fld_size + fld_pos);
	assert(reg_padded_size % 64 == 0);
	assert(reg_size <= reg_padded_size);
	assert(fld_size > 0);

	/* compute the last word of the output buffer because big
	 * endian
	 */
	out_idx = (fld_size - 1) / BPW;

#ifdef DEBUG_READ
	printf("first output word: %u\n", out_idx);
#endif
	
	/* count up bits from fld_pos*/
	while (rem_size > 0) {
		/* clear the output word */
		assert(out_idx >= 0);
		out_fld[out_idx] = 0;

		/* find the input word for the lowest significant bit */
		assert((reg_padded_size - fld_pos - fld_size + rem_size) > 0);
		in_idx = (reg_padded_size - fld_pos - fld_size + rem_size - 1) / BPW;

		/* calculate the base bit position in this word */
		in_pos = fld_pos % BPW;

		/* trim the size for this input word */
		in_size = rem_size;
		read_upper = 0;
		if (in_size + in_pos > BPW) {
			in_size = BPW - in_pos;
			read_upper = 1;
		}
		
		/* calculate a mask */
		if (in_size == BPW)
			mask = ~0ULL;
		else
			mask = (1ULL << in_size) - 1;

#ifdef DEBUG_READ
		printf("in_idx: %u\n", in_idx);
		printf("mask: 0x%llx\n", mask);
		printf("fld_size: %u -> %u\n", fld_size, in_size);
#endif
	
		/* copy in the first part of the word */
		out_fld[out_idx] |= (in_reg[in_idx] >> in_pos) & mask;

		/* determine if we need to read part of the next word */
		if (read_upper) {
			/* need to read the remaining bits in this input word */
			if (BPW < rem_size)
				in_size_hi = BPW - in_size;
			else
				in_size_hi = rem_size - in_size;
			assert(in_size_hi < BPW); /* can't be BPW, would be read above */

			/* construct the mask */
			mask = (1ULL << in_size_hi) - 1;

			/* or in the value */
			assert((in_idx - 1) >= 0);
			out_fld[out_idx] |= (in_reg[in_idx-1] & mask) << in_size;
		} else
			in_size_hi = 0;

#ifdef DEBUG_READ
		printf("rem_size %u, in_size %u, in_size_hi %u = %u\n",
		       rem_size, in_size, in_size_hi, rem_size -  in_size + in_size_hi);
#endif
		
		/* next output word */
		out_idx--;
		rem_size -= in_size + in_size_hi;
	}
}

#endif /* __CSR_FIELDS_H__ */
