#include <fcntl.h>
#include <ctype.h>
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
	FILE *srcfilep;
};

#define CH_SWIZZLE 1
#define HBM_MODE  4

static struct infile shards[NSHARDS];
static size_t minsize = ~0ULL;
static bool warned = false;
static bool sparse;
static size_t sparse_size = 0;

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


ssize_t write_or_die(int fd, const void *buf, size_t count)
{
	ssize_t n = write(fd, buf, count);

	if (n <= 0) {
		perror("write");
		exit(1);
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
	if (sparse == 1) {
		char *lineptr = NULL;
		size_t linesize = 0;
		ssize_t nread;
		size_t last_word_num = 0;
		size_t cur_word_num = 0;
		WORD_TYPE value;
#define blank_size 1024
		WORD_TYPE blank[blank_size] = {};
		f->srcfilep = fdopen(f->srcfd, "r");


		while ((nread = getline(&lineptr, &linesize, f->srcfilep)) != -1) {
			char *v;
			if (nread == 0)
				continue;

			if (lineptr[0] == '$')
				continue;

			cur_word_num = strtoul(lineptr, &v, 16);

			// skip whitespace
			while(isblank(v[0]))
				v++;
			v++; // skip first CRC
			value = decode_line(v);

			while (last_word_num < cur_word_num) {
				unsigned long cnt = blank_size;
				if (last_word_num + cnt < cur_word_num) {
					n = write_or_die(f->binfd, blank, sizeof(blank));
				} else {
					cnt = cur_word_num - last_word_num;
					n = write_or_die(f->binfd, blank, cnt*sizeof(*blank));
				}
				last_word_num += cnt;
			}

			n = write_or_die(f->binfd, &value, sizeof(value));
			last_word_num++;
		}

		cur_word_num = sparse_size * 1024 * 1024 * 1024 / (NSHARDS * sizeof(WORD_TYPE));

		while (last_word_num < cur_word_num) {
			unsigned long cnt = blank_size;
			if (last_word_num + cnt < cur_word_num) {
				n = write_or_die(f->binfd, blank, sizeof(blank));
			} else {
				cnt = cur_word_num - last_word_num;
				n = write_or_die(f->binfd, blank, cnt*sizeof(WORD_TYPE));
			}
			last_word_num += cnt;
		}
		f->size = last_word_num * sizeof(WORD_TYPE);
#undef blank_size
	} else { // sparse
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
				n = write_or_die(f->binfd, obuf, j * sizeof(*obuf));
				if (n <= 0) {
					perror("write");
					exit(1);
				}
				f->size += n;
			} else {
				done = true;
			}
		}
	} // sparse

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


void exit_usage(char *argv[])
{
	printf("usage: %s <outfile> <shard-prefix> [sparse=size_gb]\n", argv[0]);
	exit(1);
}


int main(int argc, char *argv[])
{
	const char *prefix = NULL;
	const char *outfile = NULL;
	int fd = -1;

	if (argc < 3 || argc > 4) {
		exit_usage(argv);
	}

	/* extract the actual output filename & prefix */
	outfile = argv[1];
	prefix = argv[2];

	if (argc == 4) {
		char *param = argv[3];
		param = strtok(param, "=");
		if (0 != strcmp(param, "sparse"))
			exit_usage(argv);

		sparse_size = atoi(strtok(NULL, "="));
		if (0 == sparse_size)
			exit_usage(argv);

		sparse = true;
	}

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
