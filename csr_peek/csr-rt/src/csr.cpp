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

ring_coll_t& F1NS::operator[](const std::string& name) {
    auto it = sys_rings.find(name);
    assert(it != sys_rings.end());
    return it->second;
}

csr_prop_t& F1NS::get_handle(const std::string& csr_name,
        const uint8_t& i_num) {
    auto it = csr_addrs.find(csr_name);
    assert(it != csr_addrs.end());
    auto& ans = it->second;
    return ans[i_num]->get_csr(csr_name, i_num);
}



void F1NS::add_csr(addr_node_t* an,
        const std::string& name,
        csr_grp_t& csr) {

        auto it = csr_addrs.find(name);
        uint8_t st_gid = 0;

        if (it != csr_addrs.end()) {
            st_gid = (it->second).size();
            (it->second).emplace_back(an);
        } else {
            std::vector<addr_node_t*> p;
            p.emplace_back(an);
            csr_addrs.emplace(std::piecewise_construct,
                    std::forward_as_tuple(name),
                    std::forward_as_tuple(p));
        }
        csr.set_gid(st_gid);
        an->add_csr(name, csr);

}





