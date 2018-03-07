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
    base_addr(other.base_addr),
    start_id(other.start_id),
    n_instances(other.n_instances),
    skip_addr(other.skip_addr),
    csr_props(other.csr_props) {

}

addr_node_t& addr_node_t::operator=(const addr_node_t& other) {
    if (this != &other) {
        name = other.name;
        base_addr = other.base_addr;
        start_id = other.start_id;
        n_instances = other.n_instances;
        skip_addr = other.skip_addr;
        csr_props = other.csr_props;
    }
    return *this;
}

addr_node_t::addr_node_t(const std::string& _name,
                         const uint64_t& _addr,
                         const uint8_t& _start_id,
                         const uint8_t& _n_instances,
                         const uint64_t& _skip_addr):
    name(_name),
    base_addr(_addr),
    start_id(_start_id),
    n_instances(_n_instances),
    skip_addr(_skip_addr){}


void addr_node_t::add_csr(
        const std::string& name,
        csr_grp_t& csr,
        rd_fptr r_fn,
        wr_fptr w_fn
        ) {
    if (r_fn) {
        csr.set_rd_cb(r_fn);
    }
    if (w_fn) {
        csr.set_wr_cb(w_fn);
    }
    csr.set_an_props(base_addr, n_instances, skip_addr);
    csr_props.insert(std::make_pair(name, csr));
}

csr_prop_t& addr_node_t::get_csr(const std::string& csr_name,
        const uint8_t& gid_num) {
    auto it = csr_props.find(csr_name);
    assert (it != csr_props.end());
    return (it->second).get_csr(gid_num-start_id);
}

bool addr_node_t::operator==(const addr_node_t& other) const {
    if (this->name == other.name) return true;
    return false;
}
bool addr_node_t::operator!=(const addr_node_t& other) const {
    return !(*this == other);
}
