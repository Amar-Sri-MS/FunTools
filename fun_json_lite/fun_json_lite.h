//
//  fun_json_lite.h
//
//  minimalistic fun_json encoder/decoder implementation
//  targeted for UEFI environment
//
//  does not allocate memory, using strlen, memcpy
//
//  Created by Renat Idrisov on 2022-04-15.
//  Copyright © 2022 Fungible. All rights reserved.
//

#include <stdbool.h>
#include <stddef.h>
#include <inttypes.h>

struct fun_json;
struct fun_json_container;

struct fun_json_container *fun_json_create_container(void *memory, size_t size);

// fun_json_grow_container does not allocate the space, it should be done externally
// the function only tells the container that space has increased
void fun_json_grow_container(struct fun_json_container *container, size_t new_size);

size_t fun_json_container_get_free_mem(struct fun_json_container *container);

const struct fun_json *fun_json_create_int(struct fun_json_container *container, int64_t value);
const struct fun_json *fun_json_create_bool(struct fun_json_container *container, bool value);
const struct fun_json *fun_json_create_double(struct fun_json_container *container, double value);
const struct fun_json *fun_json_create_null(struct fun_json_container *container);
const struct fun_json *fun_json_create_error(struct fun_json_container *container, const char *message);
const struct fun_json *fun_json_create_string(struct fun_json_container *container, const char *value);
struct fun_json *fun_json_create_array(struct fun_json_container *container, size_t capacity);
struct fun_json *fun_json_create_dict(struct fun_json_container *container, size_t capacity);
struct fun_json *fun_json_create_binary_array(struct fun_json_container *container, const uint8_t *value, size_t size);

bool fun_json_array_append(struct fun_json *array, const struct fun_json *element);
bool fun_json_dict_append(struct fun_json_container *container, struct fun_json *dict, const char *key, const struct fun_json *element);

bool fun_json_is_int(const struct fun_json *);
bool fun_json_is_bool(const struct fun_json *);
bool fun_json_is_double(const struct fun_json *);
bool fun_json_is_null(const struct fun_json *);
bool fun_json_is_error(const struct fun_json *);
bool fun_json_is_string(const struct fun_json *);
bool fun_json_is_array(const struct fun_json *);
bool fun_json_is_dict(const struct fun_json *);
bool fun_json_is_binary_array(const struct fun_json *);

size_t fun_json_array_count(const struct fun_json *);
size_t fun_json_dict_count(const struct fun_json *);

const struct fun_json *fun_json_array_at(const struct fun_json *, size_t index);
const struct fun_json *fun_json_dict_at(const struct fun_json *, const char *key);
const char *fun_json_dict_nth_key(const struct fun_json *, size_t index);
const struct fun_json *fun_json_dict_nth_value(const struct fun_json *, size_t index);

int64_t fun_json_int_value(const struct fun_json *);
double fun_json_double_value(const struct fun_json *);
bool fun_json_bool_value(const struct fun_json *);
const char *fun_json_error_value(const struct fun_json *);
const char *fun_json_string_value(const struct fun_json *);
bool fun_json_fill_binary_array(uint8_t *, const struct fun_json *);

// returns the size required to allocate for a container
// in order to be able to parse given binary_json
size_t fun_json_container_size(const uint8_t *, size_t);
size_t fun_json_container_overhead();
size_t fun_json_container_size_int(int64_t value);
size_t fun_json_container_size_binary_array(size_t size);
size_t fun_json_container_size_bool();
size_t fun_json_container_size_double();
size_t fun_json_container_size_null();
size_t fun_json_container_size_error(size_t);
size_t fun_json_container_size_string(size_t);
size_t fun_json_container_size_dict(size_t);
size_t fun_json_container_size_array(size_t);

// blob operations (conveniences for arrays of binary arrays)
struct fun_json *fun_json_create_blob(struct fun_json_container *container, const uint8_t *, size_t);
size_t fun_json_blob_byte_count(const struct fun_json *);
bool fun_json_blob_fill_memory(const struct fun_json *, uint8_t *, size_t);

const struct fun_json *fun_json_parse(struct fun_json_container *, const uint8_t *, size_t);

size_t fun_json_serialization_size(const struct fun_json *);

// output must be preallocated, returns capacity used
size_t fun_json_serialize(uint8_t *output, const struct fun_json *);

// deserialize streams where we don't know how much to read at first
size_t fun_json_binary_serialization_minimum_size(uint8_t first_byte);
size_t fun_json_binary_serialization_size(const uint8_t *bytes, size_t size);

