/*
 *  csr.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-26
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#include <cassert>
#include <iostream>
#include "csr.h"

ring_coll_t& F1NS::operator[](const char* name) {
    auto it = sys_rings.find(name);
    assert(it != sys_rings.end());
    return it->second;
}

csr_prop_t& F1NS::get_csr(const char* csr_name,
        const uint8_t& i_num) {
    auto it = csr_addrs.find(csr_name);
    assert(it != csr_addrs.end());
    auto& ans = it->second;
    return ans[i_num]->get_csr(csr_name, i_num);
}

uint16_t F1NS::num_inst(const char* csr_name) const {
    auto it = csr_addrs.find(csr_name);
    assert(it != csr_addrs.end());
    auto& ans = it->second;
    return ans.size(); 
}

void F1NS::add_csr(addr_node_t* an,
        const char* name,
        csr_prop_t& csr) {

        auto it = csr_addrs.find(name);

        if (it != csr_addrs.end()) {
            //assert(an->get_start_id() == (it->second).size());
            for(auto i = 0; i < an->get_num_nodes(); i ++) {
                (it->second).emplace_back(an);
            }

        } else {
            std::vector<addr_node_t*> p;
            assert(an->get_start_id() == 0);
            for(auto i = 0; i < an->get_num_nodes(); i ++) {
                p.emplace_back(an);
            }
            csr_addrs.emplace(std::piecewise_construct,
                    std::forward_as_tuple(name),
                    std::forward_as_tuple(p));
        }
        an->add_csr(name, csr);

}





