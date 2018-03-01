/*
 *  csr_an.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#include "csr_an.h"

addr_node_t::addr_node_t(const addr_node_t& other):
    name(other.name), children(other.children), csrs(other.csrs) {

}

addr_node_t& addr_node_t::operator=(const addr_node_t& other) {
    if (this != &other) {
        name = other.name;
        children = other.children;
        csrs = other.csrs;
    }
    return *this;
}


addr_node_t::addr_node_t(const std::string& _name):name(_name){}

void addr_node_t::append_csr(const csr_grp_t& csr) {
    csrs.emplace_back(csr);
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

