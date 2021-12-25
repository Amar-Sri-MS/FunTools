/* command-line wrapper around fun_json functionality */

#define _XOPEN_SOURCE
#define _GNU_SOURCE

#include <stdio.h>	// for fprintf()
#include <stdlib.h>	// for free()
#include <getopt.h>	// for getopt_long()
#include <fcntl.h>	// for open()
#include <string.h>	// for strcmp()

// We must define PLATFORM_POSIX to get fun_json_write_to_fd()
#define PLATFORM_POSIX 1
#include <FunOS/utils/threaded/fun_json.h>


int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
#ifdef BINARY_FUZZ
	struct fun_json *input = fun_json_create_from_binary(Data, Size);
#else
	uint32_t line = 0;
	size_t parsed = 0;
	struct fun_json *input = fun_json_create_from_text_with_options((const char *)Data, Size, 0, &line, &parsed);
#endif
	fun_json_release(input);
	return 0;
}
