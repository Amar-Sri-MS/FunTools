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

csr_prop_t::csr_prop_t(csr_s* _sign,
        const uint64_t& addr,
        const uint32_t& _n_entries):
    sign(_sign), m_addr(addr),
    n_entries(_n_entries), buf_sz(sign->sz()/8),
    addr_w(sign->get_addr_w()), curr_inst(0) {
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
csr_prop_t::~csr_prop_t() {
    sign->deinit();
    delete sign;
    sign = nullptr;

}

uint32_t csr_prop_t::num_entries(void) const {
    return n_entries;
}
void csr_prop_t::set_an_props(const uint64_t& addr,
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

uint16_t csr_prop_t::sz() const {
    assert(buf_sz);
    return buf_sz;
}

uint64_t csr_prop_t::addr(const uint32_t& e_idx) const {

    return m_addr + (curr_inst * skip_addr) + (e_idx*addr_w);

}
csr_prop_t& csr_prop_t::get_csr(const uint8_t& i_num) {
    //assert(i_num < num_an_nodes);
    curr_inst = i_num;
    return *this;
}
