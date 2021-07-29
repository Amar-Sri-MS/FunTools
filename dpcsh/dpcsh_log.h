/*
 *  dpcsh.h
 *
 *  Created by Renat Idrisov on 2021-06-29.
 *  Copyright © 2021 Fungible. All rights reserved.
 */

#pragma once

#define log_debug(debug_mode, ...) \
	do { \
		if(debug_mode) {\
			print_utc_time(); \
			printf(" DBG " __VA_ARGS__);\
		} \
	} while(0)

#define log_error(...) \
	do { \
    print_utc_time(); \
    printf(" ERR " __VA_ARGS__);\
	} while(0)

#define log_info(...) \
	do { \
    print_utc_time(); \
    printf(" INF " __VA_ARGS__);\
	} while(0)

void print_utc_time(void);
