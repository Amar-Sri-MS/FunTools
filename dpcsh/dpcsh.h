/*
 *  dpcsh.h
 *
 *  Created by Charles Gray on 2018-03-22.
 *  Copyright © 2018 Fungible. All rights reserved.
 */

#pragma once

#define PLATFORM_POSIX	1

#include <utils/threaded/fun_json.h>

/* pre-decl */
struct dpcsock;

// Flag that controls how JSON is printed
extern bool use_hex;

/* init the macros */
extern void dpcsh_load_macros(void);

typedef CALLER_TO_RELEASE struct fun_json *(*pretty_printer_f)(void *context, uint64_t tid, struct fun_json *result);

/* Register a pretty printer */
/* It is assumed fun_json_release() must be called on the callback return value */
extern void dpcsh_register_pretty_printer(uint64_t tid, void *context, pretty_printer_f);

/* Unregister pretty printer */
extern void dpcsh_unregister_pretty_printer(uint64_t tid, void *context);


/* run the webserver */
extern int run_webserver(struct dpcsock *funos_sock, int cmd_listen_sock);

/* callback from webserver to handle a request */
extern int json_handle_req(struct dpcsock *funos_sock, const char *path, char *buf, int *size);
