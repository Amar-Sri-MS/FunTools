
/*
 *  json_util.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#include <iostream>
#include <sstream>
#include <type_traits>

#include "json_factory.h"

/*
 * Templatize the basic
 */

struct fun_json* json_factory::__tmpl(const std::string& str, int64_t tid) {
    struct fun_json* json_root = fun_json_create_empty_dict();
    assert(fun_json_dict_add(json_root,
			    "verb",
			    fun_json_no_copy_no_own,
			    fun_json_create_string(str.c_str(), fun_json_no_copy_no_own),
			    true));

    assert(fun_json_dict_add(json_root,
			    "tid",
			    fun_json_no_copy_no_own,
			    fun_json_create_int64(tid),
			    true));
    return json_root;

}

void* json_factory::start(const std::string& verb, int64_t tid) {
   return (void *)(__tmpl(verb, tid));
}


void* json_factory::create_bin(const uint8_t* b_arr,
		const uint16_t& sz) {

    struct fun_json* bin_json = fun_json_create_array_from_uint8s(b_arr, sz);
    return (void *)bin_json;
}


