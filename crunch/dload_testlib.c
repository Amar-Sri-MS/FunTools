// The source of the shared library used by crunch_dload_test.c.

#include <string.h>

void test_fun(char *buffer)
{
    strcpy(buffer, "Hello, world!");
}
