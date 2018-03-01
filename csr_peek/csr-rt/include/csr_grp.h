/*
 *  csr_grp.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include <vector>

#include "csr_type.h"
#include "csr_prop.h"

class csr_grp_t {
    public:
        explicit csr_grp_t(const std::shared_ptr<csr_s>& sign, 
                const uint64_t& addr,
                const CSR_TYPE& type,
                const uint16_t& n_entries=1,
                const uint8_t& n_inst=1
                );
        uint16_t _get_addr_w(const uint16_t& w);
        csr_prop_t& operator[](const uint8_t& inst);
        std::vector<csr_prop_t> csr_props; 
};
