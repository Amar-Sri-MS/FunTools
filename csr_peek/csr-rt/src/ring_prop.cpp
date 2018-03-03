/*
 *  ring_prop.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#include <cassert>
//#include <cstdarg>
#include <memory>
#include <vector>

#include "csr_an.h"
#include "ring_prop.h"

ring_prop_t::ring_prop_t(const uint64_t& b_addr):base_addr(b_addr) {}

/*
csr_grp_t& ring_prop_t::operator[](const std::string& name) {
    auto it = csr_prop.find(name);
    assert (it != csr_prop.end());
    return it->second;
}
*/



/*
addr_node_t* ring_prop_t::add_an(const uint8_t& n_args, ...) {
    va_list args;
    va_start(args, n_args);
    std::vector<addr_node_t> nodes;
    for (auto i = 0; i < n_args; i ++) {
        nodes.emplace_back(va_arg(args, const char*));
    }
    va_end(args);
    return _construct(nodes);
}
*/

addr_node_t* ring_prop_t::add_an(const std::vector<std::string>& hier, const uint32_t& n_addr) {
    std::vector<addr_node_t> nodes;
    uint64_t rba = ((base_addr & 0xFF00000000) | (n_addr & 0xFFFFFFFF));
    for (auto& elem: hier) {
         nodes.emplace_back(elem, rba);
    }
    return _construct(nodes);
}


addr_node_t* ring_prop_t::_construct(const std::vector<addr_node_t>& tmp_vec) {
    uint16_t idx = 0;
    addr_node_t* m_elem{nullptr};
    while(idx < tmp_vec.size()) {
        auto curr_elem = tmp_vec[idx];
        if (idx == 0) {
            m_elem = _get(curr_elem);
        } else {
            m_elem = m_elem->get(curr_elem);
        }
        idx ++;
    }
    return m_elem;
}

addr_node_t* ring_prop_t::_get(const addr_node_t& elem) {
    for (auto& m_elem : children) {
        if (*m_elem == elem) {
            return m_elem;
        }
    }
    auto p = new addr_node_t(elem);
    children.emplace_back(p);
    return p;
}
