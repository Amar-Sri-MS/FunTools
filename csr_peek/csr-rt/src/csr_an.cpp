/*
 *  csr_an.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#include <map>
#include "csr_an.h"

addr_node_t::addr_node_t(const addr_node_t& other):
    name(other.name),
    children(other.children),
    csr_props(other.csr_props),
    base_addr(other.base_addr) {

}

addr_node_t& addr_node_t::operator=(const addr_node_t& other) {
    if (this != &other) {
        name = other.name;
        base_addr = other.base_addr;
        children = other.children;
        csr_props = other.csr_props;
    }
    return *this;
}

addr_node_t::addr_node_t(const std::string& _name,
                         const uint64_t& _addr):
    name(_name),
    base_addr(_addr & 0xFFFFFFFF){}


void addr_node_t::add_csr(
        const std::string& name,
        csr_grp_t& csr) {
    csr.set_base(base_addr);
    csr_props.insert(std::make_pair(name, csr));
}

csr_prop_t& addr_node_t::get_csr(const std::string& csr_name,
        const uint8_t& gid_num) {
    auto it = csr_props.find(csr_name);
    assert (it != csr_props.end());
    return (it->second).get_csr(gid_num);
}



bool addr_node_t::operator==(const addr_node_t& other) const {
    if (this->name == other.name) return true;
    return false;
}
bool addr_node_t::operator!=(const addr_node_t& other) const {
    return !(*this == other);
}
addr_node_t* addr_node_t::get(const addr_node_t& elem) {
    for (auto& p_elem: children) {
        if (*p_elem == elem) return p_elem;
    }
    auto p = new addr_node_t(elem);
    children.emplace_back(p);
    return p;
}
