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
#include "dpcsh_log.h"
#include "dpcsh_nvme.h"
#include "csr_command.h"
#include "dpcsh_libfunq.h"

#include <FunSDK/utils/threaded/fun_map_threaded.h>
#include <FunSDK/services/commander/fun_commander.h>
#include <FunSDK/services/commander/fun_commander_basic_commands.h>
#include <FunSDK/utils/threaded/fun_malloc_threaded.h>
#include <FunSDK/utils/common/base64.h>
#include <FunSDK/platform/include/platform/utils_platform.h>

#define SOCK_NAME	"/tmp/funos-dpc.sock"      /* default FunOS socket */
#define PROXY_NAME      "/tmp/funos-dpc-text.sock" /* default unix proxy name */
#define DPC_PORT        20110   /* default FunOS port */
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

struct dpc_thread {
	pthread_t thread;
	void *args[3];
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
			log_error("socket creation error \n");
			return sock;
		}
		memset(&serv_addr, '0', sizeof(serv_addr));

		serv_addr.sin_family = AF_INET;
		serv_addr.sin_port = htons(port);

		// Convert IPv4 and IPv6 addresses from text to binary form
		if(inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)<=0) {
			log_error("invalid address/ Address not supported \n");
			return -1;
		}

		if (tries > 0) {
			log_error("connect error, retry %d\n", tries);
			sleep(1);
		}

		r = connect(sock, (struct sockaddr *)&serv_addr,
			    sizeof(serv_addr));
		tries++;
	} while ((r < 0) && (tries < connect_retries));

	if (r < 0) {
		log_error("can't connect\n");
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

/* low-level base64+socket routines */
bool _base64_write(struct dpcsock_connection *connection,
	const uint8_t *buf, size_t nbyte)
{
	/* keep it simple */
	size_t b64size = nbyte * 2 + 1; /* big to avoid rounding issues */
	char *b64buf = malloc(b64size);
	int r;
	int fd = connection->fd;

	if (b64buf == NULL) {
		log_error("out of memory allocating output b64 buffer\n");
		exit(1);
	}

	r = base64_encode(b64buf, b64size, (void*) buf, nbyte);
	if (r <= 0) {
		log_error("error encoding base64\n");
		return false;
	}

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


/* read a line of input from the fd */
#define BUF_SIZE (1024)
static char *_read_a_line(struct dpcsock_connection *connection, ssize_t *nbytes)
{
	char *buf = NULL;
	size_t size = 0, pos = 0;
	bool echo = false;
	int fd = connection->fd;
	int r;

	*nbytes = -1; /* assume error */

	if (connection->encoding == PARSE_BINARY_JSON) {
		*nbytes = fun_json_read_enough_bytes_for_json_from_fd(fd, (uint8_t **)&buf, &size);
		return buf;
	}

	if ((connection->socket->mode == SOCKMODE_TERMINAL) && !connection->socket->base64) {
		/* fancy pants line editor on stdin */
		buf = getline_with_history(nbytes);
		return buf;
	}

	if ((connection->socket->mode == SOCKMODE_TERMINAL) && connection->socket->base64) {
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
				log_error("couldn't allocate input buffer\n");
				exit(1);
			}
		}

		/* read a byte */
		errno = 0;
		r = read(fd, &buf[pos], 1);

		if (r <= 0) {
			log_error("remote hung up / error: %d %d %s\n",
			       r, errno, strerror(errno));
			free(buf);
			*nbytes = 0;
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
static uint8_t *_base64_get_buffer(struct dpcsock_connection *sock,
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

	if(sock->mode == SOCKMODE_FUNQ) {
		sock->funq_handle = dpc_funq_init(sock->socket_name, _debug_log);
		return sock->funq_handle != NULL;
	}

	return true;
}

static void dpcsocket_destroy(struct dpcsock *sock)
{
	if(sock->mode == SOCKMODE_FUNQ) {
		dpc_funq_destroy(sock->funq_handle);
		free(sock->funq_handle);
	}
}

struct dpcsock_connection *dpcsocket_connect(struct dpcsock *sock)
{
	static size_t nvme_session_counter = 0;
	assert(sock != NULL);
	struct dpcsock_connection *connection =
		(struct dpcsock_connection *)calloc(1, sizeof(struct dpcsock_connection));

	if (!connection) {
		return NULL;
	}

	connection->socket = sock;
	connection->encoding = PARSE_BINARY_JSON;

	if (sock->server) {
		log_debug(_debug_log, "Listening\n");
		connection->fd = accept(sock->listen_fd, NULL, NULL);
		connection->encoding = PARSE_JSON;
		return connection;
	}

	if (sock->mode == SOCKMODE_NVME) {
		connection->nvme_seq_num = 0;
		connection->nvme_write_done = true;
		connection->nvme_session_id = (0xFFFF & (nvme_session_counter++)) + ((0xFFFF & getpid()) << 16);
		log_debug(_debug_log, "NVMe session id = %" PRIu32 "\n", connection->nvme_session_id);
		return connection;
	}

	if (sock->mode == SOCKMODE_FUNQ) {
		connection->funq_connection = dpc_funq_open_connection(sock->funq_handle);
		if (!connection->funq_connection) {
			free(connection);
			return NULL;
		}
	}

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
		connection->fd = _open_sock_inet(sock->port_num);
	}

	/* connection->fd < 0 in the case of failure*/
	return connection;
}

void dpcsocket_close(struct dpcsock_connection *connection)
{
	if (connection == NULL) return;

	if (connection->socket->mode != SOCKMODE_NVME && connection->socket->mode != SOCKMODE_FUNQ) {
		close(connection->fd);
	}

	if (connection->socket->mode == SOCKMODE_FUNQ) {
		if (!dpc_funq_close_connection(connection->funq_connection)) {
			perror("dpc_funq_close_connection");
		}
	}

	free(connection);
}

/* take input from a socket and make a json */
static struct fun_json *_read_from_sock(struct dpcsock_connection *connection, bool retry)
{
	uint8_t *data = NULL;
	ssize_t data_size;
	uint8_t *deallocate_ptr = NULL;
	struct fun_json *json = NULL;
	struct dpcsock *socket = connection->socket;

	if (connection->encoding != PARSE_BINARY_JSON) {
		perror("the only mode for communication with FunOS is binary json");
		return NULL;
	}

	if (!socket->base64 && socket->mode != SOCKMODE_NVME) {
		return fun_json_read_from_fd(connection->fd);
	}

	if (socket->mode == SOCKMODE_NVME) {
		data_size = _read_from_nvme(&data, &deallocate_ptr, connection);
	} else if (socket->base64) {
		data = _base64_get_buffer(connection, &data_size, retry);
		deallocate_ptr = data;
	} else {
		return NULL;
	}

	json = _buffer2json(data, data_size, NULL); /* ignores NULL */
	free(deallocate_ptr);

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
		}
	}
	fun_json_release(j);
}

static bool _write_to_sock(struct fun_json *json,
			struct dpcsock_connection *connection);

// We pass the sock INOUT in order to be able to reestablish a
// connection if the server went down and up
static bool _do_send_cmd(struct dpcsock_connection *funos,
			 struct dpcsock_connection *cmd, char *line, ssize_t read)
{
	if (read == 0)
		return false; // skip blank lines

	const char *error = "unknown";

	struct fun_json *json = NULL;
	if (cmd->encoding == PARSE_BINARY_JSON) {
		json = fun_json_create_from_binary_with_options((uint8_t *)line, read, false);
		if (fun_json_fill_error_message(json, &error)) {
			log_error("could not parse: %s, size = %zd\n", error, read);
			if (read > 3) {
				log_error("first bytes: %d %d %d %d\n", line[0], line[1], line[2], line[3]);
			}
			fun_json_release(json);
			return false;
		}
	} else {
		json = line2json(line, cmd->encoding, &error);
	}

	if (!json) {
		log_error("could not parse: %s, size = %zd\n", error, read);
		return false;
	}
	if (_verbose_log) {
		fun_json_printf_with_flags(INPUT_COLORIZE "input => %s"
				NORMAL_COLORIZE "\n",
				json, FUN_JSON_PRETTY_PRINT_HUMAN_READABLE_STRINGS);
	}

	// Hack to list local commands if the command is 'help'
	bool complete;
	apply_command_locally(json, cmd, &complete);
	if (complete) {
		return true;
	}

	bool ok = _write_to_sock(json, funos);
	fun_json_release(json);
	if (!ok) {
		log_error("write to socket failed\n");
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

		json = _buffer2json(buf, (size_t) r, NULL);
		free(buf);

		if (json) {
			size_t allocated_size = 0;
			uint32_t flags = use_hex ? FUN_JSON_PRETTY_PRINT_USE_HEX_FOR_NUMBERS : 0;
			char *pp2 = fun_json_pretty_print(json,
							  0, "    ",
							  100, flags,
							  &allocated_size);
			log_debug(_debug_log, "output => %s\n", pp2);
			free(pp2);
		} else {
			log_error("base64 output didn't decode to binary json\n");
		}
	} else {
		log_error("couldn't base64 decode input\n");
	}

	/* say we consumed it even it if was mangled so we don't send it on */
	return true;
}

static const struct fun_json *_get_result_if_present(const struct fun_json *response) {
	const struct fun_json *result = fun_json_lookup(response, "result");

	return result == NULL ? response : result;
}

// Return true if normal output, false if an error
static bool _print_response_info(const struct fun_json *response) {
	const char *str;
	int64_t tid = 0;
	bool ok = true;

	if (!fun_json_lookup(response, "result")) {
		if (_verbose_log) {
			fun_json_printf_with_flags("Old style output (NULL) - got %s\n",
					response,
					FUN_JSON_PRETTY_PRINT_HUMAN_READABLE_STRINGS);
		}
	} else if (!fun_json_lookup_int64(response, "tid", &tid)) {
		log_error("No tid\n");
	}

	if (fun_json_fill_error_message(_get_result_if_present(response),
					&str)) {
		ok = false;
		if (_verbose_log || _nocli_script_mode) {
			log_error(PRELUDE BLUE POSTLUDE "output => *** error: '%s'"
			       NORMAL_COLORIZE "\n", str);
		}
	} else if (!response) {
		log_error("NULL response returned\n");
	} else {
		if (_verbose_log || _nocli_script_mode) {
			size_t allocated_size = 0;
			uint32_t flags = FUN_JSON_PRETTY_PRINT_HUMAN_READABLE_STRINGS |
							(use_hex ? FUN_JSON_PRETTY_PRINT_USE_HEX_FOR_NUMBERS : 0);
			char *pp = fun_json_pretty_print(response, 0, "    ",
							 100, flags,
							 &allocated_size);
			const char *pattern = _verbose_log ?
				 OUTPUT_COLORIZE "output => %s" NORMAL_COLORIZE "\n" :
				 "%s\n";
			printf(pattern, pp);
			free(pp);
		}
	}
	return ok;
}

static char *_wrap_proxy_message(enum parsingmode mode, struct fun_json *response, size_t *size) {
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
			log_error("can't form proxy message\n");
			fun_json_release(result);
			return NULL;
		}
	} else if (!response) {
		log_error("NULL response returned\n");
		result = fun_json_create_null();
	} else {
		result = fun_json_retain(response);
	}

	size_t allocated_size = 0;
	uint32_t flags = use_hex ? FUN_JSON_PRETTY_PRINT_USE_HEX_FOR_NUMBERS : 0;
	char *message = NULL;
	if (mode == PARSE_TEXT || mode == PARSE_JSON) {
		message = fun_json_pretty_print(result, 0, "    ",
					      0, flags, &allocated_size);
		*size = strlen(message);
		message[(*size)++] = '\n'; // trick, since we do not need trailing zero
	} else if (mode == PARSE_BINARY_JSON) {
		struct fun_ptr_and_size pas = fun_json_serialize(result, &allocated_size);
		message = (char *)pas.ptr;
		*size = pas.size;
	} else {
		perror("*** Unsupported parsing mode for client!\n");
	}

	fun_json_release(result);
	return message;
}

static struct fun_json *_post_process_output(struct fun_json *output,
			bool nvme_write_incomplete)
{
	if (!output) {
		if (nvme_write_incomplete) {
			output = fun_json_create_empty_dict();
			fun_json_dict_add_string(output, "error", fun_json_no_copy_no_own,
				"Command failed", fun_json_no_copy_no_own, false);
			fun_json_dict_add_int64(output, "tid", fun_json_no_copy_no_own, -1, false);
			fun_json_dict_add_string(output, "proxy-msg", fun_json_no_copy_no_own,
				"Cannot connect to DPU", fun_json_no_copy_no_own, false);
		} else {
			usleep(10*1000); // to avoid consuming all the CPU after funos quit
			return NULL;
		}
	}
	return output;
}

static bool _write_response(struct fun_json *output, struct dpcsock_connection *connection)
{
	bool ok = _print_response_info(output);

	if (connection->socket->mode != SOCKMODE_TERMINAL) {
		size_t size;
		char *proxy_message = _wrap_proxy_message(connection->encoding, output, &size);
		if (proxy_message != NULL) {
			write(connection->fd, proxy_message, size);
			fsync(connection->fd);
		}
		free(proxy_message);
	}

	return ok;
}

static void _recv_callback(struct fun_ptr_and_size response, void *context)
{
	struct dpcsock_connection *cmd_sock = (struct dpcsock_connection *)context;
	struct fun_json *output;
	size_t position = 0;
	size_t read_bytes;

	do {
		output = _buffer2json(response.ptr + position, response.size - position, &read_bytes);
		if (!output) {
			perror("*** _recv_callback output is NULL");
			return;
		}

		_write_response(output, cmd_sock);
		fun_json_release(output);
		position += read_bytes;
	} while (position < response.size);
}

static bool _write_to_sock(struct fun_json *json,
			struct dpcsock_connection *connection)
{
	if (connection->encoding != PARSE_BINARY_JSON) {
		perror("the only mode for communication with FunOS is binary json");
		return NULL;
	}

	struct dpcsock *socket = connection->socket;
	if (!socket->base64 && socket->mode != SOCKMODE_NVME && socket->mode != SOCKMODE_FUNQ) {
		/* easy case */
		return fun_json_write_to_fd(json, connection->fd);
	}

	size_t allocated_size;
	struct fun_ptr_and_size pas = fun_json_serialize(json, &allocated_size);
	bool ok = false;
	if (socket->mode == SOCKMODE_NVME) {
		connection->nvme_seq_num++;
		ok = _write_to_nvme(pas, connection);
	} else if (socket->mode == SOCKMODE_FUNQ) {
		ok = dpc_funq_send(connection->funq_connection, pas);
	} else {
		/* base64 case */
		ok = _base64_write(connection, pas.ptr, pas.size);
	}

	fun_free_threaded(pas.ptr, allocated_size);

	if (ok)
		return true;

	perror("*** write error on socket");
	return false;
}

// Return true if all went well, and false if a JSON error was returned
static bool _do_recv_cmd(struct dpcsock_connection *funos_connection,
			 struct dpcsock_connection *cmd_connection, bool retry)
{
	/* receive a reply */
	struct fun_json *output = _read_from_sock(funos_connection, retry);

	if (!output && retry) {
			log_error("invalid json returned\n");
	}

	bool nvme_write_incomplete = (funos_connection->socket->mode == SOCKMODE_NVME) &&
			(funos_connection->nvme_write_done == false);
	bool ok = _write_response(_post_process_output(output, nvme_write_incomplete), cmd_connection);

	fun_json_release(output);
	return ok;
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

static bool _read_and_send_command(struct dpcsock_connection *funos,
			    struct dpcsock_connection *cmd)
{
	ssize_t read;
	char *line = _read_a_line(cmd, &read);

	if (read <= 0 || line == NULL) /* user ^D or connection closed*/
		return false;

	/* in loopback mode, check if this is output from
		* the other end & decode that & don't send it.
		*/
	if (_is_loopback_command(funos->socket, line, read))
		return true;

	bool ok = _do_send_cmd(funos, cmd, line, read);
	free(line);
	if (!ok) {
		log_error("error sending command\n");
	}

	return true;
}

static void _do_session(struct dpcsock_connection *funos,
			    struct dpcsock_connection *cmd)
{
	if (cmd->socket->mode == SOCKMODE_TERMINAL) {
		/* enable per-character input for interactive input */
		terminal_set_per_character(true);
	}

	// no select looping, only one fd
	if (funos->socket->mode == SOCKMODE_TERMINAL || funos->socket->mode == SOCKMODE_NVME || funos->socket->mode == SOCKMODE_FUNQ) {
		while (_read_and_send_command(funos, cmd)) {
			if (funos->socket->mode == SOCKMODE_NVME)
				_do_recv_cmd(funos, cmd, false);
		}

		goto restore_term;
	}


	// select loop, TODO: incomplete input may block it
	fd_set fds;
	int r, max_fd = 0;
	while (1) {
		/* configure the fd set */
		FD_ZERO(&fds);
		FD_SET(cmd->fd, &fds);
		FD_SET(funos->fd, &fds);

		max_fd = funos->fd > cmd->fd ? funos->fd : cmd->fd;

		/* wait on our input(s) */
		r = select(max_fd+1, &fds, NULL, NULL, NULL);

		if (r <= 0) {
			perror("select");
			exit(1);
		}

		if (FD_ISSET(cmd->fd, &fds)) {
			if (!_read_and_send_command(funos, cmd)) break;
		}

		if (FD_ISSET(funos->fd, &fds) && (!funos->socket->loopback)) {
			_do_recv_cmd(funos, cmd, false);
		}
	}

restore_term:
	if (cmd->socket->mode == SOCKMODE_TERMINAL) {
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

static void open_connections(struct dpcsock *funos_socket,
					struct dpcsock *cmd_socket,
					struct dpcsock_connection **funos, struct dpcsock_connection **cmd)
{
	*funos = dpcsocket_connect(funos_socket);
	*cmd = dpcsocket_connect(cmd_socket);
	if (funos_socket->mode == SOCKMODE_FUNQ) {
		if (!dpc_funq_register_receive_callback((*funos)->funq_connection, _recv_callback, *cmd)) {
			log_error("can't register a callback for libfunq\n");
		}
	}
}

static void _add_thread(struct dpc_thread *workers, size_t max_workers,
	struct dpcsock_connection *funos, struct dpcsock_connection *cmd)
{
	for (size_t i = 0; i < max_workers; i++) {
		if (workers[i].used) {
			if (workers[i].args[2]) {
			// using this as an indicator of thread got terminated,
			// may give false-negatives, that are fine, but no false-positives
				workers[i].used = false;
				pthread_join(workers[i].thread, NULL);
				close_connections(workers[i].args[0], workers[i].args[1]);
				log_debug(_debug_log, "garbage-collected thread #%zu\n", i);
			}
		}
		if (!workers[i].used) {
			workers[i].used = true;
			workers[i].args[0] = funos;
			workers[i].args[1] = cmd;
			workers[i].args[2] = 0;
			pthread_create(&workers[i].thread, NULL, _run_thread, workers[i].args);
			log_debug(_debug_log, "added thread #%zu\n", i);
			return;
		}
	}
	log_error("out of connections\n");
	close_connections(funos, cmd);
}

static void _wait_finalize_threads(struct dpc_thread *workers, size_t max_workers)
{
	void *retval;
	for (size_t i = 0; i < max_workers; i++) {
		if (workers[i].used) {
			pthread_join(workers[i].thread, &retval);
			close_connections(workers[i].args[0], workers[i].args[1]);
			log_debug(_debug_log, "joined thread #%zu\n", i);
		}
	}
}

static void _do_interactive(struct dpcsock *funos_socket,
			    struct dpcsock *cmd_socket)
{
	struct dpcsock_connection *funos, *cmd;
	struct dpc_thread workers[MAX_CLIENTS_THREADS] = {};
	do {
		open_connections(funos_socket, cmd_socket, &funos, &cmd);
		if (!funos || !cmd || cmd->fd < 0) {
			close_connections(funos, cmd);
			break;
		}
		_add_thread(workers, MAX_CLIENTS_THREADS, funos, cmd);
	} while (cmd_socket->server);
	_wait_finalize_threads(workers, MAX_CLIENTS_THREADS);
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
	open_connections(funos_socket, cmd_socket, &funos, &cmd);

	if (!funos || !cmd || cmd->fd < 0) {
		log_error("can't open connections\n");
		goto connect_fail;
	}

	for (int i = startIndex; i < argc; i++) {
		n += snprintf(buf + n, bufsize - n, "%s ", argv[i]);
		log_debug(_debug_log, "buf=%s n=%d\n", buf, n);
	}

	size_t len = strlen(buf);
	buf[--len] = 0;	// trim the last space
	log_debug(_debug_log, ">> single cmd [%s] len=%zd\n", buf, len);
	ok = _do_send_cmd(funos, cmd, buf, len);
	if (ok) {
		ok = _do_recv_cmd(funos, cmd, true);
	}

connect_fail:
	close_connections(funos, cmd);
	free(buf);
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
#ifdef WITH_LIBFUNQ
	printf("       -q, --libfunq_sock[=sockname]  connect as a client port over libfunq pcie device, put \"auto\" for auto-discover\n");
#endif
	printf("       -H, --http_proxy[=port]     listen as an http proxy\n");
	printf("       -T, --tcp_proxy[=port]      listen as a tcp proxy\n");
	printf("       -T, --text_proxy[=port]     same as \"--tcp_proxy\"\n");
	printf("       -t, --unix_proxy[=port]     listen as a unix proxy\n");
#ifdef __linux__
	printf("       -I, --inet_interface=name   listen only on <name> interface\n");
#endif // __linux__
	printf("       -n, --nocli                 issue request from command-line arguments and terminate\n");
	printf("       -Q, --nocli-quiet           issue request from command-line arguments and terminate, only print response\n");
	printf("       -S, --oneshot               don't reconnect after command side disconnect\n");
	printf("       -N, --manual_base64         just translate base64 back and forward\n");
	printf("       -X, --no_dev_init           don't init the UART device, use as-is\n");
	printf("       -R, --baud=rate             specify non-standard baud rate (default=" DEFAULT_BAUD ")\n");
	printf("       -L, --legacy_b64            support old-style base64 encoding, despite issues\n");
	printf("       -v, --verbose               log all json transactions in proxy mode\n");
	printf("       -d, --debug                 print debugging information\n");
	printf("       -l, --log[=filename]        log to a file\n");
	printf("       -Y, --retry[=N]             retry every seconds for N seconds for first socket connection\n");
	printf("       -V, --version               display version info and exit\n");
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
				 "hB::b::D:i::u::p::q::T::t::I:nQSNXFR:LvdVYW",
#else
				 "hB::b::D:i::u::T::t::nQSNXFR:LvdVY",
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
			funos_sock.port_num = opt_portnum(optarg,
							  DPC_PORT);
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
							      FUNQ_DEV_NAME);
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
			funos_sock.port_num = DPC_PORT;
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
		if (!_nocli_script_mode)
			_verbose_log = true;
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
