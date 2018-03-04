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

void csr_prop_t::set_base(const uint64_t& addr) {
    m_addr += addr;
}

void csr_prop_t::release(void) {
    if(raw_buf) {
        delete[] raw_buf;
        raw_buf = nullptr;
    }
}
uint8_t* csr_prop_t::read_raw(const uint32_t& e_idx) {
    __init();
    /* Call the registered read handler */
    for (auto i = 0; i < (sign->sz()/8); i ++) {
        raw_buf[i] = rand()%255;
    }
    return raw_buf;
}

void csr_prop_t::flush(const uint32_t& e_idx) {
    assert(raw_buf);

}
void csr_prop_t::reset(void) {
    delete[] raw_buf;
    raw_buf = nullptr;
}
uint8_t* csr_prop_t::get(void) {
    assert(raw_buf);
    return raw_buf;
}
