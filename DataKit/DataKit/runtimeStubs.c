//
//  runtimeStubs.c
//  DataKit
//
//  Created by Bertrand Serlet on 7/22/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

#include <sys/stat.h>

#include <stdlib.h>
#include <assert.h>
#include <sys/un.h>
#include <sys/socket.h>
#include <string.h>
#include <stdio.h>


// WORKAROUND
// Not defining static_assert causes an error
#define static_assert(x,y)

#include <utils/threaded/fun_json.h>

// Returns <=0 on error
extern int dpcclient_open_socket(void);

extern void dpcclient_test(void);

extern NULLABLE CALLER_TO_FREE const char *dpcrun_command(INOUT int *sock, const char *verb, const char *arguments_array);


int64_t statSizeForFile(const char *cpath) {
	// Curiously, can't find stat() in Swift
	struct stat buf;
	int err = stat(cpath, &buf);
	if (err == 0) return buf.st_size;
	return -1;
}

//
//  dpcclient.c
//  funos_viewer
//
//  Created by Bertrand Serlet on 4/18/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

static inline void _setnosigpipe(int const fd) {
#ifdef __APPLE__
	int yes = 1;
	(void)setsockopt(fd, SOL_SOCKET, SO_NOSIGPIPE, &yes, sizeof(yes));
#else
	/* unfortunately Linux does not support SO_NOSIGPIPE... */
	signal(SIGPIPE, SIG_IGN);
#endif
}

int dpcclient_open_socket(void) {
	int sock = socket(AF_UNIX, SOCK_STREAM, 0);
	if (sock <= 0) return sock;
	_setnosigpipe(sock);
	struct sockaddr_un server = { .sun_family = AF_UNIX };
	strcpy(server.sun_path, "/tmp/funos-dpc.sock");
	int r = connect(sock, (struct sockaddr *)&server, sizeof(server));
	if (r || (sock <= 0)) {
		printf("*** Can't connect to dpcserver; try to run 'build/funos-posix --dpc-server'\n");
		return 0;
	}
	return sock;
}

void dpcclient_test(void) {
	int sock = dpcclient_open_socket();
	if (sock <= 0) {
		printf("*** Can't connect to dpcserver; try to run 'build/funos-posix --dpc-server'\n");
		return;
	}
	struct fun_json *json = fun_json_create_from_text("{arguments: [], tid: 1, verb: help}");
	if (!json) {
		printf("could not parse\n");
		return;
	}
	bool ok = fun_json_write_to_fd(json, sock);
	fun_json_release(json);
	if (!ok) return;
	/* receive a reply */
	struct fun_json *output = fun_json_read_from_fd(sock);
	if (!output) {
		printf("*** invalid json returned in dpcclient_test()\n");
		return;
	}
	fun_json_printf("output => %s\n", output);
	fun_json_release(output);
}

static int tid = 1;

static NULLABLE CALLER_TO_FREE const char *dpcrun_command_with_sugared_json(INOUT int *sock, struct fun_json *json) {
	if (*sock <= 0) *sock = dpcclient_open_socket();
	if (*sock <= 0) return NULL;
	bool ok = fun_json_write_to_fd(json, *sock);
	if (!ok) {
		// try to reopen socket
		*sock = dpcclient_open_socket();
		if (*sock <= 0) return NULL;
		ok = fun_json_write_to_fd(json, *sock);
		if (!ok) {
			printf("*** Second attempt to send to socket failed too\n");
			return NULL;
		}
	}
	fun_json_release(json);
	/* receive a reply */
	struct fun_json *output = fun_json_read_from_fd(*sock);
	if (!output) {
		printf("*** invalid json returned in dpcrun_command()\n");
		return NULL;
	}
	char *pp = fun_json_to_text(output);
	fun_json_release(output);
	return pp;
}

NULLABLE CALLER_TO_FREE const char *dpcrun_command_with_subverb(INOUT int *sock, const char *verb, const char *sub_verb) {
	size_t len = 1000;
	char *buf = malloc(len);
	snprintf(buf, len, "{arguments: [%s], tid: %d, verb: %s}", sub_verb, tid++, verb);
	struct fun_json *json = fun_json_create_from_text(buf);
	free(buf);
	if (!json) {
		printf("could not parse '%s'\n", buf);
		return NULL;
	}
	return dpcrun_command_with_sugared_json(sock, json);
}

NULLABLE CALLER_TO_FREE const char *dpcrun_command_with_subverb_and_arg(INOUT int *sock, const char *verb, const char *sub_verb, const char *arg) {
	size_t len = 1000 + strlen(arg);
	char *buf = malloc(len);
	snprintf(buf, len, "{arguments: [%s, %s], tid: %d, verb: %s}", sub_verb, arg, tid++, verb);
	struct fun_json *json = fun_json_create_from_text(buf);
	free(buf);
	if (!json) {
		printf("could not parse '%s'\n", buf);
		return NULL;
	}
	return dpcrun_command_with_sugared_json(sock, json);
}

NULLABLE CALLER_TO_FREE const char *dpcrun_command(INOUT int *sock, const char *verb, const char *arguments_array) {
	size_t len = 100 + strlen(arguments_array);
	char *buf = malloc(len);
	snprintf(buf, len, "{arguments: %s, tid: %d, verb: %s}", arguments_array, tid++, verb);
	struct fun_json *json = fun_json_create_from_text(buf);
	free(buf);
	if (!json) {
		printf("could not parse '%s'\n", buf);
		return NULL;
	}
	return dpcrun_command_with_sugared_json(sock, json);
}
