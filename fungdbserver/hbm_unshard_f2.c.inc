struct infile *addr2shard(uint64_t addr, size_t *offset)
{
	uint64_t shard, saddr, row, col, bank, sid;
	uint64_t qsys_num, ch_addr, ch_num, ch_num2, pseudo_chan;
	uint64_t qsn[2];
	uint64_t qn[7];
	const uint32_t CHNUMS[] = {
				0, 4, 8, 12, 1, 5, 9, 13,
				14, 10, 6, 2, 15, 11, 7, 3};
	const uint64_t QSN0 = 0x4fffffe;
	const uint64_t QSN1 = 0x8fffffe;
	const uint64_t QN0 = 0x0020848;
	const uint64_t QN1 = 0x0041090;
	const uint64_t QN2 = 0x0410404;
	const uint64_t QN3 = 0x0082120;
	const uint64_t QN4 = 0x0904200;
	const uint64_t QN5 = 0x0000400;
	const uint64_t QN6 = 0x03FFFFE;
	const uint64_t qsys_pos = 26;

	addr /= 64;

	uint64_t temp_128B = addr&1;
	uint64_t qsys_temp = (addr >> 3) & 3;
	shard = (addr >> 1) & 3;
	saddr = ((addr & 0xffffffffffffffe0ULL) >> 4) | (qsys_temp << qsys_pos) | temp_128B;

	qsn[0] = red_xor(QSN0 & saddr);
	qsn[1] = red_xor(QSN1 & saddr);

	qn[0] = red_xor(QN0 & saddr);
	qn[1] = red_xor(QN1 & saddr);
	qn[2] = red_xor(QN2 & saddr);
	qn[3] = red_xor(QN3 & saddr);
	qn[4] = red_xor(QN4 & saddr);
	qn[5] = red_xor(QN5 & saddr);
	qn[6] = red_xor(QN6 & saddr);

	qsys_num = (qsn[1] << 1) | qsn[0];
	qsys_num = qsys_num | (shard << 2);

	if (CH_SWIZZLE) {
		assert(qsys_num >= 0);
		assert(qsys_num <= 15);
		ch_num = CHNUMS[qsys_num];
	} else {
		ch_num = qsys_num;
	}

	row = (saddr >> 10) & 0x3fff;
	col = (saddr & 0x3f) >> 3;
	col = (col << 1) | (saddr & 0x1);
	bank = (qn[3] << 3) | (qn[2] << 2) | (qn[1] << 1) | qn[0];

	sid = qn[4];
	pseudo_chan = qn[6];
	ch_num2 = (pseudo_chan * 16) + ch_num;

	assert((pseudo_chan == 0) || (pseudo_chan == 1));
	assert(ch_num >= 0);
	assert(ch_num <= 15);

	ch_addr = (sid << 22) | (bank << 18) | (row << 4) | col;
	ch_addr = ch_addr << 4;

	/* return the results in word offset from an infile */
	*offset = ch_addr;
	return &shards[ch_num2];
}

static void unshard(int fd)
{
	uint64_t addr = 0;
	struct infile *f = NULL;
	size_t offset, i, c = 0;
	ssize_t n;
	uint32_t buf[CHUNK][STRIDE/sizeof(uint32_t)] = {};

	for (addr = 0; addr < minsize * NSHARDS; addr += STRIDE) {
		/* compute where it's coming from */
		f = addr2shard(addr, &offset);

		/* copy to the output buffer */
		assert(f->map != NULL);
		for (i = 0; i < (STRIDE/sizeof(uint32_t)); i+=8) {
			buf[c][i+0] = f->map[offset+i+7];
			buf[c][i+1] = f->map[offset+i+6];
			buf[c][i+2] = f->map[offset+i+5];
			buf[c][i+3] = f->map[offset+i+4];
			buf[c][i+4] = f->map[offset+i+3];
			buf[c][i+5] = f->map[offset+i+2];
			buf[c][i+6] = f->map[offset+i+1];
			buf[c][i+7] = f->map[offset+i+0];
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
