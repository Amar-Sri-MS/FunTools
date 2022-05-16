/*
 *  Sugared csr command
 *  Created by Bertrand Serlet on 2018-06-18.
 *  Copyright © 2018 Fungible. All rights reserved.
 */

#define PLATFORM_POSIX	1

#include <stdlib.h>
#include <stdio.h>
#include <FunOS/services/commander/fun_commander.h>
#include <FunOS/utils/threaded/fun_malloc_threaded.h>
#include <FunOS/utils/threaded/csr_utils.h>

#include "dpcsh.h"
#include "csr_command.h"

#define CST_STRING(x)	fun_json_create_string((x), fun_json_no_copy_no_own)

// COMMANDER STRINGS
#define CSR_RAW		CST_STRING("csr_raw")
#define ECHO		CST_STRING("echo")

// Relative path for the metadata
#define SDK_PATH	"FunSDK/config/csr/csr_metadata.json"

// Access to argv[0]
extern const char *dpcsh_path;

// ===============  METADATA DB ===============

static struct fun_json *csr_metadata_db(void)
{
	static struct fun_json *the_db = NULL;

	if (the_db) {
		// Already read
		return the_db;
	}
	const char *slash = strrchr(dpcsh_path, '/');
	const char *dir;
	if (!slash) {
		dir = ".";
	} else {
		dir = strndup(dpcsh_path, slash - dpcsh_path);
	}
	char file[1025];
	snprintf(file, sizeof(file), "%s/../../FunSDK/" SDK_PATH, dir);
	printf("Opening CSR metadata DB at: %s\n", file);
	the_db = fun_json_read_text_file(file);
	if (!fun_json_is_dict(the_db)) {
		printf("*** Can't parse file '%s'\n", file);
		abort();
	}
	return the_db;
}

// ===============  PEEK ===============

// Sets error on error
static bool csr_peek(const struct fun_json *db, const struct fun_json *spec, struct fun_json *output, OUT struct fun_json **error) 
{
	struct csr_raw_spec csr_raw_spec;
	bool ok = csr_metadata_lookup(db, spec, &csr_raw_spec, error);

	if (!ok) {
		return false;
	}
	struct fun_json *new_args = csr_raw_generate_peek_arguments(& csr_raw_spec);

	fun_json_dict_add(output, "verb", fun_json_no_copy_no_own, CSR_RAW, true);
	fun_json_dict_add(output, "arguments", fun_json_no_copy_no_own, new_args, true);
	return true;
}

// ===============  FIND ===============

static bool csr_find(const struct fun_json *db, const struct fun_json *spec, struct fun_json *output, OUT struct fun_json **error) 
{
	struct csr_spec_parts parts;
	bool ok = csr_spec_to_parts(spec, &parts, error);

	if (!ok) {
		return false;
	}
	struct fun_json *matches = fun_json_create_empty_array();
	struct fun_json *keys = fun_json_dict_keys_matching_as_array(db, parts.name);
	for (size_t k = 0; k < fun_json_array_count(keys); k++) {
		struct fun_json *key = fun_json_array_at(keys, k);
		assert(fun_json_is_string(key));
		struct fun_json *j = fun_json_lookup(db, fun_json_to_string(key, ""));
		assert(j);
		csr_append_matching_entries(j, &parts, matches);
	}
	fun_json_dict_add(output, "verb", fun_json_no_copy_no_own, ECHO, true);
	fun_json_dict_add(output, "arguments", fun_json_no_copy_no_own, matches, true);
	return true;
}

// ===============  POKE ===============

static bool verify_value_has_proper_width(const struct fun_json *value, size_t num_words, CALLER_TO_RELEASE OUT struct fun_json **value_to_use)
{
	assert(value);
	*value_to_use = NULL; // means: use value
	printf("In verify_value_has_proper_width, num_words=%zd\n", num_words);
	if ((num_words == 1) && fun_json_is_int(value)) {
		// We accept numbers for values, but we convert them to array of bytes
		*value_to_use = fun_json_create_empty_array();
		fun_json_array_append(*value_to_use, fun_json_create_int64(fun_json_to_int64(value, 0)));
		return true;
	}
	if (!fun_json_is_array(value)) {
		fun_json_printf("*** Expecting an array of bytes, not %s\n", value);
		return false;
	}
	if (num_words != fun_json_array_count(value)) {
		printf("*** Expecting an array of %zd 64b-words, array has %d items\n", num_words, (fun_json_index_t)fun_json_array_count(value));
		return false;
	}
	return true;
}

static bool csr_poke(const struct fun_json *db, const struct fun_json *spec, const struct fun_json *value, struct fun_json *output, OUT struct fun_json **error) 
{
	struct csr_raw_spec csr_raw_spec;
	bool ok = csr_metadata_lookup(db, spec, &csr_raw_spec, error);

	if (!ok) {
		return false;
	}

	bool has_field = csr_raw_spec.field_num_bits != 0;
	size_t expected_num_words = has_field ? (csr_raw_spec.field_num_bits + 63) / 64 : csr_raw_spec.num_words;
	struct fun_json *value_to_use = NULL;
	if (!verify_value_has_proper_width(value, expected_num_words, &value_to_use)) {
		*error = fun_json_create_error("*** improper size for value", fun_json_copy);
		return false;
	}
	if (!value_to_use) value_to_use = fun_json_retain(value);

	struct fun_json *new_args = csr_raw_generate_poke_arguments(& csr_raw_spec, value_to_use);

	fun_json_dict_add(output, "verb", fun_json_no_copy_no_own, CSR_RAW, true);
	fun_json_dict_add(output, "arguments", fun_json_no_copy_no_own, new_args, true);
	return true;
}

// ===============  MACRO EXPANSION ===============

// Temporary
static CALLER_TO_RELEASE struct fun_json *csr_pretty_printer(void *context, uint64_t tid, struct fun_json *result)
{
	fun_json_printf("In csr_pretty_printer non-pretty=%s\n", result);
	const char *keys[] = { "wrapped" };
	struct fun_json *values[] = { fun_json_retain(result) };
	struct fun_json *wrapped = fun_json_create_dict(1, keys, fun_json_no_copy_no_own, (void *)values);
	dpcsh_unregister_pretty_printer(tid, context);
	return wrapped;
}

static CALLER_TO_RELEASE struct fun_json *csr_macro(const struct fun_json *input) 
{
	struct fun_json *error = NULL;
	struct fun_json *db = csr_metadata_db();

	assert(db);
	struct fun_json *output = fun_json_create_empty_dict();
	struct fun_json *args = fun_json_lookup(input, "arguments");
	assert(fun_json_is_array(args));
	if (fun_json_array_count(args) < 2) {
		return fun_json_create_error("Expecting <csr> <sub_verb> <addr> ...", fun_json_copy);
	} 
	struct fun_json *sub_verb = fun_json_array_at(args, 0);
	if (!fun_json_is_string(sub_verb)) {
		return fun_json_create_error("Expecting <csr> <sub_verb> <addr> ..., where sub_verb is a string", fun_json_copy);
	} 
	const char *sub = fun_json_to_string(sub_verb, "");
	struct fun_json *spec = fun_json_array_at(args, 1);
	uint64_t tid = 0;
	bool has_tid = fun_json_lookup_uint64(input, "tid", &tid);
	if (!strcmp(sub, "peek")) {
		if (fun_json_array_count(args) != 2) {
			return fun_json_create_error("*** too many arguments for 'csr peek'", fun_json_copy);
		}
		bool ok = csr_peek(db, spec, output, &error);
		if (!ok) {
			return error;
		}
	} else if (!strcmp(sub, "find")) {
		if (fun_json_array_count(args) != 2) {
			return fun_json_create_error("*** too many arguments for 'csr find'", fun_json_copy);
		}
		bool ok = csr_find(db, spec, output, &error);
		if (!ok) {
			return error;
		}
	} else if (!strcmp(sub, "poke")) {
		if (fun_json_array_count(args) != 3) {
			return fun_json_create_error("*** wrong number of arguments for 'csr poke'", fun_json_copy);
		}
		struct fun_json *value = fun_json_array_at(args, 2);
		bool ok = csr_poke(db, spec, value, output, &error);
		if (!ok) {
			return error;
		}
	// Temporary
	} else if (!strcmp(sub, "echo")) {
		if (has_tid) {
			dpcsh_register_pretty_printer(tid, NULL, csr_pretty_printer);
		}
		fun_json_dict_add(output, "verb", fun_json_no_copy_no_own, ECHO, true);
		struct fun_json *new_args = fun_json_create_empty_array();
		fun_json_array_append(new_args, fun_json_retain(spec));
		fun_json_dict_add(output, "arguments", fun_json_no_copy_no_own, new_args, true);
	} else {
		return fun_json_create_error("Expecting <csr> peek|find|poke ...", fun_json_copy);
	}
	fun_json_dict_add_int64(output, "tid", fun_json_no_copy_no_own, tid, true);
	return output;
}

// ===============  REGISTRATION ===============

void register_csr_macro(void)
{
	const struct fun_commander_reg_info info = {
		.verb = "csr",
		.short_description = "csr peek|poke|find <csr_spec> ...",
		.long_description = "  csr peek <csr_addr> <width_in_64b_words>\n"
			"  csr poke <csr_addr> <value>\n"
			"  csr find <csr_addr>\n"
			"    <csr_addr> is a string or a query dictionary\n"
			"    <value> is a 64b-word or an array of 64b ints\n",
		.is_macro = true,
		.privilege_needed = fun_privilege_guest,
		.arguments_schema = "{}",
		.macro = csr_macro,
	};
	fun_commander_register(&info);
}
