/* test dpcsock functionality */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <termios.h>            //termios, TCSANOW, ECHO, ICANON

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

static void _do_interactive(int sock) {
    char *line = NULL;
    size_t capa = 0;
    ssize_t read;
    int64_t tid = 1;
    static struct termios tios;
    tcgetattr(STDIN_FILENO, &tios);
    tios.c_lflag &= ~(ICANON | ECHO);          
    tcsetattr(STDIN_FILENO, TCSANOW, &tios);
    while ((read = getline_with_history(&line, &capa)) > 0) {
	if ((read == 1) && (line[0] == '\n')) continue; // skip blank lines
        struct fun_json *json = fun_commander_line_to_command(line, &tid);
        if (!json) {
            printf("could not parse\n");
            return;
        }
        char *pp2;
        pp2 = fun_json_to_text(json);
        printf("input => %s\n", pp2);
        free(pp2);
        bool ok = fun_json_write_to_fd(json, sock);
	if (!ok) {
	    // try to reopen pipe
	    printf("Write to socket failed - reopening socket\n");
	    sock = _open_sock(SOCK_NAME);
	    if (sock <= 0) {
		printf("*** Can't reopen socket\n");
	        fun_json_release(json);
		return;
	     }
	     ok = fun_json_write_to_fd(json, sock);
	}
        fun_json_release(json);
        if (!ok) {
	    printf("*** Write to socket failed\n");
	    return;
	}
        /* receive a reply */
        struct fun_json *output = fun_json_read_from_fd(sock);
        if (!output) {
            printf("invalid json returned\n");
            return;
        }
        pp2 = fun_json_to_text(output);
        printf("output => %s\n", pp2);
        free(pp2);
        fun_json_release(output);
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
	int64_t tid = 1;
	
	snprintf(line, MAXLINE, "peek %s", path);
	
        struct fun_json *json = fun_commander_line_to_command(line, &tid);
        if (!json) {
		printf("could not parse '%s'\n", line);
		return -1;
        }
        char *pp2;
        pp2 = fun_json_to_text(json);
        printf("input => %s\n", pp2);
        free(pp2);
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
        pp2 = fun_json_to_text(output);
        printf("output => %s\n", pp2);

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

#define PORTNO 9001

int
main(int argc, char *argv[])
{
	int sock;
	int proxy_mode = 0;
	
	if ((argc == 2)
	    && (strcmp(argv[1], "--proxy") == 0))
		proxy_mode = 1;
	
	printf("FunOS Dataplane Control Shell%s\n",
	       proxy_mode ? ": proxy mode" : "");

	/* open a socket to FunOS */
	sock = _open_sock(SOCK_NAME);
	if (sock <= 0) {
	    printf("*** Can't open socket\n");
	    exit(1);
	}
	if (!proxy_mode)
		_do_interactive(sock);
	else
		run_webserver(sock, PORTNO);
}
