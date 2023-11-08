#ifdef EFIAPI
#include "include/fun_json_lite.h"
#include <Library/BaseLib.h>
#include <Library/BaseMemoryLib.h>
#define memcpy CopyMem
#define strlen AsciiStrLen
#define strcmp AsciiStrCmp
#else
#include "fun_json_lite.h"
#include <string.h>
#endif

enum fun_json_types {
	fun_json_error_type = 0, // pseudo-type to specify an error was encountered during parsing - implementation depends on this being 0
	fun_json_null_type = 1,
	fun_json_bool_type = 2,
	fun_json_int_type = 3,
	fun_json_double_type = 4,
	fun_json_string_type = 5,
	fun_json_array_type = 6,
	fun_json_dict_type = 7,
	fun_json_binary_array_type = 8,
	fun_json_last_type = 9, // invalid type to check bounds
};

struct fun_json {
	enum fun_json_types type;
};

struct fun_json_primitive {
	struct fun_json header;
	union {
		bool bool_value;
		// case fun_json_int_type
		int64_t int_value;
		// case fun_json_double_type
		double double_value;
	};
};

struct fun_json_error {
	struct fun_json header;
	char message[];
};

struct fun_json_string {
	struct fun_json header;
	char value[];
};

struct fun_json_array {
	struct fun_json header;
	size_t capacity;
	size_t used;
	const struct fun_json *elements[];
};

struct fun_json_binary_array {
	struct fun_json header;
	uint8_t *elements;
	size_t size;
};

struct fun_json_kv {
	const struct fun_json *key;
	const struct fun_json *value;
};

struct fun_json_dict {
	struct fun_json header;
	size_t capacity;
	size_t used;
	struct fun_json_kv kv[];
};

struct fun_json_container {
	size_t size, used;
};

static const struct fun_json const_null = { .type = fun_json_null_type };

#define json_bool_def(value) static const struct fun_json_primitive const_bool_##value = \
	{ .header = { .type = fun_json_bool_type }, .bool_value = value, };

json_bool_def(true)
json_bool_def(false)

#define json_int_const(value) [value] = { .header = { .type = fun_json_int_type }, .int_value = value, }
#define json_int_2_values(base) json_int_const(base), json_int_const(base + 1)
#define json_int_4_values(base) json_int_2_values(base), json_int_2_values(base + 2)
#define json_int_8_values(base) json_int_4_values(base), json_int_4_values(base + 4)
#define json_int_16_values(base) json_int_8_values(base), json_int_8_values(base + 8)
#define json_int_32_values(base) json_int_16_values(base), json_int_16_values(base + 16)
#define json_int_64_values(base) json_int_32_values(base), json_int_32_values(base + 32)
#define json_int_128_values(base) json_int_64_values(base), json_int_64_values(base + 64)
#define json_int_256_values(base) json_int_128_values(base), json_int_128_values(base + 128)

static const struct fun_json_primitive const_int[256] = {
	json_int_256_values(0)
};

// The source of these constants is in FunOS
// do not modify, otherwise compatibility will be broken
#define BJSON_NULL 0x00
#define BJSON_TRUE 0x01
#define BJSON_FALSE 0x02
#define BJSON_ZEROD 0x03
#define BJSON_ARRAY 0x04
#define BJSON_DICT 0x05
#define BJSON_BYTE_ARRAY 0x06
#define BJSON_DOUBLE 0x07
#define BJSON_STR16 0x09
#define BJSON_STR32 0x0A
#define BJSON_ERROR 0x0B
#define BJSON_INT16 0x0C
#define BJSON_INT32 0x0D
#define BJSON_INT64 0x0E
#define BJSON_TINY_STR 0x40
#define BJSON_UINT7 0x80

#define BJSON_MAX_UINT7 0x7f
#define BJSON_MAX_TINY_STR_LEN 0x3f

struct fun_json_container *fun_json_create_container(void *memory, size_t size)
{
	size_t structure_size = sizeof(struct fun_json_container);
	if (size < structure_size) return NULL;
	struct fun_json_container *result = memory;
	result->size = size;
	result->used = structure_size;
	return result;
}

void fun_json_grow_container(struct fun_json_container *container, size_t new_size)
{
	container->size = new_size;
}

size_t fun_json_container_get_free_mem(struct fun_json_container *container)
{
	return container->size - container->used;
}

static void *allocate(struct fun_json_container *container, size_t size)
{
	if (fun_json_container_get_free_mem(container) < size) {
		return NULL;
	}
	void *result = (uint8_t *)container + container->used;
	container->used += size;
	return result;
}

static struct fun_json_primitive *allocate_primitive(struct fun_json_container *container, enum fun_json_types type)
{
	struct fun_json_primitive *result = allocate(container, sizeof(struct fun_json_primitive));

	if (!result) return NULL;

	result->header.type = type;
	return result;
}

const struct fun_json *fun_json_create_int(struct fun_json_container *container, int64_t value)
{
	if (value >= 0 && value < 256) return (void *)&const_int[value];

	struct fun_json_primitive *result = allocate_primitive(container, fun_json_int_type);
	if (!result) return NULL;
	result->int_value = value;
	return (void *)result;
}

const struct fun_json *fun_json_create_bool(struct fun_json_container *container, bool value)
{
	if (value) return (void *)&const_bool_true;
	return (void *)&const_bool_false;
}

const struct fun_json *fun_json_create_double(struct fun_json_container *container, double value)
{
	struct fun_json_primitive *result = allocate_primitive(container, fun_json_double_type);
	if (!result) return NULL;
	result->double_value = value;
	return (void *)result;
}

const struct fun_json *fun_json_create_null(struct fun_json_container *container)
{
	return (void *)&const_null;
}

static struct fun_json *fun_json_create_error_len(struct fun_json_container *container, const char *message, size_t len)
{
	struct fun_json_error *result = allocate(container, sizeof(struct fun_json_error) + len + 1);
	if (!result) return NULL;
	memcpy(result->message, message, len);
	result->header.type = fun_json_error_type;
	return (void *)result;
}

const struct fun_json *fun_json_create_error(struct fun_json_container *container, const char *message)
{
	return fun_json_create_error_len(container, message, strlen(message));
}

static struct fun_json *fun_json_create_string_len(struct fun_json_container *container, const char *value, size_t len)
{
	struct fun_json_string *result = allocate(container, sizeof(struct fun_json_string) + len + 1);
	if (!result) return NULL;
	memcpy(result->value, value, len);
	result->header.type = fun_json_string_type;
	return (void *)result;
}

const struct fun_json *fun_json_create_string(struct fun_json_container *container, const char *value)
{
	return fun_json_create_string_len(container, value, strlen(value));
}

struct fun_json *fun_json_create_array(struct fun_json_container *container, size_t capacity)
{
	struct fun_json_array *result = allocate(container, sizeof(struct fun_json_array) + capacity * sizeof(void *));
	if (!result) return NULL;
	result->header.type = fun_json_array_type;
	result->capacity = capacity;
	result->used = 0;
	return (void *)result;
}

struct fun_json *fun_json_create_binary_array(struct fun_json_container *container, const uint8_t *value, size_t size)
{
	struct fun_json_binary_array *result = allocate(container, sizeof(struct fun_json_binary_array));
	if (!result) return NULL;
	result->header.type = fun_json_binary_array_type;
	result->size = size;

	result->elements = allocate(container, size);
	if (!result->elements) return NULL;
	memcpy(result->elements, value, size);

	return (void *)result;
}

struct fun_json *fun_json_create_dict(struct fun_json_container *container, size_t capacity)
{
	struct fun_json_dict *result = allocate(container, sizeof(struct fun_json_dict) + capacity * sizeof(struct fun_json_kv));
	if (!result) return NULL;
	result->header.type = fun_json_dict_type;
	result->capacity = capacity;
	result->used = 0;
	return (void *)result;
}

bool fun_json_is_int(const struct fun_json *j)
{
	return j->type == fun_json_int_type;
}

bool fun_json_is_bool(const struct fun_json *j)
{
	return j->type == fun_json_bool_type;
}

bool fun_json_is_double(const struct fun_json *j)
{
	return j->type == fun_json_double_type;
}

bool fun_json_is_null(const struct fun_json *j)
{
	return j->type == fun_json_null_type;
}

bool fun_json_is_error(const struct fun_json *j)
{
	return j->type == fun_json_error_type;
}

bool fun_json_is_string(const struct fun_json *j)
{
	return j->type == fun_json_string_type;
}

bool fun_json_is_array(const struct fun_json *j)
{
	return j->type == fun_json_array_type || j->type == fun_json_binary_array_type;
}

bool fun_json_is_binary_array(const struct fun_json *j)
{
	if (j->type == fun_json_binary_array_type) return true;
	if (j->type != fun_json_array_type) return false;
	const struct fun_json_array *a = (void *)j;
	for (size_t i = 0; i < a->used; i++) {
		if (!fun_json_is_int(a->elements[i])) return false;
		const struct fun_json_primitive *e = (void *)a->elements[i];
		if (e->int_value < 0 || e->int_value > UINT8_MAX) return false;
	}
	return true;
}

bool fun_json_is_dict(const struct fun_json *j)
{
	return j->type == fun_json_dict_type;
}

size_t fun_json_array_count(const struct fun_json *j)
{
	if (j->type == fun_json_binary_array_type) {
		const struct fun_json_binary_array *a = (void *)j;
		return a->size;
	}

	if (!fun_json_is_array(j)) return 0;
	struct fun_json_array *a = (void *)j;
	return a->used;
}

size_t fun_json_dict_count(const struct fun_json *j)
{
	if (!fun_json_is_dict(j)) return 0;
	struct fun_json_dict *d = (void *)j;
	return d->used;
}

const struct fun_json *fun_json_array_at(const struct fun_json *j, size_t index)
{
	if (j->type == fun_json_binary_array_type) {
		const struct fun_json_binary_array *a = (void *)j;
		if (a->size <= index) return NULL;
		return (void *)(const_int + a->elements[index]);
	}

	if (!fun_json_is_array(j)) return 0;
	struct fun_json_array *a = (void *)j;
	if (a->used <= index) return NULL;
	return a->elements[index];
}

const struct fun_json *fun_json_dict_at(const struct fun_json *j, const char *key)
{
	if (!fun_json_is_dict(j)) return 0;
	struct fun_json_dict *d = (void *)j;
	for (size_t i = 0; i < d->used; i++) {
		struct fun_json_string *k = (void *)d->kv[i].key;
		if (strcmp(k->value, key) == 0) {
			return d->kv[i].value;
		}
	}
	return NULL;
}

const char *fun_json_dict_nth_key(const struct fun_json *j, size_t index)
{
	if (!fun_json_is_dict(j)) return 0;

	struct fun_json_dict *d = (void *)j;
	if (d->used <= index) return NULL;
	if (!fun_json_is_string(d->kv[index].key)) return NULL;

	struct fun_json_string *key = (void *)d->kv[index].key;
	return key->value;
}

const struct fun_json *fun_json_dict_nth_value(const struct fun_json *j, size_t index)
{
	if (!fun_json_is_dict(j)) return 0;

	struct fun_json_dict *d = (void *)j;
	if (d->used <= index) return NULL;
	return d->kv[index].value;
}

bool fun_json_array_append(struct fun_json *array, const struct fun_json *element)
{
	struct fun_json_array *a = (void *)array;
	if (a->used == a->capacity) return false;
	a->elements[a->used] = element;
	a->used++;
	return true;
}

static bool fun_json_dict_append_len(struct fun_json_container *container, struct fun_json *dict, const char *key, size_t key_length, const struct fun_json *element)
{
	struct fun_json_dict *d = (void *)dict;
	if (d->used == d->capacity) return false;
	struct fun_json *key_json = fun_json_create_string_len(container, key, key_length);
	if (!key_json) return false;
	d->kv[d->used].key = key_json;
	d->kv[d->used].value = element;
	d->used++;
	return true;
}

bool fun_json_dict_append(struct fun_json_container *container, struct fun_json *dict, const char *key, const struct fun_json *element)
{
	return fun_json_dict_append_len(container, dict, key, strlen(key), element);
}

int64_t fun_json_int_value(const struct fun_json *j)
{
	return ((struct fun_json_primitive *)j)->int_value;
}

double fun_json_double_value(const struct fun_json *j)
{
	return ((struct fun_json_primitive *)j)->double_value;
}

bool fun_json_bool_value(const struct fun_json *j)
{
	return ((struct fun_json_primitive *)j)->bool_value;
}

const char *fun_json_error_value(const struct fun_json *j)
{
	if (!fun_json_is_error(j)) return NULL;
	struct fun_json_error *err = (void *)j;
	return err->message;
}

const char *fun_json_string_value(const struct fun_json *j)
{
	if (!fun_json_is_string(j)) return NULL;
	struct fun_json_string *str = (void *)j;
	return str->value;
}

static uint16_t deserialize_uint16(const uint8_t *bytes) {
	return bytes[0] | (bytes[1] << 8);
}

static int16_t deserialize_int16(const uint8_t *bytes) {
	return *((int16_t *)bytes);
}

static int32_t deserialize_int32(const uint8_t *bytes) {
	return *((int32_t *)bytes);
}

static int64_t deserialize_int64(const uint8_t *bytes) {
	return *((int64_t *)bytes);
}

static uint32_t deserialize_uint32(const uint8_t *bytes) {
	return bytes[0] | (bytes[1] << 8) | (bytes[2] << 16) | (bytes[3] << 24);
}

#if (defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__) || \
    defined(__BIG_ENDIAN__) || defined(_MIPSEB) || defined(__MIPSEB) ||    \
    defined(__MIPSEB__)
#define SWAP_DOUBLES 0
#elif (defined(__BYTE_ORDER__) &&                                          \
       __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__) ||                       \
    defined(__LITTLE_ENDIAN__) || defined(_MIPSEL) || defined(__MIPSEL) || \
    defined(__MIPSEL__)
#define SWAP_DOUBLES 1
#else
#error "UNCLEAR ENDIAN"
#endif  // endian check

static void swap_double_in_place_if_needed(double *pd) {
#if SWAP_DOUBLES
  uint64_t i = *((uint64_t *)pd);
  *((uint64_t *)pd) = __builtin_bswap64(i);
#endif
}

static double deserialize_double(const uint8_t *bytes) {
  double d = *((double *)bytes);
  swap_double_in_place_if_needed(&d);
  return d;
}

size_t fun_json_binary_serialization_minimum_size(uint8_t first_byte) {
	switch (first_byte) {
		case BJSON_NULL: case BJSON_TRUE: case BJSON_FALSE: case BJSON_ZEROD: return 1;
		case BJSON_ARRAY: case BJSON_DICT:
			return 9;
		case BJSON_BYTE_ARRAY:
			return 3;
		case BJSON_DOUBLE:
			return 9;
		case BJSON_STR16:
			return 4;
		case BJSON_STR32: case BJSON_ERROR:
			return 6;
		case BJSON_INT16:
			return 3;
		case BJSON_INT32:
			return 5;
		case BJSON_INT64:
			return 9;
		default:
			if ((first_byte >= BJSON_TINY_STR) && (first_byte < BJSON_UINT7)) {
				return 2;
			}
			if (first_byte >= BJSON_UINT7) return 1;
			return 0;
	}
}

// returns 0 on error
size_t fun_json_binary_serialization_size(const uint8_t *bytes, size_t size) {
	if (size == 0) {
		return 0;
	}

	uint8_t ch = bytes[0];
	if (size < fun_json_binary_serialization_minimum_size(ch)) {
		return 0;
	}
	switch (ch) {
		case BJSON_NULL:
		case BJSON_TRUE:
		case BJSON_FALSE:
		case BJSON_ZEROD:
			return 1;
		case BJSON_ARRAY:
		case BJSON_DICT: {
			uint32_t subs_size = deserialize_uint32(bytes + 1);
			return 9 + subs_size;
		}
		case BJSON_BYTE_ARRAY: {
			uint16_t count = deserialize_uint16(bytes + 1);
			return 3 + count;
		}
		case BJSON_DOUBLE:
			return 9;
		case BJSON_STR16: {
			uint16_t len = deserialize_uint16(bytes + 1);
			return 1 + 2 + len + 1;
		}
		case BJSON_STR32:
		case BJSON_ERROR: {
			uint32_t len = deserialize_uint32(bytes + 1);
			return 1 + 4 + len + 1;
		}
		case BJSON_INT16:
			return 3;
		case BJSON_INT32:
			return 5;
		case BJSON_INT64:
			return 9;
		default:
			if ((ch >= BJSON_TINY_STR) && (ch < BJSON_UINT7)) {
				uint8_t len = ch & 0x3f;
				return 1 + len + 1;
			}
			if (ch >= BJSON_UINT7) return 1;
			return 0;
	}
}

size_t fun_json_container_size_int(int64_t value)
{
	if (value >= 0 && value < 256) return 0; // pre-allocated statically
	return sizeof(struct fun_json_primitive);
}

size_t fun_json_container_size_bool()
{
	return 0; // pre-allocated statically
}

size_t fun_json_container_size_double()
{
	return sizeof(struct fun_json_primitive);
}

size_t fun_json_container_size_null()
{
	return 0; // pre-allocated statically
}

size_t fun_json_container_size_error(size_t len)
{
	return sizeof(struct fun_json_error) + len + 1;
}

size_t fun_json_container_size_string(size_t len)
{
	return sizeof(struct fun_json_string) + len + 1;
}

size_t fun_json_container_size_dict(size_t size)
{
	return sizeof(struct fun_json_dict) + sizeof(struct fun_json_kv) * size;
}

size_t fun_json_container_size_array(size_t size)
{
	return sizeof(struct fun_json_array) + sizeof(void *) * size;
}

size_t fun_json_container_size_binary_array(size_t size)
{
	return sizeof(struct fun_json_binary_array) + size;
}

size_t fun_json_container_overhead()
{
	return sizeof(struct fun_json_container);
}

static size_t fun_json_container_size_internal(const uint8_t *bytes, size_t size)
{
	uint8_t ch = bytes[0];
	switch (ch) {
		case BJSON_NULL:
			return fun_json_container_size_null();
		case BJSON_TRUE:
		case BJSON_FALSE:
			return fun_json_container_size_bool();
		case BJSON_ZEROD:
		case BJSON_DOUBLE:
			return fun_json_container_size_double();
		case BJSON_INT16:
			return fun_json_container_size_int(deserialize_int16(bytes + 1));
		case BJSON_INT32:
			return fun_json_container_size_int(deserialize_int32(bytes + 1));
		case BJSON_INT64:
			return fun_json_container_size_int(deserialize_int64(bytes + 1));
		case BJSON_ARRAY:{
			uint32_t count = deserialize_uint32(bytes + 5);
			size_t total = fun_json_container_size_array(count);
			bytes += 9;
			for (uint32_t i = 0; i < count; i++) {
				total += fun_json_container_size_internal(bytes, size);
				bytes += fun_json_binary_serialization_size(bytes, size);
			}
			return total;
		}
		case BJSON_DICT: {
			uint32_t count = deserialize_uint32(bytes + 5);
			size_t total = fun_json_container_size_dict(count);
			bytes += 9;
			for (uint32_t i = 0; i < count; i++)
				for (uint32_t j = 0; j < 2; j++) {
					total += fun_json_container_size_internal(bytes, size);
					bytes += fun_json_binary_serialization_size(bytes, size);
				}
			return total;
		}
		case BJSON_BYTE_ARRAY: {
			uint16_t count = deserialize_uint16(bytes + 1);
			return fun_json_container_size_binary_array(count);
		}
		case BJSON_STR16: {
			uint16_t len = deserialize_uint16(bytes + 1);
			return fun_json_container_size_string(len);
		}
		case BJSON_STR32: {
			uint32_t len = deserialize_uint32(bytes + 1);
			return fun_json_container_size_string(len);
		}
		case BJSON_ERROR: {
			uint32_t len = deserialize_uint32(bytes + 1);
			return fun_json_container_size_error(len);
		}
		default:
			if ((ch >= BJSON_TINY_STR) && (ch < BJSON_UINT7)) {
				uint8_t len = ch & 0x3f;
				return fun_json_container_size_string(len);
			}
			if (ch >= BJSON_UINT7) return fun_json_container_size_int(ch - BJSON_UINT7);
			return 0;
	}
}

size_t fun_json_container_size(const uint8_t *bytes, size_t size)
{
	return fun_json_container_size_internal(bytes, size) + fun_json_container_overhead();
}


const char *deserialize_string(const uint8_t *bytes, size_t *len)
{
	uint8_t ch = bytes[0];
	*len = 0;
	char *ptr = NULL;

	if (ch == BJSON_STR16) {
		*len = deserialize_uint16(bytes + 1);
		ptr = (char *)bytes + 2 + 1;
	} else
	if (ch == BJSON_STR32 || ch == BJSON_ERROR) {
		*len = deserialize_uint32(bytes + 1);
		ptr = (char *)bytes + 4 + 1;
	} else
	if ((ch >= BJSON_TINY_STR) && (ch < BJSON_UINT7)) {
		*len = ch & 0x3f;
		ptr = (char *)bytes + 1;
	}

	if (len == 0) return NULL;
	for (size_t i = 0; i < *len; i++) {
		if (ptr[i] == 0) {
			// early string termination
			return NULL;
		}
	}
	return ptr;
}

#define BLOB_BYTE_ARRAY_LOG_SIZE	(15)
#define BLOB_BYTE_ARRAY_SIZE	(1 << BLOB_BYTE_ARRAY_LOG_SIZE)

struct fun_json *fun_json_create_blob(struct fun_json_container *container, const uint8_t *bytes, size_t count)
{
	if (!count) {
		return NULL; // we need to exclude 0 for being able to round trip
	}
	if (count > UINT32_MAX) {
		return NULL;
	}
	struct fun_json *blob = NULL;
	size_t num_full_bas = count >> BLOB_BYTE_ARRAY_LOG_SIZE;
	bool leftovers = (num_full_bas << BLOB_BYTE_ARRAY_LOG_SIZE) != count;
	size_t num_bas = num_full_bas + (leftovers ? 1 : 0);

	blob = fun_json_create_array(container, num_bas);
	if (!blob) {
		return NULL;
	}
	size_t i = 0;

	for (i = 0; i < num_full_bas; i++) {
		struct fun_json *ba = fun_json_create_binary_array(container, bytes + (i << BLOB_BYTE_ARRAY_LOG_SIZE), BLOB_BYTE_ARRAY_SIZE);
		if (!ba) goto err;
		fun_json_array_append(blob, ba);
	}
	if (leftovers) {
		struct fun_json *ba = fun_json_create_binary_array(container, bytes + (i << BLOB_BYTE_ARRAY_LOG_SIZE), count - (num_full_bas << BLOB_BYTE_ARRAY_LOG_SIZE));
		if (!ba) goto err;
		i++;
		fun_json_array_append(blob, ba);
	}
	return blob;
err:
	// TODO: deallocate space in container: will leak on failure otherwise
	return NULL;
}

// It is assumed that all the byte-arrays have the BLOB_BYTE_ARRAY_SIZE items, except the last
// (this is important to quickly compute the byte count)
// If 0 is returned the blob is malformed
size_t fun_json_blob_byte_count(const struct fun_json *blob)
{
	size_t num_bas = fun_json_array_count(blob);

	if (!num_bas) {
		return 0;
	}
	const struct fun_json *ba0 = fun_json_array_at(blob, 0);
	size_t c0 = fun_json_array_count(ba0);

	if (!c0) {
		return 0;
	}
	if (num_bas == 1) {
		return c0;
	}
	if (c0 != BLOB_BYTE_ARRAY_SIZE) {
		return 0;
	}
	const struct fun_json *ba_last = fun_json_array_at(blob, num_bas-1);
	size_t c_last = fun_json_array_count(ba_last);

	if (!c_last) {
		return 0;
	}
	return ((num_bas - 1) << BLOB_BYTE_ARRAY_LOG_SIZE) + c_last;
}

bool fun_json_blob_fill_memory(const struct fun_json *blob, uint8_t *ptr, size_t size)
{
	size_t num_bas = fun_json_array_count(blob);

	if (!num_bas) {
		return false;
	}
	uint64_t count = 0;

	// For simplicity, we do 2 passes
	for (size_t i = 0; i < num_bas; i++) {
		const struct fun_json *ba = fun_json_array_at(blob, i);
		size_t this_count = fun_json_array_count(ba);
		if (!this_count) {
			return false;
		}
		if ((i != num_bas-1) && (this_count != BLOB_BYTE_ARRAY_SIZE)) {
			return false;
		}
		count += this_count;
	}
	if (count > UINT32_MAX) {
		return false;
	}
	if (size != count) {
		return false;
	}

	for (size_t i = 0; i < num_bas; i++) {
		const struct fun_json *ba = fun_json_array_at(blob, i);
		size_t this_count = fun_json_array_count(ba);

		if (!fun_json_fill_binary_array(ptr, ba)) {
			return false;
		}
		ptr += this_count;
	}
	return true;
}

const struct fun_json *fun_json_parse(struct fun_json_container *container, const uint8_t *bytes, size_t size)
{
	uint8_t ch = bytes[0];
	switch (ch) {
		case BJSON_NULL:
			return fun_json_create_null(container);
		case BJSON_TRUE:
		case BJSON_FALSE:
			return fun_json_create_bool(container, ch == BJSON_TRUE);
		case BJSON_ZEROD:
			return fun_json_create_double(container, 0);
		case BJSON_DOUBLE:
			return fun_json_create_double(container, deserialize_double(bytes + 1));
		case BJSON_INT16:
			return fun_json_create_int(container, deserialize_int16(bytes + 1));
		case BJSON_INT32:
			return fun_json_create_int(container, deserialize_int32(bytes + 1));
		case BJSON_INT64:
			return fun_json_create_int(container, deserialize_int64(bytes + 1));
		case BJSON_ARRAY:{
			uint32_t count = deserialize_uint32(bytes + 5);
			struct fun_json *array = fun_json_create_array(container, count);
			size_t parsed = 9;
			for (uint32_t i = 0; i < count; i++) {
				size_t element_size = fun_json_binary_serialization_size(bytes + parsed, size - parsed);
				if (!fun_json_array_append(array, fun_json_parse(container, bytes + parsed, element_size))) {
					return NULL;
				}
				parsed += element_size;
			}
			return array;
		}
		case BJSON_DICT: {
			uint32_t count = deserialize_uint32(bytes + 5);
			struct fun_json *dict = fun_json_create_dict(container, count);
			size_t parsed = 9;
			for (uint32_t i = 0; i < count; i++) {
				size_t key_size = fun_json_binary_serialization_size(bytes + parsed, size - parsed);
				size_t value_size = fun_json_binary_serialization_size(bytes + parsed + key_size, size - parsed - key_size);
				size_t len;
				const char *string_value = deserialize_string(bytes + parsed, &len);
				if (!fun_json_dict_append_len(container, dict, string_value, len, fun_json_parse(container, bytes + parsed + key_size, value_size))) {
					return NULL;
				}
				parsed += key_size + value_size;
			}
			return dict;
		}
		case BJSON_BYTE_ARRAY: {
			uint16_t count = deserialize_uint16(bytes + 1);
			return fun_json_create_binary_array(container, bytes + 3, count);
		}
		case BJSON_STR16: 
		case BJSON_STR32: {
			size_t len;
			const char *string_value = deserialize_string(bytes, &len);
			return fun_json_create_string_len(container, string_value, len);
		}
		case BJSON_ERROR: {
			size_t len;
			const char *string_value = deserialize_string(bytes, &len);
			return fun_json_create_error_len(container, string_value, len);
		}
		default:
			if ((ch >= BJSON_TINY_STR) && (ch < BJSON_UINT7)) {
				size_t len;
				const char *string_value = deserialize_string(bytes, &len);
				return fun_json_create_string_len(container, string_value, len);
			}
			if (ch >= BJSON_UINT7) {
				return fun_json_create_int(container, bytes[0] - BJSON_UINT7);
			}
			return NULL;
	}
}

bool fun_json_fill_binary_array(uint8_t *buffer, const struct fun_json *j)
{
	if (j->type == fun_json_binary_array_type) {
		const struct fun_json_binary_array *a = (void *)j;
		memcpy(buffer, a->elements, a->size);
		return true;
	}

	if (!fun_json_is_binary_array(j)) return false;
	const struct fun_json_array *a = (void *)j;

	for (size_t index = 0; index < a->used; index++) {
		struct fun_json_primitive *e = (void *)a->elements[index];
		buffer[index] = e->int_value;
	}
	return true;
}

size_t fun_json_serialization_size(const struct fun_json *j)
{
	if (j->type == fun_json_int_type) {
		struct fun_json_primitive *p = (void *)j;
		if (p->int_value >= 0 && p->int_value < BJSON_MAX_UINT7) return 1;
		if (p->int_value >= INT16_MIN && p->int_value <= INT16_MAX) return 2 + 1;
		if (p->int_value >= INT32_MIN && p->int_value <= INT32_MAX) return 4 + 1;
		return 8 + 1;
	}
	if (j->type == fun_json_double_type) {
		struct fun_json_primitive *p = (void *)j;
		if (p->double_value == 0) return 1;
		return 8 + 1;
	}
	if (j->type == fun_json_bool_type || j->type == fun_json_null_type) {
		return 1;
	}
	if (j->type == fun_json_string_type) {
		struct fun_json_string *p = (void *)j;
		size_t len = strlen(p->value);
		if (len <= BJSON_MAX_TINY_STR_LEN) return len + 1 + 1;
		if (len <= UINT16_MAX) return len + 2 + 1 + 1;
		return len + 4 + 1 + 1;
	}
	if (j->type == fun_json_error_type) {
		struct fun_json_error *p = (void *)j;
		size_t len = strlen(p->message);
		return len + 4 + 1;
	}
	if (j->type == fun_json_array_type) {
		struct fun_json_array *a = (void *)j;
		if (fun_json_is_binary_array(j)) {
			return 2 + 1 + a->used;
		}
		size_t total = 4 + 4 + 1;
		for (size_t index = 0; index < a->used; index++) {
			total += fun_json_serialization_size(a->elements[index]);
		}
		return total;
	}
	if (j->type == fun_json_dict_type) {
		struct fun_json_dict *a = (void *)j;
		size_t total = 4 + 4 + 1;
		for (size_t index = 0; index < a->used; index++) {
			total += fun_json_serialization_size(a->kv[index].key);
			total += fun_json_serialization_size(a->kv[index].value);
		}
		return total;
	}
	return 0;
}

size_t fun_json_serialize(uint8_t *output, const struct fun_json *j)
{
	if (j->type == fun_json_int_type) {
		struct fun_json_primitive *p = (void *)j;
		if (p->int_value >= 0 && p->int_value < BJSON_MAX_UINT7) {
			output[0] = BJSON_UINT7 + p->int_value;
			return 1;
		}
		if (p->int_value >= INT16_MIN && p->int_value <= INT16_MAX) {
			output[0] = BJSON_INT16;
			output++;
			*((int16_t *)output) = p->int_value;
			return 2 + 1;
		}

		if (p->int_value >= INT32_MIN && p->int_value <= INT32_MAX) {
			output[0] = BJSON_INT32;
			output++;
			*((int32_t *)output) = p->int_value;
			return 4 + 1;
		}

		output[0] = BJSON_INT64;
		output++;
		*((int64_t *)output) = p->int_value;
		return 8 + 1;
	}

	if (j->type == fun_json_double_type) {
		struct fun_json_primitive *p = (void *)j;
		if (p->double_value == 0) {
			output[0] = BJSON_ZEROD;
			return 1;
		}

		output[0] = BJSON_DOUBLE;
		double *output_d = (double *)(output + 1);
		*output_d = p->double_value;
		swap_double_in_place_if_needed(output_d);
		return 8 + 1;
	}

	if (j->type == fun_json_bool_type) {
		struct fun_json_primitive *p = (void *)j;
		output[0] = p->bool_value ? BJSON_TRUE : BJSON_FALSE;
		return 1;
	}
	
	if (j->type == fun_json_null_type) {
		output[0] = BJSON_NULL;
		return 1;
	}

	if (j->type == fun_json_string_type) {
		struct fun_json_string *p = (void *)j;
		size_t len = strlen(p->value);
		if (len <= BJSON_MAX_TINY_STR_LEN) {
			output[0] = BJSON_TINY_STR + (uint8_t)len;
			memcpy(output + 1, p->value, len + 1);
			return len + 1 + 1;
		}

		if (len <= UINT16_MAX) {
			output[0] = BJSON_STR16;
			output++;
			*((uint16_t *)output) = len;
			memcpy(output + 2, p->value, len + 1);
			return 3 + len + 1;
		}
		output[0] = BJSON_STR32;
		output++;
		*((uint32_t *)output) = len;
		memcpy(output + 4, p->value, len + 1);
		return 5 + len + 1;
	}

	if (j->type == fun_json_error_type) {
		struct fun_json_error *p = (void *)j;
		size_t len = strlen(p->message);
		output[0] = BJSON_ERROR;
		output++;
		*((uint32_t *)output) = len;
		memcpy(output + 4, p->message, len);
		return 5 + len;
	}

	if (j->type == fun_json_array_type) {
		struct fun_json_array *a = (void *)j;

		if (fun_json_is_binary_array(j)) {
			output[0] = BJSON_BYTE_ARRAY;
			*((uint16_t *)(output + 1)) = a->used;
			fun_json_fill_binary_array(output + 3, j);

			return 2 + 1 + a->used;
		}

		output[0] = BJSON_ARRAY;
		*((uint32_t *)(output + 1 + 4)) = a->used;
		size_t total = 1 + 4 + 4;
		for (size_t index = 0; index < a->used; index++) {
			size_t el_size = fun_json_serialize(output + total, a->elements[index]);
			total += el_size;
		}
		*((uint32_t *)(output + 1)) = total - 9;
		return total;
	}

	if (j->type == fun_json_dict_type) {
		struct fun_json_dict *a = (void *)j;
		output[0] = BJSON_DICT;
		*((uint32_t *)(output + 1 + 4)) = a->used;
		size_t total = 1 + 4 + 4;
		for (size_t index = 0; index < a->used; index++) {
			total += fun_json_serialize(output + total, a->kv[index].key);
			total += fun_json_serialize(output + total, a->kv[index].value);
		}
		*((uint32_t *)(output + 1)) = total - 9;
		return total;
	}
	return 0;
}
