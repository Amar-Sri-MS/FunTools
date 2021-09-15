#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "../dpcsh/bin_ctl.h"

void dump(struct fun_ptr_and_size response)
{
  printf("size = %zu\n", response.size);
  for (size_t i = 0; i < response.size;i++) {
    printf("%d ", response.ptr[i]);
  }
  printf("\n");
}

void callback_function(struct fun_ptr_and_size response, void *context)
{
  printf("callback started\n");
  dump(response);
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

  struct bin_ctl_connection *c = bin_ctl_open_connection(h);

  if (!c) {
    printf("error opening connection\n");
    exit(1);
  }

  if (!bin_ctl_register_receive_callback()) {
    printf("error registering callback\n");
    exit(1);
  }

  char buffer[10];
  struct fun_ptr_and_size p = {.ptr = (void *)buffer, .size = 10};

  for (int i = 0; i < 10; i++) {
    for (int j = 0; j < 10; j++) {
      buffer[j] = 100 * rand();
    }
    printf("sending\n");
    dump(p);
    if (!bin_ctl_send(c, p)) {
      printf("send unsuccessful\n");
    }
  }

  if (!bin_ctl_close_connection(c)) {
    printf("error while closing connection\n");
    exit(1);
  }

  if (!bin_ctl_destroy(h)) {
    printf("destroy error\n");
    exit(1);
  }
}