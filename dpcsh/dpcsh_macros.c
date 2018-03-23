/*
 *  Macros for dpcsh
 *  Created by Bertrand Serlet on 2018-03-15.
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

static struct fun_json *csr_macro(const struct fun_json *input) 
{
	struct fun_json *output = fun_json_create_empty_dict();
	struct fun_json *args = fun_json_lookup(input, "arguments");
	assert(args->type == fun_json_array_type);
	if (fun_json_array_count(args) < 2) {
		return fun_json_create_error("Expecting <csr> <sub_verb> <addr> ...", fun_json_copy);
	} 
	struct fun_json *sub_verb = fun_json_array_at(args, 0);
	if (sub_verb->type != fun_json_string_type) {
		return fun_json_create_error("Expecting <csr> <sub_verb> <addr> ..., where sub_verb is a string", fun_json_copy);
	} 
	const char *sub = sub_verb->string_value;
	struct fun_json *addr = fun_json_array_at(args, 1);
	if (!strcmp(sub, "peek")) {
		struct fun_json *verb_internal = fun_json_create_string("csr_peek", fun_json_no_copy_no_own);
		fun_json_dict_add(output, "verb", fun_json_no_copy_no_own, verb_internal, true);
		struct fun_json *new_args = fun_json_create_empty_array();
		fun_json_array_append(new_args, fun_json_retain(addr));
		fun_json_dict_add(output, "arguments", fun_json_no_copy_no_own, new_args, true);
		return output;
	} else {
		return fun_json_create_error("Expecting <csr> peek|poke ...", fun_json_copy);
	}
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
	fun_commander_macro_register("csr", 
		"csr peek|poke|ppek_flat|meta <addr> ...",
		csr_macro
	);
}


