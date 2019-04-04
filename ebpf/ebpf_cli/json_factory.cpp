
#include <iostream>

#include "json_factory.h"

void *json_factory::create_arr(const std::vector<int64_t> &vec) {
  struct fun_json *json_root = fun_json_create_empty_array();
  for (auto &val : vec) {
    fun_json_array_append(json_root, fun_json_create_int64(val));
  }
  return (void *)json_root;
}

void *json_factory::create_arr(const std::vector<std::string> &vec) {
  struct fun_json *json_root = fun_json_create_empty_array();

  for (auto &val : vec) {
    fun_json_array_append(json_root,
                          fun_json_create_string(val.c_str(), fun_json_copy));
  }
  return (void *)json_root;
}

void *json_factory::start(const std::string &verb, int64_t tid) {
  struct fun_json *json_root = fun_json_create_empty_dict();
  fun_json_dict_add_string(json_root, "verb", fun_json_copy, verb.c_str(),
                           fun_json_copy, false);
  fun_json_dict_add_int64(json_root, "tid", fun_json_copy, tid, true);

  return (void *)(json_root);
}

void *json_factory::create_dict(
    const std::unordered_map<std::string, std::string> &mp) {
  struct fun_json *json_root = fun_json_create_empty_dict();

  for (auto &val : mp) {
    fun_json_dict_add_string(json_root, val.first.c_str(), fun_json_copy,
                             val.second.c_str(), fun_json_copy, true);
  }

  return (void *)json_root;
}

void *json_factory::create_dict(
    const std::unordered_map<std::string, int64_t> &mp) {
  struct fun_json *json_root = fun_json_create_empty_dict();

  for (auto &val : mp) {
    fun_json_dict_add_int64(json_root, val.first.c_str(), fun_json_copy,
                            val.second, true);
  }

  return (void *)json_root;
}

bool json_factory::add_bin_to_dict(void *root, const std::string &key,
                                   uint8_t *val, const uint16_t sz) {
  struct fun_json *bin_json = fun_json_create_byte_array(val, sz);
  return fun_json_dict_add((struct fun_json *)root, key.c_str(), fun_json_copy,
                           bin_json, true);
}

bool json_factory::add_string_to_dict(void *root, const std::string &key,
                                      const std::string &val) {
  return fun_json_dict_add_string((struct fun_json *)root, key.c_str(),
                                  fun_json_copy, val.c_str(), fun_json_copy,
                                  true);
}

bool json_factory::add_json_to_dict(void *&root, const std::string &key,
                                    void *&val) {
  return fun_json_dict_add((struct fun_json *)root, key.c_str(), fun_json_copy,
                           (struct fun_json *)val, true);
}

void json_factory::add_json_to_arr(void *&json_root, void *json_elem) {
  fun_json_array_append((struct fun_json *)(json_root),
                        (struct fun_json *)(json_elem));
}

void *json_factory::get_json(uint8_t *bin_arr, size_t sz) {
  return fun_json_deserialize({bin_arr, sz});
}

void *json_factory::json_from_txt(const std::string &str) {
  return fun_json_create_from_text(str.c_str());
}

void json_factory::print(void *root) {
  /*
  size_t allc_sz;

  auto str = fun_json_pretty_print((const struct fun_json *)(root),
                                   1,
                                   "   ",
                                   100,
                                   (FUN_JSON_PRETTY_PRINT_CONVERT_ERRORS_TO_STRING
  | FUN_JSON_PRETTY_PRINT_USE_HEX_FOR_NUMBERS), &allc_sz); std::cout << str <<
  std::endl; free(str);
  */
  fun_json_printf("%s\n", (struct fun_json *)(root));
}

std::pair<uint8_t *, size_t> json_factory::get_binary(void *json_root) {
  size_t alloc_sz;
  auto [ptr, size] =
      fun_json_serialize((struct fun_json *)json_root, &alloc_sz);
  return std::make_pair(ptr, size);
}

std::string json_factory::stringify(void *json_root) {
  auto p = std::string(fun_json_to_text((struct fun_json *)json_root));
  return p;
}
