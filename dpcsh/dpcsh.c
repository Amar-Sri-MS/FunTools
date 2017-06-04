/* test dpcsock functionality */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <termios.h>            //termios, TCSANOW, ECHO, ICANON
#include <sys/types.h>
#include <signal.h>            //termios, TCSANOW, ECHO, ICANON
#include <pthread.h>

#include <funos/fun_utils.h>
#include <funos/fun_json.h>
#include <funos/fun_commander.h>

#define SOCK_NAME	"/tmp/funos-dpc.sock"

static inline void _setnosigpipe(int const fd) {
#ifdef __APPLE__
    int yes = 1;
    (void)setsockopt(fd, SOL_SOCKET, SO_NOSIGPIPE, &yes, sizeof(yes));
#else
    /* unfortunately Linux does not support SO_NOSIGPIPE... */
    signal(SIGPIPE, SIG_IGN);
#endif
}

static int _open_sock(const char *name) {
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

static void ensure_buffer_big_enough(OUT char **line, OUT size_t *capa, size_t len) {
    if (len + 1 >= *capa) {
        *capa = (*capa * 2) + 1;
	*line = realloc(*line, *capa);
    }
}
static void push_char(char **line, OUT size_t *capa, OUT size_t *len, char ch) {
    ensure_buffer_big_enough(line, capa, (*len)+1);
    (*line)[(*len)++] = ch;
}
static void push_string(char **line, OUT size_t *capa, OUT size_t *len, char *str) {
    size_t l = strlen(str);
    ensure_buffer_big_enough(line, capa, (*len)+l);
    strcpy((*line) + (*len), str);
    *len += l;
}

static char **history = NULL; // most recent first
static int history_count = 0;

static void append_to_history(char *line) {
    size_t l = strlen(line);
    if (!l) return;
    if (line[l-1] == '\n') l--; // exclude '\n'
    if (!l) return;
    history = realloc(history, (history_count+1) * sizeof(char *));
    if (history_count != 0) {
        char *last = history[history_count-1];
	if (!strncmp(last, line, l) && !last[l]) return; // same - don't add
    }
    history[history_count++] = strndup(line, l);
    // printf("History : %d\n", history_count);
}
static void use_history(char **line, OUT size_t *capa, OUT size_t *len, int history_index) {
    if (!history) return; // no effect
    if (history_index >= history_count) return;
    char *str = history[history_index];
    // erase current characters
    for (int i = 0; i < (*len); i++) printf("%c[D", 27);
    // kill rest of line
    printf("%c[K", 27);
    printf("%s", str);
//		fflush(stdout);
    *len = 0;
    push_string(line, capa, len, str);
}
static void history_previous(char **line, OUT size_t *capa, OUT size_t *len, OUT int *history_index) {
    if ((* history_index) > 0) (*history_index)--;
    use_history(line, capa, len, *history_index);
}
static void history_next(char **line, OUT size_t *capa, OUT size_t *len, OUT int *history_index) {
    if ((*history_index) + 1 < history_count) (*history_index )++;
    use_history(line, capa, len, *history_index);
}
static int getline_with_history(OUT char **line, OUT size_t *capa) {
    size_t len = 0;
    int current_history = history_count;
    ensure_buffer_big_enough(line, capa, 16);
    while (true) {
        char ch = getchar();
	if (ch == 14 /* ^N */) {
	    history_next(line, capa, &len, &current_history);
	} else if (ch == 16 /* ^P */) {
	    history_previous(line, capa, &len, &current_history);
        } else if ((ch == EOF) || (ch == 4 /* ^D*/)) {
	    (*line)[len] = 0;
   	    append_to_history(*line);
	    return len;
	} else if (ch == 27) {
	    if (getchar() != 91) continue;
	    char ch2 = getchar();
	    if (ch2 == 'A') {
    		history_previous(line, capa, &len, &current_history);
	    } else if (ch2 == 'B') {
    		history_next(line, capa, &len, &current_history);
	    } else {
		// printf("Ignoring ch2=%d\n", ch2);
	    }
	} else if (ch == '\n') {
	    write(STDOUT_FILENO, &ch, 1);
	    push_char(line, capa, &len, ch);
	    (*line)[len] = 0;
   	    append_to_history(*line);
	    return len;
	} else if (ch == 127 /*DEL*/) {
            if (len > 0) {
	        printf("%c[D", 27);
	        printf("%c[K", 27);
		len--;
	    }
	} else {
	// printf("GOT ch=%d\n", ch);
	    write(STDOUT_FILENO, &ch, 1);
	    push_char(line, capa, &len, ch);
	}
    }
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

// We pass the sock INOUT in order to be able to reestablish a connection if the server went down and up
static void _do_process_cmd(INOUT int *sock, char *line, ssize_t read, uint64_t *tid)
{

	if ((read == 1) && (line[0] == '\n')) return; // skip blank lines

	const char *error;
        struct fun_json *json = fun_commander_line_to_command(line, tid, &error);
        if (!json) {
            printf("could not parse: %s\n", error);
            return;
        }
        fun_json_printf(INPUT_COLORIZE "input => %s" NORMAL_COLORIZE "\n", json);
        bool ok = fun_json_write_to_fd(json, *sock);
	if (!ok) {
	    // try to reopen pipe
	    printf("Write to socket failed - reopening socket\n");
	    *sock = _open_sock(SOCK_NAME);
	    if (*sock <= 0) {
		printf("*** Can't reopen socket\n");
	        fun_json_release(json);
		return;
	     }
	     ok = fun_json_write_to_fd(json, *sock);
	}
        fun_json_release(json);
        if (!ok) {
	    printf("*** Write to socket failed\n");
	    return;
	}
        /* receive a reply */
        struct fun_json *output = fun_json_read_from_fd(*sock);
        if (!output) {
            printf("invalid json returned\n");
            return;
        }
        fun_json_printf(OUTPUT_COLORIZE "output => %s" NORMAL_COLORIZE "\n", output);
        fun_json_release(output);
}

static void _do_interactive(int sock) {
    char *line = NULL;
    size_t capa = 0;
    ssize_t read;
    uint64_t tid = 1;
    static struct termios tios;
    tcgetattr(STDIN_FILENO, &tios);
    tios.c_lflag &= ~(ICANON | ECHO);          
    tcsetattr(STDIN_FILENO, TCSANOW, &tios);
    while ((read = getline_with_history(&line, &capa)) > 0) {
	_do_process_cmd(&sock, line, read, &tid);
    }

    free(line);
}

/* XXX */
extern int run_webserver(int jsock, int port);
#define MAXLINE (512)

int json_handle_req(int jsock, const char *path, char *buf, int *size) {
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
        bool ok = fun_json_write_to_fd(json, jsock);
        fun_json_release(json);
        if (!ok)
		return -1;
	
        /* receive a reply */
        struct fun_json *output = fun_json_read_from_fd(jsock);
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

static ssize_t read_more(int fd, INOUT char **buffer, INOUT size_t *len, INOUT size_t *capacity) {
	size_t wanted = 1024;
	while (*len + wanted + 1 > *capacity) {
		*capacity += *capacity + 1;
		*buffer = realloc(*buffer, *capacity);
	}
	ssize_t n = read(fd, *buffer + *len, wanted);
	// printf("Read %ld chars\n", n);
	if (n > 0) {
		*len += n;
		(*buffer)[*len] = 0;
	}
	return n;
}

static ssize_t read_at_least_one_line(int fd, INOUT char **buffer, INOUT size_t *len, INOUT size_t *capacity) {
	ssize_t so_far = 0;
	while (true) {
		ssize_t n = read_more(fd, buffer, len, capacity);
		if (n == -1) return n;
		if (n == 0) return so_far;
		so_far += n;
		if (strchr(*buffer, '\n')) return so_far;
	}
}

static inline void write_string(int client_sock, const char *str, bool write_zero) {
	write(client_sock, str, strlen(str));
	//	if (write_zero) write(client_sock, "", 1);
}

static bool push_to_dpc_get_reply_to_client(const char *line, INOUT uint64_t *tid, int dpc_sock,  int client_sock) {
	// return true if we should continue to process lines
	const char *error;
	struct fun_json *json = fun_commander_line_to_command(line, tid, &error);
	if (!json) {
		char buf[1000];
		snprintf(buf, sizeof(buf), "*** Could not parse: %s - line: %s\n", error, line);
		write_string(client_sock, buf, true);
		return true;
	}
	bool ok = fun_json_write_to_fd(json, dpc_sock);
	fun_json_release(json);
	if (!ok) {
		printf("*** Connection to dpc server failed\n");
		return false;
	}
	/* receive a reply */
	struct fun_json *output = fun_json_read_from_fd(dpc_sock);
	if (!output) {
		write_string(client_sock, "*** invalid json returned\n", true);
		return true;
	}
	if (output->type == fun_json_error_type) {
		printf("Got error reply '%s'\n", output->error_message);
		printf("*** Received error from dpc server\n");
		write_string(client_sock, "*** ", false);
		write_string(client_sock, output->error_message, false);
		write_string(client_sock, "\n", true);
		fun_json_release(output);
		return true;
	}
	char *pp2 = fun_json_to_text(output);
	fun_json_release(output);
	if (!pp2) {
		printf("*** No output from dpc server\n");
		return true;
	}
	printf("Got reply '%s'\n", pp2);
	write_string(client_sock, pp2, false);
	write_string(client_sock, "\n", true);
	free(pp2);
	return true;
}

static void *handle_text_thread(void *arg) {
	int client_sock = (uintptr_t) arg;
	printf("New client on socket %d\n", client_sock);
	int dpc_sock = _open_sock(SOCK_NAME);
	if (dpc_sock <= 0) {
		printf("*** Can't open socket to dpc\n");
		return NULL;
	}
	_setnosigpipe(dpc_sock);
	uint64_t tid = 1;
	size_t capacity = 1000;
	char *buffer = malloc(capacity);
	size_t len = 0;
	while (true) {
		ssize_t n = read_at_least_one_line(client_sock, &buffer, &len, &capacity);
		if (n == -1) {
			printf("*** Socket in error\n");
			break;
		}
		if (!n) {
			if (!len) break;
			printf("Received '%s' then EOF\n", buffer);
			push_to_dpc_get_reply_to_client(buffer, &tid, dpc_sock, client_sock);
			break;
		}
		char *line_break = strchr(buffer, '\n');
		while (line_break) {
			*line_break = 0;
			printf("Received line '%s'\n", buffer);
			bool ok = push_to_dpc_get_reply_to_client(buffer, &tid, dpc_sock, client_sock);
			if (!ok) break;
			size_t this_line_len = line_break - buffer + 1;
			memmove(buffer, line_break+1, len - this_line_len + 1);
			len -= this_line_len;
			line_break = strchr(buffer, '\n');
		}
	}
	free(buffer);
	close(dpc_sock);
	printf("Closed client %d\n", client_sock);
	return NULL;
}

static void run_text_proxy(const char *client_sock_name) {
	printf("Publishing %s\n", client_sock_name);
	int listen_sock;
	struct sockaddr_un local = { 0 }, remote = { 0 };
	socklen_t s;

	/* create a server socket */
	listen_sock = socket(AF_UNIX, SOCK_STREAM, 0);
	assert(listen_sock > 0);

	local.sun_family = AF_UNIX;

	snprintf(local.sun_path, sizeof(local.sun_path), "%s", client_sock_name);
	unlink(local.sun_path);

	if (bind(listen_sock, (struct sockaddr *)&local, sizeof(local)) == -1) {
		perror("bind");
		exit(1);
	}

	if (listen(listen_sock, 1) == -1) {
		perror("listen");
		exit(1);
	}

	/* main server loop */
	while(1) {
		// printf("[dpcsock] Listening for connection\n");
		s = sizeof(remote);
		int rsock = accept(listen_sock,
				   (struct sockaddr *)&remote, &s);
		_setnosigpipe(rsock);

		if (rsock == -1) {
			perror("accept");
		} else {
			pthread_t _handle_thread;
			int r = pthread_create(&_handle_thread, NULL,
					   handle_text_thread, (void*)(uintptr_t)rsock);
			if (r) {
				perror("pthread_create");
				exit(1);
			}
		}
	}
}

#define PORTNO 9001

#define HELP	\
	"\t--help: 	you know\n"\
	"\t--http_proxy:	webproxy, browse 'http://localhost:9001'\n"\
	"\t--nocli:	no cli mode, type cmd as arg\n"\
	"\t--text_proxy:	text JSON proxy, use port '/tmp/funos-dpc-text.sock'\n"

static void _do_cli(int argc, char *argv[], int sock) {
	uint64_t tid = 1;
	char buf[512];
	int n = 0;
	for (int i = 2; i < argc; i++) {
		n += snprintf(buf + n, sizeof(buf) - n, "%s ", argv[i]);
		printf("buf=%s n=%d\n", buf, n);
	}

	size_t len = strlen(buf);
	buf[--len] = 0;	// trim the last space
	printf(">> single cmd [%s] len=%zd\n", buf, len);
	_do_process_cmd(&sock, buf, len, &tid);
}

int main(int argc, char *argv[]) {
	bool http_proxy_mode = false;
	bool text_proxy_mode = false;
	bool interractive_mode = false;

	if (argc < 2) {
		interractive_mode = true;
	} else if (strcmp(argv[1], "--http_proxy") == 0) {
		http_proxy_mode = true;
	} else if (strcmp(argv[1], "--text_proxy") == 0) {
		text_proxy_mode = true;
	} else if (strcmp(argv[1], "--help") == 0) {
		printf("Help: \n" HELP "\n");
		return 0;
	} else if (argc > 2 && strcmp(argv[1], "--nocli") == 0) {
		interractive_mode = false;
	} else {
		printf("*** Usage: \n" HELP "\n");
		exit(2);
	}
	printf("FunOS Dataplane Control Shell%s\n", http_proxy_mode ? ": HTTP proxy mode" : text_proxy_mode ? ": Text JSON proxy mode" : "");

	/* open a socket to FunOS */
	int sock = _open_sock(SOCK_NAME);
	if (sock <= 0) {
		printf("*** Can't open socket\n");
		exit(1);
	}
	if (http_proxy_mode) {
		run_webserver(sock, PORTNO);
	} else if (text_proxy_mode) {
		run_text_proxy("/tmp/funos-dpc-text.sock");
	} else if (interractive_mode) {
		_do_interactive(sock);
	} else {
		_do_cli(argc, argv, sock);
	}
	return 0;
}
