#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <unistd.h>
#include <string.h>
#include <stdbool.h>
#include <inttypes.h>
#include <sys/mman.h>

#define NCHANNELS 16
#define NPC 2
#define NSHARDS (NCHANNELS * NPC)

#define BLEN    16
#define JUNKLEN 2
#define LINELEN (BLEN+JUNKLEN+1)
#define CHUNK   1024

#define STRIDE 64

#define CH_SWIZZLE 1
static const uint32_t CHNUMS[] = {2, 3, 6, 7, 0, 1, 4, 5, 10,
				  11, 14, 15, 8, 9, 12, 13};

struct infile {
	char *name;
	int srcfd;
	int binfd;
	uint64_t *map;
	size_t size;
};

#define H0 0x001
#define H1 0x002
#define H2 0x180
#define H3 0x240
#define H4 0x028
#define H5 0x410
#define H6 0x000
#define H7 0x004

#define CH_SWIZZLE 1
#define HBM_MODE  4

static struct infile shards[NSHARDS];
static size_t minsize = ~0ULL;
static bool warned = false;

#define TEXT_FMT "%s.ch%d_pc%d"

static void open_shard_files(const char *prefix)
{
	size_t nlen = strlen(prefix) + strlen(TEXT_FMT)+1;
	int i, j, n;

	for (j = 0; j < NPC; j++) {
		for (i = 0; i < NCHANNELS; i++) {
			n = j * NCHANNELS + i;
			/* make a filename and open it */
			shards[n].name = malloc(nlen);
			sprintf(shards[n].name, TEXT_FMT, prefix, i, j);
			shards[n].srcfd = open(shards[n].name, O_RDONLY);
			if (shards[n].srcfd < 0) {
				printf("failed to open shard %s\n",
				       shards[n].name);
				exit(1);
			}
		}
	}
}

static int create_bin_file(const char *outfile)
{
	int fd = -1;

	fd = open(outfile, O_CREAT | O_WRONLY | O_TRUNC);
	
	if (fd < 0) {
		printf("failed to open output file %s\n", outfile);
		exit(1);
	}

	return fd;
}

static uint64_t hexval(char c)
{
	if ((c >= '0') && (c <= '9'))
		return c - '0';

	if ((c >= 'a') && (c <= 'f'))
		return c - 'a' + 0xa;
	
	if ((c >= 'A') && (c <= 'F'))
		return c - 'A' + 0xA;

	abort();
}

static uint64_t decode_line(const char *p)
{
	uint64_t n = 0;
	int i;
	
	for (i = 0; i < BLEN; i++) {
		n <<= 4;
		n |= hexval(p[i]);
	}

	return n;
}

static void decode_input(int i)
{
	ssize_t n;
	size_t j;
	bool done = false;
	char buf[CHUNK * LINELEN];
	uint64_t obuf[CHUNK];
	struct infile *f = &shards[i];
	char *p, *fname = NULL;
	
	/* create a temporary fd for the binary*/
	fname = strdup("shard-XXXXXX.bin");
	f->binfd = mkstemp(fname);
	if (f->binfd < 0) {
		perror("mkstemp");
		exit(1);
	}
	unlink(fname);
		
	/* do the actual decode */
	while (!done) {
		/* read in a large number of lines */
		n = read(f->srcfd, buf, sizeof(buf));
		if (n < 0) {
			perror("read");
			exit(1);
		}

		if (n % LINELEN) {
			printf("short read. barf.\n");
			exit(1);
		}

		/* for each line that was read in... */
		j = n / LINELEN;
		for (i = 0; i < j; i++) {
			/* compute the address of the line */
			p = &buf[i * LINELEN + JUNKLEN];
			obuf[i] = decode_line(p);
		}

		if (j > 0) {
			n = write(f->binfd, obuf, j * sizeof(*obuf));
			if (n <= 0) {
				perror("write");
				exit(1);
			}
			f->size += n;
		} else {
			done = true;
		}
	}

	if (minsize == ~0ULL) {
		minsize = f->size;
	} else {
		if ((f->size != minsize) && !warned) {
			printf("WARNING: input file sizes differ\n");
			warned = true;
		}
			
		if (f->size < minsize)
			minsize = f->size;
	}

	/* now mmap the file */
	f->map = mmap(NULL, f->size, PROT_READ, MAP_FILE | MAP_SHARED,
		      f->binfd, 0);
	if (f->map == MAP_FAILED) {
		perror("mmap");
		exit(1);
	}
}

static void decode_inputs(void)
{
	int i;

	for (i = 0; i < NSHARDS; i++) {
		printf("decoding input %d\n", i);
		decode_input(i);
	}
}

static uint64_t red_xor(uint64_t x)
{
	x = (x>>16) ^ x;
	x = (x>>8)  ^ x;
	x = (x>>4)  ^ x;
	x = (x>>2)  ^ x;
	x = (x>>1)  ^ x;
	x &= 1;
	
	return x;
}

struct infile *addr2shard(uint64_t addr, size_t *offset)
{
	uint64_t shard, saddr, row, col, bank;
	uint64_t qsys_num, ch_addr, ch_num, ch_num2, pseudo_chan;
	uint64_t qsn[2];
	uint64_t qn[7];
		
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
	size_t offset, c = 0;
	ssize_t n;
	char buf[CHUNK][STRIDE];

	for (addr = 0; addr < minsize * NSHARDS; addr += STRIDE) {

		/* compute where it's coming from */
		f = addr2shard(addr, &offset);

		/* copy to the output buffer */
		assert(f->map != NULL);
		memcpy(&buf[c][0], &f->map[offset], STRIDE);
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

		if (addr & !(addr % (1ULL << 25))) {
			printf(".");
			fflush(stdout);
		}
		if (addr & !(addr % (1ULL << 30))) {
			printf("%" PRId64 "\n", addr >> 30);
		}
	}

	if (c > 0) {
		n = write(fd, buf, c * STRIDE);
		if (n != (c * STRIDE)) {
			perror("write");
			exit(1);
		}
	}

}

int main(int argc, char *argv[])
{
	const char *prefix = NULL;
	const char *outfile = NULL;
	int fd = -1;
	
	if (argc != 3) {
		printf("usage: %s <outfile> <shard-prefix>\n", argv[0]);
		exit(1);
	}

	/* extract the actual output filename & prefix */
	outfile = argv[1];
	prefix = argv[2];

	/* open all the files */
	open_shard_files(prefix);

	/* create the actual output file */
	fd = create_bin_file(outfile);

	/* translate the shard files from text->binary */
	decode_inputs();

	/* do the actual assembly */
	unshard(fd);
	
	return 0;
}
