/* command-line wrapper around fun_json functionality */

#define _XOPEN_SOURCE
#define _GNU_SOURCE

#include <ctype.h>	// for isspace()
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
#include <FunOS/utils/common/base64.h>

#define NOMODE        (0)
#define TEXT          (1)
#define BINARY        (2)
#define TEXT_ONE_LINE (3)
#define FUN_JSON      (4)
#define BASE64        (6)

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

static char *_read_line_from_file(int fd)
{
	char ch;
	size_t length = 0;
	char *result = NULL;
	do {
		ssize_t n = read(fd, &ch, 1);
		if (n != 1) break;
		result = realloc(result, ++length);

		if (result == NULL) {
			fprintf(stderr, "out of memory\n");
			return NULL;
		}

		result[length - 1] = ch;
	} while (ch != '\n' && ch != '\r' && ch != '\0');

	if (length == 0) return NULL;

	if (result[length - 1] != '\0' && result[length - 1] != '\n' && result[length - 1] != '\r') {
		result = realloc(result, ++length);
	}

	result[length - 1] = 0;

	return result;
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

static struct fun_json *_line_to_command(char *buf)
{
	if (buf == NULL) {
		return NULL;
	}

	const char *error = NULL;
	static uint64_t tid = 0;
	struct fun_json *input = fun_commander_line_to_command(buf, &tid, &error);

	if (input == NULL) {
		input = fun_json_create_error("Error parsing JSON command", fun_json_no_copy_no_own);
	}

	free(buf);
	return input;
}

static bool empty_line(char *line)
{
	while (*line) {
		if (!isspace(*line)) return false;
		line++;
	}
	return true;
}

static struct fun_json *_read_funjson(int fd, bool *skip)
{
	char *buf = _read_line_from_file(fd);
	if (buf && empty_line(buf)) {
		*skip = true;
		free(buf);
		return NULL;
	}
	return _line_to_command(buf);
}

static struct fun_json *_read_base64(int fd, bool *skip)
{
	char *buf = _read_line_from_file(fd);
	if (!buf)
		return NULL;

	if (empty_line(buf)) {
		*skip = true;
		free(buf);
		return NULL;
	}

	size_t len = strlen(buf);
	char *decode_buf = malloc(len);
	int r = base64_decode((void *)decode_buf, len, buf);
	free(buf);

	if (r <= 0) {
		fprintf(stderr, "error encoding base64\n");
		free(decode_buf);
		return NULL;
	}

	struct fun_json *input = NULL;
	size_t actual_size = fun_json_binary_serialization_size((void *)decode_buf, len);

	if (actual_size <= len) {
		input = fun_json_create_from_binary_with_options((void *)decode_buf, actual_size, false);
	}

	if (input == NULL) {
		fprintf(stderr, "error decoding binary json\n");
	}

	free(decode_buf);
	return input;
}

static struct fun_json *_read_bjson(int fd)
{
	struct fun_json *input = NULL;
	uint8_t *buf = NULL;
	size_t size, allocation_size = 0;

	size = fun_json_read_enough_bytes_for_json_from_fd(fd, &buf, &allocation_size);
	assert(buf);
	input = fun_json_create_from_binary(buf, size);

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
	else if (mode == TEXT_ONE_LINE)
		buf = fun_json_to_text_oneline(json, &dummy_size);
		
	if (!buf)
		return -1;

	r = _write_output_file(fd, buf, strlen(buf));
	free(buf);

	/* be nice and print a newline */
	if (r == 0)
		_write_output_file(fd, "\n", 1);
	
	return r;
}

static int _write_bjson(int fd, struct fun_json *json)
{
	bool r;

	r = fun_json_write_to_fd(json, fd);

	/* true on success -> 0 on success  */
	return (r != true);
}

static int _write_base64(int fd, struct fun_json *json)
{
	size_t allocated_size;
	struct fun_ptr_and_size data = fun_json_serialize(json, &allocated_size);

	if (data.ptr == NULL) {
		fprintf(stderr, "cannot serialize to json\n");
		return -1;
	}

	size_t b64size = data.size * 2 + 1; /* big to avoid rounding issues */
	char *b64buf = malloc(b64size);

	if (b64buf == NULL) {
		free(data.ptr);
		fprintf(stderr, "out of memory allocating output b64 buffer\n");
		return -1;
	}

	int r = base64_encode(b64buf, b64size, (void*)data.ptr, data.size);

	free(data.ptr);

	if (r <= 0) {
		fprintf(stderr, "error encoding base64\n");
		free(b64buf);
		return -1;
	}

	b64size = strlen(b64buf);
	ssize_t written = write(fd, b64buf, b64size);

	free(b64buf);

	if (b64size != written) {
		fprintf(stderr, "unable to write base64 data\n");
		return -1;
	}

	return 0;
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
	fprintf(stderr,
"usage: %s <input> [<output>]\n\
    options\n\
 -i, --in <file>          input  <file> as text json\n\
 -I, --inb <file>         input  <file> as binary json\n\
 -f, --inf <file>         input  <file> as a fun json command\n\
 -e, --in-base64 <file>   input  <file> as base64 encoded binary json\n\
 -o, --out <file>         output <file> as text json\n\
 -O, --outb <file>        output <file> as binary json\n\
 -l, --line <file>        output <file> as single-line text json\n\
 -E, --out-base64 <file>  output <file> as base64 encoded binary json\n\
Default output is text to stdout\n\
Filename \"-\" can be used ot output single or multi-line text to stdout.\n", fname);
	exit(1);
}

int
main(int argc, char *argv[])
{
	int r = 0;
	int c;
	
	int inmode = NOMODE;
	int outmode = NOMODE;
	char *infile = NULL;
	char *outfile = "-"; /* default text to stdout */
	int infd, outfd;
	
	while (1) {
		int option_index = 0;
		static struct option long_options[] = {
			{"in",         required_argument, 0,  'i' },
			{"out",        required_argument, 0,  'o' },
			{"line",       required_argument, 0,  'l' },
			{"inb",        required_argument, 0,  'I' },
			{"outb",       required_argument, 0,  'O' },
			{"inf",        required_argument, 0,  'f' },
			{"in-base64",  required_argument, 0,  'e' },
			{"out-base64", required_argument, 0,  'E' },
		};

		
		c = getopt_long(argc, argv, "i:o:l:I:O:f:e:E:",
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
			inmode = _setmode(inmode, FUN_JSON);
			infile = optarg;
			break;
		case 'O':
			outmode = _setmode(outmode, BINARY);
			outfile = optarg;
			break;
		case 'l':
			outmode = _setmode(outmode, TEXT_ONE_LINE);
			outfile = optarg;
			break;
		case 'e':
			inmode = _setmode(inmode, BASE64);
			infile = optarg;
			break;
		case 'E':
			outmode = _setmode(outmode, BASE64);
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

	bool productive = false;

	do {
		struct fun_json *input = NULL;
		bool skip = false;

		switch (inmode) {
			case TEXT:
				input = _read_json(infd);
				break;
			case BINARY:
				input = _read_bjson(infd);
				break;
			case FUN_JSON:
				input = _read_funjson(infd, &skip);
				break;
			case BASE64:
				input = _read_base64(infd, &skip);
				break;
			default:
				abort();
		}

		if (skip) continue;

		if (!input) {
			break;
		}

		if (fun_json_is_error_message(input)) {
			const char *message;
			fun_json_fill_error_message(input, &message);
			fprintf(stderr, "%s\n", message);
			exit(1);
		}

		productive = true;

		/* write out some json */
		if (outmode == BINARY)
			r = _write_bjson(outfd, input);
		else if (outmode == BASE64)
			r = _write_base64(outfd, input);
		else
			r = _write_json(outfd, input, outmode);

		fun_json_release(input);

		if (r) {
			fprintf(stderr, "error writing json\n");
			break;
		}
	} while (inmode != BINARY && inmode != TEXT);

	if (!productive) {
		r = 5;
		fprintf(stderr, "no json found in input\n");
	}
	
	return r;
}
