/*
 *  dpcsh.h
 *
 *  Created by Charles Gray on 2018-03-22.
 *  Copyright © 2018 Fungible. All rights reserved.
 */

#pragma once

#define PLATFORM_POSIX	1

#include <FunSDK/utils/threaded/fun_json.h>

/* handy socket abstraction */
enum sockmode {
	SOCKMODE_TERMINAL,
	SOCKMODE_IP,
	SOCKMODE_UNIX,
	SOCKMODE_DEV,
	SOCKMODE_NVME,
	SOCKMODE_FUNQ
};

enum parsingmode {
	PARSE_UNKNOWN, /* bug trap */
	PARSE_TEXT,    /* friendly command-line parsing (and legacy proxy mode) */
	PARSE_JSON,
	PARSE_BINARY_JSON,
};

struct dpcsock {

	/* configuration */
	enum sockmode mode;      /* whether & how this is used */
	bool server;             /* listen/accept instead of connect */
	bool base64;             /* talk base64 over this socket */
	bool loopback;           /* if this socket is ignored */
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
	bool nvme_write_done;    /* flag indicating whether write to nvme device
                                    is successful so that we can read from it */
	enum parsingmode encoding;   /* use binary json for encoding */
	uint32_t nvme_session_id;
	uint32_t nvme_seq_num;
	void *funq_connection;
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
