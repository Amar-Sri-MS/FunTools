/*
 *  funsandbox.c
 *
 *  Created by Charles Gray on 2019-02-05.
 *  Copyright © 2019 Fungible. All rights reserved.
 */

/* demo shared sandbox code */

#include <stdbool.h>
#include <stdint.h>

static bool keep_running = true;

static void puts(const char *str)
{
	/* XXX */
	__asm__ __volatile__ (
		"      move $a0, %0   \n"
		"      li  $v1, 0x20  \n"
		"      syscall 0      \n"
		: /* no outputs */
		: "r" (str));
}

static void sleep(uint64_t nsecs)
{
	/* XXX */
	__asm__ __volatile__ (
		"      move $a0, %0   \n"
		"      li  $v1, 0x21  \n"
		"      syscall 0      \n"
		: /* no outputs */
		: "r" (nsecs));
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

int main(int argc, char *argv[])
{
	while (keep_running) {
		puts("sleeping...\n");
		sleep(1000000000);
	}
	
	puts("done!\n");
		
	return 0;
}
