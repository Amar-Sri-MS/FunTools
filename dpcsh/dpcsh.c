/* test dpcsock functionality */

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <getopt.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <termios.h>            //termios, TCSANOW, ECHO, ICANON
#include <sys/types.h>
#include <signal.h>            //termios, TCSANOW, ECHO, ICANON
#include <pthread.h>
#include <netinet/in.h>		// TCP socket
#include <arpa/inet.h>
#include <getopt.h>
#include <sys/select.h>

#define PLATFORM_POSIX	1

#include <utils/threaded/fun_json.h>
#include <utils/threaded/fun_commander.h>
#include <utils/threaded/fun_malloc_threaded.h>
#include <utils/common/base64.h>

#define SOCK_NAME	"/tmp/funos-dpc.sock"      /* default FunOS socket */
#define PROXY_NAME      "/tmp/funos-dpc-text.sock" /* default unix proxy name */
#define DPC_PORT        40220   /* default FunOS port */
#define DPC_PROXY_PORT  40221   /* default TCP proxy port */
#define DPC_SRV_PORT    40222   /* default dpcuart listen port */
#define HTTP_PORTNO     9001    /* default HTTP listen port */

/* handy socket abstraction */
enum sockmode {
	SOCKMODE_UNUSED,
	SOCKMODE_IP,
	SOCKMODE_UNIX,
};

struct dpcsock {

	/* configuration */
	enum sockmode mode;      /* whether & how this is used */
	bool server;             /* listen/accept instead of connect */
	bool base64;             /* talk base64 over this socket */
	const char *socket_name; /* unix socket name */
	uint16_t port_num;       /* TCP port number */

	/* runtime */
	int fd;                  /* connected fd */
	int listen_fd;           /* fd if this is a server */
};

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

static char * use_history(char *line, size_t len, int history_index)
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

static char * history_previous(char *line, size_t len, OUT int *history_index)
{
    if ((* history_index) > 0)
	    (*history_index)--;
    return use_history(line, len, *history_index);

}
static char * history_next(char *line, size_t len, OUT int *history_index)
{
    if ((*history_index) + 1 < history_count)
	    (*history_index )++;
    return use_history(line, len, *history_index);
}

static char *getline_with_history(OUT size_t *nbytes)
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
			if (ch == '\n')
				write(STDOUT_FILENO, &ch, 1);
			line[len] = '\0';
			append_to_history(line);
			*nbytes = len;
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
			line[len++] = ch;
			line[len] = '\0';
		}
	}
}


/* socket routines */
static int _open_sock_inet(uint16_t port)
{
	int sock = 0;
	struct sockaddr_in serv_addr;

	if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
	{
		printf("\n Socket creation error \n");
		return sock;
	}
	_setnosigpipe(sock);

	memset(&serv_addr, '0', sizeof(serv_addr));

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_port = htons(port);

	// Convert IPv4 and IPv6 addresses from text to binary form
	if(inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)<=0)
	{
		printf("\nInvalid address/ Address not supported \n");
		return -1;
	}

	if (connect(sock, (struct sockaddr *)&serv_addr,
		    sizeof(serv_addr)) < 0)
	{
		printf("*** Can't connect\n");
		perror("connect");
		exit(1);
	}

	return sock;
}

static int _open_sock_unix(const char *name) {
	int sock = socket(AF_UNIX, SOCK_STREAM, 0);
	if (sock <= 0) return sock;
	_setnosigpipe(sock);
	struct sockaddr_un server = { .sun_family = AF_UNIX };
	strcpy(server.sun_path, name);
	int r = connect(sock, (struct sockaddr *)&server, sizeof(server));
	if (r) {
		printf("*** Can't connect: %d\n", r);
		perror("connect");
		exit(1);
	}
	return sock;
}

static void _listen_sock_init(struct dpcsock *sock)
{
	struct sockaddr_in local_inet = { 0 }, remote_inet = { 0 };
	struct sockaddr_un local_unix = { 0 }, remote_unix = { 0 };
	struct sockaddr *local, *remote;
	socklen_t s;
	int optval = 1;

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
		unlink(local_unix.sun_path);

		local = (struct sockaddr *) &local_unix;
		remote = (struct sockaddr *) &remote_unix;
		s = sizeof(struct sockaddr_un);

	} else {
		/* create a server socket */
		sock->listen_fd = socket(AF_INET, SOCK_STREAM, 0);
		assert(sock->listen_fd > 0);

		if (setsockopt(sock->listen_fd, SOL_SOCKET, SO_REUSEADDR,
			       (const void *)&optval , sizeof(int)) < 0) {
			perror("setsockopt(SO_REUSEADDR)");
			exit(1);
		}

		/* set socket parameters */

		printf("Publishing on port %d\n", sock->port_num);

		local_inet.sin_family = AF_INET;
		local_inet.sin_addr.s_addr = INADDR_ANY;
		local_inet.sin_port = htons(sock->port_num);

		local = (struct sockaddr *) &local_inet;
		remote = (struct sockaddr *) &remote_inet;
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

	/* send it */
	r = write(fd, b64buf, strlen(b64buf));

	if (r < 0)
		return false;

	/* frame it with a newline */
	if (write(fd, "\n", 1) < 0)
		return false;

	return true;
}

/* read a line of input from the fd */
#define BUF_SIZE (1024)
static char *_read_a_line(struct dpcsock *sock, size_t *nbytes)
{
	char *buf = NULL;
	size_t size = 0, pos = 0;
	bool echo = false;
	int fd;
	int r;
	
	if ((sock->mode == SOCKMODE_UNUSED) && !sock->base64) {
		/* fancy pants line editor on stdin */
		printf("readline\n");
		buf = getline_with_history(nbytes);
		return buf;
	}

	if ((sock->mode == SOCKMODE_UNUSED) && sock->base64) {
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
		r = read(fd, &buf[pos], 1);

		if (r <= 0) {
			printf("**** remote hung up / error\n");
			free(buf);
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

	return buf;
}

/* read a line of input from the fd and try to decode it (FunOS
 * resonse side only)
 */
static uint8_t *_base64_get_buffer(struct dpcsock *sock,
				   size_t *nbytes, bool retry)
{
	char *buf = NULL;
	uint8_t *binbuf = NULL;
	ssize_t r;

do_retry:
	
	if (sock->fd == STDOUT_FILENO) {
		printf("funos response => ");
		fflush(stdout);
	}

	/* read the input */
	buf = _read_a_line(sock, nbytes);

	if (!buf)
		return NULL;
	
	/* now we have a buffer, decode it. buffer is oversize. Meh. */
	binbuf = malloc(*nbytes);
	if (binbuf == NULL) {
		printf("couldn't allocate input buffer\n");
		exit(1);
	}

	r = base64_decode(binbuf, *nbytes, buf);
	if (r < 0) {
		printf("bad decode: %s\n", buf);
		free(buf);
		
		if (retry) {
			/* if we want a synchronous response */
			free(binbuf);
			goto do_retry;
		}
		
		return NULL;
	}

	/* tell them how many bytes were actually decoded */
	*nbytes = (size_t) r;

	free(buf);
	return binbuf;
}

/* dpcsocket abstraction */

int dpcsocket_connnect(struct dpcsock *sock)
{
	assert(sock != 0);

	/* unused == no-op */
	if (sock->mode == SOCKMODE_UNUSED)
		return 0;

	if (sock->server) {
		/* setup the server socket*/
		if (sock->listen_fd <= 0)
			_listen_sock_init(sock);

		/* wait for someone to connect */
		_listen_sock_accept(sock);
	} else {
		if (sock->mode == SOCKMODE_UNIX)
			sock->fd = _open_sock_unix(sock->socket_name);
		else
			sock->fd = _open_sock_inet(sock->port_num);
	}

	/* return non-zero on failure */
	return (sock->fd < 0);
}

/* disambiguate json */
static bool _write_to_sock(struct fun_json *json, struct dpcsock *sock)
{
	size_t size;

	if (!sock->base64) {
		/* easy case */
		return fun_json_write_to_fd(json, sock->fd);
	}

	/* base64 case */
	uint8_t *ptr = fun_json_to_binary(json, &size);
	bool ok = _base64_write(sock, ptr, size);

	fun_free_threaded(ptr, size);

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
		size_t r, max;
		buffer = _base64_get_buffer(sock, &max, retry);
		if (!buffer)
			return NULL;
		r = fun_json_binary_serialization_size(buffer, max);
		if (r <= max) {
			json = fun_json_create_from_parsing_binary(buffer, r);
		}
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

#define INPUT_COLORIZE	PRELUDE RED POSTLUDE
#define OUTPUT_COLORIZE	PRELUDE BLUE POSTLUDE
#define NORMAL_COLORIZE	PRELUDE BLACK POSTLUDE

// We pass the sock INOUT in order to be able to reestablish a
// connection if the server went down and up
static bool _do_send_cmd(struct dpcsock *sock, char *line,
			 ssize_t read, uint64_t *tid)
{

	if ((read == 1) && (line[0] == '\n'))
		return false; // skip blank lines

	const char *error;
        struct fun_json *json = fun_commander_line_to_command(line, tid,
							      &error);
        if (!json) {
            printf("could not parse: %s\n", error);
            return false;
        }
        fun_json_printf(INPUT_COLORIZE "input => %s" NORMAL_COLORIZE "\n",
			json);
        bool ok = _write_to_sock(json, sock);
	if (!ok) {
		// try to reopen pipe
		printf("Write to socket failed - reopening socket\n");
		dpcsocket_connnect(sock);

		if (sock->fd <= 0) {
			printf("*** Can't reopen socket\n");
			fun_json_release(json);
			return false;
		}
		ok = _write_to_sock(json, sock);
	}
        fun_json_release(json);
        if (!ok) {
		printf("*** Write to socket failed\n");
		return false;
	}

	return true;
}

static void _do_recv_cmd(struct dpcsock *sock, bool retry)
{
	/* receive a reply */
        struct fun_json *output = _read_from_sock(sock, retry);
        if (!output) {
		if (retry)
			printf("invalid json returned\n");
		return;
        }
        fun_json_printf(OUTPUT_COLORIZE "output => %s" NORMAL_COLORIZE "\n",
			output);
        fun_json_release(output);
}

static void _do_interactive(struct dpcsock *funos_sock,
			    struct dpcsock *cmd_sock)
{
    char *line = NULL;
    size_t read;
    uint64_t tid = 1;
    int r, nfds = 0;
    bool ok;

    if (cmd_sock->mode == SOCKMODE_UNUSED) {
	    /* enable per-character input for interactive input */
	    static struct termios tios;
	    tcgetattr(STDIN_FILENO, &tios);
	    tios.c_lflag &= ~(ICANON | ECHO);
	    tcsetattr(STDIN_FILENO, TCSANOW, &tios);
    }


    fd_set fds;
    while (1) {
	    
	    /* if a socket went away, try and reconnect */
	    if (funos_sock->fd == -1) {
		    dpcsocket_connnect(funos_sock);
	    }

	    if (cmd_sock->fd == -1) {
		    dpcsocket_connnect(cmd_sock);
	    }
 
	    /* configure the fd set */
	    FD_ZERO(&fds);
	    FD_SET(cmd_sock->fd, &fds);
	    nfds = cmd_sock->fd;
	    if (funos_sock->mode != SOCKMODE_UNUSED) {
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

	    if (FD_ISSET(cmd_sock->fd, &fds)) {
		    // printf("user input\n");
		    line = _read_a_line(cmd_sock, &read);

		    if (read == 0) /* ^D */
			    break;

		    assert(line != NULL);

		    /* no base64 on the cmd end of things */
		    
		    ok = _do_send_cmd(funos_sock, line, read, &tid);

		    /* for loopback we have to do this inline */
		    if (ok)
			    _do_recv_cmd(funos_sock, true);
	    }

	    if (FD_ISSET(funos_sock->fd, &fds)) {
		    // printf("funos input\n");
		    _do_recv_cmd(funos_sock, false);
	    }
    }

    free(line);
}

/* XXX */
extern int run_webserver(int funos_sock, int cmd_listen_sock);

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
	run_webserver(funos_sock->fd, cmd_sock->listen_fd);
}

#define MAXLINE (512)

int json_handle_req(struct dpcsock *jsock, const char *path,
		    char *buf, int *size)
{
	printf("got jsock request for '%s'\n", path);
	char line[MAXLINE];
	int r = -1;
	uint64_t tid = 1;

	/* rewrite request for root */
	if (strcmp(path, "/") == 0)
		path = "\"\"";
	else if (strcmp(path, ".") == 0)
		path = "\"\"";

	snprintf(line, MAXLINE, "peek %s", path);
	const char *error;
        struct fun_json *json = fun_commander_line_to_command(line, &tid, &error);
        if (!json) {
		printf("could not parse '%s': %s\n", line, error);
		return -1;
        }
        fun_json_printf("input => %s\n", json);
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
        char *pp2 = fun_json_to_text(output);
        printf("output => %s\n", pp2);

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


static void _do_cli(int argc, char *argv[],
		    struct dpcsock *funos_sock, int startIndex)
{
	uint64_t tid = 1;
	char buf[512];
	int n = 0;
	bool ok;

	for (int i = startIndex; i < argc; i++) {
		n += snprintf(buf + n, sizeof(buf) - n, "%s ", argv[i]);
		printf("buf=%s n=%d\n", buf, n);
	}

	size_t len = strlen(buf);
	buf[--len] = 0;	// trim the last space
	printf(">> single cmd [%s] len=%zd\n", buf, len);
	ok = _do_send_cmd(funos_sock, buf, len, &tid);
	if (ok)
		_do_recv_cmd(funos_sock, true);
}

/** argument parsing **/

/* help for port numbers*/
static uint16_t opt_portnum(char *optarg, uint16_t dflt)
{
	if (optarg == NULL)
		return dflt;

	return strtoul(optarg, NULL, 0);
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
	{ "help",          no_argument,       NULL, 'h' },
	{ "base64_srv",    optional_argument, NULL, 'B' },
	{ "inet_sock",     optional_argument, NULL, 'i' },
	{ "unix_sock",     optional_argument, NULL, 'u' },
	{ "http_proxy",    optional_argument, NULL, 'H' },
	{ "tcp_proxy",     optional_argument, NULL, 'T' },
	{ "text_proxy",    optional_argument, NULL, 't' },
	{ "nocli",         no_argument,       NULL, 'n' },
	{ "manual_base64", no_argument,       NULL, 'N' },

	/* end */
	{ NULL, 0, NULL, 0 },
};


static void usage(const char *argv0)
{
	printf("usage: %s [<mode> [option]]", argv0);
	printf("       by default connect as a --inet_sock\n");
	printf("       --help                  this text\n");
	printf("       --base64_srv [port]     listen as a server port on IP using base64 (dpcuart to qemu)\n");
	printf("       --inet_sock  [port]     connect as a client port over IP\n");
	printf("       --unix_sock  [sockname] connect as a client port over unix sockets\n");
	printf("       --http_proxy [port]     listen as an http proxy\n");
	printf("       --tcp_proxy  [port]     listen as a tcp proxy\n");
	printf("       --text_proxy [port]     listen as a tcp proxy\n");
	printf("       --nocli                 issue request from command-line arguments and terminate\n");
	printf("       --manual_base64         just translate base64 back and forward\n");
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
	bool one_shot;  /* run a single command and terminate */
	int ch, first_unknown = -1;
	struct dpcsock funos_sock; /* connection to FunOS */
	struct dpcsock cmd_sock;   /* connection to commanding agent */

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


	/* default connection to FunOS posix simulator dpcsock */
	memset(&funos_sock, 0, sizeof(funos_sock));
	funos_sock.mode = SOCKMODE_UNIX;
	funos_sock.server = false;
	funos_sock.socket_name = SOCK_NAME;

	/* default command connection is console (so socket disabled) */
	memset(&cmd_sock, 0, sizeof(cmd_sock));
	cmd_sock.mode = SOCKMODE_UNUSED;
	cmd_sock.socket_name = NULL; /* safety */


	while ((ch = getopt_long(argc, argv,
				 "hs::i::u::H::T::t::nN",
				 longopts, NULL)) != -1) {

		switch(ch) {
			/** help **/
		case 'h':
			usage(argv[0]);
			exit(0);

			/** mode parsing **/

		case 'B':  /* base64 server */

			/* run as base64 mode for dpcuart */
			funos_sock.base64 = true;
			funos_sock.mode = SOCKMODE_IP;
			funos_sock.server = true;
			funos_sock.port_num = opt_portnum(optarg,
							  DPC_SRV_PORT);
			mode = MODE_INTERACTIVE;

			break;
		case 'i':  /* inet client */

			/* in case this got stamped over... */
			funos_sock.mode = SOCKMODE_IP;
			cmd_sock.server = false;
			funos_sock.port_num = opt_portnum(optarg,
							  DPC_PORT);

			mode = MODE_INTERACTIVE;

			break;
		case 'u':  /* unix domain client */

			funos_sock.mode = SOCKMODE_UNIX;
			cmd_sock.server = false;
			funos_sock.socket_name = opt_sockname(optarg,
							      SOCK_NAME);

			mode = MODE_INTERACTIVE;

			break;
		case 'H':  /* http proxy */

			cmd_sock.mode = SOCKMODE_IP;
			cmd_sock.server = true;
			funos_sock.port_num = opt_portnum(optarg,
							  HTTP_PORTNO);

			mode = MODE_HTTP_PROXY;

			break;
		case 'T':  /* TCP proxy */

			cmd_sock.mode = SOCKMODE_IP;
			cmd_sock.server = true;
			funos_sock.port_num = opt_portnum(optarg,
							  DPC_PROXY_PORT);

			mode = MODE_PROXY;
			break;

		case 't':  /* text proxy */

			cmd_sock.mode = SOCKMODE_UNIX;
			cmd_sock.server = true;
			funos_sock.socket_name = opt_sockname(optarg,
							      PROXY_NAME);

			mode = MODE_PROXY;

			break;

			/** other options **/

		case 'n':  /* "nocli" -- run one command and exit */
			one_shot = true;
			break;
		case 'N':  /* manual base64 mode -- drive a UART by hand */

			funos_sock.base64 = true;
			funos_sock.server = false;
			funos_sock.mode = SOCKMODE_UNUSED;
			funos_sock.fd = STDOUT_FILENO;
			mode = MODE_NOCONNECT;

			break;
		default:
			usage(argv[0]);
			exit(1);
		}

		if (first_unknown != -1)
			break;
	}

	/* this only makes sense for local input */
	if (one_shot && (mode != MODE_INTERACTIVE)) {
		usage(argv[0]);
		exit(1);
	}
		
	/* make an announcement as to what we are */
	printf("FunOS Dataplane Control Shell");

	switch (mode) {
	case MODE_INTERACTIVE:
		/* do nothing */
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

	/* start by opening the socket to FunOS */
	int r = dpcsocket_connnect(&funos_sock);
	printf("FunOS is connected!\n");

	if (r != 0) {
		printf("*** Can't open socket\n");
		exit(1);
	}

	switch(mode) {
	case MODE_HTTP_PROXY:
		_do_run_webserver(&funos_sock, &cmd_sock);
		break;
	case MODE_PROXY:
	case MODE_INTERACTIVE:
	case MODE_NOCONNECT: {
		if (one_shot)
			_do_cli(argc, argv, &funos_sock, optind);
		else
			_do_interactive(&funos_sock, &cmd_sock);
	}

	}

	return 0;
}
