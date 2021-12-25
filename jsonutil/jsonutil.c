/* command-line wrapper around fun_json functionality */

#define _XOPEN_SOURCE
#define _GNU_SOURCE

#include <stdio.h>	// for fprintf()
#include <unistd.h>	// for STDOUT_FILENO
#include <stdlib.h>	// for free()
#include <getopt.h>	// for getopt_long()
#include <fcntl.h>	// for open()
#include <string.h>	// for strcmp()

// We must define PLATFORM_POSIX to get fun_json_write_to_fd()
#define PLATFORM_POSIX 1
#include <FunOS/utils/threaded/fun_json.h>
#include <FunOS/services/commander/fun_commander.h>

#define NOMODE      (0)
#define TEXT        (1)
#define BINARY      (2)
#define TEXTONELINE (3)
#define FUNJSON     (4)


static void oom(void)
{
	printf("out of memory\n");
	exit(-1);
}

static char *_read_input_file(int fd, size_t *outsize)
{
	char *buffer;
	char *pp;
	int r;
	ssize_t n;
	size_t alloc_size, size = 0;

	alloc_size = (1024 * 1024);
	buffer = malloc(alloc_size+1);
	if (buffer == NULL)
		oom();
	pp = buffer;
	
	while ((n = read(fd, pp, alloc_size - size)) > 0) {
		/* total json so far + just read */
		size += n;

		/* if it's full, up the buffer */
		if (size == alloc_size) {
			alloc_size *= 2;
			buffer = realloc(buffer, alloc_size+1);
			if (buffer == NULL)
				oom();
		}

		/* next read pointer = buffer + existing json */
		pp = buffer + size;
	}

	if (n < 0) {
		perror("read");
		exit(1);
	}

	if (outsize)
		*outsize = size;
	// append a null for strings?
	buffer[size] = '\0';
	return buffer;
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
	bool parsed_all;

	buf = _read_input_file(fd, &size);
	assert(buf);

	input = fun_json_create_from_text_with_status(buf, &parsed_all);

	if (!parsed_all || size != strlen(buf)) {
		fun_json_release(input);
		input = fun_json_create_error("JSON terminated earlier than the end of file", fun_json_no_copy_no_own);
	}

	free(buf);
	return input;
}

static struct fun_json *_read_funjson(int fd)
{
	struct fun_json *input = NULL;
	char *buf;
	size_t size = 0;
	bool parsed_all;
	const char *error = NULL;
	uint64_t tid = 0;

	buf = _read_input_file(fd, &size);
	assert(buf);

	input = fun_commander_line_to_command(buf, &tid, &error);

	if (input == NULL) {
		input = fun_json_create_error("Error parsing JSON command", fun_json_no_copy_no_own);
	}

	free(buf);
	return input;
}

static struct fun_json *_read_bjson(int fd)
{
	struct fun_json *input = NULL;
	char *buf;
	size_t size;

	buf = _read_input_file(fd, &size);
	assert(buf);
	
	input = fun_json_create_from_binary((uint8_t*)buf, size);

	free(buf);
	return input;
}
	
static int _write_json(int fd, struct fun_json *json, int mode)
{
	char *buf = NULL;
	size_t dummy_size = 0;
	int r;

	if (mode == TEXT)
		buf = fun_json_to_text(json);
	else if (mode == TEXTONELINE)
		buf = fun_json_pretty_print(json, 0, "    ", 0, 0, &dummy_size);
		
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
	fprintf(stderr, "usage: %s <input> [<output>]\n", fname);
	fprintf(stderr, "    options\n");
	fprintf(stderr, "        -i <file>      input <file> as text json\n");
	fprintf(stderr, "        -I <file>      input <file> as binary json\n");
	fprintf(stderr, "        -f <file>      input <file> as a fun json command\n");
	fprintf(stderr, "        -o <file>      output <file> as text json\n");
	fprintf(stderr, "        -O <file>      output <file> as binary json\n");
	fprintf(stderr, "        -l <file>      output <file> as single-line text json\n");
	fprintf(stderr, "Default output is text to stdout\n");
	fprintf(stderr, "Filename \"-\" can be used ot output single or");
	fprintf(stderr, "multi-line text to stdout.\n");
	
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
			{"line", required_argument, 0,  'l' },
			{"inb",  required_argument, 0,  'I' },
			{"outb", required_argument, 0,  'O' },
			{"inf",  required_argument, 0,  'f' },
		};

		
		c = getopt_long(argc, argv, "i:o:l:I:O:f:",
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
		case 'f':
			inmode = _setmode(inmode, FUNJSON);
			infile = optarg;
			break;
		case 'O':
			outmode = _setmode(outmode, BINARY);
			outfile = optarg;
			break;
		case 'l':
			outmode = _setmode(outmode, TEXTONELINE);
			outfile = optarg;
			break;
		case '?':
		default:
			_usage(argv[0]);
		}
	}

	if (infile == NULL)
		_usage(argv[0]);

	if (outmode == NOMODE)
		outmode = TEXT;
	
	/* open input file */
	if (strcmp(infile, "-") == 0) {
		if (inmode == BINARY) {
			fprintf(stderr, "not reading binary from stdin\n");
			exit(1);
		}
		infd = STDIN_FILENO;
	} else {
		infd = open(infile, O_RDONLY);
		if (infd < 0) {
			perror("open input");
			exit(1);
		}
	}

	if (strcmp(outfile, "-") == 0) {
		if (outmode == BINARY) {
			fprintf(stderr, "not writing binary to stdout\n");
			exit(1);
		}
		outfd = STDOUT_FILENO;
	} else {
		outfd = open(outfile, O_WRONLY | O_CREAT | O_TRUNC, 0644);
		if (outfd < 0) {
			perror("open output");
			exit(1);
		}
	}


	/* read in some json */
	struct fun_json *input = NULL;
	if (inmode == TEXT) {
		input = _read_json(infd);
	} else if (inmode == BINARY) {
		input = _read_bjson(infd);
	} else if (inmode == FUNJSON) {
		input = _read_funjson(infd);
	} else {
		/* bad input */
		abort();
	}

	if (!input) {
		fprintf(stderr, "failed to read a JSON\n");
		exit(1);
	}

	if (fun_json_is_error_message(input)) {
		const char *message;
		fun_json_fill_error_message(input, &message);
		fprintf(stderr, "%s\n", message);
		exit(1);
	}

	/* write out some json */
	if (outmode == BINARY)
		r = _write_bjson(outfd, input);
	else
		r = _write_json(outfd, input, outmode);

	if (r) {
		fprintf(stderr, "error writing json\n");
	}

	fun_json_release(input);
	
	return r;
}
