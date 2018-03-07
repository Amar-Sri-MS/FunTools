/*
 *  ring_prop.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#include <cassert>
#include <memory>
#include <vector>

#include "csr_an.h"
#include "ring_prop.h"

ring_node_t::ring_node_t(const std::string& _name,
        const uint8_t& _level):name(_name), level(_level){}

bool ring_node_t::operator==(const ring_node_t& other) const {
    return ((other.name == name) && (other.level == level));
}

uint8_t ring_node_t::get_level(void) const { return level; }
const char* ring_node_t::get_name(void) const { return name.c_str(); }

std::unordered_map<std::string, uint8_t, string_hash> ring_prop_t::an_id_map;

ring_prop_t::ring_prop_t(
        const uint64_t& b_addr):base_addr(b_addr) {}

ring_prop_t& ring_prop_t::operator()(const std::string& str) {
    ring_node_t ring_node{str, curr_lvl};
    auto it = addr_tree.find(ring_node);
    if (it != addr_tree.end()) {
        curr_key = str;
        curr_lvl ++;
        return (*this);
    } else {
        std::cout <<"No node :" << str << "at level " << static_cast<uint16_t>(curr_lvl) << std::endl;
        assert(false);
    }
}

addr_node_t* ring_prop_t::add_an(
        const std::vector<std::string>& hier,
        const uint32_t& an_addr,
        const uint8_t& n_inst,
        const uint32_t& skip_addr) {
    /*
     * First, create the address node
     */
    auto name = hier[hier.size() - 1];

    uint64_t rba = ((base_addr & 0xFF00000000) | (an_addr & 0xFFFFFFFF));
    auto start_id = an_id_map[name];
    auto p = new addr_node_t(name,
            rba,
            start_id,
            n_inst,
            skip_addr);
    an_id_map[name] += n_inst;

    /*
     * Next insert it into the tree
     */
    uint8_t level = 0;
    for (auto& elem: hier) {
        auto ring_p = ring_node_t(elem, level);
        auto it = addr_tree.equal_range(ring_p);
        if (it.first == it.second) {
            addr_tree.emplace(std::make_pair(ring_p, p));
        } else {
            auto found = false;
            for (auto its = it.first; its != it.second; its ++) {
                if (its->second == p) {
                    found = true;
                    break;
                }
            }
            if (not found) {
                addr_tree.emplace(std::make_pair(ring_p, p));
            }
        }
        level ++;
    }
    return p;
}

/*
iterator ring_prop_t::begin() noexcept {
    if(curr_key.empty()) {
        return nullptr;
    } else {
        auto lst = addr_tree.equal_range(std::forward_as_tuple(curr_key, curr_lvl));
        return lst.first;
    }
}
iterator ring_prop_t::end() noexcept {
    if(curr_key.empty()) {
        return nullptr;
    } else {
        auto lst = addr_tree.equal_range(std::forward_as_tuple(curr_key, curr_lvl));
        return lst.second;
    }
}

iterator ring_prop_t::cbegin() noexcept {
    if(curr_key.empty()) {
        return nullptr;
    } else {
        auto lst = addr_tree.equal_range(std::forward_as_tuple(curr_key, curr_lvl));
        return lst.first;
    }
}
iterator ring_prop_t::cend() noexcept {
    if(curr_key.empty()) {
        return nullptr;
    } else {
        auto lst = addr_tree.equal_range(std::forward_as_tuple(curr_key, curr_lvl));
        return lst.second;
    }
}
*/
