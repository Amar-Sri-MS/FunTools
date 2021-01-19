// Copyright © 2021 Fungible, Inc. All rights reserved.
//
// A simple RLE compressor for unit test data;
// used by crunch_dload_test.c.
//
// Created by Vassili Bykov

/*
    Typical usage to produce pasteable C code:

        cat <file> | ./util_compress | xxd -i | pbcopy

    Assumes little-endian architecture.

    Data format:

    The compressed data is a sequence of variable-size records.
    Each record begins with an int16 word N, interpreted as follows:

    If N > 0, the following N bytes of the compressed data are to be
    written to the output verbatim.

    If N < 0, the following byte is to be repeated in the output -N times.

    If N == 0, this is the end of the compressed data. It is followed by
    a uint32 word containing the size of the uncompressed data. The total
    number of bytes written to the output so far must equal this value.
*/

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

struct state {
    void (*enter)(int ch);
    void (*step)(int ch);
    void (*commit)(void);
};

static void init_step(int ch);
static void init_commit(void);

static void run_enter(int ch);
static void run_step(int ch);
static void run_commit(void);
static void run_enter_with_count(int ch, int run_length);

static void verbatim_enter(int ch);
static void verbatim_step(int ch);
static void verbatim_commit(void);

struct state init_state = {
    .enter = NULL,
    .step = init_step,
    .commit = init_commit
};

struct state run_state = {
    .enter = run_enter,
    .step = run_step,
    .commit = run_commit
};

struct state verbatim_state = {
    .enter = verbatim_enter,
    .step = verbatim_step,
    .commit = verbatim_commit
};

static struct state *current_state;

#define SWITCH_STATE(state, ch) current_state->commit(); current_state = &state; state.enter(ch);

/*
        init_state
*/

static void init_step(int ch)
{
    SWITCH_STATE(verbatim_state, ch);
}

static void init_commit(void)
{
}

/*
        verbatim_state
*/

static uint8_t buffer[4096];
static int pos;
static int last_char;
static int last_run;

static void verbatim_enter(int ch)
{
    buffer[0] = ch;
    pos = 1;
    last_char = ch;
    last_run = 1;
}

static void verbatim_reset(void)
{
    pos = 0;
    last_char = -1;
    last_run = 0;
}

static void verbatim_step(int ch)
{
    buffer[pos++] = ch;
    if (last_char == ch) {
        last_run++;
        if (last_run > 3) {
            int n = pos - last_run; // num of chars before the run
            if (n > 0) {
                pos = n;
                verbatim_commit();
            }
            current_state = &run_state;
            run_enter_with_count(last_char, last_run);
        }
    } else {
        last_run = 1;
    }
    last_char = ch;
    if (pos == sizeof(buffer)) {
        // Buffer full; it's ok to just flush it and start afresh.
        // We might miss the beginning of a run this way, but it's not a big deal.
        verbatim_commit();
        verbatim_reset();
        return;
    }
}

static void verbatim_commit()
{
    if (pos > 0) {
        int16_t size = pos;
        fwrite(&size, sizeof(size), 1, stdout);
        fwrite(buffer, sizeof(uint8_t), size, stdout);
    }
}

/*
        run_state
*/

static int run_char;
static uint16_t run_length;

static void run_enter(int ch)
{
    run_char = ch;
    run_length = 1;
}

static void run_enter_with_count(int ch, int count)
{
    run_char = ch;
    run_length = count;
}

static void run_step(int ch)
{
    if (ch == run_char) {
        run_length++;
    } else {
        SWITCH_STATE(verbatim_state, ch);
    }
}

static void run_commit(void)
{
    uint16_t code = -run_length;
    fwrite(&code, sizeof(code), 1, stdout);
    uint8_t byte = run_char;
    fwrite(&byte, sizeof(byte), 1, stdout);
}

/*
        main
*/

int main()
{
    int ch;
    uint32_t count = 0;
    current_state = &init_state;
    while ((ch = getchar()) != EOF) {
        count++;
        current_state->step(ch);
    }
    current_state->commit();
    ch = 0;
    fwrite(&ch, sizeof(int16_t), 1, stdout);
    fwrite(&count, sizeof(count), 1, stdout);
    return 0;
}
