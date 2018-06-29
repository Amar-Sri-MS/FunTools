/*
 *  Sugared csr command
 *  Created by Bertrand Serlet on 2018-06-18.
 *  Copyright © 2018 Fungible. All rights reserved.
 */

#define PLATFORM_POSIX	1

#include <utils/threaded/fun_commander.h>
#include <utils/threaded/fun_malloc_threaded.h>
#include <utils/threaded/csr_utils.h>

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
	if (!the_db || (the_db->type != fun_json_dict_type)) {
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
		assert(key->type == fun_json_string_type);
		struct fun_json *j = fun_json_lookup(db, key->string_value);
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
	if ((num_words == 1) && (value->type == fun_json_int_type)) {
		// We accept numbers for values, but we convert them to array of bytes
		*value_to_use = fun_json_create_empty_array();
		fun_json_array_append(*value_to_use, fun_json_create_int64(value->int_value));
		return true;
	}
	if (value->type != fun_json_array_type) {
		fun_json_printf("*** Expecting an array of bytes, not %s\n", value);
		return false;
	}
	if (num_words != value->array->count) {
		printf("*** Expecting an array of %zd 64b-words, array has %zd items\n", num_words, value->array->count);
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
	const struct fun_json *values[] = { fun_json_retain(result) };
	struct fun_json *wrapped = fun_json_create_dict(1, keys, fun_json_no_copy_no_own, values);
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
	assert(args->type == fun_json_array_type);
	if (fun_json_array_count(args) < 2) {
		return fun_json_create_error("Expecting <csr> <sub_verb> <addr> ...", fun_json_copy);
	} 
	struct fun_json *sub_verb = fun_json_array_at(args, 0);
	if (sub_verb->type != fun_json_string_type) {
		return fun_json_create_error("Expecting <csr> <sub_verb> <addr> ..., where sub_verb is a string", fun_json_copy);
	} 
	const char *sub = sub_verb->string_value;
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
	static const struct fun_commander_reg_info info = {
		.verb = "csr",
		.short_description = "csr peek|poke|find <csr_spec> ...",
		.long_description = "  csr peek <csr_addr> <width_in_64b_words>\n"
			"  csr poke <csr_addr> <value>\n"
			"  csr find <csr_addr>\n"
			"    <csr_addr> is a string or a query dictionary\n"
			"    <value> is a 64b-word or an array of 64b ints\n",
		.is_macro = true,
		.macro = csr_macro,
	};
	fun_commander_register(&info);
}
