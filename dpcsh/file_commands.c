/*
 *  Macro to input json files
 *  Created by Bertrand Serlet on 2021-10-15.
 *  Copyright © 2021 Fungible. All rights reserved.
 */

#define PLATFORM_POSIX	1

#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>
#include <FunOS/services/commander/fun_commander.h>
#include <FunOS/utils/threaded/fun_malloc_threaded.h>

#include "dpcsh.h"
#include "file_commands.h"

#define JSON_HELP	"json_file <$var> <path>"

static uint64_t tid = 1;

static struct fun_json *wrap_with_setenv(const struct fun_json *varj, FUN_JSON_XFER struct fun_json *json)
{
	struct fun_json *quoted[] = {
		fun_json_create_string("quote", fun_json_no_copy_no_own),
		json
	};
	struct fun_json *new_args[] = { fun_json_retain(varj), fun_json_create_array(quoted, 2) };
	const char *keys[] = { "verb", "arguments", "tid" };
	struct fun_json *values[] = { 
		fun_json_create_string("setenv", fun_json_no_copy_no_own),
		fun_json_create_array(new_args, 2),
		fun_json_create_int64(tid++)
	};
	return fun_json_create_dict(3, keys, fun_json_no_copy_no_own, values);
}

static CALLER_TO_RELEASE struct fun_json *json_file_macro(const struct fun_json *input) 
{
	struct fun_json *args = fun_json_lookup(input, "arguments");
	struct fun_json *varj = fun_json_array_at(args, 0);
	const char *var = fun_json_to_string(varj, "");
	if (!strlen(var)) {
		return fun_json_create_error("Expecting " JSON_HELP ", where var is an environment variable", fun_json_copy);
	}
	if (var[0] != '$') {
		return fun_json_create_errorf("Expecting " JSON_HELP ", where var is an environment variable starting with $, not '%s'", var);
	}
	struct fun_json *filej = fun_json_array_at(args, 1);
	if (!filej) {
		return fun_json_create_error("Expecting " JSON_HELP, fun_json_copy);
	} 
	const char *file = fun_json_to_string(filej, "");
	if (!strlen(file)) {
		return fun_json_create_error("Expecting " JSON_HELP ", where path is a string", fun_json_copy);
	}
	struct fun_json *json = fun_json_read_text_file(file);
	bool binary = false;
	if (!json) {
		int fd = open(file, O_RDONLY);
		if (fd > 0) {
			json = fun_json_read_from_fd(fd);
			close(fd);
			binary = true;
		}
	}
	if (!json) {
		return fun_json_create_errorf("Can't read file at '%s' as json", file);
	}
	printf("Successfully read file '%s' as %s JSON and stored in environment variable '%s': %s\n", 
			file, binary ? "binary" : "text", var, FUN_JSON_TO_TEXT_100(json));
	return wrap_with_setenv(varj, json);
}

static NULLABLE struct fun_json *blob_from_file(const char *file)
{
	struct stat stat_buf;
	int err = stat(file, &stat_buf);
	if (err) {
		printf("*** Can't stat file '%s'\n", file);
		return NULL;
	}
	int fd = open(file, O_RDONLY);
	if (fd <= 0) {
		printf("*** Can't open file '%s'\n", file);
		return NULL;
	}
	struct fun_ptr_and_size pas = { .size = stat_buf.st_size };
	pas.ptr = malloc(pas.size + 1);
	ssize_t rr = read(fd, pas.ptr, pas.size);
	close(fd);
	if (rr != pas.size) {
		printf("*** Can't read all the bytes of file '%s'\n", file);
		close(fd);
		return NULL;
	}
	pas.ptr[rr] = 0;
	struct fun_json *json = fun_json_create_blob(pas);
	free(pas.ptr);
	return json;
}

#define BLOB_HELP	"blob_file <$var> <path>"

static CALLER_TO_RELEASE struct fun_json * blob_file_macro(const struct fun_json *input) 
{
	struct fun_json *args = fun_json_lookup(input, "arguments");
	struct fun_json *varj = fun_json_array_at(args, 0);
	struct fun_json *ret = NULL;

	const char *var = fun_json_to_string(varj, "");
	if (!strlen(var)) {
		return fun_json_create_error("Expecting " BLOB_HELP ", where var is an environment variable", fun_json_copy);
	}
	if (var[0] != '$') {
		return fun_json_create_errorf("Expecting " BLOB_HELP ", where var is an environment variable starting with $, not '%s'", var);
	}
	struct fun_json *filej = fun_json_array_at(args, 1);
	if (!filej) {
		return fun_json_create_error("Expecting " BLOB_HELP, fun_json_copy);
	} 
	const char *file = fun_json_to_string(filej, "");
	if (!strlen(file)) {
		return fun_json_create_error("Expecting " BLOB_HELP ", where path is a string", fun_json_copy);
	}
	struct fun_json *blob = blob_from_file(file);
	if (! blob) {
		return fun_json_create_errorf("Can't read file at '%s'", file);
	}

	printf("Successfully read file '%s' as blob. Storing to var... \n", file);
	ret =  wrap_with_setenv(varj, blob);

	if ((ret != NULL) && !fun_json_is_error_message(ret)) {
		printf("Stored blob in environment variable '%s'\n", var);
	} else {
		fun_json_printf("Error on blob: %s\n", ret);
	}

	return ret;
}

// ===============  REGISTRATION ===============

void register_file_commands(void)
{
	const struct fun_commander_reg_info info1 = {
		.verb = "json_file",
		.short_description = JSON_HELP ": sets environment variable $var with contents of the json text file",
		.is_macro = true,
		.privilege_needed = fun_privilege_guest,
		.arguments_schema = "{}",
		.macro = json_file_macro,
	};
	fun_commander_register(&info1);
	const struct fun_commander_reg_info info2 = {
		.verb = "blob_file",
		.short_description = BLOB_HELP ": sets environment variable $var with blob from contents of file",
		.is_macro = true,
		.privilege_needed = fun_privilege_guest,
		.arguments_schema = "{}",
		.macro = blob_file_macro,
	};
	fun_commander_register(&info2);
}
