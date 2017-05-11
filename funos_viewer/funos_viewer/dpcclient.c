//
//  dpcclient.c
//  funos_viewer
//
//  Created by Bertrand Serlet on 4/18/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

#include "dpcclient.h"

#include <stdlib.h>
#include <assert.h>
#include <sys/un.h>
#include <sys/socket.h>
#include <string.h>
#include <stdio.h>
#include <funos/fun_json.h>

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
    char *pp2 = fun_json_to_text(output);
    printf("output => %s\n", pp2);
    free(pp2);
    fun_json_release(output);
}

static int tid = 1;

NULLABLE CALLER_TO_FREE const char *dpcrun_command(INOUT int *sock, const char *verb, const char *arguments_array) {
    if (*sock <= 0) *sock = dpcclient_open_socket();
    if (*sock <= 0) return NULL;
    char buf[1024];
    snprintf(buf, sizeof(buf), "{arguments: %s, tid: %d, verb: %s}", arguments_array, tid++, verb);
    struct fun_json *json = fun_json_create_from_text(buf);
    if (!json) {
        printf("could not parse '%s'\n", buf);
        return NULL;
    }
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
