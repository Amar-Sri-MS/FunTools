/*
 *  dpcsh.h
 *
 *  Created by Charles Gray on 2018-03-22.
 *  Copyright © 2018 Fungible. All rights reserved.
 */

#pragma once

#define PLATFORM_POSIX	1

#include "dpcsh_ptr_queue.h"
#include <FunOS/utils/threaded/fun_json.h>
#include <pthread.h>

/* handy socket abstraction */
enum sockmode {
	SOCKMODE_TERMINAL,
	SOCKMODE_IP,
	SOCKMODE_UNIX,
	SOCKMODE_DEV,
	SOCKMODE_FUNQ
};

enum parsingmode {
	PARSE_UNKNOWN, /* bug trap */
	PARSE_TEXT,    /* friendly command-line parsing (and legacy proxy mode) */
	PARSE_JSON,
	PARSE_BINARY_JSON,
};

struct dpcsock {
	const char *verbose_log_name;

	/* configuration */
	enum sockmode mode;      /* whether & how this is used */
	bool server;             /* listen/accept instead of connect */
	bool base64;             /* talk base64 over this socket */
	bool loopback;           /* if this socket is ignored */
	bool dpcsh_connection;   /* socket is connected to another dpcsh */
	const char *socket_name; /* unix socket name */
	const char *eth_name;    /* eth interface to listen on */
	uint16_t port_num;       /* TCP port number */
	uint32_t retries;        /* whether to retry connect on failure */
	uint32_t cmd_timeout;    /* cmd timeout in ms */

	/* runtime */
	void *funq_handle;       /* handle for libfunq connection */
	int listen_fd;           /* fd if this is a server */
};

struct dpcsock_connection {
	struct dpcsock *socket;
	int fd;                  /* connected fd */
	enum parsingmode encoding;   /* use binary json for encoding */
	void *funq_connection;

	bool closing;

	struct fun_ptr_and_size read_buffer;
	size_t read_buffer_position;

	// since one of the ends is always binary json,
	// it would never lead to a double-transcoding
	struct dpcsh_ptr_queue *binary_json_queue;

	// for libfunq only
	pthread_mutex_t funq_queue_lock;
	pthread_cond_t data_available;
};

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
