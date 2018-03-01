/*
 *  csr_grp.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#include <memory>

#include "csr_grp.h"
#include "csr_type.h"

csr_grp_t::csr_grp_t(const std::shared_ptr<csr_s>& sign,
        const uint64_t& addr,
        const CSR_TYPE& type,
        const uint16_t& n_entries,
        const uint8_t& n_inst) {
    auto addr_w = _get_addr_w(sign->sz());
    for (auto i = 0; i < n_inst; i ++) {
       auto m_addr = addr + (i*addr_w*n_entries);
       csr_props.emplace_back(sign, m_addr, type, addr_w, n_entries);
    }
}
uint16_t csr_grp_t::_get_addr_w(const uint16_t& w) {
    if (w <= 64) return 8;
    return (_get_addr_w(w >> 1) << 1);
}

csr_prop_t& csr_grp_t::operator[](const uint8_t& inst) {
    assert(inst < csr_props.size());
    return csr_props[inst];
}
