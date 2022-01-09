/*
 *  fun_json_diff.c
 *
 *  Created by Bertrand Serlet on 2022-01-09.
 *  Copyright © 2022 Fungible. All rights reserved.
 */

// A json file differ.
// Syntax:
// fun_json_diff <json_file>1 ... <json_file>n {-d <directory_for_deltas>}
// The common part to all the input files is written to stdout.
// Each of the deltas is stored on the deltas directory (or /tmp).

#include <libgen.h>
#include <FunOS/utils/threaded/fun_json.h>
#include <FunOS/utils/threaded/fun_malloc_threaded.h>

#ifndef PLATFORM_POSIX
#error This tool must be built for Posix
#endif

// Example:
// 	set WORKSPACE=...
// 	build_x86_64/fun_json_diff $WORKSPACE/FunOS/configs/nu_config/nu_qos_f1d1.cfg $WORKSPACE/FunOS/configs/nu_config/nu_qos_s1.cfg $WORKSPACE/FunOS/configs/nu_config/nu_qos.cfg 
// will show the common json on stdout and write write the 3 deltas to /tmp/

static void usage(const char *fname)
{
	fprintf(stderr, "usage: %s <input>1 ... <input>n [-d <directory_for_deltas>]\n", fname);
	fprintf(stderr, "Default output is common json to stdout\n");
	fprintf(stderr, "directory_for_deltas defaults to /tmp.\n");
	exit(1);
}

// Checks that the deltas properly apply and generate the original
static void verify_reversible(const char *file, struct fun_json *json, const struct fun_json *common, const struct fun_json *override)
{
	size_t allocated_size;
	struct fun_ptr_and_size pas = fun_json_serialize(common, &allocated_size);
	// reread the common to get a fresh copy
	struct fun_json *current = fun_json_deserialize(pas);
	assert(current);
	fun_free_threaded(pas.ptr, allocated_size);
	const char *error = "";
	bool ok = fun_json_override_in_place(current, override, &error);
	
	if (!ok) {
		fprintf(stderr, "*** Can't revert to %s: ok=%d; error=%s; override=%s applied results into %s - Please let Bertrand know\n", 
			file, ok, error, 
			FUN_JSON_TO_TEXT_100(override), 	
			FUN_JSON_TO_TEXT_100(current));
		abort();
	}
	if (!fun_json_is_equal(current, json)) {
		fprintf(stderr, "*** Can't revert to %s: differs; override=%s applied results into %s - Please let Bertrand know\n", 
			file,
			FUN_JSON_TO_TEXT_100(override), 	
			FUN_JSON_TO_TEXT_100(current));
		fun_json_printf("Full current: %s\n", current);
		abort();
	}
	fun_json_release(current);
}

static int doit(const char **files, unsigned count, const char *deltas_dir)
{
	struct fun_json **jsons = malloc(count * sizeof(void *));
	for (int i = 0; i < count; i++) {
		jsons[i] = fun_json_read_text_file(files[i]);
		if (!jsons[i]) {
		    fprintf(stderr, "*** Unable to parse json file '%s'\n", files[i]);
		    return -1;
		}
	}
	struct fun_json *inputs = fun_json_create_array(jsons, count);
	struct fun_json *overrides;
	const char *error;
	struct fun_json *common = fun_json_identify_common_and_overrides(inputs, &overrides, &error);
	if (!common) {
		fprintf(stderr, "*** Finding commonality failed: %s\n", error);
		return -1;
	}
	// Print common to stdout
	fun_json_printf("%s\n", common);
	// Now we check that applying each override to common results into the original
	if (fun_json_is_null(common)) {
		fprintf(stderr, "No commonality amoung the input files; No override file written.\n");
		return 0;
	} else {
		for (int i = 0; i < count; i++) {
			verify_reversible(files[i], jsons[i], common, fun_json_array_at(overrides, i));
		}
	}
	// Write the delta files
	for (int i = 0; i < fun_json_array_count(inputs); i++) {
		const struct fun_json *delta = fun_json_array_at(overrides, i);
		char buf[1025];
		snprintf(buf, ARRAY_SIZE(buf), "%s/%s.override", deltas_dir, basename((char *)files[i]));
		fun_json_write_text_file(delta, buf, 0);
	}
	return 0;
}

int main(int argc, char *argv[])
{
	char **files = malloc(argc * sizeof(void *));
	unsigned count = 0;
	char *deltas_dir = "/tmp";
	for (int i = 1; i < argc; i++) {
		if (!strcmp(argv[i], "-d") && (i+1<argc)) {
			deltas_dir = argv[i+1];
			i++;
		} else if (argv[i][0] == '-') {
			usage(argv[0]);
		} else {
			files[count++] = argv[i];
		}
	}
	if (!count) {
		usage(argv[0]);
	}
	return doit((const char **)files, count, deltas_dir); 
}
