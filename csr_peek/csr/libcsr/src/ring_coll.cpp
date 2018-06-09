/*
 *  ring_coll.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#include "ring_coll.h"
#include <iomanip>
#include <iostream>

ring_prop_t& ring_coll_t::operator[](const uint8_t& idx) {
    auto it = r_props.find(idx);
    assert (it != r_props.end());
    return it->second;
}

void ring_coll_t::add_ring(const uint8_t& r_idx, const uint64_t& base_addr) {
    auto it = r_props.find(r_idx);
    assert (it == r_props.end());
    /*
    std::cout << "ADD:RING: " << static_cast<uint16_t>(r_idx)
        << std::hex << ":ADDR:0x" << std::setw(10) << base_addr << std::endl;
        */
    r_props.emplace(std::piecewise_construct,
            std::forward_as_tuple(r_idx),
            std::forward_as_tuple(base_addr));
}

const uint16_t ring_coll_t::num_rings(void) const {
    return r_props.size();
}
