/* Test Linux dump works. */

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "dump_linux.h"


int main(int argc, char **argv) {
  struct fun_admin_epsq_req req;
  fun_admin_epsq_destroy_req_init(&req,
				  FUN_ADMIN_SUBOP_DESTROY,
				  0,
				  0);

  fun_admin_epsq_req_dump(stdout, &req);
}
