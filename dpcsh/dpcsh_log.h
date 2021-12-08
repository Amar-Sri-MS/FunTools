/*
 *  dpcsh_log.h
 *
 *  Created by Renat Idrisov on 2021-06-29.
 *  Copyright © 2021 Fungible. All rights reserved.
 */

#pragma once

#include <stdio.h>

#define BLACK	"0;30"
#define RED	"0;31"
#define GREEN	"0;32"
#define BLUE	"0;34"
#define PURPLE	"0;35"

#define LIGHT_GREEN	"1;32"
#define LIGHT_BLUE	"1;34"
#define LIGHT_PURPLE	"1;35"

#define PRELUDE		"\e["
#define POSTLUDE	"m"
#define CLEAR		"0"

#define INPUT_COLORIZE	PRELUDE RED POSTLUDE
#define OUTPUT_COLORIZE	PRELUDE BLUE POSTLUDE
#define NORMAL_COLORIZE	PRELUDE CLEAR POSTLUDE

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
