/*
 *  csr_prop.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#include <iostream>
#include <memory>

#include "csr_s.h"
#include "csr_prop.h"

csr_prop_t::csr_prop_t(const std::shared_ptr<csr_s>& _sign,
        const uint64_t& addr,
        const CSR_TYPE& _type,
        const uint16_t& _addr_w,
        const uint32_t& _n_entries):
    sign(_sign), m_addr(addr), type(_type), addr_w(_addr_w), n_entries(_n_entries) {
    if (n_entries > 1) {
        assert(type == CSR_TYPE::TBL);
    }

}
void csr_prop_t::__init(void) {

    if (!is_init) {
        sign->_initialize();
        is_init = true;
    }
    if (not raw_buf) {
        raw_buf = new uint8_t[sign->sz()/8];
    }

}

void csr_prop_t::_set_base(const uint64_t& addr) {
    m_addr += addr;
}
void csr_prop_t::_set_rd_cb(rd_fptr rd_fn) {
    r_fn = rd_fn;
}

void csr_prop_t::_set_wr_cb(wr_fptr wr_fn) {
    w_fn = wr_fn;
}


void csr_prop_t::release(void) {
    if(raw_buf) {
        delete[] raw_buf;
        raw_buf = nullptr;
    }
}
uint8_t* csr_prop_t::read_raw(const uint32_t& e_idx) {
    __init();
    if (r_fn != nullptr) {
        (*r_fn)(m_addr, raw_buf);
        return raw_buf;
    }
    return nullptr;
}

void csr_prop_t::flush(const uint32_t& e_idx) {
    assert(raw_buf);
    uint64_t f_addr = m_addr + (e_idx*addr_w);
    if (w_fn != nullptr) {
        (*w_fn)(f_addr, raw_buf);
    }

}
void csr_prop_t::reset(void) {
    delete[] raw_buf;
    raw_buf = nullptr;
}
uint8_t* csr_prop_t::get(void) {
    assert(raw_buf);
    return raw_buf;
}
