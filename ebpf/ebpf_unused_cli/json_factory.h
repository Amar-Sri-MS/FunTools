/*
*  json_factory.h
*
*  Created by Hariharan Thantry on 2019-04-01
*
*  Helper JSON factory routines for use by modules to communicate with DPC
*
*  Copyright © 2019 Fungible Inc. All rights reserved.
*
*/
#pragma once
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#ifdef __cplusplus
extern "C" {
#endif
#include <utils/threaded/fun_json.h>
#ifdef __cplusplus
}
#endif
/*
 * This is meant to provide a utility interface
 * to craft JSON tree for modules.
 *
 * Every module should embed an instance of this
 * and use its public interfaces to craft a tree.
 *
 */
class json_factory
{
  public:
    json_factory(){}

    void* start(const std::string& verb, int64_t tid = 0);

    template<typename T>
	 void* create_arr(const std::vector<T>& vec);

    void* create_dict(const std::unordered_map<std::string, int64_t>& mp);
    void* create_dict(const std::unordered_map<std::string, std::string>& mp);

    void* create_arr(const std::vector<std::string>& vec);
    void* create_arr(const std::vector<int64_t>& vec);

    bool add_bin_to_dict(void* root,
		    const std::string& key,
		    uint8_t* val,
		    const uint16_t sz);
    bool add_string_to_dict(void* root,
		    const std::string& key,
		    const std::string& val);
    bool add_json_to_dict(void*& root,
		    const std::string& key,
		    void*& val);

    void add_json_to_arr(void*& root,
		    void* val);
    std::pair<uint8_t*, size_t> get_binary(void* root);

    void print(void* json_root);
    void* get_json(uint8_t* ptr, size_t sz);
    std::string stringify(void* json_root);
    void* json_from_txt(const std::string& str);
};
template<typename T>
void* json_factory::create_arr(const std::vector<T>& vec) {
    struct fun_json* json_root = fun_json_create_empty_array();

    if (std::is_same<T, std::string>::value) {
    } else if(std::is_same<T, int64_t>::value) {
        for(auto &val: vec) {
	}

    }
    return (void *)json_root;

}
