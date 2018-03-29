/*
 *  dpcsh.h
 *
 *  Created by Charles Gray on 2018-03-22.
 *  Copyright © 2018 Fungible. All rights reserved.
 */

#ifndef __DPCSH_H__
#define __DPCSH_H__

/* init the macros */
extern void dpcsh_load_macros(void);

/* run the webserver */
extern int run_webserver(int funos_sock, int cmd_listen_sock);


#endif /* __DPCSH_H__ */
