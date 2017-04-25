/* test dpcsock functionality */

#define _XOPEN_SOURCE
#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <unistd.h>
#include <getopt.h>
#include <fcntl.h>

#include "fun_json.h"

#define MAX_JSON (1024*1024)

static char _buf[MAX_JSON];

static char *_read_input_file(int fd, size_t *outsize)
{
	char *pp;
	int r;
	ssize_t n;
	size_t size = 0;
	
	pp = _buf;
	while ((n = read(fd, pp, MAX_JSON - (pp-_buf))) > 0) {
		pp += n;
		size += n;
	}

	if (n < 0) {
		perror("read");
		exit(1);
	}

	if (outsize)
		*outsize = size;
	return _buf;
}

static int _write_output_file(int fd, char *buf, ssize_t len)
{
	ssize_t delta = 0;
	ssize_t offset = 0;
	
	do {
		delta = write(fd, &buf[offset], len-offset);
		if (delta > 0)
			offset += delta;
	} while(delta > 0);

	if (delta < 0) {
		perror("write");
		return -1;
	}
	
	if (offset != len) {
		fprintf(stderr, "truncated output\n");
		return -1;
	}

	return 0;
}
			    

static struct fun_json *_read_json(int fd)
{
        struct fun_json *input = NULL;
	char *buf;
	size_t size = 0;
	size_t line = 0;
	size_t parsed = 0;

	buf = _read_input_file(fd, &size);
	assert(buf);
	
	input = fun_json_create_from_text_with_length(buf, size, &line, &parsed);

	return input;
}

static struct fun_json *_read_bjson(int fd)
{
        struct fun_json *input = NULL;
	char *buf;
	size_t size;

	buf = _read_input_file(fd, &size);
	assert(buf);
	
	input = fun_json_create_from_parsing_binary(buf, size);

	return input;
}
	
static int _write_json(int fd, struct fun_json *json)
{
	char *buf;
	int r;
	
	buf = fun_json_to_text(json);
	if (!buf)
		return -1;

	r = _write_output_file(fd, buf, strlen(buf));
	free(buf);

	/* be nice and print a newline if it's stdout */
	if ((r == 0) && (fd == 0))
		printf("\n");
	
	return r;
}

static int _write_bjson(int fd, struct fun_json *json)
{
	bool r;

	r = fun_json_write_to_fd(json, fd);

	/* true on success -> 0 on success  */
	return (r != true);
}



#define NOMODE (0)
#define TEXT   (1)
#define BINARY (2)

static int
_setmode(int curmode, int newmode)
{
	if (curmode != NOMODE) {
		fprintf(stderr, "can only specify one input or output file\n");
		exit(1);
	}

	return newmode;
}

static void
_usage(const char *fname)
{
	fprintf(stderr, "usage: %s <options>\n", fname);
	exit(1);
}

int
main(int argc, char *argv[])
{
	int r;
	int c;
	
	int inmode = NOMODE;
	int outmode = NOMODE;
	char *infile = NULL;
	char *outfile = "-"; /* default text to stdout */
	int infd, outfd;
	
	while (1) {
		int option_index = 0;
		static struct option long_options[] = {
			{"in",   required_argument, 0,  'i' },
			{"out",  required_argument, 0,  'o' },
			{"inb",  required_argument, 0,  'I' },
			{"outb", required_argument, 0,  'O' },
		};

		
		c = getopt_long(argc, argv, "i:o:I:O:",
				long_options, NULL);
		if (c == -1)
			break;

		switch (c) {
		case 'i':
			inmode = _setmode(inmode, TEXT);
			infile = optarg;
			break;
		case 'o':
			outmode = _setmode(outmode, TEXT);
			outfile = optarg;
			break;
		case 'I':
			inmode = _setmode(inmode, BINARY);
			infile = optarg;
			break;
		case 'O':
			outmode = _setmode(outmode, BINARY);
			outfile = optarg;
			break;
		case '?':
		default:
			printf("bad char?\n");
			_usage(argv[0]);
		}

#if 0
		if (optind < argc) {
			printf("optind??\n");
			_usage(argv[0]);
		}
#endif
	}

	if (infile == NULL)
		_usage(argv[0]);

	if (outmode == NOMODE)
		outmode = TEXT;
	
	/* open input file */
	infd = open(infile, O_RDONLY);
	if (infd < 0) {
		perror("open input");
		exit(1);
	}

	if (strcmp(outfile, "-") == 0) {
		if (outmode == BINARY) {
			fprintf(stderr, "not writing binary to stdout\n");
			exit(1);
		}
		outfd = 0;
	} else {
		outfd = open(outfile, O_WRONLY | O_CREAT | O_TRUNC, 0644);
		if (outfd < 0) {
			perror("open output");
			exit(1);
		}
	}


	/* read in some json */
        struct fun_json *input = NULL;
	if (inmode == TEXT)
		input = _read_json(infd);
	else
		input = _read_bjson(infd);

	/* FIXME: check for errors here */
	if (!input) {
		fprintf(stderr, "failed to read a JSON\n");
		exit(1);
	}
	
	/* write out some json */
	if (outmode == TEXT)
		r = _write_json(outfd, input);
	else
		r = _write_bjson(outfd, input);

	if (r) {
		fprintf(stderr, "error writing json\n");
	}

	fun_json_release(input);
	
	return r;
}
