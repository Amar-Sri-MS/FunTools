/*
 *  dpcsh.c
 *
 *  Copyright © 2017-2018 Fungible. All rights reserved.
 */

/* test dpcsock functionality */

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
#include <sys/un.h>
#include <termios.h>          	// termios, TCSANOW, ECHO, ICANON
#include <sys/types.h>
#include <signal.h>          	// termios, TCSANOW, ECHO, ICANON
#include <pthread.h>
#include <netinet/in.h>		// TCP socket
#include <arpa/inet.h>
#include <sys/select.h>
#include <sys/stat.h>
#include <time.h>

#include "dpcsh.h"
#include "dpcsh_nvme.h"
#include "csr_command.h"

#include <FunSDK/utils/threaded/fun_map_threaded.h>
#include <FunSDK/services/commander/fun_commander.h>
#include <FunSDK/services/commander/fun_commander_basic_commands.h>
#include <FunSDK/utils/threaded/fun_malloc_threaded.h>
#include <FunSDK/utils/common/base64.h>
#include <FunSDK/platform/include/platform/utils_platform.h>

#define SOCK_NAME	"/tmp/funos-dpc.sock"      /* default FunOS socket */
#define PROXY_NAME      "/tmp/funos-dpc-text.sock" /* default unix proxy name */
#define DPC_PORT        40220   /* default FunOS port */
#define DPC_PROXY_PORT  40221   /* default TCP proxy port */
#define DPC_B64_PORT    40222   /* default dpcuart port in qemu */
#define DPC_B64SRV_PORT 40223   /* default dpcuart listen port */
#define HTTP_PORTNO     9001    /* default HTTP listen port */
#define NO_FLOW_CTRL_DELAY_USEC	10000	/* no flow control delay in usec */

enum parsingmode {
	PARSE_UNKNOWN, /* bug trap */
	PARSE_TEXT,    /* friendly command-line parsing (and legacy proxy mode) */
	PARSE_JSON,    /* just proxy json */
};

static enum parsingmode _parse_mode = PARSE_UNKNOWN;

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
static uint32_t dpcsh_session_id;
static uint32_t cmd_seq_num;

/* whether to log all json */
static bool _verbose_log = false;

/* cmd timeout, use driver default timeout */
#define DEFAULT_NVME_CMD_TIMEOUT_MS "0"

/* socket connect retry parameters */
#define RETRY_DEFAULT (15)  /* retry for 15 seconds */
#define RETRY_NOARG   (15)
static uint16_t connect_retries = RETRY_DEFAULT;

// We stash argv[0]
const char *dpcsh_path;

static inline void _setnosigpipe(int const fd)
{
#ifdef __APPLE__
	int yes = 1;
	(void)setsockopt(fd, SOL_SOCKET, SO_NOSIGPIPE, &yes, sizeof(yes));
#else
	/* unfortunately Linux does not support SO_NOSIGPIPE... */
	signal(SIGPIPE, SIG_IGN);
#endif
}

static void _print_version(void)
{
	/* single line version when everything matches up */
	printf("FunSDK version %s, branch: %s\n",
	       FunSDK_version, branch_version);

	/* extra logging when things are built a little weird */
	if (strcmp(FunSDK_version, platform_SDK_version) != 0) {
		printf("libfunclient FunSDK version %s, branch: %s\n",
		       platform_SDK_version, platform_branch_version);
	}
}

/* quiet logging -- just log events for proxy mode to avoid print
 * sensitive information like crypto keys. For now ignore the json
 * arg, but we could do something useful like trying to fish the
 * verb out of it
 */
enum log_event {
	LOG_RX,
	LOG_TX,
	LOG_RX_LOCAL,
	LOG_RX_OLD,
	LOG_RX_ERROR,
};

static void _quiet_log(enum log_event mode, const struct fun_json *json)
{
	const char *msg = NULL;

	switch (mode) {
	case LOG_RX:
		msg = "RX";
		break;
	case LOG_TX:
		msg = "TX";
		break;
	case LOG_RX_LOCAL:
		msg = "RX local";
		break;
	case LOG_RX_OLD:
		msg = "RX old";
		break;
	case LOG_RX_ERROR:
		msg = "RX error";
		break;
	default:
		msg = "unknown mystery";
		break;
	};

	printf("dpc %s event\n", msg);
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
				printf("error allocating input line buffer\n");
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
			*nbytes = len;
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
static int _open_sock_inet(uint16_t port)
{
	int sock = 0;
	int r, tries = 0;
	struct sockaddr_in serv_addr;

	do {
		if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
			printf("\n Socket creation error \n");
			return sock;
		}
		_setnosigpipe(sock);

		memset(&serv_addr, '0', sizeof(serv_addr));

		serv_addr.sin_family = AF_INET;
		serv_addr.sin_port = htons(port);

		// Convert IPv4 and IPv6 addresses from text to binary form
		if(inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)<=0) {
			printf("\nInvalid address/ Address not supported \n");
			return -1;
		}

		if (tries > 0) {
			printf("connect error, retry %d\n", tries);
			sleep(1);
		}

		r = connect(sock, (struct sockaddr *)&serv_addr,
			    sizeof(serv_addr));
		tries++;
	} while ((r < 0) && (tries < connect_retries));

	if (r < 0) {
		printf("*** Can't connect\n");
		perror("connect");
		exit(1);
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

	_setnosigpipe(sock);
	struct sockaddr_un server = { .sun_family = AF_UNIX };
	strcpy(server.sun_path, name);
	do {
		if (tries > 0) {
			printf("connection fail, retry %d\n", tries);
			sleep(1);
		}

		r = connect(sock, (struct sockaddr *)&server, sizeof(server));
		tries++;
	} while(r && (tries < connect_retries));

	if (r) {
		printf("*** Can't connect: %d\n", r);
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

	/* if we already have a listen sock, just return */
	if (sock->listen_fd > 0)
		return;

	if (sock->mode == SOCKMODE_UNIX) {
		/* create a server socket */
		sock->listen_fd = socket(AF_UNIX, SOCK_STREAM, 0);
		assert(sock->listen_fd > 0);

		/* set socket parameters */
		printf("Publishing %s\n", sock->socket_name);

		local_unix.sun_family = AF_UNIX;

		snprintf(local_unix.sun_path,
			 sizeof(local_unix.sun_path), "%s", sock->socket_name);
		if ((r = unlink(local_unix.sun_path))
		    && (errno != ENOENT)) {
			printf("failed to remove existing socket file: %s\n",
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

	/* still haven't accepted anything */
	sock->fd = -1;
}

void _listen_sock_accept(struct dpcsock *sock)
{
	struct sockaddr_in clientaddr;
	socklen_t clientlen = sizeof(clientaddr);

	/* just do an accept */
	sock->fd = accept(sock->listen_fd, (void*) &clientaddr, &clientlen);
}

/* low-level base64+socket routines */
bool _base64_write(struct dpcsock *sock, const uint8_t *buf, size_t nbyte)
{
	/* keep it simple */
	size_t b64size = nbyte * 2 + 1; /* big to avoid rounding issues */
	char *b64buf = malloc(b64size);
	int r;
	int fd = sock->fd;

	if (b64buf == NULL) {
		printf("**** out of memory allocating output b64 buffer\n");
		exit(1);
	}

	r = base64_encode(b64buf, b64size, (void*) buf, nbyte);
	if (r <= 0) {
		printf("**** error encoding base64\n");
		return false;
	}

	// printf("[dpcsh] sending b64 %s\n", b64buf);

	/* send it */
	if (_no_flow_control) {
		int num_buf = strlen(b64buf);
		for (int i = 0; i < num_buf; i++) {
			r = write(fd, &b64buf[i], 1);
			if (r < 0)
				return false;
			fsync(fd);
			usleep(NO_FLOW_CTRL_DELAY_USEC);
		}
	} else {

		r = write(fd, b64buf, strlen(b64buf));

		if (r < 0)
			return false;
	}

	/* frame it with a newline */
	if (write(fd, "\n", 1) < 0)
		return false;

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
		printf("couldn't allocate input buffer\n");
		exit(1);
	}

	*size = base64_decode(binbuf, nbytes, line);

	if (*size <= 0) {
		free(binbuf);
		binbuf = NULL;
	}

	return binbuf;
}

struct fun_json *_buffer2json(const uint8_t *buffer, size_t max)
{
	struct fun_json *json = NULL;
	size_t r;

	if (!buffer)
		return NULL;

	r = fun_json_binary_serialization_size(buffer, max);
	if (r <= max) {
		json = fun_json_create_from_binary_with_options(buffer,
				r,
				true);
	}

	return json;
}


/* read a line of input from the fd */
#define BUF_SIZE (1024)
static char *_read_a_line(struct dpcsock *sock, ssize_t *nbytes)
{
	char *buf = NULL;
	size_t size = 0, pos = 0;
	bool echo = false;
	int fd = sock->fd;
	int r;

	*nbytes = -1; /* assume error */

	if ((sock->mode == SOCKMODE_TERMINAL) && !sock->base64) {
		/* fancy pants line editor on stdin */
		buf = getline_with_history(nbytes);
		return buf;
	}

	if ((sock->mode == SOCKMODE_TERMINAL) && sock->base64) {
		fd = STDIN_FILENO; /* lldb fails if you use stderr
				    * #emojieyeroll
				    */
		echo = true;
	}

	do {
		/* check buffer hasn't overflowed */
		if (pos == size) {
			size += BUF_SIZE;
			buf = realloc(buf, size);

			if (buf == NULL) {
				printf("couldn't allocate input buffer\n");
				exit(1);
			}
		}

		/* read a byte */
		errno = 0;
		r = read(fd, &buf[pos], 1);

		if (r <= 0) {
			printf("**** remote hung up / error: %d %d %s\n",
			       r, errno, strerror(errno));
			free(buf);
			if (sock->mode != SOCKMODE_NVME) {
				close(sock->fd);
			}
			*nbytes = 0;
			sock->fd = -1;
			return NULL;
		}

		/* ignore CR */
		if (buf[pos] == '\r')
			continue;

		/* if this is a fake socket, echo it */
		if (echo) {
			char c = buf[pos];
			if (!(isprint(c) || isspace(c)))
				c = '?';
			printf("%c", c);
			fflush(stdout); // xxx
		}

		/* newline == end */
		if (buf[pos] == '\n')
			buf[pos] = '\0';

		/* next character */
		pos++;

	} while(buf[pos-1] != '\0');

	if (pos >= 1) {
		*nbytes = (ssize_t) pos - 1;
	} else {
		/* sometimes we get truncated lines? */
		*nbytes = 0;
		buf[0] = '\0';
	}

	return buf;
}

/* read a line of input from the fd and try to decode it (FunOS
 * resonse side only)
 */
static uint8_t *_base64_get_buffer(struct dpcsock *sock,
				   ssize_t *nbytes, bool retry)
{
	char *buf = NULL, *b64buf = NULL;
	uint8_t *binbuf = NULL;
	ssize_t r;
	bool badline;

do_retry:

	/* so far so good */
	badline = false;

	/* read the input */
	buf = _read_a_line(sock, nbytes);

	if (!buf)
		return NULL;

	/* make sure it's NUL terminated for error conditinos in which
	 * funos dropped out without sendng a full line
	 */
	buf[*nbytes] = '\0';

	/* make sure there's a header on it */
	b64buf = _is_b64json_line(buf);
	if (b64buf == NULL) {
		/* not b64json */
		badline = true;
	}

	if (!badline) {
		/* now we have a buffer, decode it.*/
		binbuf = _b64_to_bin(b64buf, &r);

		if (binbuf == NULL)
			badline = true;
	}

	/* if it didn't have a header, or it failed to decode, print it out */
	if (badline) {
		printf("$ %s\n", buf);
		free(buf);

		if (retry) {
			/* if we want a synchronous response */
			free(binbuf);
			goto do_retry;
		}

		return NULL;
	}

	/* tell them how many bytes were actually decoded */
	*nbytes = r;

	free(buf);
	return binbuf;
}

/* dpcsocket abstraction */

int dpcsocket_connnect(struct dpcsock *sock)
{
	assert(sock != 0);

	/* unused == no-op */
	if (sock->mode == SOCKMODE_TERMINAL) {
		sock->fd = STDIN_FILENO; /* give it a real FD */
		return 0;
	}

	if (sock->mode == SOCKMODE_DEV) {
		sock->fd = open(sock->socket_name, O_RDWR | O_NOCTTY);
		if (sock->fd < 0)
			perror("open");
	} else if (sock->server) {
		/* setup the server socket*/
		printf("connecting server socket\n");
		if (sock->listen_fd <= 0)
			_listen_sock_init(sock);

		/* wait for someone to connect */
		_listen_sock_accept(sock);
	} else if(sock->mode == SOCKMODE_NVME) {
		sock->fd = -1;
		sock->nvme_write_done = false;
	} else {
		printf("connecting client socket\n");
		if (sock->mode == SOCKMODE_UNIX)
			sock->fd = _open_sock_unix(sock->socket_name);
		else
			sock->fd = _open_sock_inet(sock->port_num);
	}

	/* return non-zero on failure */
	return (sock->mode == SOCKMODE_NVME) ? 0 : (sock->fd < 0);
}

#define FMT_PAD (256)

/* configure the device baud rate, 8N1 */
void _configure_device(struct dpcsock *sock)
{
	/* setup the argument list. FIXME: this was painfully
	 * constructed to match exactly what minicom does on centos while
	 * tryin to isolate palladium clocking issues. We can probably get
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
		printf("skipping UART device configuration\n");
		return;
	}

	/* make sure we can actually fit the string */
	if (strlen(sock->socket_name) + strlen(_baudrate) + 1 >= FMT_PAD) {
		printf("stty arguments too long\n");
		exit(1);
	}

	/* make the string */
	snprintf(cmd, strlen(cmdfmt) + FMT_PAD, cmdfmt,
		 sock->socket_name, _baudrate);

	printf("Executing command to configure device: %s\n", cmd);

	r = system(cmd);

	if (r) {
		printf("error configuring UART with stty\n");
		exit(1);
	}
}

/* disambiguate json */
static bool _write_to_sock(struct fun_json *json, struct dpcsock *sock)
{
	if (!sock->base64) {
		/* easy case */
		return fun_json_write_to_fd(json, sock->fd);
	}

	/* base64 case */
	size_t allocated_size;
	struct fun_ptr_and_size pas = fun_json_serialize(json, &allocated_size);
	bool ok = _base64_write(sock, pas.ptr, pas.size);

	fun_free_threaded(pas.ptr, allocated_size);

	if (ok)
		return true;

	perror("*** write error on socket");
	return false;
}


/* take input from a socket and make a json */
static struct fun_json *_read_from_sock(struct dpcsock *sock, bool retry)
{
	uint8_t *buffer = NULL;
	struct fun_json *json = NULL;

	if (!sock->base64) {
		json = fun_json_read_from_fd(sock->fd);
	} else {
		ssize_t max;
		buffer = _base64_get_buffer(sock, &max, retry);
		json = _buffer2json(buffer, max); /* ignores NULL */
		free(buffer);
	}

	return json;
}

#define BLACK	"0;30"
#define RED	"0;31"
#define GREEN	"0;32"
#define BLUE	"0;34"
#define PURPLE	"0;35"

#define LIGHT_GREEN	"1;32"
#define LIGHT_BLUE	"1;34"
#define LIGHT_PURPLE	"1;35"

#define PRELUDE		"\e["
#define POSTLUDE	"m"
#define CLEAR		"0"

#define INPUT_COLORIZE	PRELUDE RED POSTLUDE
#define OUTPUT_COLORIZE	PRELUDE BLUE POSTLUDE
#define NORMAL_COLORIZE	PRELUDE CLEAR POSTLUDE

/* given a line of input, try and return a JSON object.
 *
 * Pay attention to which parsing mode we're in (free text or strict json),
 * and whether an override was specified.
 *
 * NOTE: mixing text & json modes with async transactions is in no way
 * supported. Just use json mode for that (or cross your fingers...)
 */
static struct fun_json *line2json(char *line, const char **error)
{
	enum parsingmode pmode = _parse_mode;
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

// ===============  PRETTY PRINTERS ===============

static struct fun_map *tid_to_context;
static struct fun_map *tid_to_pretty_printer;

void dpcsh_register_pretty_printer(uint64_t tid, void *context, pretty_printer_f pretty_printer)
{
	if (!tid_to_context) {
		tid_to_context = fun_map(NULL, NULL, NULL, (fun_map_key_t)(uint64_t)(-1));
	}
	fun_map_add(tid_to_context, (fun_map_key_t)tid, (fun_map_value_t)context, true);
	if (!tid_to_pretty_printer) {
		tid_to_pretty_printer = fun_map(NULL, NULL, NULL, (fun_map_key_t)(uint64_t)(-1));
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

// Somewhat of a hack: help needs to apply to both local (dpcsh-side) and remote (funos-side)
// So we apply it once locally first
static void apply_command_locally(const struct fun_json *json)
{
	const char *verb = NULL;

	if (!fun_json_lookup_string(json, "verb", &verb)) {
		return;
	}
	if (!verb || strcmp(verb, "help")) {
		return;
	}
	struct fun_json_command_environment *env = fun_json_command_environment_create();
	struct fun_json *j = fun_commander_execute(env, json);

	fun_json_command_environment_release(env);
	if (!j || fun_json_fill_error_message(j, NULL)) {
		return;
	}
	struct fun_json *result = fun_json_lookup(j, "result");
	if (result && !fun_json_fill_error_message(result, NULL)) {
		if (_verbose_log) {
			fun_json_printf_with_flags(PRELUDE BLUE POSTLUDE "Locally applied command: %s" NORMAL_COLORIZE "\n", result,
				FUN_JSON_PRETTY_PRINT_HUMAN_READABLE_STRINGS);
		} else {
			_quiet_log(LOG_RX_LOCAL, result);
		}
	}
	fun_json_release(j);
}

// We pass the sock INOUT in order to be able to reestablish a
// connection if the server went down and up
static bool _do_send_cmd(struct dpcsock *sock, char *line,
			 ssize_t read, uint32_t seq_num)
{
	if (read == 0)
		return false; // skip blank lines

	const char *error;

	struct fun_json *json = line2json(line, &error);

	if (!json) {
		printf("could not parse: %s\n", error);
		return false;
	}
	if (_verbose_log) {
		fun_json_printf_with_flags(INPUT_COLORIZE "input => %s"
				NORMAL_COLORIZE "\n",
				json, FUN_JSON_PRETTY_PRINT_HUMAN_READABLE_STRINGS);
	} else {
		_quiet_log(LOG_TX, json);
	}

	// Hack to list local commands if the command is 'help'
	apply_command_locally(json);
	bool ok = false;
	if(sock->mode == SOCKMODE_NVME) {
		ok = _write_to_nvme(json, sock, dpcsh_session_id, seq_num);
	} else {
		ok = _write_to_sock(json, sock);
	}
	if (!ok) {
		// try to reopen pipe
		printf("Write to socket failed - reopening socket\n");
		dpcsocket_connnect(sock);

		if (sock->fd <= 0) {
			printf("*** Can't reopen socket\n");
			fun_json_release(json);
			return false;
		}
		if(sock->mode == SOCKMODE_NVME) {
			ok = _write_to_nvme(json, sock, dpcsh_session_id, seq_num);
		} else {
			ok = _write_to_sock(json, sock);
		}
	}
	fun_json_release(json);
	if (!ok) {
		printf("*** Write to socket failed\n");
		return false;
	}

	return true;
}

static bool _is_loopback_command(struct dpcsock *sock, char *line,
				 ssize_t read)
{
	uint8_t *buf = NULL;
	ssize_t r;

	/* can't have a loopback command if we don't have a loopback
	 * socket
	 */
	if (!sock->loopback)
		return false;

	/* if there was an error reading, just bail */
	if (read <= 0)
		return false;

	/* check for the header */
	buf = (void*) _is_b64json_line(line);
	if (buf == NULL)
		return false;

	/* now decode and print it */
	buf = _b64_to_bin((void*) buf, &r);

	if (buf) {
		struct fun_json *json = NULL;

		json = _buffer2json(buf, (size_t) r);
		free(buf);

		if (json) {
			size_t allocated_size = 0;
			uint32_t flags = use_hex ? FUN_JSON_PRETTY_PRINT_USE_HEX_FOR_NUMBERS : 0;
			char *pp2 = fun_json_pretty_print(json,
							  0, "    ",
							  100, flags,
							  &allocated_size);
			printf("output => %s\n", pp2);
			free(pp2);
		} else {
			printf("base64 output didn't decode to binary json\n");
		}
	} else {
		printf("couldn't base64 decode input\n");
	}

	/* say we consumed it even it if was mangled so we don't send it on */
	return true;
}

static const struct fun_json *_get_result_if_present(const struct fun_json *response) {
	const struct fun_json *result = fun_json_lookup(response, "result");

	return result == NULL ? response : result;
}

static void _print_response_info(const struct fun_json *response) {
	const char *str;
	int64_t tid = 0;

	if (!fun_json_lookup(response, "result")) {
		if (_verbose_log) {
			fun_json_printf_with_flags("Old style output (NULL) - got %s\n",
					response,
					FUN_JSON_PRETTY_PRINT_HUMAN_READABLE_STRINGS);
		} else {
			_quiet_log(LOG_RX_OLD, response);
		}
	} else if (!fun_json_lookup_int64(response, "tid", &tid)) {
		printf("No tid\n");
	}

	if (fun_json_fill_error_message(_get_result_if_present(response),
					&str)) {
		if (_verbose_log) {
			printf(PRELUDE BLUE POSTLUDE "output => *** error: '%s'"
			       NORMAL_COLORIZE "\n", str);
		} else {
			_quiet_log(LOG_RX_ERROR, response);
		}
	} else {
		if (_verbose_log) {
			size_t allocated_size = 0;
			uint32_t flags = FUN_JSON_PRETTY_PRINT_HUMAN_READABLE_STRINGS |
							(use_hex ? FUN_JSON_PRETTY_PRINT_USE_HEX_FOR_NUMBERS : 0);
			char *pp = fun_json_pretty_print(response, 0, "    ",
							 100, flags,
							 &allocated_size);
			printf(OUTPUT_COLORIZE "output => %s"
			       NORMAL_COLORIZE "\n",
			       pp);
			free(pp);
		} else {
			_quiet_log(LOG_RX, response);
		}
	}
}

static char *_wrap_proxy_message(struct fun_json *response) {
	const char *error_message;
	struct fun_json *result;

	if (fun_json_fill_error_message(_get_result_if_present(response), &error_message)) {
		result = fun_json_create_empty_dict();
		int64_t tid;
		if (!fun_json_lookup_int64(response, "tid", &tid)) {
			tid = -1;
		}

		if (!fun_json_dict_add(result, "error", fun_json_no_copy_no_own,
				fun_json_create_string(error_message, fun_json_no_copy_no_own), true)
				|| !fun_json_dict_add(result, "tid", fun_json_no_copy_no_own,
				fun_json_create_int64(tid), true)) {
			printf("Can't form proxy message\n");
			fun_json_release(result);
			return NULL;
		}
	} else {
		result = fun_json_retain(response);
	}

	size_t allocated_size = 0;
	uint32_t flags = use_hex ? FUN_JSON_PRETTY_PRINT_USE_HEX_FOR_NUMBERS : 0;
	char *message = fun_json_pretty_print(result, 0, "    ",
					      0, flags, &allocated_size);

	fun_json_release(result);
	return message;
}

static void _do_recv_cmd(struct dpcsock *funos_sock,
			 struct dpcsock *cmd_sock, bool retry, uint32_t seq_num)
{
	/* receive a reply */
	struct fun_json *output;
	if(funos_sock->mode == SOCKMODE_NVME) {
		output = _read_from_nvme(funos_sock, dpcsh_session_id, seq_num);
	} else {
		output = _read_from_sock(funos_sock, retry);
	}
	if (!output) {
		if (retry)
			printf("invalid json returned\n");

		if ((cmd_sock->mode != SOCKMODE_TERMINAL) &&
			(funos_sock->mode == SOCKMODE_NVME) &&
			(funos_sock->nvme_write_done == false)) {
			output = fun_json_create_empty_dict();
			fun_json_dict_add_string(output, "error", fun_json_no_copy_no_own,
				"Command failed", fun_json_no_copy_no_own, false);
			fun_json_dict_add_int64(output, "tid", fun_json_no_copy_no_own, -1, false);
			fun_json_dict_add_string(output, "proxy-msg", fun_json_no_copy_no_own,
				"Cannot connect to DPU", fun_json_no_copy_no_own, false);
		} else {
			usleep(10*1000); // to avoid consuming all the CPU after funos quit
			return;
		}
	}

	_print_response_info(output);

	if (cmd_sock->mode != SOCKMODE_TERMINAL) {
		char *proxy_message = _wrap_proxy_message(output);
		write(cmd_sock->fd, proxy_message, strlen(proxy_message));
		write(cmd_sock->fd, "\n", 1);
		fun_free_string(proxy_message);
	}

	fun_json_release(output);
}

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

static void _do_interactive(struct dpcsock *funos_sock,
			    struct dpcsock *cmd_sock)
{
	ssize_t read;
	int r, nfds = 0;
	bool ok;

	if (cmd_sock->mode == SOCKMODE_TERMINAL) {
		/* enable per-character input for interactive input */
		terminal_set_per_character(true);
	}


	fd_set fds;
	while (1) {

		/* if a socket went away, try and reconnect */
		if ((funos_sock->fd == -1) && (funos_sock->retries-- > 0)) {
			dpcsocket_connnect(funos_sock);
		}

		if (cmd_sock->fd == -1) {
			if (cmd_sock->retries-- > 0) {
				printf("(re)-connect\n");
				dpcsocket_connnect(cmd_sock);
				printf("connected\n");
			} else {
				printf("out of re-connect attempts\n");
				break;
			}
		}

		/* configure the fd set */
		FD_ZERO(&fds);
		FD_SET(cmd_sock->fd, &fds);
		nfds = cmd_sock->fd;
		if (funos_sock->mode != SOCKMODE_TERMINAL) {
			FD_SET(funos_sock->fd, &fds);

			if (funos_sock->fd > nfds)
				nfds = funos_sock->fd;
		}

		/* wait on our input(s) */
		// printf("waiting on input\n");
		r = select(nfds+1, &fds, NULL, NULL, NULL);

		if (r <= 0) {
			perror("select");
			exit(1);
		}

		uint32_t seq_num = cmd_seq_num;
		cmd_seq_num++;
		if (FD_ISSET(cmd_sock->fd, &fds)) {
			// printf("user input\n");
			char *line = _read_a_line(cmd_sock, &read);

			if (read == -1) /* user ^D */
				break;

			if (line == NULL) {
				// printf("error reading line\n");
				continue;
			}

			/* in loopback mode, check if this is output from
			 * the other end & decode that & don't send it.
			 */
			if (_is_loopback_command(funos_sock, line, read))
				continue;

			ok = _do_send_cmd(funos_sock, line, read, seq_num);
			free(line);
			if (!ok) {
				printf("error sending command\n");
			}
		}

		/* if it changed while in flight */
		if ((funos_sock->mode != SOCKMODE_NVME) && (funos_sock->fd == -1)) {
			continue;
		}

		if ((funos_sock->mode == SOCKMODE_NVME) || (FD_ISSET(funos_sock->fd, &fds)
		    && (!funos_sock->loopback))) {
			// printf("funos input\n");
			_do_recv_cmd(funos_sock, cmd_sock, false, seq_num);
		}
	}
	if (cmd_sock->mode == SOCKMODE_TERMINAL) {
		/* reset terminal */
		terminal_set_per_character(false);
	}
}

static void _do_run_webserver(struct dpcsock *funos_sock,
			      struct dpcsock *cmd_sock)
{
	/* we expect FunOS is connected, connect the command server */
	_listen_sock_init(cmd_sock);

	if (cmd_sock->listen_fd < 0) {
		printf("error listening\n");
		exit(1);
	}

	/* strip the FDs out */
	run_webserver(funos_sock, cmd_sock->listen_fd);
}

#define MAXLINE (512)

int json_handle_req(struct dpcsock *jsock, const char *path,
		    char *buf, int *size)
{
	printf("got jsock request for '%s'\n", path);
	char line[MAXLINE];
	int r = -1;

	/* rewrite request for root */
	if (strcmp(path, "/") == 0)
		path = "\"\"";
	else if (strcmp(path, ".") == 0)
		path = "\"\"";

	snprintf(line, MAXLINE, "peek %s", path);
	const char *error;
	struct fun_json *json = line2json(line, &error);
	if (!json) {
		printf("could not parse '%s': %s\n", line, error);
		return -1;
	}
	if (_verbose_log)
		fun_json_printf_with_flags("input => %s\n", json, FUN_JSON_PRETTY_PRINT_HUMAN_READABLE_STRINGS);
	else
		_quiet_log(LOG_TX, json);

	bool ok = _write_to_sock(json, jsock);
	fun_json_release(json);
	if (!ok)
		return -1;

	/* receive a reply */
	struct fun_json *output = _read_from_sock(jsock, true);
	if (!output) {
		printf("invalid json returned\n");
		return -1;
	}

	size_t allocated_size = 0;
	uint32_t flags = FUN_JSON_PRETTY_PRINT_HUMAN_READABLE_STRINGS |
					(use_hex ? FUN_JSON_PRETTY_PRINT_USE_HEX_FOR_NUMBERS : 0);
	char *pp2 = fun_json_pretty_print(output, 0, "    ",
					  100, flags, &allocated_size);
	if (_verbose_log)
		printf("output => %s\n", pp2);
	else
		_quiet_log(LOG_RX, output);

	if (!pp2)
		return -1;

	/* copy it out */
	if (strlen(pp2) < *size) {
		strcpy(buf, pp2);
		*size = strlen(pp2);
		r = 0;
	}

	free(pp2);
	fun_json_release(output);

	return r;
}

#define LINE_MAX	(100 * 1024)

static void _do_cli(int argc, char *argv[],
		    struct dpcsock *funos_sock,
		    struct dpcsock *cmd_sock, int startIndex)
{
	char *buf = malloc(LINE_MAX);
	int n = 0;
	bool ok;
	uint32_t seq_num = cmd_seq_num;

	cmd_seq_num++;
	for (int i = startIndex; i < argc; i++) {
		n += snprintf(buf + n, LINE_MAX - n, "%s ", argv[i]);
		printf("buf=%s n=%d\n", buf, n);
	}

	size_t len = strlen(buf);
	buf[--len] = 0;	// trim the last space
	printf(">> single cmd [%s] len=%zd\n", buf, len);
	ok = _do_send_cmd(funos_sock, buf, len, seq_num);
	if (ok) {
		_do_recv_cmd(funos_sock, cmd_sock, true, seq_num);
	}
	free(buf);
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
	{ "unix_sock",       optional_argument, NULL, 'u' },
// DPC over NVMe is needed only in Linux
#ifdef __linux__
	{ "pcie_nvme_sock",  optional_argument, NULL, 'p' },
#endif //__linux__
	{ "http_proxy",      optional_argument, NULL, 'H' },
	{ "tcp_proxy",       optional_argument, NULL, 'T' },
	{ "text_proxy",      optional_argument, NULL, 'T' },
	{ "unix_proxy",      optional_argument, NULL, 't' },
// inet interface restriction needed only in Linux,
// current implementation doesn't work on Mac
#ifdef __linux__
	{ "inet_interface",  required_argument, NULL, 'I' },
#endif //__linux_
	{ "nocli",           no_argument,       NULL, 'n' },
	{ "oneshot",         no_argument,       NULL, 'S' },
	{ "manual_base64",   no_argument,       NULL, 'N' },
	{ "no_dev_init",     no_argument,       NULL, 'X' },
	{ "no_flow_control", no_argument,       NULL, 'F' },
	{ "baud",            required_argument, NULL, 'R' },
	{ "legacy_b64",      no_argument,       NULL, 'L' },
	{ "verbose",         no_argument,       NULL, 'v' },
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
	printf("       -h, --help                  this text\n");
	printf("       -D, --dev[=device]          open device and read/write base64 to FunOS UART\n");
	printf("       -F, --no_flow_control       no flow control in uart. send char one by one with delay\n");
	printf("       -B, --base64_srv[=port]     listen as a server port on IP using base64 (dpcuart to qemu)\n");
	printf("       -b, --base64_sock[=port]    connect as a client port on IP using base64 (dpcuart to qemu)\n");
	printf("       -i, --inet_sock[=port]      connect as a client port over IP\n");
	printf("       -u, --unix_sock[=sockname]  connect as a client port over unix sockets\n");
// DPC over NVMe is needed only in Linux
#ifdef __linux__
	printf("       -p, --pcie_nvme_sock[=sockname]  connect as a client port over nvme pcie device\n");
#endif //__linux__
	printf("       -H, --http_proxy[=port]     listen as an http proxy\n");
	printf("       -T, --tcp_proxy[=port]      listen as a tcp proxy\n");
	printf("       -T, --text_proxy[=port]     same as \"--tcp_proxy\"\n");
	printf("       -t, --unix_proxy[=port]     listen as a unix proxy\n");
#ifdef __linux__
	printf("       -I, --inet_interface=name   listen only on <name> interface\n");
#endif // __linux__
	printf("       -n, --nocli                 issue request from command-line arguments and terminate\n");
	printf("       -S, --oneshot               don't reconnect after command side disconnect\n");
	printf("       -N, --manual_base64         just translate base64 back and forward\n");
	printf("       -X, --no_dev_init           don't init the UART device, use as-is\n");
	printf("       -R, --baud=rate             specify non-standard baud rate (default=" DEFAULT_BAUD ")\n");
	printf("       -L, --legacy_b64            support old-style base64 encoding, despite issues\n");
	printf("       -v, --verbose               log all json transactions in proxy mode\n");
	printf("       -Y, --retry[=N]             retry every seconds for N seconds for first socket connection\n");
#ifdef __linux__
	printf("       --nvme_cmd_timeout=timeout specify cmd timeout in ms (default=" DEFAULT_NVME_CMD_TIMEOUT_MS ")\n");
#endif //__linux__

}

enum mode {
	MODE_INTERACTIVE,  /* commmand-line (ish) */
	MODE_PROXY,        /* proxy commands from a socket */
	MODE_HTTP_PROXY,   /* http proxy */
	MODE_NOCONNECT,    /* no connection to FunOS */
};

/** entrypoint **/
int main(int argc, char *argv[])
{
	enum mode mode = MODE_INTERACTIVE; /* default user control */
	bool one_shot = false;  /* run a single command and terminate */
	int ch, first_unknown = -1;
	struct dpcsock funos_sock; /* connection to FunOS */
	struct dpcsock cmd_sock;   /* connection to commanding agent */

	srand (time(NULL));
	dpcsh_path = argv[0];
	dpcsh_session_id = getpid();
	dpcsh_load_macros();
	register_csr_macro();

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

	/* check whether NVMe connection to DPU is available */
	/* DPC over NVMe will work only in Linux */
	/* In macOS, libfunq is used */
	char nvme_device_name[64];
	bool nvme_dpu_present = false;
	/* In macOS, always returns false */
	nvme_dpu_present = find_nvme_dpu_device(nvme_device_name,
						sizeof(nvme_device_name));
	memset(&funos_sock, 0, sizeof(funos_sock));
	/* In Linux, use NVMe as default if present */
	if (nvme_dpu_present) {
		funos_sock.mode = SOCKMODE_NVME;
		funos_sock.socket_name = nvme_device_name;
		funos_sock.server = false;
		funos_sock.fd = -1;
		funos_sock.retries = UINT32_MAX;
		funos_sock.cmd_timeout = atoi(DEFAULT_NVME_CMD_TIMEOUT_MS);
	}
	/* Use libfunq otherwsie */
	else {
		/* default connection to FunOS posix simulator dpcsock */
		funos_sock.mode = SOCKMODE_IP;
		funos_sock.server = false;
		funos_sock.port_num = DPC_PORT;
		funos_sock.fd = -1;
		funos_sock.retries = UINT32_MAX;
	}

	/* default command connection is console (so socket disabled) */
	memset(&cmd_sock, 0, sizeof(cmd_sock));
	cmd_sock.mode = SOCKMODE_TERMINAL;
	cmd_sock.fd = -1;
	cmd_sock.retries = UINT32_MAX;

	while ((ch = getopt_long(argc, argv,
				 "hs::i::u::H::T::I:t::D:nNFXR:v",
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
			break;

		case 'B':  /* base64 server */

			/* run as base64 mode for dpcuart */
			funos_sock.base64 = true;
			funos_sock.mode = SOCKMODE_IP;
			funos_sock.server = true;
			funos_sock.port_num = opt_portnum(optarg,
							  DPC_B64SRV_PORT);
			break;
		case 'D':  /* base64 device (pty/tty) */

			/* run as base64 mode for dpcuart */
			funos_sock.base64 = true;
			funos_sock.mode = SOCKMODE_DEV;
			funos_sock.socket_name = opt_sockname(optarg,
							      "/unknown");
			break;
		case 'i':  /* inet client */

			/* in case this got stamped over... */
			funos_sock.mode = SOCKMODE_IP;
			funos_sock.server = false;
			funos_sock.port_num = opt_portnum(optarg,
							  DPC_PORT);

			break;
		case 'u':  /* unix domain client */

			funos_sock.mode = SOCKMODE_UNIX;
			cmd_sock.server = false;
			funos_sock.socket_name = opt_sockname(optarg,
							      SOCK_NAME);

			break;
// DPC over NVMe is needed only in Linux
#ifdef __linux__
		case 'p':
			funos_sock.mode = SOCKMODE_NVME;
			cmd_sock.server = false;
			funos_sock.socket_name = opt_sockname(optarg,
							      NVME_DEV_NAME);
			break;
#endif //__linux__
		case 'H':  /* http proxy */

			cmd_sock.mode = SOCKMODE_IP;
			cmd_sock.server = true;
			cmd_sock.port_num = opt_portnum(optarg,
							HTTP_PORTNO);

			mode = MODE_HTTP_PROXY;

			break;
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
			funos_sock.fd = STDOUT_FILENO;
			mode = MODE_NOCONNECT;

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
			break;
#endif //__linux__

		default:
			usage(argv[0]);
			exit(1);
		}

		if (first_unknown != -1)
			break;
	}

	/* sanity check */
	if (cmd_sock.eth_name && cmd_sock.mode != SOCKMODE_IP) {
		printf("Interface name is valid for IP proxy modes only\n");
		exit(1);
	}

	/* make an announcement as to what we are */
	printf("FunOS Dataplane Control Shell");

	switch (mode) {
	case MODE_INTERACTIVE:
		/* do nothing */
		_verbose_log = true;
		break;
	case MODE_PROXY:
		printf(": socket proxy mode");
		break;
	case MODE_HTTP_PROXY:
		printf(": HTTP proxy mode");
		break;
	case MODE_NOCONNECT:
		printf(": manual base64 mode");
		break;
	}

	printf("\n");

	_print_version(); /* always print this for the logs */

	/* if we're running a device, make sure we configure it */
	if (funos_sock.mode == SOCKMODE_DEV)
		_configure_device(&funos_sock);


	/* start by opening the socket to FunOS */
	int r = dpcsocket_connnect(&funos_sock);

	if (r != 0) {
		printf("*** Can't connect FunOS\n");
		exit(1);
	}

	printf("FunOS is connected!\n");

	switch(mode) {
	case MODE_HTTP_PROXY:
		_parse_mode = PARSE_JSON;
		_do_run_webserver(&funos_sock, &cmd_sock);
		break;
	case MODE_PROXY:
		_parse_mode = PARSE_JSON;
		if (one_shot)
			cmd_sock.retries = 1;
		_do_interactive(&funos_sock, &cmd_sock);
		break;
	case MODE_INTERACTIVE:
	case MODE_NOCONNECT: {
		_parse_mode = PARSE_TEXT;
		if (one_shot)
			_do_cli(argc, argv, &funos_sock, &cmd_sock, optind);
		else
			_do_interactive(&funos_sock, &cmd_sock);
	}

	}

	return 0;
}
