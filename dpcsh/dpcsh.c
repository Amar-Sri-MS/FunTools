/* test dpcsock functionality */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>

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

static void _do_interactive(int sock) {
    char *line = NULL;
    size_t len = 0;
    ssize_t read;
    int64_t tid = 1;

    while ((read = getline(&line, &len, stdin)) > 0) {
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
	
	printf("FunOS Dataplane Control test%s\n",
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
