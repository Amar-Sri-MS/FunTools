// Copyright © 2021 Fungible, Inc. All rights reserved.
//
// A matching decompressor for util_compress.c.
// This is used more for sanity checking of the compressor implementation.
// See the in-memory decompressor in crunch/crunch_dload_test.c.
//
// Created by Vassili Bykov

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>

static int16_t safei16()
{
    int b1 = getchar();
    int b2 = getchar();
    if (b1 == EOF || b2 == EOF) {
        fprintf(stderr, "safei16: premature end of output\n");
        exit(1);
    }
    return (b2 << 8) | b1;
}

static uint32_t safeu32()
{
    int b1 = getchar();
    int b2 = getchar();
    int b3 = getchar();
    int b4 = getchar();
    if (b1 == EOF || b2 == EOF || b3 == EOF || b4 == EOF) {
        fprintf(stderr, "safeu32: premature end of output\n");
        exit(1);
    }
    return (b4 << 24) | (b3 << 16) | (b2 << 8) | b1;
}

static int safechar()
{
    int ch = getchar();
    if (ch == EOF) {
        fprintf(stderr, "safechar: premature end of output\n");
        exit(1);
    }
    return ch;
}

int main()
{
    uint32_t count = 0;
    while (1) {
        int16_t n = safei16();
        if (n > 0) { // write n following bytes verbatim
            for (int i = 0; i < n; i++, count++) putchar(safechar());
        } else if (n < 0) { // write the following byte -n times
            uint8_t byte = safechar();
            for (int i = 0; i < -n; i++, count++) putchar(byte);
        } else { // n == 0 means end of input
            uint32_t expected = safeu32();
            if (expected != count) {
                fprintf(stderr, "size mismatch; expected=%"PRIu32", actual=%"PRIu32"\n", expected, count);
                exit(1);
            }
            break;
        }
    }
    return 0;
}
