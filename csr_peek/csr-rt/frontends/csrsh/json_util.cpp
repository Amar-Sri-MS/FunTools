
/*
 *  json_util.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#include <iostream>
#include <sstream>
#include "json_util.h"
fun_json* json_util::__tmpl(void) {
    struct fun_json* json_root = fun_json_create_empty_dict();
    assert(fun_json_dict_add(json_root,
			    "verb",
			    fun_json_no_copy_no_own,
			    fun_json_create_string("csr_raw", fun_json_no_copy_no_own),
			    true));

    assert(fun_json_dict_add(json_root,
			    "tid",
			    fun_json_no_copy_no_own,
			    fun_json_create_int64(0),
			    true));
    return json_root;

}

fun_json* json_util::peek(const uint64_t& addr,
		const uint16_t& size) {

    struct fun_json* json_root = __tmpl();
    const char* arr[] = {
	    "peek"
    };

    struct fun_json* json_arr = fun_json_create_array_from_strings(arr,
		    fun_json_no_copy_no_own, 1);

    fun_json_array_append(json_arr,
		    fun_json_create_int64(addr));
    fun_json_array_append(json_arr,
		    fun_json_create_int64(size));


    assert(fun_json_dict_add(json_root,
			    "arguments",
			    fun_json_no_copy_no_own,
			    json_arr,
			    true));
    return json_root;
}

fun_json* json_util::poke(const uint64_t& addr,
		const uint8_t* b_arr,
		const uint16_t& size) {
    struct fun_json* json_root = __tmpl();

    const char* arr[] = {
	    "poke"
    };
    struct fun_json* json_arr = fun_json_create_array_from_strings(arr,
		    fun_json_no_copy_no_own, 1);


    fun_json_array_append(json_arr,
		    fun_json_create_int64(addr));

    struct fun_json* bin_json = fun_json_create_array_from_uint8s(b_arr, size);

    fun_json_array_append(json_arr, bin_json);

    assert(fun_json_dict_add(json_root,
			    "arguments",
			    fun_json_no_copy_no_own,
			    json_arr,
			    true));
    return json_root;
}

std::string json_util::stringify(struct fun_json* json) {

    return std::string(fun_json_to_text(json));

}

uint8_t* json_util::peek_rsp(const std::string& json_str) {
    struct fun_json* b_arr = fun_json_create_from_text(json_str.c_str());
    assert(b_arr->type == fun_json_array_type);
    auto n_elems = fun_json_array_count(b_arr);
    uint8_t* byte_arr = new uint8_t[n_elems]();
    struct fun_json* elem = nullptr;
    for (uint16_t i = 0; i < n_elems; i ++) {
        elem = fun_json_array_at(b_arr, i);
        assert (elem != nullptr);
	assert(elem->type == fun_json_int_type);
	byte_arr[i] = (uint8_t)(elem->int_value);
    }
    return byte_arr;
}

bool json_util::poke_rsp(const std::string& json_str) {
    struct fun_json* rsp = fun_json_create_from_text(json_str.c_str());
    assert (rsp != nullptr && rsp->type == fun_json_bool_type);
    return rsp->bool_value;
}
