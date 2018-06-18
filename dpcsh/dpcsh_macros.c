/*
 *  Macros for dpcsh
 *  Created by Bertrand Serlet on 2018-03-18.
 *  Copyright © 2018 Fungible. All rights reserved.
 */

#define PLATFORM_POSIX	1

#include <utils/threaded/fun_json.h>
#include <utils/threaded/fun_commander.h>
#include <utils/threaded/fun_malloc_threaded.h>

#include "dpcsh.h"

static struct fun_json *test_macro1(const struct fun_json *input) 
{
	struct fun_json *output = fun_json_create_empty_dict();
	fun_json_dict_add_other_dict(output, input, true);
	struct fun_json *echo = fun_json_create_string("echo", fun_json_no_copy_no_own);
	fun_json_dict_add(output, "verb", fun_json_no_copy_no_own, echo, true);
	return output;
}

static struct fun_json *test_macro2(const struct fun_json *input) 
{
	struct fun_json *output = fun_json_create_empty_dict();
	fun_json_dict_add_other_dict(output, input, true);
	struct fun_json *same = fun_json_create_string("_macro2", fun_json_no_copy_no_own);
	fun_json_dict_add(output, "verb", fun_json_no_copy_no_own, same, true);
	return output;
}

void dpcsh_load_macros(void) 
{
	fun_commander_macro_register("_macro1", 
		"test macro that expands to 'echo'",
		test_macro1
	);
	fun_commander_macro_register("_macro2", 
		"test macro that expands to itself, i.e. loops",
		test_macro2
	);
}


