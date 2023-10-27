#include "fun_json_lite.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
	if (argc != 3) {
		printf("Requires exactly two file names as arguments.\n"
		"Reads and decodes binary json from the first file, writes to the second.\n");
		return 1;
	}
	FILE *fp_in = fopen(argv[1], "rb");
	if (!fp_in) {
		printf("can't open input file\n");
		return 1;
	}

	FILE *fp_out = fopen(argv[2], "wb");
	if (!fp_out) {
		fclose(fp_in);
		printf("can't open output file\n");
		return 1;
	}

	uint8_t *input_buffer = NULL, *context_buffer = NULL, *output_buffer = NULL;
	int return_code = 0;
	size_t input_buffer_size, context_buffer_size, output_buffer_size;
	struct fun_json_container *container;
	const struct fun_json *json;

	fseek(fp_in, 0, SEEK_END);
	input_buffer_size = (size_t)ftell(fp_in);
	fseek(fp_in, 0, SEEK_SET);

	input_buffer = malloc(input_buffer_size);
	if (!input_buffer) {
		printf("can't allocate input_buffer memory\n");
		return_code = 1;
		goto cleanup;
	}

	if (fread(input_buffer, input_buffer_size, 1, fp_in) != 1) {
		printf("can't read from input file\n");
		return_code = 2;
		goto cleanup;
	}

	context_buffer_size = fun_json_container_size(input_buffer, input_buffer_size);

	if (!context_buffer_size) {
		printf("zero container size\n");
		return_code = 3;
		goto cleanup;
	}

	context_buffer = malloc(context_buffer_size);

	if (!context_buffer) {
		printf("cannot allocate memory for context_buffer\n");
		return_code = 4;
		goto cleanup;
	}

	container = fun_json_create_container(context_buffer, context_buffer_size);

	if (!container) {
		printf("cannot create container\n");
		return_code = 5;
		goto cleanup;
	}

	json = fun_json_parse(container, input_buffer, input_buffer_size);

	if (!json) {
		printf("cannot parse json\n");
		return_code = 6;
		goto cleanup;
	}

	output_buffer_size = fun_json_serialization_size(json);

	if (!output_buffer_size) {
		printf("cannot get serialization size\n");
		return_code = 7;
		goto cleanup;
	}

	output_buffer = malloc(output_buffer_size);

	if (!output_buffer) {
		printf("cannot allocate output buffer\n");
		return_code = 8;
		goto cleanup;
	}

	if (output_buffer_size != fun_json_serialize(output_buffer, json)) {
		printf("output size is inconsistent\n");
		return_code = 9;
		goto cleanup;
	}

	if (fwrite(output_buffer, output_buffer_size, 1, fp_out) != 1) {
		printf("cannot write the output\n");
		return_code = 10;
		goto cleanup;
	}

cleanup:
	free(context_buffer);
	free(input_buffer);
	fclose(fp_in);
	fclose(fp_out);
	return return_code;
}