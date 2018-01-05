//
//  dpcclient.h
//  funos_viewer
//
//  Created by Bertrand Serlet on 4/18/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

#pragma once

// WORKAROUND
// Not defining static_assert causes an error
#define static_assert(x,y)

#define PLATFORM_POSIX	1

#include <utils/threaded/fun_json.h>

// Returns <=0 on error
extern int dpcclient_open_socket(void);

extern void dpcclient_test(void);

extern NULLABLE CALLER_TO_FREE const char *dpcrun_command(INOUT int *sock, const char *verb, const char *arguments_array);
