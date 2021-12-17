/*
 *  dpcsh.c
 *
 *  Copyright © 2017-2018 Fungible. All rights reserved.
 */

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <fcntl.h>
#include <getopt.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <sys/un.h>
#include <termios.h>          	// termios, TCSANOW, ECHO, ICANON
#include <signal.h>          	// termios, TCSANOW, ECHO, ICANON
#include <netinet/in.h>		// TCP socket
#include <arpa/inet.h>
#include <sys/select.h>
#include <sys/stat.h>
#include <time.h>

#include "dpcsh.h"
#include "dpcsh_log.h"
#include "dpcsh_nvme.h"
#include "csr_command.h"
#include "file_commands.h"

#ifdef WITH_LIBFUNQ
#include "bin_ctl.h"
#endif

#include <FunSDK/utils/threaded/fun_map_threaded.h>
#include <FunSDK/services/commander/fun_commander.h>
#include <FunSDK/services/commander/fun_commander_basic_commands.h>
#include <FunSDK/utils/threaded/fun_malloc_threaded.h>
#include <FunSDK/utils/common/base64.h>
#include <FunSDK/platform/include/platform/utils_platform.h>

#define SOCK_NAME	"/tmp/funos-dpc.sock"      /* default FunOS socket */
#define PROXY_NAME      "/tmp/funos-dpc-text.sock" /* default unix proxy name */
#define DPC_PORT_STR    "20110"   /* default FunOS port */
#define DPC_PROXY_PORT  40221   /* default TCP proxy port */
#define DPC_B64_PORT    40222   /* default dpcuart port in qemu */
#define DPC_B64SRV_PORT 40223   /* default dpcuart listen port */
#define HTTP_PORTNO     9001    /* default HTTP listen port */
#define NO_FLOW_CTRL_DELAY_USEC	10000	/* no flow control delay in usec */

const char *dpcsh_path;

/* for debug */
static const USED char *FunSDK_version = XSTRINGIFY(VER);
static const USED char *branch_version = XSTRINGIFY(BRANCH);

/* Force user input mode */
#define OVERRIDE_TEXT  "#!sh "
#define OVERRIDE_JSON  "#!json "

/* header on bas64 json lines to avoid confusing other output for json */
#define B64JSON_HDR "#!b64json "

/* tty (uart) device controls */
#define DEFAULT_BAUD "19200"
static bool _do_device_init = true; /* if we have a device, init by default */
static char *_baudrate = DEFAULT_BAUD; /* default BAUD rate */
static bool _no_flow_control = false;  /* run without flow_control */
static bool _legacy_b64 = false;

/* whether to log all json */
static bool _verbose_log = false;

/* whether to print various debugging messages */
static bool _debug_log = false;

/* nocli mode for script integration, by default keep quiet */
static bool _nocli_script_mode = false;

#define MAX_CLIENTS_THREADS (256)
#define READ_BUFFER_SIZE (4 * 1024)

struct dpc_thread {
	pthread_t thread;
	void *args[3];
};

struct dpc_worker {
	struct dpc_thread in, out; // in and out of FunOS
	bool used;
};

/* cmd timeout, use driver default timeout */
#define DEFAULT_NVME_CMD_TIMEOUT_MS "0"

/* socket connect retry parameters */
#define RETRY_DEFAULT (100)  /* retry for 100 seconds; 60 is not enough sometimes in jenkins */
#define RETRY_NOARG   (RETRY_DEFAULT)
static uint16_t connect_retries = RETRY_DEFAULT;

static void _print_version(void)
{
	if (_nocli_script_mode && !_debug_log)
		return;

	/* single line version when everything matches up */
	log_info("FunSDK version %s, branch: %s\n",
	       FunSDK_version, branch_version);

	/* extra logging when things are built a little weird */
	if (strcmp(FunSDK_version, platform_SDK_version) != 0) {
		log_info("libfunclient FunSDK version %s, branch: %s\n",
		       platform_SDK_version, platform_branch_version);
	}
}

// ===============  HISTORY SUPPORT ===============

/* simple readline support */
static char **history = NULL; // most recent first
static int history_count = 0;

static void append_to_history(char *line)
{
	size_t l = strlen(line);
	if (l == 0)
		return;
	if (line[l-1] == '\n')
		l--; // exclude '\n'
	if (l == 0)
		return;
	history = realloc(history, (history_count+1) * sizeof(char *));
	if (history_count != 0) {
		char *last = history[history_count-1];
		if (!strncmp(last, line, l) && !last[l])
			return; // same - don't add
	}
	history[history_count++] = strdup(line);
	// printf("History : %d\n", history_count);
}

static char *use_history(char *line, size_t len, int history_index)
{
	if (!history)
		return line; // no effect
	if (history_index >= history_count)
		return line;
	char *str = history[history_index];

	// erase current characters
	for (int i = 0; i < len; i++)
		printf("%c[D", 27);

	// kill rest of line
	printf("%c[K", 27);
	printf("%s", str);
//		fflush(stdout);

	free(line);
	return strdup(str);
}

static char *history_previous(char *line, size_t len, OUT int *history_index)
{
	if ((* history_index) > 0)
		(*history_index)--;
	return use_history(line, len, *history_index);

}
static char *history_next(char *line, size_t len, OUT int *history_index)
{
	if ((*history_index) + 1 < history_count)
		(*history_index )++;
	return use_history(line, len, *history_index);
}

static char *getline_with_history(OUT ssize_t *nbytes)
{
	size_t len = 0, capa = 0;
	char *line = NULL;
	int current_history = history_count;

	while (true) {

		if ((len+1) > capa) {
			capa += 16;
			line = realloc(line, capa);
			if (line == NULL) {
				log_error("error allocating input line buffer\n");
				exit(1);
			}
		}

		char ch = getchar();
		if (ch == 14 /* ^N */) {
			line = history_next(line, len, &current_history);
			len = capa = strlen(line);
		} else if (ch == 16 /* ^P */) {
			line = history_previous(line, len, &current_history);
			len = capa = strlen(line);
		} else if ((ch == EOF) || (ch == 4 /* ^D*/) || (ch == '\n')) {
			*nbytes = len + 1;
			if (ch == '\n')
				write(STDOUT_FILENO, &ch, 1);
			else if (len == 0)
				/* if the only signal is EOF, we end */
				*nbytes = -1;
			line = realloc(line, len+1);
			line[len] = '\0';
			append_to_history(line);
			return line;
		} else if (ch == 27) {
			if (getchar() != 91)
				continue;
			char ch2 = getchar();
			if (ch2 == 'A') {
				line = history_previous(line, len,
							&current_history);
				len = capa = strlen(line);
			} else if (ch2 == 'B') {
				line = history_next(line, len,
						    &current_history);
				len = capa = strlen(line);
			} else {
				// printf("Ignoring ch2=%d\n", ch2);
			}
		} else if (ch == 127 /*DEL*/) {
			if (len > 0) {
				printf("%c[D", 27);
				printf("%c[K", 27);
				len--;
				line[len] = '\0';
			}
		} else {
			// printf("GOT ch=%d\n", ch);
			write(STDOUT_FILENO, &ch, 1);
			line = realloc(line, len+2);
			line[len++] = ch;
			line[len] = '\0';
		}
	}
}

// ===============  SOCKET HANDLING ===============

/* socket routines */
static int _open_sock_inet(const char *host_port, uint16_t port)
{
	int sock = -1;
	int r = -1, tries = 0;
	struct addrinfo hints;
	struct addrinfo *result, *rp;

	memset(&hints, 0, sizeof(hints));
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;

	if (host_port == NULL) {
		char port_str[6];
		sprintf(port_str, "%" PRIu16, port);
		log_debug(_debug_log, "trying 127.0.01:%s\n", port_str);
		int s = getaddrinfo("127.0.0.1", port_str, &hints, &result);
		if (s != 0) {
				log_error("getaddrinfo: %s\n", gai_strerror(s));
				exit(EXIT_FAILURE);
		}
	} else {
		char *host_port_d = strdup(host_port);
		if (!host_port_d) {
			log_error("failed to copy host_port string");
			exit(EXIT_FAILURE);
		}

		char *delimiter = strstr(host_port_d, ":");
		char *port_s = (delimiter == NULL) ? host_port_d : delimiter + 1;
		char *host_s = (delimiter == NULL) ? "127.0.0.1" : host_port_d;
		if (delimiter != NULL) *delimiter = 0;

		log_debug(_debug_log, "trying %s:%s\n", host_s, port_s);

		int s = getaddrinfo(host_s, port_s, &hints, &result);
		if (s != 0) {
			log_error("getaddrinfo: %s\n", gai_strerror(s));
			exit(EXIT_FAILURE);
		}
		free(host_port_d);
	}

	do {
		for (rp = result; rp != NULL; rp = rp->ai_next) {
				sock = socket(rp->ai_family, rp->ai_socktype,
										rp->ai_protocol);
				if (sock == -1) {
					continue;
				}

				r = connect(sock, rp->ai_addr, rp->ai_addrlen);
				if (r != -1) break;
				close(sock);
		}

		if (tries > 0) {
			log_error("connect error, retry %d\n", tries);
			sleep(1);
		}

		tries++;
	} while ((r < 0) && (tries < connect_retries));

	freeaddrinfo(result);

	if (r < 0 || sock < 0) {
		log_error("can't connect\n");
		perror("connect");
		exit(1);
	}

	if (host_port == NULL) {
		log_debug(_debug_log, "connected to %" PRIu16 "\n", port);
	} else {
		log_debug(_debug_log, "connected to %s\n", host_port);
	}

	return sock;
}

static int _open_sock_unix(const char *name)
{
	int r = -1;
	int sock = socket(AF_UNIX, SOCK_STREAM, 0);
	int tries = 0;

	if (sock <= 0)
		return sock;

	struct sockaddr_un server = { .sun_family = AF_UNIX };
	strcpy(server.sun_path, name);
	do {
		if (tries > 0) {
			log_error("connection fail, retry %d\n", tries);
			sleep(1);
		}

		r = connect(sock, (struct sockaddr *)&server, sizeof(server));
		tries++;
	} while(r && (tries < connect_retries));

	if (r) {
		log_error("can't connect: %d\n", r);
		perror("connect");
		exit(1);
	}
	return sock;
}

static void _listen_sock_init(struct dpcsock *sock)
{
	struct sockaddr_in local_inet = { 0 };
	struct sockaddr_un local_unix = { 0 };
	struct sockaddr *local;
	socklen_t s;
	int optval = 1, r;

	/* make sure it's sane */
	assert((sock->mode == SOCKMODE_UNIX) || (sock->mode == SOCKMODE_IP));
	assert(sock->server);

	if (sock->mode == SOCKMODE_UNIX) {
		/* create a server socket */
		sock->listen_fd = socket(AF_UNIX, SOCK_STREAM, 0);
		assert(sock->listen_fd > 0);

		/* set socket parameters */
		log_info("publishing %s\n", sock->socket_name);

		local_unix.sun_family = AF_UNIX;

		snprintf(local_unix.sun_path,
			 sizeof(local_unix.sun_path), "%s", sock->socket_name);
		if ((r = unlink(local_unix.sun_path))
		    && (errno != ENOENT)) {
			log_error("failed to remove existing socket file: %s\n",
			       strerror(errno));
			exit(1);
		}

		local = (struct sockaddr *) &local_unix;
		s = sizeof(struct sockaddr_un);
	} else {
		/* create a server socket */
		sock->listen_fd = socket(AF_INET, SOCK_STREAM, 0);
		assert(sock->listen_fd > 0);

		if (setsockopt(sock->listen_fd, SOL_SOCKET, SO_REUSEADDR,
			       (const void *)&optval, sizeof(int)) < 0) {
			perror("setsockopt(SO_REUSEADDR)");
			exit(1);
		}

#ifdef __linux__
		if (sock->eth_name && (setsockopt(sock->listen_fd, SOL_SOCKET, SO_BINDTODEVICE,
				sock->eth_name, strlen(sock->eth_name)) < 0)) {
			perror("setsockopt(SO_BINDTODEVICE)");
			exit(1);
		}
#endif // __linux__

		/* set socket parameters */

		printf("Publishing on port %d\n", sock->port_num);

		local_inet.sin_family = AF_INET;
		local_inet.sin_addr.s_addr = INADDR_ANY;
		local_inet.sin_port = htons(sock->port_num);

		local = (struct sockaddr *) &local_inet;
		s = sizeof(struct sockaddr_in);
	}

	if (bind(sock->listen_fd, local, s) == -1) {
		perror("bind");
		exit(1);
	}

	if (listen(sock->listen_fd, 1) == -1) {
		perror("listen");
		exit(1);
	}
}

static struct fun_ptr_and_size _base64_transcode(struct fun_ptr_and_size data)
{
	/* keep it simple */
	struct fun_ptr_and_size result = {.ptr = NULL, .size = 0};
	size_t b64size = data.size * 2 + 1; /* big to avoid rounding issues */
	char *b64buf = malloc(b64size);

	if (b64buf == NULL) {
		log_error("out of memory allocating output b64 buffer\n");
		exit(1);
	}

	int r = base64_encode(b64buf, b64size, (void*)data.ptr, data.size);
	if (r <= 0) {
		log_error("error encoding base64\n");
		free(b64buf);
		return result;
	}

	result.ptr = (uint8_t *)b64buf;
	result.size = strlen(b64buf) + 1;

	return result;
}

static struct fun_ptr_and_size _transcode(struct fun_ptr_and_size source,
	struct dpcsock_connection *dest)
{
	if (dest->socket->base64) return _base64_transcode(source);
	if (dest->encoding == PARSE_BINARY_JSON) return source;

	struct fun_json *json = fun_json_create_from_binary_with_options(source.ptr,
				source.size, true);

	if (!json) {
		json = fun_json_create_const_error("malformed JSON, transcode failed");
	}

	// transcode to text json
	size_t unused;
	char *json_text = NULL;
	struct fun_ptr_and_size result = {};

	if (fun_json_is_error_message(json)) {
		const char *msg = NULL;
		fun_json_fill_error_message(json, &msg);
		log_info("Transcode error: %s\n", msg);
	} else if (dest->socket->mode == SOCKMODE_TERMINAL) {
		uint32_t flags = use_hex ? FUN_JSON_PRETTY_PRINT_USE_HEX_FOR_NUMBERS : 0;
		json_text = fun_json_pretty_print(json,
							  0, "    ",
							  100, flags,
							  &unused);
	} else {
		json_text = fun_json_to_text_oneline(json, &unused);
	}
	fun_json_release(json);

	if (json_text) {
		size_t json_length = strlen(json_text);
		result.ptr = (uint8_t *)json_text;
		result.size = json_length + 1;
		json_text[json_length] = '\n';
	}

	return result;
}

// returns false in case of error,
// in case of success position is advanced for the number of bytes written
static bool _write_to_fd(struct dpcsock_connection *connection,
	struct fun_ptr_and_size write_buffer, size_t *position)
{
	int r;
	struct fun_ptr_and_size w = write_buffer;
	w.ptr += *position;
	w.size -= *position;
	int fd = connection->fd;

	if (connection->socket->mode == SOCKMODE_TERMINAL) {
		fd = STDOUT_FILENO;
	}

	if (!_no_flow_control) {
		r = write(fd, w.ptr, w.size);

		if (r < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
			perror("write");
			return false;
		}

		fsync(fd);

		if (r > 0) *position += r;

		return true;
	}

	for (size_t i = 0; i < w.size; i++) {
		r = write(fd, w.ptr + i, 1);
		if (r < 0)
			return false;
		fsync(fd);
		usleep(NO_FLOW_CTRL_DELAY_USEC);
	}
	*position += w.size;
	return true;
}

static char *_is_b64json_line(char *line)
{
	if (strncmp(line, B64JSON_HDR, strlen(B64JSON_HDR)) == 0)
		return line + strlen(B64JSON_HDR);

	/* legacy base64 encoding support. TODO: remove */
	if (_legacy_b64) {
		size_t len = strlen(line) + 1;
		int r;
		uint8_t *decode_buf = malloc(len);

		if (decode_buf == NULL) {
			return NULL; /* silent fail on OOM */
		}

		r = base64_decode(decode_buf, len, line);

		free(decode_buf);

		/* if we decoded something */
		if (r > 0)
			return line;
	}

	return NULL;
}

/* returns a newly allocated buffer which is the base64 decoded
 * version of line, if the decoder is happy. expects the header to be
 * stripped already
 */
static uint8_t *_b64_to_bin(char *line, ssize_t /* out */ *size)
{
	uint8_t *binbuf = NULL;
	size_t nbytes = strlen(line);

	/* this means the buffer is oversize. meh. */
	binbuf = malloc(nbytes);
	if (binbuf == NULL) {
		log_error("couldn't allocate input buffer\n");
		exit(1);
	}

	*size = base64_decode(binbuf, nbytes, line);

	if (*size <= 0) {
		free(binbuf);
		binbuf = NULL;
	}

	return binbuf;
}

struct fun_json *_buffer2json(const uint8_t *buffer, size_t max, size_t *read_bytes)
{
	struct fun_json *json = NULL;
	size_t r;

	if (read_bytes == NULL)
		read_bytes = &r;

	if (!buffer)
		return NULL;

	*read_bytes = fun_json_binary_serialization_size(buffer, max);
	if (*read_bytes <= max) {
		json = fun_json_create_from_binary_with_options(buffer,
				*read_bytes,
				true);
	}

	return json;
}

/* given a line of input, try and return a JSON object.
 *
 * Pay attention to which parsing mode we're in (free text or strict json),
 * and whether an override was specified.
 *
 * NOTE: mixing text & json modes with async transactions is in no way
 * supported. Just use json mode for that (or cross your fingers...)
 */
static struct fun_json *line2json(char *line, enum parsingmode pmode, const char **error)
{
	struct fun_json *json = NULL;

	/* clear this up in case we return early */
	*error = NULL;

	/* sanity check the global */
	assert((pmode == PARSE_TEXT) || (pmode == PARSE_JSON));

	/* check for override */
	if (strncmp(line, OVERRIDE_TEXT, strlen(OVERRIDE_TEXT)) == 0) {
		pmode = PARSE_TEXT;
		line = &line[strlen(OVERRIDE_TEXT)];
	} else if (strncmp(line, OVERRIDE_JSON, strlen(OVERRIDE_JSON)) == 0) {
		pmode = PARSE_JSON;
		line = &line[strlen(OVERRIDE_JSON)];
	}

	if (pmode == PARSE_TEXT) {
		/* parse as a command-line with an always increasing tid */
		static uint64_t tid = 0;
		json = fun_commander_line_to_command(line, &tid, error);
	} else {
		/* parse as a real JSON blob */
		/* FIXME: needs macro expansion */
		json = fun_json_create_from_text(line);
	}

	return json;
}

static char *_get_line(uint8_t *start, size_t max)
{
	size_t position = 0;
	while (position < max
		&& start[position] != '\n' && start[position] != '\0') {
			position++;
		}

	if (position < max) {
		start[position] = 0;
		return (char *)start;
	}
	return NULL;
}

// Somewhat of a hack: help needs to apply to both local (dpcsh-side) and remote (funos-side)
// So we apply it once locally first
static void apply_command_locally(const struct fun_json *json,
			struct dpcsock_connection *cmd, bool *complete)
{
	const char *verb = NULL;
	*complete = false;

	if (!fun_json_lookup_string(json, "verb", &verb)) {
		return;
	}

	if (!verb) {
		return;
	}

	if (!strcmp(verb, "encoding_json")) {
		*complete = true;
		cmd->encoding = PARSE_JSON;
		log_debug(_debug_log, "changing encoding to json\n");
		return;
	}

	if (!strcmp(verb, "encoding_text")) {
		*complete = true;
		cmd->encoding = PARSE_TEXT;
		log_debug(_debug_log, "changing encoding to text\n");
		return;
	}

	if (!strcmp(verb, "encoding_binary_json")) {
		*complete = true;
		cmd->encoding = PARSE_BINARY_JSON;
		log_debug(_debug_log, "changing encoding to binary json\n");
		return;
	}

	if (strcmp(verb, "help")) {
		return;
	}

	struct fun_command_environment *env = fun_command_environment_create();
	struct fun_json *j = fun_commander_execute(env, json);

	fun_command_environment_release(env);
	if (!j || fun_json_fill_error_message(j, NULL)) {
		return;
	}
	struct fun_json *result = fun_json_lookup(j, "result");
	if (result && !fun_json_fill_error_message(result, NULL)) {
		if (_verbose_log) {
			fun_json_printf_with_flags(PRELUDE BLUE POSTLUDE "Locally applied command: %s" NORMAL_COLORIZE "\n", result,
				FUN_JSON_PRETTY_PRINT_HUMAN_READABLE_STRINGS);
		}
	}
	fun_json_release(j);
}

static bool _decode_jsons_from_buffer(struct dpcsock_connection *connection)
{
	size_t position = 0;
	struct fun_ptr_and_size next, transcoded;
	bool no_copy, any_no_copy = false;

	do {
		no_copy = (connection->encoding == PARSE_BINARY_JSON) && !connection->socket->base64;
		any_no_copy = any_no_copy || no_copy;
		transcoded.ptr = NULL;
		next.ptr = connection->read_buffer.ptr + position;
		next.size = connection->read_buffer_position - position;
		if (connection->encoding == PARSE_BINARY_JSON) {
			if (!connection->socket->base64) {
				transcoded.size = fun_json_binary_serialization_size(next.ptr, next.size);
				if (transcoded.size > 0 && transcoded.size <= next.size) {
					transcoded.ptr = next.ptr;
					position += transcoded.size;
				}
			} else {
				char *line = _get_line(next.ptr, next.size);
				if (line) {
					if (_is_b64json_line(line)) {
						ssize_t line_len;
						transcoded.ptr = _b64_to_bin(line, &line_len);
						if (line_len > 0) {
							transcoded.size = line_len;
						} else {
							log_error("got bad base64 line: %s\n", line);
							transcoded.ptr = NULL;
						}
					} else {
						log_error("got bad base64 line: %s\n", line);
					}
					position += strlen(line) + 1;
				}
			}

			if (_verbose_log && transcoded.ptr) {
				struct fun_json *json = fun_json_create_from_binary_with_options(transcoded.ptr, transcoded.size, true);
				log_debug(_debug_log, "parsed binary json from %s\n", connection->socket->verbose_log_name);
				fun_json_printf_with_flags(INPUT_COLORIZE "%s" NORMAL_COLORIZE "\n",
						json, FUN_JSON_PRETTY_PRINT_HUMAN_READABLE_STRINGS);
				fun_json_release(json);
			}

		} else {
			struct fun_json *json = NULL;
			char *line = _get_line(next.ptr, next.size);
			if (line != NULL) {
				const char *error = NULL;
				json = line2json(line, connection->encoding, &error);

				if (error) {
					log_error("line2json returned an error: %s\n", error);
				}
				position += strlen(line) + 1;
			}
			if (json) {
				if (_verbose_log) {
					log_debug(_debug_log, "parsed json from %s\n", connection->socket->verbose_log_name);
					fun_json_printf_with_flags(INPUT_COLORIZE "%s" NORMAL_COLORIZE "\n",
							json, FUN_JSON_PRETTY_PRINT_HUMAN_READABLE_STRINGS);
				}

				bool complete;
				// Hack to list local commands if the command is 'help'
				// Note: this call does not exist on binary json path
				// which means that 'help' and 'change encoding' are available
				// only for 'text' or 'json' modes, which covers all current usecases
				apply_command_locally(json, connection, &complete);
				if (complete) {
					fun_json_release(json);
					continue;
				}

				size_t unused;
				transcoded = fun_json_serialize(json, &unused);
				fun_json_release(json);
			}
		}

		if (!transcoded.ptr) {
			break;
		}
		if (!dpcsh_ptr_queue_enqueue(connection->binary_json_queue, transcoded, no_copy ? connection->read_buffer.ptr : transcoded.ptr)) return false;
	} while (position < connection->read_buffer_position);

	if (position > 0) {
		struct fun_ptr_and_size new_buffer;
		size_t remainder_size = connection->read_buffer_position - position;

		new_buffer.size = MAX(READ_BUFFER_SIZE, remainder_size);
		new_buffer.ptr = malloc(new_buffer.size);

		if (!new_buffer.ptr) {
			log_error("malloc failed");
			return false;
		}

		if (remainder_size > 0) {
			memcpy(new_buffer.ptr, connection->read_buffer.ptr + position, remainder_size);
		}

		if (!any_no_copy) {
			free(connection->read_buffer.ptr);
		}

		connection->read_buffer_position = remainder_size;
		connection->read_buffer = new_buffer;
	}

	return true;
}

static bool _read_all_available_data_from_fd(struct dpcsock_connection *connection)
{
	if ((connection->socket->mode == SOCKMODE_TERMINAL) && !connection->socket->base64) {
		/* fancy pants line editor on stdin */
		ssize_t nbytes;
		free(connection->read_buffer.ptr);

		connection->read_buffer.ptr = (uint8_t *)getline_with_history(&nbytes);
		if (nbytes < 0) return false;
		connection->read_buffer.size = nbytes;
		connection->read_buffer_position = nbytes;
		return true;
	}

	ssize_t bytes_read;
	bool productive = false;

	do {
		size_t bytes_available = connection->read_buffer.size - connection->read_buffer_position;
		if (bytes_available == 0) {
			size_t new_buffer_size = connection->read_buffer.size == 0 ? READ_BUFFER_SIZE : (connection->read_buffer.size * 2);
			void *new_buffer = realloc(connection->read_buffer.ptr, new_buffer_size);

			if (!new_buffer) {
				log_error("failed to allocate %zu bytes for read buffer\n", new_buffer_size);
				return NULL;
			}

			connection->read_buffer.ptr = new_buffer;
			connection->read_buffer.size = new_buffer_size;
			bytes_available = connection->read_buffer.size - connection->read_buffer_position;
		}

		bytes_read = read(connection->fd, connection->read_buffer.ptr + connection->read_buffer_position, bytes_available);
		if (bytes_read > 0) {
			connection->read_buffer_position += bytes_read;
			productive = true;
		}
		log_debug(_debug_log, "%s: read returned %zd, requested %zu\n", connection->socket->verbose_log_name, bytes_read, bytes_available);
	} while (bytes_read > 0);

	return (errno == EAGAIN || errno == EWOULDBLOCK) && productive;
}

#define FMT_PAD (256)

/* configure the device baud rate, 8N1 */
void _configure_device(struct dpcsock *sock)
{
	/* setup the argument list. FIXME: this was painfully
	 * constructed to match exactly what minicom does on CentOS while
	 * trying to isolate palladium clocking issues. We can probably get
	 * by with a much simpler string. (sane -echo?)
	 */
	char *cmdfmt  = "stty -F %s %s sane -echo -onlcr -icrnl crtscts "
			"-brkint -echoctl -echoe -echok -echoke -icanon -iexten "
			"-imaxbel -isig -opost ignbrk time 5 cs8 hupcl -clocal";
	char cmd[strlen(cmdfmt) + FMT_PAD];
	int r;

	assert(sock->mode == SOCKMODE_DEV);

	/* if the user wants to rock the existing setup */
	if (!_do_device_init) {
		log_info("skipping UART device configuration\n");
		return;
	}

	/* make sure we can actually fit the string */
	if (strlen(sock->socket_name) + strlen(_baudrate) + 1 >= FMT_PAD) {
		log_error("stty arguments too long\n");
		exit(1);
	}

	/* make the string */
	snprintf(cmd, strlen(cmdfmt) + FMT_PAD, cmdfmt,
		 sock->socket_name, _baudrate);

	log_info("Executing command to configure device: %s\n", cmd);

	r = system(cmd);

	if (r) {
		log_error("error configuring UART with stty\n");
		exit(1);
	}
}

bool dpcsocket_init(struct dpcsock *sock)
{
	assert(sock != 0);

	/* if we're running a device, make sure we configure it */
	if (sock->mode == SOCKMODE_DEV)
		_configure_device(sock);

	if (sock->server) {
		/* setup the server socket*/
		log_info("connecting server socket\n");
		_listen_sock_init(sock);
	}

#ifdef WITH_LIBFUNQ
	if(sock->mode == SOCKMODE_FUNQ) {
		sock->funq_handle = bin_ctl_init_dpc(sock->socket_name, _debug_log);
		return sock->funq_handle != NULL;
	}
#endif

	return true;
}

static void dpcsocket_destroy(struct dpcsock *sock)
{
#ifdef WITH_LIBFUNQ
	if(sock->mode == SOCKMODE_FUNQ) {
		bin_ctl_destroy(sock->funq_handle);
		free(sock->funq_handle);
	}
#endif
}

static void set_nonblocking_fd(int fd)
{
	if (fd < 0) return;
	int flags = fcntl(fd, F_GETFL, 0);
	if (fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
		log_error("can't set nonblock attribute to fd\n");
	}
}

struct dpcsock_connection *dpcsocket_new(struct dpcsock *sock)
{
	assert(sock != NULL);
	struct dpcsock_connection *connection =
		(struct dpcsock_connection *)calloc(1, sizeof(struct dpcsock_connection));

	if (!connection) {
		return NULL;
	}

	connection->binary_json_queue = dpcsh_ptr_queue_new();
	if (!connection->binary_json_queue) {
		free(connection);
		return NULL;
	}

	if (pthread_cond_init(&connection->data_available, NULL) != 0 ||
		  pthread_mutex_init(&connection->nvme_lock, NULL) != 0  ||
		  pthread_mutex_init(&connection->funq_queue_lock, NULL) != 0) {
		log_error("pthread cond and lock error");
		free(connection);
		return NULL;
	}

	connection->socket = sock;
	return connection;
}

bool switch_to_binary(int fd)
{
	const char *switch_cmd = "{\"verb\":\"encoding_binary_json\", \"args\":[], \"tid\":0}\n";
	return write(fd, switch_cmd, strlen(switch_cmd)) == strlen(switch_cmd);
}

bool dpcsocket_open(struct dpcsock_connection *connection)
{
	static size_t nvme_session_counter = 0;

	if (connection == NULL) return false;

	struct dpcsock *sock = connection->socket;
	connection->encoding = PARSE_BINARY_JSON;

	if (sock->server) {
		log_debug(_debug_log, "Listening\n");
		connection->fd = accept(sock->listen_fd, NULL, NULL);
		connection->encoding = PARSE_JSON;
		set_nonblocking_fd(connection->fd);
		return true;
	}

	if (sock->mode == SOCKMODE_NVME) {
		connection->nvme_seq_num = 0;
		connection->nvme_write_done = true;
		connection->nvme_session_id = (0xFFFF & (nvme_session_counter++)) + ((0xFFFF & getpid()) << 16);
		log_debug(_debug_log, "NVMe session id = %" PRIu32 "\n", connection->nvme_session_id);
		return true;
	}

#ifdef WITH_LIBFUNQ
	if (sock->mode == SOCKMODE_FUNQ) {
		connection->funq_connection = bin_ctl_open_connection(sock->funq_handle);
		if (!connection->funq_connection) {
			return false;
		}
	}
#endif

	/* unused == no-op */
	if (sock->mode == SOCKMODE_TERMINAL) {
		connection->fd = STDIN_FILENO; /* give it a real FD */
		connection->encoding = PARSE_TEXT;
	}

	if (sock->mode == SOCKMODE_DEV) {
		connection->fd = open(sock->socket_name, O_RDWR | O_NOCTTY);
		if (connection->fd < 0)
			perror("open");
	}

	if (sock->mode == SOCKMODE_UNIX) {
		connection->fd = _open_sock_unix(sock->socket_name);
	}

	if (sock->mode == SOCKMODE_IP) {
		connection->fd = _open_sock_inet(sock->socket_name, sock->port_num);
	}

	if (connection->fd > 0) {
		set_nonblocking_fd(connection->fd);
	}

	if (sock->dpcsh_connection) {
		return switch_to_binary(connection->fd);
	}

	/* connection->fd < 0 in the case of failure*/
	return true;
}

void dpcsocket_close(struct dpcsock_connection *connection)
{
	if (connection == NULL) return;

	connection->closing = true;

	if (connection->socket->mode != SOCKMODE_NVME && connection->socket->mode != SOCKMODE_FUNQ) {
		close(connection->fd);
	}

#ifdef WITH_LIBFUNQ
	if (connection->socket->mode == SOCKMODE_FUNQ) {
		if (!bin_ctl_close_connection(connection->funq_connection)) {
			perror("bin_ctl_close_connection");
		}
		pthread_cond_signal(&connection->data_available);
	}
#endif

	if (connection->socket->mode == SOCKMODE_NVME) {
		pthread_cond_signal(&connection->data_available);
	}
}

void dpcsocket_delete(struct dpcsock_connection *connection)
{
	if (connection == NULL) return;

	dpcsh_ptr_queue_delete(connection->binary_json_queue);

	free(connection->read_buffer.ptr);
	free(connection);
}

static bool _read_enqueue(struct dpcsock_connection *connection)
{
	if (connection->socket->mode == SOCKMODE_FUNQ) {
		// handled asynchronously
		return true;
	}

	if (connection->socket->mode != SOCKMODE_NVME) {
		if (!_read_all_available_data_from_fd(connection)) return false;

		return _decode_jsons_from_buffer(connection);
	}

	pthread_mutex_lock(&connection->nvme_lock);
	log_debug(_debug_log, "NVME read\n");

	struct fun_ptr_and_size data = {};
	uint8_t *deallocate_ptr = NULL;
	data.size = _read_from_nvme(&data.ptr, &deallocate_ptr, connection);

	connection->nvme_data_written = false;
	pthread_mutex_unlock(&connection->nvme_lock);

	dpcsh_ptr_queue_enqueue(connection->binary_json_queue, data, deallocate_ptr);

	return true;
}

// ===============  PRETTY PRINTERS ===============

static struct fun_map *tid_to_context;
static struct fun_map *tid_to_pretty_printer;

void dpcsh_register_pretty_printer(uint64_t tid, void *context, pretty_printer_f pretty_printer)
{
	if (!tid_to_context) {
		tid_to_context = fun_map_create(NULL, 0, FUN_MAP_RAW64_NEG_OUTSIDER_CALLBACKS);
	}
	fun_map_add(tid_to_context, (fun_map_key_t)tid, (fun_map_value_t)context, true);
	if (!tid_to_pretty_printer) {
		tid_to_pretty_printer = fun_map_create(NULL, 0, FUN_MAP_RAW64_NEG_OUTSIDER_CALLBACKS);
	}
	fun_map_add(tid_to_pretty_printer, (fun_map_key_t)tid, (fun_map_value_t)pretty_printer, true);
}

void dpcsh_unregister_pretty_printer(uint64_t tid, void *context)
{
	if (tid_to_context) {
		fun_map_remove(tid_to_context, (fun_map_key_t)tid, NULL, NULL);
	}
	if (tid_to_pretty_printer) {
		fun_map_remove(tid_to_pretty_printer, (fun_map_key_t)tid, NULL, NULL);
	}
}

// ===============  RUN LOOP ===============

#ifdef WITH_LIBFUNQ
static bool _write_dequeue_funq(struct dpcsock_connection *dest,
			 struct dpcsock_connection *source)
{
	while (true) {
		size_t queue_size = dpcsh_ptr_queue_size(source->binary_json_queue);

		if (!queue_size) break;

		struct fun_ptr_and_size *head = dpcsh_ptr_queue_first(source->binary_json_queue);
		size_t sent = bin_ctl_send_batch(dest->funq_connection, head, queue_size);

		if (!sent && queue_size) {
			log_error("unable to send a batch with libfunq\n");
			return false;
		}
		log_debug(_debug_log, "sent a batch of %zu\n", sent);
		if (!dpcsh_ptr_queue_dequeue(source->binary_json_queue, sent)) {
			log_error("unable to dequeue\n");
			return false;
		}
	}
	return true;
}
#endif

static bool _write_dequeue_nvme(struct dpcsock_connection *dest,
			 struct dpcsock_connection *source)
{
	while (true) {
		size_t queue_size = dpcsh_ptr_queue_size(source->binary_json_queue);

		if (!queue_size) break;

		struct fun_ptr_and_size *head = dpcsh_ptr_queue_first(source->binary_json_queue);
		pthread_mutex_lock(&dest->nvme_lock);
		log_debug(_debug_log, "NVME write\n");
		dest->nvme_seq_num++;
		if (!_write_to_nvme(*head, dest)) {
			log_error("NVME write failed");
			pthread_mutex_unlock(&dest->nvme_lock);
			return false;
		}
		dest->nvme_data_written = true;
		pthread_cond_signal(&dest->data_available);
		pthread_mutex_unlock(&dest->nvme_lock);
		if (!dpcsh_ptr_queue_dequeue(source->binary_json_queue, 1)) {
			log_error("unable to dequeue\n");
			return false;
		}
	}
	return true;
}

static void _lock_queue_if_needed(struct dpcsock_connection *connection)
{
	if (connection->socket->mode == SOCKMODE_FUNQ) {
		pthread_mutex_lock(&connection->funq_queue_lock);
	}
}

static void _unlock_queue_if_needed(struct dpcsock_connection *connection)
{
	if (connection->socket->mode == SOCKMODE_FUNQ) {
		pthread_mutex_unlock(&connection->funq_queue_lock);
	}
}

static bool _wait_write_unlocked(struct dpcsock_connection *dest,
			 struct dpcsock_connection *source)
{
	int r;
	_unlock_queue_if_needed(source);

	do {
		fd_set fds;
		struct timeval tv;

		tv.tv_sec = 1;
		tv.tv_usec = 0;

		FD_ZERO(&fds);
		FD_SET(dest->fd, &fds);

		r = select(dest->fd+1, NULL, &fds, NULL, &tv);

		if (dest->closing) {
			_lock_queue_if_needed(source);
			return false;
		}

		if (r < 0) {
			perror("select");
			_lock_queue_if_needed(source);
			return false;
		}
	} while (r == 0);

	_lock_queue_if_needed(source);
	return true;
}

// We pass the sock INOUT in order to be able to reestablish a
// connection if the server went down and up
static bool _write_dequeue(struct dpcsock_connection *dest,
			 struct dpcsock_connection *source)
{

#ifdef WITH_LIBFUNQ
	if (dest->socket->mode == SOCKMODE_FUNQ) return _write_dequeue_funq(dest, source);
#endif
	if (dest->socket->mode == SOCKMODE_NVME) return _write_dequeue_nvme(dest, source);

	_lock_queue_if_needed(source);

	while (dpcsh_ptr_queue_size(source->binary_json_queue)) {
		struct fun_ptr_and_size current = *dpcsh_ptr_queue_first(source->binary_json_queue);

		struct fun_ptr_and_size write_buffer = _transcode(current, dest);
		size_t write_buffer_position = 0;

		do {
			if (!_write_to_fd(dest, write_buffer, &write_buffer_position)) {
				log_error("write error\n");
				_unlock_queue_if_needed(source);
				return false;
			}
		} while (write_buffer_position < write_buffer.size && _wait_write_unlocked(dest, source));

		if (write_buffer.ptr != current.ptr) free(write_buffer.ptr);

		if (!dpcsh_ptr_queue_dequeue(source->binary_json_queue, 1)) {
			log_error("unable to dequeue\n");
			_unlock_queue_if_needed(source);
			return false;
		}
	}

	_unlock_queue_if_needed(source);
	return true;
}

#ifdef WITH_LIBFUNQ
static void _recv_callback(struct fun_ptr_and_size response, void *context)
{
	struct dpcsock_connection *connection = (struct dpcsock_connection *)context;
	size_t position = 0;
	struct fun_ptr_and_size next;

	pthread_mutex_lock(&connection->funq_queue_lock);

	do {
		next.ptr = response.ptr + position;
		next.size = response.size - position;
		next.size = fun_json_binary_serialization_size(next.ptr, next.size);

		if (!next.size) {
			log_error("malformed json from FunOS at %zu of %zu\n", position, response.size);
			break;
		}

		if (!dpcsh_ptr_queue_enqueue(connection->binary_json_queue, next, response.ptr)) {
			log_error("can't enqueue the response\n");
		}

		position += next.size;
	} while (position < response.size);

	pthread_cond_signal(&connection->data_available);
	pthread_mutex_unlock(&connection->funq_queue_lock);
}
#endif

static void terminal_set_per_character(bool enable)
{
	/* enable per-character input for interactive input */
	static struct termios tios;
	tcgetattr(STDIN_FILENO, &tios);
	if (enable) {
		tios.c_lflag &= ~(ICANON | ECHO);
	} else {
		tios.c_lflag |= ICANON | ECHO;
	}
	tcsetattr(STDIN_FILENO, TCSANOW, &tios);
}

static bool _wait_cond_unlock(pthread_cond_t *cond, pthread_mutex_t *lock)
{
	int ret = pthread_cond_wait(cond, lock);
	if (ret) {
		log_error("failed to wait for new data, code = %d\n", ret);
		return false;
	}
	pthread_mutex_unlock(lock);
	return true;
}

// blocks until there is something to do. returns false on error
static bool _wait_read(struct dpcsock_connection *source)
{
	if (source->closing) return false;

	if (source->socket->mode == SOCKMODE_TERMINAL) return true;

	if (source->socket->mode == SOCKMODE_NVME) {
		pthread_mutex_lock(&source->nvme_lock);
		if (source->nvme_data_written) {
			pthread_mutex_unlock(&source->nvme_lock);
			return true;
		}
		return _wait_cond_unlock(&source->data_available, &source->nvme_lock);
	}

	if (source->socket->mode == SOCKMODE_FUNQ) {
		pthread_mutex_lock(&source->funq_queue_lock);
		if (dpcsh_ptr_queue_size(source->binary_json_queue)) {
			pthread_mutex_unlock(&source->funq_queue_lock);
			return true;
		}
		return _wait_cond_unlock(&source->data_available, &source->funq_queue_lock);
	}

	if (source->fd > 0) {
		int r;
		do {
			/* wait on our input(s) */
			fd_set fds;
			struct timeval tv;

			tv.tv_sec = 1;
			tv.tv_usec = 0;

			FD_ZERO(&fds);
			FD_SET(source->fd, &fds);

			r = select(source->fd+1, &fds, NULL, NULL, &tv);

			if (source->closing) return false;

			if (r < 0) {
				perror("select");
				return false;
			}
		} while (r == 0);

		return true;
	}

	return true;
}

static void _do_session(struct dpcsock_connection *dest,
	struct dpcsock_connection *source)
{
	if (source->socket->mode == SOCKMODE_TERMINAL) {
		/* enable per-character input for interactive input */
		terminal_set_per_character(true);
	}

	while (_wait_read(source)) {
		if (!_read_enqueue(source)) /* user ^D or connection closed*/
			break;

		if (!_write_dequeue(dest, source)) {
			log_error("error sending to %s\n", dest->socket->verbose_log_name);
			break;
		}
	}

	if (source->socket->mode == SOCKMODE_TERMINAL) {
		/* reset terminal */
		terminal_set_per_character(false);
	}
}

static void *_run_thread(void *args)
{
	void **connections = args;
	_do_session(connections[0], connections[1]);
	connections[2] = args; // setting this to a non-NULL
	return NULL;
}

static void close_connections(struct dpcsock_connection *funos, struct dpcsock_connection *cmd)
{
	dpcsocket_close(funos);
	dpcsocket_close(cmd);
}

static void delete_connections(struct dpcsock_connection *funos, struct dpcsock_connection *cmd)
{
	dpcsocket_delete(funos);
	dpcsocket_delete(cmd);
}

static void open_new_connections(struct dpcsock *funos_socket,
					struct dpcsock *cmd_socket,
					struct dpcsock_connection **funos, struct dpcsock_connection **cmd)
{
	*funos = dpcsocket_new(funos_socket);
	*cmd = dpcsocket_new(cmd_socket);

	if (!dpcsocket_open(*funos) || !dpcsocket_open(*cmd)) {
		log_error("unable to open connection");
	}

#ifdef WITH_LIBFUNQ
	if (funos_socket->mode == SOCKMODE_FUNQ) {
		if (!bin_ctl_register_receive_callback((*funos)->funq_connection, _recv_callback, *funos)) {
			log_error("can't register a callback for libfunq\n");
		}
	}
#endif
}

static void _finalize_worker(struct dpc_worker *worker, bool force_terminate)
{
	worker->used = false;

	if (force_terminate)
		close_connections(worker->in.args[0], worker->in.args[1]);

	pthread_join(worker->in.thread, NULL);
	pthread_join(worker->out.thread, NULL);

	if (!force_terminate)
		close_connections(worker->in.args[0], worker->in.args[1]);

	delete_connections(worker->in.args[0], worker->in.args[1]);
}

static void _start_thread(struct dpc_thread *t,
	struct dpcsock_connection *source, struct dpcsock_connection *dest)
{
	t->args[0] = source;
	t->args[1] = dest;
	t->args[2] = 0;
	pthread_create(&t->thread, NULL, _run_thread, t->args);
}

static void _add_worker(struct dpc_worker *workers, size_t max_workers,
	struct dpcsock_connection *funos, struct dpcsock_connection *cmd)
{
	for (size_t i = 0; i < max_workers; i++) {
		if (workers[i].used) {
			if (workers[i].in.args[2] || workers[i].out.args[2]) {
			// using this as an indicator of thread got terminated,
			// may give false-negatives, that are fine, but no false-positives
				_finalize_worker(workers + i, true);
				log_debug(_debug_log, "garbage-collected thread #%zu\n", i);
			}
		}
		if (!workers[i].used) {
			workers[i].used = true;
			_start_thread(&workers[i].in, funos, cmd);
			_start_thread(&workers[i].out, cmd, funos);
			log_debug(_debug_log, "added thread #%zu\n", i);
			return;
		}
	}
	log_error("out of connections\n");
	close_connections(funos, cmd);
	delete_connections(funos, cmd);
}

static void _wait_finalize_workers(struct dpc_worker *workers, size_t max_workers)
{
	for (size_t i = 0; i < max_workers; i++) {
		if (workers[i].used) {
			_finalize_worker(workers + i, false);
			log_debug(_debug_log, "joined thread #%zu\n", i);
		}
	}
}

static void _do_interactive(struct dpcsock *funos_socket,
			    struct dpcsock *cmd_socket)
{
	struct dpcsock_connection *funos, *cmd;
	struct dpc_worker workers[MAX_CLIENTS_THREADS] = {};
	do {
		open_new_connections(funos_socket, cmd_socket, &funos, &cmd);
		if (!funos || !cmd || cmd->fd < 0) {
			close_connections(funos, cmd);
			delete_connections(funos, cmd);
			break;
		}
		_add_worker(workers, MAX_CLIENTS_THREADS, funos, cmd);
	} while (cmd_socket->server);
	_wait_finalize_workers(workers, MAX_CLIENTS_THREADS);
}

// Return true if execution proceeded normally, false on any error
static bool _do_cli(int argc, char *argv[],
		    struct dpcsock *funos_socket,
		    struct dpcsock *cmd_socket, int startIndex)
{
	bool ok = false;
	size_t bufsize = 1; // 1 for the terminating zero
	for (int i = startIndex; i < argc; i++) {
		bufsize += strlen(argv[i]) + 1; // +1 for the separator space
	}
	char *buf = malloc(bufsize);
	if (!buf) {
		log_error("failed to allocate command buffer of size %zu", bufsize);
		goto malloc_fail;
	}

	int n = 0;
	struct dpcsock_connection *funos, *cmd;
	open_new_connections(funos_socket, cmd_socket, &funos, &cmd);

	if (!funos || !cmd || cmd->fd < 0) {
		log_error("can't open connections\n");
		goto connect_fail;
	}

	for (int i = startIndex; i < argc; i++) {
		n += snprintf(buf + n, bufsize - n, "%s ", argv[i]);
		log_debug(_debug_log, "buf=%s n=%d\n", buf, n);
	}

	size_t len = strlen(buf);

	buf[len - 1] = 0;	// trim the last space

	cmd->read_buffer.ptr = (uint8_t *)buf;
	cmd->read_buffer.size = len;
	cmd->read_buffer_position = len;

	log_debug(_debug_log, ">> single cmd [%s] len=%zd\n", buf, len);
	ok = _decode_jsons_from_buffer(cmd);
	ok = ok && _write_dequeue(funos, cmd);

	ok = ok && _wait_read(funos);
	ok = ok && _read_enqueue(funos);
	ok = ok && _write_dequeue(cmd, funos);

connect_fail:
	close_connections(funos, cmd);
	delete_connections(funos, cmd);
malloc_fail:
	return ok;
}

/** argument parsing **/

/* help for port numbers */
static uint16_t opt_portnum(char *optarg, uint16_t dflt)
{
	if (optarg == NULL)
		return dflt;

	return strtoul(optarg, NULL, 0);
}

static uint16_t opt_num(char *optarg, uint16_t dflt)
{
	return opt_portnum(optarg, dflt);
}

/* helper for socket file names */
static char *opt_sockname(char *optarg, char *dflt)
{
	if (optarg == NULL)
		return dflt;

	return optarg;
}


/* options descriptor */
static struct option longopts[] = {
	{ "help",            no_argument,       NULL, 'h' },
	{ "base64_srv",      optional_argument, NULL, 'B' },
	{ "base64_sock",     optional_argument, NULL, 'b' },
	{ "dev",             required_argument, NULL, 'D' },
	{ "inet_sock",       optional_argument, NULL, 'i' },
	{ "connect_dpc",     required_argument, NULL, 'c' },
	{ "unix_sock",       optional_argument, NULL, 'u' },
// DPC over NVMe is needed only in Linux
#ifdef __linux__
	{ "pcie_nvme_sock",  optional_argument, NULL, 'p' },
#endif //__linux__
#ifdef WITH_LIBFUNQ
	{ "libfunq_sock",    optional_argument, NULL, 'q' },
#endif
	{ "tcp_proxy",       optional_argument, NULL, 'T' },
	{ "text_proxy",      optional_argument, NULL, 'T' },
	{ "unix_proxy",      optional_argument, NULL, 't' },
// inet interface restriction needed only in Linux,
// current implementation doesn't work on Mac
#ifdef __linux__
	{ "inet_interface",  required_argument, NULL, 'I' },
#endif //__linux_
	{ "nocli",           no_argument,       NULL, 'n' },
	{ "nocli-quiet",     no_argument,       NULL, 'Q' },
	{ "oneshot",         no_argument,       NULL, 'S' },
	{ "manual_base64",   no_argument,       NULL, 'N' },
	{ "no_dev_init",     no_argument,       NULL, 'X' },
	{ "no_flow_control", no_argument,       NULL, 'F' },
	{ "baud",            required_argument, NULL, 'R' },
	{ "legacy_b64",      no_argument,       NULL, 'L' },
	{ "verbose",         no_argument,       NULL, 'v' },
	{ "debug",           no_argument,       NULL, 'd' },
	{ "log",             required_argument, NULL, 'l' },
	{ "version",         no_argument,       NULL, 'V' },
	{ "retry",           optional_argument, NULL, 'Y' },
#ifdef __linux__
	{ "nvme_cmd_timeout", required_argument, NULL, 'W' },
#endif //__linux__

	/* end */
	{ NULL, 0, NULL, 0 },
};


static void usage(const char *argv0)
{
	printf("usage: %s [<mode> [option]]", argv0);
	printf("       by default connect over TCP\n");
	printf("       -h, --help                    this text\n");
	printf("       -D, --dev[=device]            open device and read/write base64 to FunOS UART\n");
	printf("       -F, --no_flow_control         no flow control in uart. send char one by one with delay\n");
	printf("       -B, --base64_srv[=port]       listen as a server port on IP using base64 (dpcuart to qemu)\n");
	printf("       -b, --base64_sock[=port]      connect as a client port on IP using base64 (dpcuart to qemu)\n");
	printf("       -i, --inet_sock[=port]        connect as a client port over IP\n");
	printf("       -c, --connect_dpc[=host:port|=sockname] connect as a client to another dpcsh\n");
	printf("       -u, --unix_sock[=sockname]    connect as a client port over unix sockets\n");
// DPC over NVMe is needed only in Linux
#ifdef __linux__
	printf("       -p, --pcie_nvme_sock[=sockname] connect as a client port over nvme pcie device\n");
#endif //__linux__
#ifdef WITH_LIBFUNQ
	printf("       -q, --libfunq_sock[=sockname] connect as a client port over libfunq pcie device, put \"auto\" for auto-discover\n");
#endif
	printf("       -H, --http_proxy[=port]       listen as an http proxy\n");
	printf("       -T, --tcp_proxy[=port]        listen as a tcp proxy\n");
	printf("       -T, --text_proxy[=port]       same as \"--tcp_proxy\"\n");
	printf("       -t, --unix_proxy[=port]       listen as a unix proxy\n");
#ifdef __linux__
	printf("       -I, --inet_interface=name     listen only on <name> interface\n");
#endif // __linux__
	printf("       -n, --nocli                   issue request from command-line arguments and terminate\n");
	printf("       -Q, --nocli-quiet             issue request from command-line arguments and terminate, only print response\n");
	printf("       -S, --oneshot                 don't reconnect after command side disconnect\n");
	printf("       -N, --manual_base64           just translate base64 back and forward\n");
	printf("       -X, --no_dev_init             don't init the UART device, use as-is\n");
	printf("       -R, --baud=rate               specify non-standard baud rate (default=" DEFAULT_BAUD ")\n");
	printf("       -L, --legacy_b64              support old-style base64 encoding, despite issues\n");
	printf("       -v, --verbose                 log all json transactions in proxy mode\n");
	printf("       -d, --debug                   print debugging information\n");
	printf("       -l, --log[=filename]          log to a file\n");
	printf("       -Y, --retry[=N]               retry every seconds for N seconds for first socket connection\n");
	printf("       -V, --version                 display version info and exit\n");
#ifdef __linux__
	printf("       --nvme_cmd_timeout=timeout specify cmd timeout in ms (default=" DEFAULT_NVME_CMD_TIMEOUT_MS ")\n");
#endif //__linux__

}

enum mode {
	MODE_INTERACTIVE,  /* commmand-line (ish) */
	MODE_PROXY,        /* proxy commands from a socket */
	MODE_NOCONNECT,    /* no connection to FunOS */
};

/** entrypoint **/
int main(int argc, char *argv[])
{
	enum mode mode = MODE_INTERACTIVE; /* default user control */
	bool one_shot = false;  /* run a single command and terminate */
	int ch, first_unknown = -1;
	struct dpcsock funos_sock = {0}; /* connection to FunOS */
	struct dpcsock cmd_sock = {0};   /* connection to commanding agent */
	bool autodetect_input_device = true;
	bool cmd_timeout_is_set = false;
	char detected_nvme_device_name[64]; /* when no input device is specified */
	int log_fd = -1;

	// otherwise it will be killed on unsuccessful write to a pipe
	signal(SIGPIPE, SIG_IGN);

	srand(time(NULL));
	dpcsh_path = argv[0];
	dpcsh_load_macros();
	register_csr_macro();
	register_file_commands();

	// help should list both local and distant commands
	fun_commander_register_help_command();

	/* general flow of dpcsh:
	 *
	 * We're a conduit between FunOS and something else. The
	 * connection to FunOS may be via UNIX or TCP socket (as a
	 * client), UNIX or TCP socket (as a server), by hand, or
	 * possibly via a direct connection to a serial device. The
	 * other end may be a proxy via TCP, UNIX sockets, or the
	 * console for manual input. There's some level of processing
	 * in between those two.
	 *
	 * So, based on the command-line configure generic sockets at
	 * either end (or not), and then call the specified handler to
	 * deal. For legacy reasons, these setups are not fully
	 * flexible.
	 *
	 * As usual for command-line utilities, if you specify
	 * multiple conflicting command-line arguments, the last one
	 * probably wins.
	 */

	/* default command connection is console (so socket disabled) */
	cmd_sock.mode = SOCKMODE_TERMINAL;
	cmd_sock.retries = UINT32_MAX;

	while ((ch = getopt_long(argc, argv,
#ifdef __linux__
				 "hB::b::D:i::c::u::p::q::T::t::I:nQSNXFR:LvdVYW",
#else
				 "hB::b::D:i::c::u::T::t::nQSNXFR:LvdVY",
#endif
				 longopts, NULL)) != -1) {

		switch(ch) {
		/** help **/
		case 'h':
			usage(argv[0]);
			exit(0);

		/** mode parsing **/

		case 'b':  /* base64 client */

			/* run as base64 mode for dpcuart */
			funos_sock.base64 = true;
			funos_sock.mode = SOCKMODE_IP;
			funos_sock.server = false;
			funos_sock.port_num = opt_portnum(optarg,
							  DPC_B64_PORT);
			autodetect_input_device = false;
			break;

		case 'B':  /* base64 server */

			/* run as base64 mode for dpcuart */
			funos_sock.base64 = true;
			funos_sock.mode = SOCKMODE_IP;
			funos_sock.server = true;
			funos_sock.port_num = opt_portnum(optarg,
							  DPC_B64SRV_PORT);
			autodetect_input_device = false;
			break;
		case 'D':  /* base64 device (pty/tty) */

			/* run as base64 mode for dpcuart */
			funos_sock.base64 = true;
			funos_sock.mode = SOCKMODE_DEV;
			funos_sock.socket_name = opt_sockname(optarg,
							      "/unknown");
			autodetect_input_device = false;
			break;
		case 'i':  /* inet client */

			/* in case this got stamped over... */
			funos_sock.mode = SOCKMODE_IP;
			funos_sock.server = false;
			funos_sock.socket_name = opt_sockname(optarg,
							  DPC_PORT_STR);
			autodetect_input_device = false;
			break;
		case 'c':  /* inet dpc client */

			funos_sock.dpcsh_connection = true;
			funos_sock.mode = strchr(optarg, ':') == NULL ? SOCKMODE_UNIX : SOCKMODE_IP;
			funos_sock.server = false;
			funos_sock.socket_name = optarg;
			autodetect_input_device = false;
			break;
		case 'u':  /* unix domain client */

			funos_sock.mode = SOCKMODE_UNIX;
			cmd_sock.server = false;
			funos_sock.socket_name = opt_sockname(optarg,
							      SOCK_NAME);
			autodetect_input_device = false;
			break;
// DPC over NVMe is needed only in Linux
#ifdef __linux__
		case 'p':
			funos_sock.mode = SOCKMODE_NVME;
			funos_sock.server = false;
			funos_sock.socket_name = opt_sockname(optarg,
							      NVME_DEV_NAME);
			autodetect_input_device = false;
			break;
#endif //__linux__
#ifdef WITH_LIBFUNQ
		case 'q':
			funos_sock.mode = SOCKMODE_FUNQ;
			funos_sock.server = false;
			funos_sock.socket_name = opt_sockname(optarg,
							      BIN_CTL_DEFAULT_DEVICE);
			autodetect_input_device = false;
			break;
#endif
		case 'T':  /* TCP proxy */

			cmd_sock.mode = SOCKMODE_IP;
			cmd_sock.server = true;
			cmd_sock.port_num = opt_portnum(optarg,
							DPC_PROXY_PORT);

			mode = MODE_PROXY;
			break;

		case 't':  /* unix proxy */

			cmd_sock.mode = SOCKMODE_UNIX;
			cmd_sock.server = true;
			cmd_sock.socket_name = opt_sockname(optarg,
							    PROXY_NAME);

			mode = MODE_PROXY;

			break;

		/** other options **/
#ifdef __linux__
		case 'I':
			cmd_sock.eth_name = optarg;
			break;
#endif // __linux__
		case 'Q':  /* "nocli-quiet" -- run one command and exit */
			_nocli_script_mode = true;
		case 'n':  /* "nocli" -- run one command and exit */
		case 'S':  /* "oneshot" -- run one connection and exit */
			one_shot = true;
			break;
		case 'F':  /* "no_flow_control" -- run without flow control */
			_no_flow_control = true;
			break;
		case 'N':  /* manual base64 mode -- drive a UART by hand */

			funos_sock.base64 = true;
			funos_sock.server = false;
			funos_sock.loopback = true;
			funos_sock.mode = SOCKMODE_TERMINAL;
			mode = MODE_NOCONNECT;
			autodetect_input_device = false;
			break;
		case 'X':  /* "no_dev_init" -- don't init the uartr */
			_do_device_init = false;
			break;
		case 'R':  /* "baud" -- set baud rate for stty */
			_baudrate = optarg;
			if (atoi(_baudrate) <= 0) {
				printf("baud rate must be a positive decimal integer\n");
				usage(argv[0]);
				exit(1);
			}
			break;

		case 'L':
			_legacy_b64 = true;
			break;

		case 'v':  /* "verbose" -- log all json as it goes by */
			_verbose_log = true;
			break;

		case 'V':  /* "version" -- print version and quit */
			_print_version();
			exit(0);
			break;

		case 'd':
			_debug_log = true;
			break;

		case 'l':
			log_fd = open(optarg, O_CREAT|O_APPEND|O_SYNC|O_WRONLY, 0644);
			if (log_fd == -1
			|| dup2(log_fd, fileno(stdout)) == -1
			|| dup2(log_fd, fileno(stderr)) == -1) {
				printf("failed to open a file or redirect standard output\n");
				exit(1);
			}
			setvbuf(stdout, NULL, _IOLBF, 0);
			break;

		case 'Y':  /* retry=N */

			connect_retries = opt_num(optarg, RETRY_NOARG);

			break;
#ifdef __linux__
		case 'W':  /* "timeout" -- set timeout for cmd */
			funos_sock.cmd_timeout = atoi(optarg);
			if (funos_sock.cmd_timeout <= 0) {
				printf("timeout must be a positive decimal integer\n");
				usage(argv[0]);
				exit(1);
			}
			cmd_timeout_is_set = true;
			break;
#endif //__linux__

		default:
			usage(argv[0]);
			exit(1);
		}

		if (first_unknown != -1)
			break;
	}

	if (autodetect_input_device) {
		/* check whether NVMe connection to DPU is available */
		/* DPC over NVMe will work only in Linux */
		/* In macOS, libfunq is used */

		/* In macOS, always returns false */
		bool nvme_dpu_found = find_nvme_dpu_device(detected_nvme_device_name,
							sizeof(detected_nvme_device_name));

		/* In Linux, use NVMe as default if present */
		if (nvme_dpu_found) {
			funos_sock.mode = SOCKMODE_NVME;
			funos_sock.socket_name = detected_nvme_device_name;
			funos_sock.server = false;
			funos_sock.retries = UINT32_MAX;
			if (!cmd_timeout_is_set) {
				funos_sock.cmd_timeout = atoi(DEFAULT_NVME_CMD_TIMEOUT_MS);
			}
		}
		/* Use libfunq otherwise */
		else {
			/* default connection to FunOS posix simulator dpcsock */
			funos_sock.mode = SOCKMODE_IP;
			funos_sock.server = false;
			funos_sock.socket_name = DPC_PORT_STR;
			funos_sock.retries = UINT32_MAX;
		}
	}

	/* sanity check */
	if (cmd_sock.eth_name && cmd_sock.mode != SOCKMODE_IP) {
		printf("Interface name is valid for IP proxy modes only\n");
		exit(1);
	}

	/* make an announcement as to what we are */
	if (!_nocli_script_mode)
		log_debug(_debug_log, "FunOS Dataplane Control Shell");

	switch (mode) {
	case MODE_INTERACTIVE:
		/* do nothing */
		break;
	case MODE_PROXY:
		log_debug(_debug_log, "socket proxy mode");
		break;
	case MODE_NOCONNECT:
		log_debug(_debug_log, "manual base64 mode");
		break;
	}

	printf("\n");

	_print_version(); /* always print this for the logs */

	/* start by initializing the sockets */
	if (!dpcsocket_init(&funos_sock) || !dpcsocket_init(&cmd_sock)) {
		log_error("can't initialize connections\n");
		exit(1);
	}

	funos_sock.verbose_log_name = "FunOS";
	cmd_sock.verbose_log_name = "client";

	switch(mode) {
	case MODE_PROXY:
		if (one_shot)
			cmd_sock.retries = 1;
		_do_interactive(&funos_sock, &cmd_sock);
		break;
	case MODE_INTERACTIVE:
	case MODE_NOCONNECT: {
		if (one_shot) {

			bool ok = _do_cli(argc, argv, &funos_sock, &cmd_sock, optind);

			if (!ok) {
				// We got a JSON error back, let's return an error code
				exit(EINVAL);
			}
		} else {
			_do_interactive(&funos_sock, &cmd_sock);
		}
	}

	}

	dpcsocket_destroy(&funos_sock);
	dpcsocket_destroy(&cmd_sock);
	if (log_fd != -1) close(log_fd);
	return 0;
}
