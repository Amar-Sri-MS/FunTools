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

int dpcclient_open_socket(void) {
    int sock = socket(AF_UNIX, SOCK_STREAM, 0);
    assert(sock > 0);
    struct sockaddr_un server = { .sun_family = AF_UNIX };
    strcpy(server.sun_path, "/tmp/funos-dpc.sock");
    int r = connect(sock, (struct sockaddr *)&server, sizeof(server));
    if (r) {
        perror("connect");
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
        printf("invalid json returned\n");
        return;
    }
    char *pp2 = fun_json_to_text(output);
    printf("output => %s\n", pp2);
    free(pp2);
    fun_json_release(output);

}
