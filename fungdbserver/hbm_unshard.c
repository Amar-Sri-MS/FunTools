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

#ifdef CONFIG_F1
#define BLEN    16
#define JUNKLEN 2
#define WORD_TYPE uint64_t
#elif defined CONFIG_F2
#define BLEN    8
#define JUNKLEN 1
#define WORD_TYPE uint32_t
#else
#error unknown config type
#endif

#define LINELEN (BLEN+JUNKLEN+1)
#define CHUNK   (16*1024)

#define STRIDE 64

#define CH_SWIZZLE 1

struct infile {
	char *name;
	char *fname;
	int srcfd;
	int binfd;
	WORD_TYPE *map;
	size_t size;
};

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

	fd = open(outfile, O_CREAT | O_WRONLY | O_TRUNC, 0644);

	if (fd < 0) {
		printf("failed to open output file %s\n", outfile);
		exit(1);
	}

	return fd;
}

static const char HEXVALS[256] = {
	['0'] = 0,
	['1'] = 1,
	['2'] = 2,
	['3'] = 3,
	['4'] = 4,
	['5'] = 5,
	['6'] = 6,
	['7'] = 7,
	['8'] = 8,
	['9'] = 9,
	['a'] = 0xa,
	['b'] = 0xb,
	['c'] = 0xc,
	['d'] = 0xd,
	['e'] = 0xe,
	['f'] = 0xf,
	['A'] = 0xa,
	['B'] = 0xb,
	['C'] = 0xc,
	['D'] = 0xd,
	['E'] = 0xe,
	['F'] = 0xf,
};

static WORD_TYPE hexval(char c)
{
	return HEXVALS[c];
}

static WORD_TYPE decode_line(const char *p)
{
	WORD_TYPE n = 0;
	int i;

	/* atoi() and byte-swap in one */
	for (i = BLEN-2; i >= 0; i-=2) {
		n <<= 4;
		n |= hexval(p[i]);
		n <<= 4;
		n |= hexval(p[i+1]);
	}

	return n;
}

static void decode_input(int i)
{
	ssize_t n;
	size_t j;
	bool done = false;
	char buf[CHUNK * LINELEN];
	WORD_TYPE obuf[CHUNK];
	struct infile *f = &shards[i];
	char *p;

	/* create a temporary fd for the binary*/
	f->fname = strdup("shard-XXXXXX");
	f->binfd = mkstemp(f->fname);
	if (f->binfd < 0) {
		perror("mkstemp");
		exit(1);
	}
	// printf("opened shard %s\n", f->fname);
	unlink(f->fname);

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
	f->map = mmap(NULL, f->size, PROT_READ, MAP_FILE | MAP_PRIVATE,
		      f->binfd, 0);
	if (f->map == MAP_FAILED) {
		perror("mmap");
		exit(1);
	}
	close(f->binfd);
	f->binfd = -1;
}

static void decode_inputs(void)
{
	int i;

	for (i = 0; i < NSHARDS; i++) {
		printf("#");
		fflush(stdout);
		decode_input(i);
	}
	printf("\n");
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

#ifdef CONFIG_F1
#include "hbm_unshard_f1.c.inc"
#elif defined CONFIG_F2
#include "hbm_unshard_f2.c.inc"
#endif


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
