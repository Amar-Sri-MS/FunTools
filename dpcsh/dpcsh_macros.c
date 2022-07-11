/*
 *  Macros for dpcsh
 *  Created by Bertrand Serlet on 2018-03-18.
 *  Copyright © 2018 Fungible. All rights reserved.
 */

#define PLATFORM_POSIX	1

#include <FunOS/services/commander/fun_commander.h>
#include <FunOS/utils/threaded/fun_json.h>
#include <FunOS/utils/threaded/fun_malloc_threaded.h>

#include "dpcsh.h"

// Flag that controls how JSON is printed
bool use_hex = false;

struct fun_json *hex_macro(const struct fun_json *input)
{
	struct fun_json *arguments = fun_json_dict_at(input, "arguments");
	if (!fun_json_array_count(arguments)) {
		use_hex = !use_hex;
	} else {
		use_hex = fun_json_to_bool(fun_json_array_at(arguments, 0), false) != false;
	}
	struct fun_json *output = fun_json_create_empty_dict();
	fun_json_dict_add_other_dict(output, fun_json_retain(input), true);
	struct fun_json *echo = fun_json_create_string("echo", fun_json_no_copy_no_own);
	fun_json_dict_add(output, "verb", fun_json_no_copy_no_own, echo, true);
	const struct fun_json *b = fun_json_create_bool(use_hex);
	struct fun_json *new_arguments = fun_json_create_array((void *)&b, 1);
	fun_json_dict_add(output, "arguments", fun_json_no_copy_no_own, new_arguments, true);
	return output;
}

static struct fun_json *test_macro1(const struct fun_json *input) 
{
	struct fun_json *output = fun_json_create_empty_dict();
	fun_json_dict_add_other_dict(output, fun_json_retain(input), true);
	struct fun_json *echo = fun_json_create_string("echo", fun_json_no_copy_no_own);
	fun_json_dict_add(output, "verb", fun_json_no_copy_no_own, echo, true);
	return output;
}

static struct fun_json *test_macro2(const struct fun_json *input) 
{
	struct fun_json *output = fun_json_create_empty_dict();
	fun_json_dict_add_other_dict(output, fun_json_retain (input), true);
	struct fun_json *same = fun_json_create_string("_macro2", fun_json_no_copy_no_own);
	fun_json_dict_add(output, "verb", fun_json_no_copy_no_own, same, true);
	return output;
}

void dpcsh_load_macros(void) 
{
	struct fun_commander_reg_info infos[] = {
		{
			.verb = "hex",
			.short_description = "switch display to hex/decimal",
			.long_description = "hex { true / false }",
			.is_macro = true,
			.privilege_needed = fun_privilege_guest,
			.arguments_schema = "{type: array, items: boolean, maxItems: 1}",
			.macro = hex_macro,
		},
		// Next 2 are test macros
		{
			.verb = "_macro1",
			.short_description = "test macro that expands to 'echo'",
			.is_macro = true,
			.privilege_needed = fun_privilege_guest,
			.arguments_schema = "{}",
			.macro = test_macro1,
		},
		{
			.verb = "_macro2",
			.short_description = "test macro that expands to itself, i.e. loops",
			.is_macro = true,
			.privilege_needed = fun_privilege_guest,
			.arguments_schema = "{}",
			.macro = test_macro2,
		},
	};
	for (int i = 0; i < ARRAY_SIZE(infos); i++) {
		fun_commander_register(infos + i);
	}
}
