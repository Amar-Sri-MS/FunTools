/*
 *  csr_prop.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#include <cstring>
#include <iomanip>
#include <iostream>
#include <memory>

#include "csr_s.h"
#include "csr_prop.h"

csr_prop_t::csr_prop_t(const std::shared_ptr<csr_s>& _sign,
        const uint64_t& addr,
        const CSR_TYPE& _type,
        const uint32_t& _n_entries):
    sign(_sign), m_addr(addr), type(_type),
    n_entries(_n_entries), buf_sz(sign->sz()/8),
    addr_w(sign->_get_addr_w()), curr_inst(0) {
        /*
        std::cout << "ALLOC:CSR:"
            <<"N_ENTRIES:" << n_entries
            << ":BUF_SZ:" << buf_sz
            << ":ADDR_W:" << addr_w
            << ":REL_ADDR:0x"
            << std::hex << std::setfill('0') << std::setw(8)
            << m_addr << std::endl;
            */

}
void csr_prop_t::__init(void) {

    if (!is_init) {
        sign->_initialize();
        is_init = true;
    }

}

void csr_prop_t::_set_an_props(const uint64_t& addr,
        const uint8_t& n_ans,
        const uint64_t& _skip_addr) {
    m_addr += addr;
    /*
    std::cout << "SET_ADDR:CSR"
        << ":AN_NODES: " << static_cast<uint16_t>(n_ans)
        << ":SKIP_VAL:0x" << _skip_addr
        << ":B_ADDR:0x"
        << std::hex << std::setfill('0') << std::setw(10) << addr
        << ":E_SA:0x"
        << std::setw(10) << m_addr << std::endl;
        */
    num_an_nodes = n_ans;
    skip_addr = _skip_addr;
}
void csr_prop_t::_set_rd_cb(rd_fptr rd_fn) {
    r_fn = rd_fn;
}

void csr_prop_t::_set_wr_cb(wr_fptr wr_fn) {
    w_fn = wr_fn;
}

void csr_prop_t::release(void) {
    if(is_init) {
        sign->_deinit();
        is_init = false;
        curr_inst = 0;
    }
}
void csr_prop_t::raw_rd(uint8_t* raw_buf,
        const uint32_t& e_idx) {
    if (r_fn == nullptr) return;
    __init();
    assert (e_idx < n_entries);
    std::memset(raw_buf, 0, buf_sz);
    uint64_t f_addr = m_addr + (curr_inst * skip_addr) + (e_idx*addr_w);
    /*
    std::cout << "RD:CSR:INSTANCE:" << static_cast<uint16_t>(curr_inst)
        << ":ENTRY:" << e_idx << ":ADDR:0x"
        << std::hex << std::setfill('0') << std::setw(10)
        << f_addr << std::endl;
        */
    (*r_fn)(f_addr, raw_buf);
}
uint16_t csr_prop_t::sz() const {
    assert(buf_sz);
    return buf_sz;
}

void csr_prop_t::raw_wr(uint8_t* raw_buf,
        const uint32_t& e_idx) {
    if (w_fn == nullptr) return;
    assert(raw_buf);

    assert (e_idx < n_entries);
    uint64_t f_addr = m_addr + (curr_inst * skip_addr) + (e_idx*addr_w);
    /*
    std::cout << "WR:CSR:INSTANCE:" << static_cast<uint16_t>(curr_inst )
        << ":ENTRY:" << e_idx << ":ADDR:0x"
        << std::hex << std::setfill('0') << std::setw(10)
        << f_addr << std::endl;
        */
    (*w_fn)(f_addr, raw_buf);

}

uint64_t csr_prop_t::addr(const uint32_t& e_idx) const {

    return m_addr + (curr_inst * skip_addr) + (e_idx*addr_w);

}
csr_prop_t& csr_prop_t::_get_csr(const uint8_t& i_num) {
    assert(i_num < num_an_nodes);
    curr_inst = i_num;
    return *this;
}
