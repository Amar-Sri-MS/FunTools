/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <unistd.h>
#include <getopt.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/mman.h>

#include "utils.h"

#define COL_SIZE                16
#define LEFT_SPACE              "        "
#define IS_CHAR(x)              ((x >= 0x20) && (x <= 0x7e))
#define CRC32_POLYNOMIAL	0xEDB88320

int fifo_fd;
int flags;

void hexdump(uint8_t *addr, int len)
{
	char str[COL_SIZE + 4];
	uint32_t cntr = 0, i, j = 0;

	for(i = 0; i < len; i++) {
		str[j++] = IS_CHAR(*addr) ? *addr : '.';

		if (!(i % COL_SIZE)) {
			printf("[0x%04x] ", cntr);
			cntr += COL_SIZE;
		}

		printf("%02x ", *addr);

		if (!((i+1) % COL_SIZE)) {
			str[j] = 0;
			printf("%s%s\n", LEFT_SPACE, str);
			j = 0;
		}
		addr++;
	}

	if (i % COL_SIZE) {
		str[j] = 0;
		for(j = (i % COL_SIZE); j < COL_SIZE; j++)
			printf("   ");
		printf("%s%s\n", LEFT_SPACE, str);
	}
}

void print_version(char *name)
{
	fprintf(stderr, "%s %s (%s) @ %s\n", name, VERSION_STR, GIT_BRANCH, COMPILE_DATE);
}

uint32_t crc32(uint8_t  *data_buf, uint32_t byte_cnt, uint32_t crc_in)
{
        uint32_t idx, bit, crc;
        uint8_t c;

        crc = ~crc_in;
        for (idx = 0; idx < byte_cnt; idx++) {
                c = *data_buf++;
                for (bit = 0; bit < 8; bit++, c >>= 1) {
                        crc = (crc >> 1) ^ (((crc ^ c) & 1) ? CRC32_POLYNOMIAL : 0);
                }
        }
        return ~crc;
}

uint8_t crc8(const uint8_t *buf, int len)
{
        uint32_t crc = 0;
        int i, j;

        for (j = len; j; j--, buf++) {
                crc ^= (*buf << 8);
                for(i = 8; i; i--) {
                        if (crc & 0x8000)
                                crc ^= (0x1070 << 3);
                        crc <<= 1;
                }
        }
        return (uint8_t)(crc >> 8);
}
