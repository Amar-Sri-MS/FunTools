#include "fun_json_lite.h"
#include <stdio.h>
#include <stdlib.h>

#define BIG_CONTAINER_SIZE 1000000
#define BINARY_ARRAY_SIZE 10000
#define BLOB_SIZE 100000
#define BLOB_SERIALIZATION_SIZE 100021

static void binary_array_test(void) {
    // random binary array
    uint8_t binary_array[BINARY_ARRAY_SIZE];

    for (int i = 0; i < sizeof(binary_array); i++) {
        binary_array[i] = rand() % 256;
    }

    void *json_memory = malloc(BIG_CONTAINER_SIZE);
    struct fun_json_container *container = fun_json_create_container(json_memory, BIG_CONTAINER_SIZE);
    struct fun_json *json = fun_json_create_binary_array(container, binary_array, sizeof(binary_array));
    if (json == NULL) {
        printf("fun_json_create_binary_array failed\n");
        exit(1);
    }

    uint8_t binary_array_out[sizeof(binary_array)];
    if (!fun_json_fill_binary_array(binary_array_out, json)) {
        printf("fun_json_fill_binary_array failed\n");
        exit(1);
    }

    for (int i = 0; i < sizeof(binary_array); i++) {
        if (binary_array[i] != binary_array_out[i]) {
            printf("binary array mismatch\n");
            exit(1);
        }
    }

    for (int i = 0; i < sizeof(binary_array); i++) {
        const struct fun_json *json_element = fun_json_array_at(json, i);
        if (json_element == NULL) {
            printf("fun_json_array_at failed\n");
            exit(1);
        }
        if (!fun_json_is_int(json_element)) {
            printf("fun_json_is_int failed\n");
            exit(1);
        }
        if (binary_array[i] != fun_json_int_value(json_element)) {
            printf("binary array mismatch\n");
            exit(1);
        }
    }
}

static void blob_test(void) {
    // random binary array
    uint8_t binary_array[BLOB_SIZE];

    for (int i = 0; i < sizeof(binary_array); i++) {
        binary_array[i] = rand() % 256;
    }

    void *json_memory = malloc(BIG_CONTAINER_SIZE);
    struct fun_json_container *container = fun_json_create_container(json_memory, BIG_CONTAINER_SIZE);
    struct fun_json *json = fun_json_create_blob(container, binary_array, sizeof(binary_array));
    if (json == NULL) {
        printf("fun_json_create_blob failed\n");
        exit(1);
    }

    uint8_t binary_array_out[sizeof(binary_array)];
    if (!fun_json_blob_fill_memory(json, binary_array_out, sizeof(binary_array_out))) {
        printf("fun_json_fill_blob failed\n");
        exit(1);
    }

    for (int i = 0; i < sizeof(binary_array); i++) {
        if (binary_array[i] != binary_array_out[i]) {
            printf("binary array mismatch\n");
            exit(1);
        }
    }

    if (fun_json_serialization_size(json) > BLOB_SERIALIZATION_SIZE) {
        printf("size is incorrect %zu > %d\n", fun_json_serialization_size(json), BLOB_SERIALIZATION_SIZE);
        exit(1);
    }
}

int main(int argc, char *argv[]) {
    binary_array_test();
    blob_test();
}