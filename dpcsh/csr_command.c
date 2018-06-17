/*
 *  Sugared csr command
 *  Created by Bertrand Serlet on 2018-06-18.
 *  Copyright © 2018 Fungible. All rights reserved.
 */

#define PLATFORM_POSIX	1

#include <utils/threaded/fun_json.h>
#include <utils/threaded/fun_commander.h>
#include <utils/threaded/fun_malloc_threaded.h>
#include <fcntl.h>		// for open()
#include <stdlib.h>		// for malloc()
#include <sys/stat.h>
#include <unistd.h>		// for read()

#include "dpcsh.h"
#include "csr_command.h"

// COMMANDER STRINGS
#define CSR_RAW		fun_json_create_string("csr_raw", fun_json_no_copy_no_own)
#define ECHO		fun_json_create_string("echo", fun_json_no_copy_no_own)
#define PEEK		fun_json_create_string("peek", fun_json_no_copy_no_own)
#define POKE		fun_json_create_string("poke", fun_json_no_copy_no_own)

// Relative path for the metadata
#define SDK_PATH	"FunSDK/config/csr/csr_metadata.json"

// FIELDS IN THE METADATA DB
#define AN_ADDR		"an_addr"
#define AN_PATH		"an_path"
#define RING_NAME	"ring_name"
#define CSR_ADDR	"csr_addr"
#define FIELD_LIST	"fld_lst"
#define FIELD_NAME	"fld_name"
#define FIELD_WIDTH	"fld_width"

// FIELDS IN THE DPCSH QUERY
#define Q_NAME		"name"
#define Q_RING		"ring"
#define Q_PATH		"an_path"
#define Q_FIELD		"field"

// Access to argv[0]
extern const char *dpcsh_path;

// Parsed CSR spec (i.e. the address)
struct csr_spec_parts {
	const char *name;
	NULLABLE const char *ring_name; // NULL => not specified
	const char *an_path;
	const char *field;
};

// The relevant information necessary for csr_raw
struct csr_raw_spec {
	uint64_t addr;
	size_t width; // in bytes
	uint16_t field_num_bits; // 0 => no field
	uint16_t field_start;
};

// ===============  UTILITIES ===============

static bool fun_json_lookup_hex_string(const struct fun_json *dict, const char *key, NULLABLE OUT uint64_t *value)
{
	if (value) *value = 0;
	if (dict->type != fun_json_dict_type) {
		return false;
	}
	struct fun_json *j = fun_json_lookup(dict, key);
	if (!j) {
		return false;
	}
	if (j->type == fun_json_int_type) {
		if (value) *value = j->int_value;
		return true;
	}
	if (j->type == fun_json_string_type) {
		int64_t x = strtoll(j->string_value, NULL, 0);
		if (value) *value = x;
		return true;
	}
	return false;
}

static NULLABLE MAYBE_UNUSED struct fun_json *fun_json_read_file(const char *file)
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
	char *bytes = malloc(stat_buf.st_size + 1);
	ssize_t rr = read(fd, bytes, stat_buf.st_size);
	close(fd);
	if (rr != stat_buf.st_size) {
		printf("*** Can't read all the bytes of file '%s'\n", file);
		close(fd);
		return NULL;
	}
	bytes[rr] = 0;
	struct fun_json *json = fun_json_create_from_text(bytes);
	free(bytes);
	return json;
}

static bool fun_json_lookup_string_matches(const struct fun_json *json, const char *key, const char *expected)
{
	const char *str;
	if (!fun_json_lookup_string(json, key, &str)) {
		return false;
	}
	return !strcmp(str, expected);
}

struct enum_state {
	struct fun_json *matching_keys;
	const char *pattern;
};

static bool /*stop*/ match_each(fun_map_context_t _, NULLABLE void *per_call, fun_map_key_t key, fun_map_value_t value)
{
	struct enum_state *state = per_call;
	if (strstr((char *)key, state->pattern)) {
		struct fun_json *key_json = fun_json_create_string((char *)key, fun_json_copy);
		fun_json_array_append(state-> matching_keys, key_json);
	}
	return false;
}

static struct fun_json *fun_json_dict_keys_matching(const struct fun_json *dict, const char *pattern)
{
	struct enum_state state;
	state.matching_keys = fun_json_create_empty_array();
	state.pattern = pattern;
	fun_map_enumerate(dict->dict, &state, match_each);
	return state.matching_keys;
}

static void fun_json_array_add_bytes_from_uint64(struct fun_json *array, uint8_t width_in_bytes, uint64_t x)
{
	for (uint8_t i = 0; i < width_in_bytes; i++) {
		fun_json_array_append(array, fun_json_create_int64(x & 255));
		x >>= 8;
	}
}

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
	the_db = fun_json_read_file(file);
	if (!the_db || (the_db->type != fun_json_dict_type)) {
		printf("*** Can't parse file '%s'\n", file);
		abort();
	}
	return the_db;
}

// ===============  ADDR LOOKUP ===============

// Parses a spec.  The strings may be patterns
static bool csr_spec_to_parts(const struct fun_json *spec, OUT struct csr_spec_parts *parts)
{
	memset(parts, 0, sizeof(*parts));
	if (spec->type == fun_json_string_type) {
		parts->name = spec->string_value;
		return true;
	}
	if (spec->type == fun_json_dict_type) {
		// For now, expect name and ring_name
		if (! fun_json_lookup_string(spec, Q_NAME, &parts->name)) {
			fun_json_printf("*** CSR spec expected to be a dictionary with 'name', not %s\n", spec);
			return false;
		}
		fun_json_lookup_string(spec, Q_RING, &parts->ring_name);
		fun_json_lookup_string(spec, Q_PATH, &parts->an_path);
		fun_json_lookup_string(spec, Q_FIELD, &parts->field);
		return true;
	}
	fun_json_printf("*** Can't parse CSR spec '%s'\n", spec);
	return false;	
}

static bool entry_matches_parts(const struct fun_json *entry, const struct csr_spec_parts *parts)
{
	// we dont check the name, but everything else
	if (parts->ring_name) {
		if (!fun_json_lookup_string_matches(entry, RING_NAME, parts->ring_name)) {
			return false; // no match
		}
	}
	if (parts->an_path) {
		if (!fun_json_lookup_string_matches(entry, AN_PATH, parts->an_path)) {
			return false; // no match
		}
	}
	return true;
}

static void append_matching_entries(const struct fun_json *entries, const struct csr_spec_parts *parts, struct fun_json *matches)
{
	if (entries->type != fun_json_array_type) {
		fun_json_printf("*** Found CSR spec are not an array '%s'\n", entries);
		return;
	}
	for (size_t i = 0; i < entries->array->count; i++) {
		struct fun_json *entry = fun_json_array_at(entries, i);
		if (entry_matches_parts(entry, parts)) {
			fun_json_array_append(matches, fun_json_retain(entry));
		}
	}
}

static bool get_field_info(const char *field_wanted, const struct fun_json *entry, OUT struct csr_raw_spec *csr_raw_spec)
{
	struct fun_json *fields = fun_json_lookup(entry, FIELD_LIST);
	if (!fields || (fields->type != fun_json_array_type)) {
		fun_json_printf("*** Can't find field list in '%s'\n", entry);
		return false;
	}
	size_t c = fields->array->count;
	uint64_t offset = 0;
	for (size_t i = 0; i < c; i++) {
		struct fun_json *field = fun_json_array_at(fields, i);
		const char *field_name;
		uint64_t field_width;
		if (!fun_json_lookup_string(field, FIELD_NAME, &field_name) || !fun_json_lookup_uint64(field, FIELD_WIDTH, &field_width)) {
			fun_json_printf("*** Fields malformed in '%s'\n", entry);
			return false;
		}
		assert(field_width < (1 << 16));
		if (!strcmp(field_wanted, field_name)) {
			// found the right field
			assert(offset < (1 << 16));
			csr_raw_spec->field_start = offset;
			csr_raw_spec->field_num_bits = field_width;
			return true;
		}
		offset += field_width;
	}
	printf("*** Can't find field '%s'\n", field_wanted);
	return false;
}

static bool entry_to_csr_raw_spec(const struct csr_spec_parts *parts, const struct fun_json *entry, OUT struct csr_raw_spec *csr_raw_spec)
{
	memset(csr_raw_spec, 0, sizeof(*csr_raw_spec));
	uint64_t base_addr = 0;
	if (!fun_json_lookup_hex_string(entry, AN_ADDR, &base_addr)) {
		fun_json_printf("*** Can't parse an_addr for '%s'\n", entry);
		return false;
	}
	uint64_t displ = 0;
	if (!fun_json_lookup_hex_string(entry, CSR_ADDR, &displ)) {
		fun_json_printf("*** Can't parse csr_addr for '%s'\n", entry);
		return false;
	}
	csr_raw_spec->addr = base_addr + displ;
	uint64_t width_in_bits = 0;
	if (!fun_json_lookup_hex_string(entry, "csr_width", &width_in_bits)) {
		fun_json_printf("*** Can't parse csr_width for '%s'\n", entry);
		return false;
	}
	csr_raw_spec->width = (width_in_bits + 7) / 8; // to bytes
	if (parts->field) {
		if (!get_field_info(parts->field, entry, csr_raw_spec)) {
			return false;
		}
	}
	return true;
}

static bool metadata_lookup(const struct fun_json *db, const struct fun_json *spec, OUT struct csr_raw_spec *result)
{
	struct csr_spec_parts parts;
	bool ok = csr_spec_to_parts(spec, &parts);
	if (!ok) {
		return false;
	}
	struct fun_json *j = fun_json_lookup(db, parts.name);
	if (!j) {
		printf("*** Cannot find any CSR equal to '%s'\n", parts.name);
		return false;
	}
	struct fun_json *matches = fun_json_create_empty_array();
	append_matching_entries(j, &parts, matches);
	size_t c = matches->array->count;
	if (c == 0) {
		fun_json_printf("*** CSR name was found but no entry matches CSR spec %s\n", spec);
		return false;
	}
	if (c != 1) {
		printf("*** Found %zd matches for CSR spec\n", c);
		fun_json_printf("*** Matches: %s\n", matches);
		return false;
	}
	struct fun_json *first = fun_json_array_at(matches, 0);
	memset(result, 0, sizeof(*result));
	return entry_to_csr_raw_spec(&parts, first, result);
}

// ===============  PEEK ===============

static bool csr_peek(const struct fun_json *db, const struct fun_json *spec, struct fun_json *output) 
{
	struct csr_raw_spec csr_raw_spec;
	bool ok = metadata_lookup(db, spec, &csr_raw_spec);

	if (!ok) {
		return false;
	}
	struct fun_json *new_args = fun_json_create_empty_array();

	fun_json_dict_add(output, "verb", fun_json_no_copy_no_own, CSR_RAW, true);
	fun_json_array_append(new_args, PEEK);
	fun_json_array_append(new_args, fun_json_create_int64(csr_raw_spec.addr));
	fun_json_array_append(new_args, fun_json_create_int64(csr_raw_spec.width));
	fun_json_dict_add(output, "arguments", fun_json_no_copy_no_own, new_args, true);
	if (csr_raw_spec.field_num_bits) {
		printf("Current NYI: field width=%db offset=%db\n", csr_raw_spec.field_num_bits, csr_raw_spec.field_start);
	}
	return true;
}

// ===============  FIND ===============

static bool csr_find(const struct fun_json *db, const struct fun_json *spec, struct fun_json *output) 
{
	struct csr_spec_parts parts;
	bool ok = csr_spec_to_parts(spec, &parts);

	if (!ok) {
		return false;
	}
	struct fun_json *matches = fun_json_create_empty_array();
	struct fun_json *keys = fun_json_dict_keys_matching(db, parts.name);
	for (size_t k = 0; k < fun_json_array_count(keys); k++) {
		struct fun_json *key = fun_json_array_at(keys, k);
		assert(key->type == fun_json_string_type);
		struct fun_json *j = fun_json_lookup(db, key->string_value);
		assert(j);
		append_matching_entries(j, &parts, matches);
	}
	fun_json_dict_add(output, "verb", fun_json_no_copy_no_own, ECHO, true);
	fun_json_dict_add(output, "arguments", fun_json_no_copy_no_own, matches, true);
	return true;
}

// ===============  POKE ===============

static bool verify_value_has_proper_width(const struct fun_json *value, size_t width, CALLER_TO_RELEASE OUT struct fun_json **value_to_use)
{
	assert(value);
	*value_to_use = NULL; // means: use value
	if ((width <= 8) && (value->type == fun_json_int_type)) {
		// We accept numbers for values, but we convert them to array of bytes
		uint64_t v = (uint64_t)value->int_value;

		if ((width != 8) && (v >= (1ull << (width * 8)))) {
			printf("*** Value %" PRIu64 " exceeds a value of %zd bytes\n", v, width);
			return false;
		}
		*value_to_use = fun_json_create_empty_array();
		fun_json_array_add_bytes_from_uint64(*value_to_use, width, v);
		return true;
	}
	if (value->type != fun_json_array_type) {
		fun_json_printf("*** Expecting an array of bytes, not %s\n", value);
		return false;
	}
	if (width != value->array->count) {
		printf("*** Expecting an array of %zd bytes, array has %zd bytes\n", width, value->array->count);
		return false;
	}
	return true;
}

static bool csr_poke(const struct fun_json *db, const struct fun_json *spec, const struct fun_json *value, struct fun_json *output) 
{
	struct csr_raw_spec csr_raw_spec;
	bool ok = metadata_lookup(db, spec, &csr_raw_spec);

	if (!ok) {
		return false;
	}

	const char *field = NULL;
	
	fun_json_lookup_string(spec, Q_FIELD, &field);

	if (!field) {
		struct fun_json *value_to_use = NULL;
		if (!verify_value_has_proper_width(value, csr_raw_spec.width, &value_to_use)) {
			return false;
		}
		if (!value_to_use) value_to_use = fun_json_retain(value);
		struct fun_json *new_args = fun_json_create_empty_array();

		fun_json_dict_add(output, "verb", fun_json_no_copy_no_own, CSR_RAW, true);
		fun_json_array_append(new_args, POKE);
		fun_json_array_append(new_args, fun_json_create_int64(csr_raw_spec.addr));
		fun_json_array_append(new_args, value_to_use);
		fun_json_dict_add(output, "arguments", fun_json_no_copy_no_own, new_args, true);
		return true;
	} else {
		printf("*** Field poke not yet implemented\n");
		return false;
	}
}

// ===============  MACRO EXPANSION ===============

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
		bool ok = csr_peek(db, spec, output);
		if (!ok) {
			return fun_json_create_error("*** error mapping csr spec to an address", fun_json_copy);
		}
	} else if (!strcmp(sub, "find")) {
		if (fun_json_array_count(args) != 2) {
			return fun_json_create_error("*** too many arguments for 'csr find'", fun_json_copy);
		}
		bool ok = csr_find(db, spec, output);
		if (!ok) {
			return fun_json_create_error("*** error mapping csr spec to an address", fun_json_copy);
		}
	} else if (!strcmp(sub, "poke")) {
		if (fun_json_array_count(args) != 3) {
			return fun_json_create_error("*** wrong number of arguments for 'csr poke'", fun_json_copy);
		}
		struct fun_json *value = fun_json_array_at(args, 2);
		bool ok = csr_poke(db, spec, value, output);
		if (!ok) {
			return fun_json_create_error("*** error mapping csr spec to an address", fun_json_copy);
		}
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
	fun_commander_macro_register("csr", 
		"csr peek|poke|find <csr_spec> ...",
		csr_macro
	);
}
