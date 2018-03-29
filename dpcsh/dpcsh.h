/*
 *  dpcsh.h
 *
 *  Created by Charles Gray on 2018-03-22.
 *  Copyright © 2018 Fungible. All rights reserved.
 */

#ifndef __DPCSH_H__
#define __DPCSH_H__

/* pre-decl */
struct dpcsock;

/* init the macros */
extern void dpcsh_load_macros(void);

/* run the webserver */
extern int run_webserver(struct dpcsock *funos_sock, int cmd_listen_sock);

/* callback from webserver to handle a request */
extern int json_handle_req(struct dpcsock *funos_sock, const char *path, char *buf, int *size);


#endif /* __DPCSH_H__ */
