/*
 *  bpf_module.cpp
 *
 *  Created by Hariharan Thantry on 2019-04-01
 *
 *  Implementation of the dpc communicating module for bpf
 *  Subclasses cli_module
 *
 *  Copyright © 2019 Fungible Inc. All rights reserved.
 *
 */

#include <cassert>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include "bpf_module.h"
#include "cli_module.h"
#include "json_factory.h"

bpf_module::bpf_module(void) {}

bpf_module::~bpf_module() {}

bool bpf_module::__validate(
    std::unordered_map<std::string, std::string> &params) {
    std::string err_key{"cmd"};
    auto it = params.find(err_key);
    bool rval = (it != params.end());
    if (!rval) goto exit;

    if (it->second == "attach") {
        for (auto &key :
             {"bpf_file", "cl_id", "tx_id", "sec", "order", "qid"}) {
            it = params.find(key);
            rval &= (it != params.end());
            if (!rval) {
                err_key = key;
                goto exit;
            }
        }

    } else if (it->second == "detach")

    {
        for (auto &key : {"cl_id", "tx_id", "sec"}) {
            it = params.find(key);
            rval &= (it != params.end());
            if (!rval) {
                err_key = key;
                goto exit;
            }
        }
    }
    return rval;
exit:
    std::cerr << "Error: " << err_key << " not found " << std::endl;
    return rval;
}

void *bpf_module::__create_request(
    std::unordered_map<std::string, std::string> &params) {
    std::unordered_map<std::string, int64_t> int_vals;
    int64_t val;
    void *root = NULL;
    json_factory __f;

    if (!__validate(params)) return nullptr;

    if (params["cmd"] == "attach") {
        auto f_name = params["bpf_file"];
        std::ifstream fp(f_name, std::ios::in | std::ios::binary);
        fp.seekg(0, std::ios::end);
        auto len = fp.tellg();
        assert(len != 0);
        fp.seekg(0, std::ios::beg);
        auto buf = new char[len];
        fp.read(buf, len);
        fp.close();

        int_vals.emplace("bpf_len", len);
        val = std::atol(params["cl_id"].c_str());
        int_vals.emplace("cl_id", val);
        val = std::atol(params["tx_id"].c_str());
        int_vals.emplace("tx_id", val);
        val = std::atol(params["order"].c_str());
        int_vals.emplace("slot_num", val);
        val = std::atol(params["qid"].c_str());
        int_vals.emplace("xdp_qid", val);

        auto sub_root = __f.create_dict(int_vals);
        assert(__f.add_string_to_dict(sub_root, "section", params["sec"]));
        assert(
            __f.add_bin_to_dict(sub_root, "bpf_code", (uint8_t *)(buf), len));
        delete[] buf;

        auto sub_arr = __f.create_arr({"attach"});
        __f.add_json_to_arr(sub_arr, sub_root);
        root = __f.start("ebpf");
        assert(__f.add_json_to_dict(root, "arguments", sub_arr));

    } else if (params["cmd"] == "detach") {
        val = std::atol(params["cl_id"].c_str());
        int_vals.emplace("cl_id", val);
        val = std::atol(params["tx_id"].c_str());
        int_vals.emplace("tx_id", val);

        auto sub_root = __f.create_dict(int_vals);
        assert(__f.add_string_to_dict(sub_root, "section", params["sec"]));
        auto sub_arr = __f.create_arr({"detach"});
        __f.add_json_to_arr(sub_arr, sub_root);
        root = __f.start("ebpf");
        assert(__f.add_json_to_dict(root, "arguments", sub_arr));
    }

    return root;
}

/*
 * Returns a binary array, and size of that array
 * that is ideal for transmission over a nw socket
 */

std::pair<uint8_t *, size_t> bpf_module::create_bin_request(
    std::unordered_map<std::string, std::string> &params) {
    /*
     * First create the dictionary for all int64_t
     */
    json_factory __f;
    auto root = __create_request(params);
    auto [ptr, sz] = __f.get_binary(root);
    return std::make_pair(ptr, sz);
}

/*
 * Returns the JSON
 */

void *bpf_module::create_js_req(
    std::unordered_map<std::string, std::string> &params) {
    auto rval = __create_request(params);
    return rval;
}
