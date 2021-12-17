#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "bin_ctl.h"

#define MIN_REQUEST_LENGTH	(1)
#define MAX_REQUEST_LENGTH	(102400)

#define MIN_RESPONSE_LENGTH	(1)
#define MAX_RESPONSE_LENGTH	(102400)

#define REQEST_N	(100)

#define CONNECTION_N	(3)

struct bin_ctl_sample_request {
	size_t reply_bytes;
	size_t request_bytes;
	uint8_t data[];
};

struct bin_ctl_sample_reply {
	size_t connection_n;
	size_t request_n;
	size_t data_bytes;
	uint8_t data[];
};

void dump_reply(struct fun_ptr_and_size data)
{
	struct bin_ctl_sample_reply *reply = (void *)data.ptr;

	printf("connection_number = %zu, requst_number = %zu, data_bytes = %zu\n", reply->connection_n, reply->request_n, reply->data_bytes);

	for (size_t i = 0; i < reply->data_bytes && i < 10;i++) {
		printf("%d ", reply->data[i]);
	}

	if (reply->data_bytes > 10) printf("...");

	printf("\n");
}

void dump_request(struct bin_ctl_sample_request *request, size_t i)
{
	printf("%zu: request_bytes = %zu, reply_bytes = %zu\n", i, request->request_bytes, request->reply_bytes);

	for (size_t i = 0; i < request->request_bytes && i < 10;i++) {
		printf("%d ", request->data[i]);
	}

	if (request->request_bytes > 10) printf("...");

	printf("\n");
}


void callback_function(struct fun_ptr_and_size response, void *context)
{
	printf("callback started\n");
	dump_reply(response);
}

int main(int argc, char *argv[])
{
	if (argc < 2) {
		printf("Usage: bin_ctl_sample <device_name>\n");
		exit(1);
	}
	printf("Using device: %s\n", argv[1]);

	struct bin_ctl_handle *h = bin_ctl_init(argv[1], true, 0); // FUN_ADMIN_BIN_CTL_HANDLER_SAMPLE_APP = 0

	if (!h) {
		printf("init error\n");
		exit(1);
	}

	for (size_t connection_i = 0; connection_i < CONNECTION_N; connection_i++) {
		struct bin_ctl_connection *c = bin_ctl_open_connection(h);

		if (!c) {
			printf("error opening connection\n");
			exit(1);
		}

		if (!bin_ctl_register_receive_callback(c, callback_function, NULL)) {
			printf("error registering callback\n");
			exit(1);
		}

		struct fun_ptr_and_size p;

		for (size_t i = 0; i < REQEST_N; i++) {
			size_t request_size = MIN_REQUEST_LENGTH + (rand() % (MAX_REQUEST_LENGTH - MIN_REQUEST_LENGTH));
			size_t response_size = MIN_RESPONSE_LENGTH + (rand() % (MAX_RESPONSE_LENGTH - MIN_RESPONSE_LENGTH));
			size_t request_complete_size = sizeof(struct bin_ctl_sample_request) + request_size;
			struct bin_ctl_sample_request *request = malloc(request_complete_size);

			if (!request) {
				printf("OOM while allocating %zu\n", request_complete_size);
				exit(1);
			}

			request->reply_bytes = response_size;
			request->request_bytes = request_size;
			for (int j = 0; j < request_size; j++) {
				request->data[j] = rand() % 256;
			}

			dump_request(request, i);

			p.ptr = (void *)request;
			p.size = request_complete_size;

			printf("sending\n");
			if (!bin_ctl_send(c, p)) {
				printf("send unsuccessful\n");
			}

			free(request);
		}

		if (!bin_ctl_close_connection(c)) {
			printf("error while closing connection\n");
			exit(1);
		}
	}

	if (!bin_ctl_destroy(h)) {
		printf("destroy error\n");
		exit(1);
	}
}
