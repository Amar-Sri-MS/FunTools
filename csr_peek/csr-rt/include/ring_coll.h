/*
 *  ring_coll.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once
#include <map>
#include "ring_prop.h"

class ring_coll_t {
    public:
        ring_coll_t(){}

        ring_prop_t& operator[](const uint8_t& idx);
        void add_ring(const uint8_t& r_idx, 
                const uint64_t& base_addr);
        const uint16_t num_rings() const;

    private:
        std::string ring_name;
        std::map<uint8_t, ring_prop_t> r_props;

};
