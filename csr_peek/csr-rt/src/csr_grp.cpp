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
    auto addr_w = sign->_get_addr_w(sign->sz());
    for (auto i = 0; i < n_inst; i ++) {
       auto m_addr = addr + (i*addr_w*n_entries);
       csr_props.emplace_back(sign, m_addr, type, addr_w, n_entries);
    }
}

csr_prop_t& csr_grp_t::operator[](const uint8_t& inst) {
    assert(inst < csr_props.size());
    return csr_props[inst];
}
void csr_grp_t::set_an_props(const uint64_t& base_addr,
        const uint8_t& n_an_inst,
        const uint64_t& skip_addr) {
    m_base += base_addr;
    for (auto& m_elem: csr_props) {
        m_elem._set_an_props(m_base, n_an_inst, skip_addr);
    }
}

void csr_grp_t::set_rd_cb(rd_fptr r_fn) {
    for (auto& m_elem: csr_props) {
        m_elem._set_rd_cb(r_fn);
    }
}
void csr_grp_t::set_wr_cb(wr_fptr w_fn) {
    for (auto& m_elem: csr_props) {
        m_elem._set_wr_cb(w_fn);
    }
}
void csr_grp_t::set_gid(const uint8_t& gid) {
    m_gid = gid;
}

csr_prop_t& csr_grp_t::get_csr(const uint8_t& gid) {
    uint8_t i_id = gid - m_gid;
    return csr_props[i_id];

}
