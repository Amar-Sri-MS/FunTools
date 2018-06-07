/*
 *  ring_prop.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#include <cassert>
#include <iomanip>
#include <iostream>
#include <memory>
#include <vector>

#include "csr_an.h"
#include "ring_prop.h"

ring_node_t::ring_node_t(const char* _name,
        const uint8_t& _level):name(_name), level(_level){}

bool ring_node_t::operator==(const ring_node_t& other) const {
    return ((other.name == name) && (other.level == level));
}

uint8_t ring_node_t::get_level(void) const { return level; }
const char* ring_node_t::get_name(void) const { return name; }

std::unordered_map<const char*, uint8_t> ring_prop_t::an_id_map;

ring_prop_t::ring_prop_t(
        const uint64_t& b_addr):base_addr(b_addr) {}

std::vector<addr_node_t*>
ring_prop_t::get_anodes(const std::vector<const char*>& hier) {
    uint8_t lvl = 0;
    std::vector<addr_node_t*> m;
    for (auto& elem: hier) {
        ring_node_t ring_node{elem, lvl};
        auto it = addr_tree.equal_range(ring_node);
        if (it.first != it.second) {
            for (auto m_its = it.first; m_its != it.second; m_its ++) {
                m.emplace_back(m_its->second);
            }

        } else break;
        lvl ++;
    }
    return m;

}

addr_node_t* ring_prop_t::add_an(
        const std::vector<const char*>& hier,
        const uint32_t& an_addr,
        const uint8_t& n_inst,
        const uint32_t& skip_addr) {
    /*
     * First, create the address node
     */
    auto name = hier[hier.size() - 1];

    uint64_t rba = ((base_addr & 0xFF00000000) | (an_addr & 0xFFFFFFFF));

    auto start_id = an_id_map[name];
    /*   
    std::cout << "ADD:AN:"
        << name << ":ADDR:0x"
        << std::setw(8) << std::setfill('0') << std::hex << an_addr
        << ":ST_INST:" << static_cast<uint16_t>(start_id)
        << ":NINST:" << static_cast<uint16_t>(n_inst)
        << ":SKIP_ADDR:0x" << skip_addr
        << std::setw(10) << std::hex << ":E_ADDR:0x" << rba
        << std::endl;
    */
    auto p = new addr_node_t(name,
            rba,
            start_id,
            n_inst,
            skip_addr);
    //std::cout << "ALLOC:AN:" << name << ":PTR:0x" << std::hex << p << std::endl;
    an_id_map[name] += n_inst;

    /*
     * Next insert it into the tree
     */
    uint8_t level = 0;
    for (auto& elem: hier) {
        auto ring_p = ring_node_t(elem, level);
        auto it = addr_tree.equal_range(ring_p);
        if (it.first == it.second) {
            //std::cout << "INSERT:AN:" << elem
            //    << ":LVL: " << static_cast<uint16_t>(level)
            //    << ":PTR:0x" << std::hex << p << std::endl;
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
              //  std::cout << "INSERT:AN: " << elem
              //      << ":LVL: " << static_cast<uint16_t>(level)
              //      << ":PTR: 0x" << std::hex << p << std::endl;
                addr_tree.emplace(std::make_pair(ring_p, p));
            }
        }
        level ++;
    }
    return p;
}
