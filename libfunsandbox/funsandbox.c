/*
 *  funsandbox.c
 *
 *  Created by Charles Gray on 2019-02-05.
 *  Copyright © 2019 Fungible. All rights reserved.
 */

/* demo shared sandbox code */

#include <stdbool.h>
#include <stddef.h>
#include <stdint-gcc.h>

static void puts(const char *str)
{
	/* XXX */
	__asm__ __volatile__ (
		"      move $a0, %0   \n"
		"      li  $v1, 0x20  \n"
		"      syscall 0      \n"
		: /* no outputs */
		: "r" (str)
		: "v0", "v1", "a0");
}

static void sleep(uint64_t nsecs)
{
	/* XXX */
	__asm__ __volatile__ (
		"      move $a0, %0   \n"
		"      li  $v1, 0x21  \n"
		"      syscall 0      \n"
		: /* no outputs */
		: "r" (nsecs)
		: "v0", "v1", "a0");
}

uint64_t fibo(uint64_t n)
{
	if (n == 0)
		return 0;

	if (n == 1)
		return 1;

	return fibo(n-1) + fibo(n-2);
}

uint64_t filter_even(uint64_t a0, uint64_t a1, uint64_t *pkt)
{
	return pkt[0] & 1;
}

static void _setstr(char *s)
{
	s[0] = 's';
	s[1] = 'l';
	s[2] = 'e';
	s[3] = 'e';
	s[4] = 'p';
	s[5] = 'i';
	s[6] = 'n';
	s[7] = 'g';
	s[8] = s[9] = s[10] = '.';
	s[11] = '\n';
	s[12] = '\0';
}

int main(int argc, char *argv[])
{
	int i = 5;
	char str[15];

	_setstr(str);
	while (i-- > 0) {
		puts(str);
		sleep(1000000000);
	}
	
	puts("done!\n");
		
	return 0;
}

int __start(void)
{
	return main(0, NULL);
}
