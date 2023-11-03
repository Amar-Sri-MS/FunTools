struct infile *addr2shard(uint64_t addr, size_t *offset)
{
	uint64_t shard, saddr, row, col, bank;
	uint64_t qsys_num, ch_addr, ch_num, ch_num2, pseudo_chan;
	uint64_t qsn[2];
	uint64_t qn[7];
	const uint32_t CHNUMS[] = {2, 3, 6, 7, 0, 1, 4, 5, 10,
				  11, 14, 15, 8, 9, 12, 13};
	const uint64_t H0 = 0x001;
	const uint64_t H1 = 0x002;
	const uint64_t H2 = 0x180;
	const uint64_t H3 = 0x240;
	const uint64_t H4 = 0x028;
	const uint64_t H5 = 0x410;
	const uint64_t H6 = 0x000;
	const uint64_t H7 = 0x004;

	shard = addr & 3;
	saddr = addr >> 2;

	qsn[0] = red_xor(H0 & saddr);
	qsn[1] = red_xor(H1 & saddr);

	qn[1] = red_xor(H2 & saddr);
	qn[2] = red_xor(H3 & saddr);
	qn[3] = red_xor(H4 & saddr);
	qn[4] = red_xor(H5 & saddr);
	// qn[5] = red_xor(H6 & saddr); // XXX: doesn't exist?!
	qn[6] = red_xor(H7 & saddr);

	qsys_num = (qsn[1] << 1) | qsn[0];
	qsys_num = qsys_num + shard * 4;

	if (CH_SWIZZLE) {
		assert(qsys_num >= 0);
		assert(qsys_num <= 15);
		ch_num = CHNUMS[qsys_num];
	} else {
		ch_num = qsys_num;
	}

	row = (saddr >> 11) & 0x3fff;
	col = (saddr & 0xf0) >> 1;
	bank = (qn[4] << 3) | (qn[3] << 2) | (qn[2] << 1) | qn[1];

	pseudo_chan = qn[6];
	ch_num2 = (pseudo_chan * 16) + ch_num;

	assert((pseudo_chan == 0) || (pseudo_chan == 1));
	assert(ch_num >= 0);
	assert(ch_num <= 15);

	ch_addr = (bank << 21) | (row << 7) | col;

	/* return the results in word offset from an infile */
	*offset = ch_addr / sizeof(uint64_t);
	return &shards[ch_num2];

}

static void unshard(int fd)
{
	uint64_t addr = 0;
	struct infile *f = NULL;
	size_t offset, i, c = 0;
	ssize_t n;
	uint64_t buf[CHUNK][STRIDE/sizeof(uint64_t)];

	for (addr = 0; addr < minsize * NSHARDS; addr += STRIDE) {

		/* compute where it's coming from */
		f = addr2shard(addr, &offset);

		/* copy to the output buffer in swapped pairs */
		assert(f->map != NULL);
		for (i = 0; i < (STRIDE/sizeof(uint64_t)); i+=2) {
			buf[c][i+0] = f->map[offset+1];
			buf[c][i+1] = f->map[offset+0];
		}
		c++;

		/* see if we should flush the output buffer */
		if (c == CHUNK) {
			n = write(fd, buf, c * STRIDE);
			if (n != (c * STRIDE)) {
				perror("write");
				exit(1);
			}
			c = 0;
		}

		if (addr && !(addr % (1ULL << 25))) {
			printf(".");
			fflush(stdout);
		}
		if (addr && !(addr % (1ULL << 30))) {
			printf("%" PRId64 "gb\n", addr >> 30);
		}
	}

	printf("\n");
	if (c > 0) {
		n = write(fd, buf, c * STRIDE);
		if (n != (c * STRIDE)) {
			perror("write");
			exit(1);
		}
	}
}
