/*
 *  dummy.cpp
 *
 *  Created by Hariharan Thantry on 2018-03-03
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#include <cassert>
#include <iomanip>
#include <iostream>
#include <map>


std::map<uint64_t, uint64_t> gbl;
void dummy_wr(uint64_t addr, uint8_t* arr) {
    uint64_t m_val = 0;
    uint8_t i = 0;
    for (; i < 7; i ++) {
        m_val |= arr[i];
        m_val <<= 8;
    }
    m_val |= arr[i];
    std::cout << "[WR]: ADDR:0x"
        << std::setfill('0') << std::setw(10)
        << std::hex << addr
        << ":VAL: 0x"
        << std::setfill('0') << std::setw(16)
        << std::hex << m_val << std::endl;
    gbl[addr] = m_val;
}
void dummy_rd(uint64_t addr, uint8_t* arr) {
    auto it = gbl.find(addr);
    assert (it != gbl.end());
    auto m_val = it->second;
    std::cout << "[RD]: ADDR:0x"
        << std::setfill('0') << std::setw(10)
        << std::hex << addr
        << ":VAL: 0x"
        << std::setfill('0') << std::setw(16)
        << std::hex << m_val << std::endl;
    auto i = 7;
    while (i >= 0) {
        arr[i] = m_val & 0xFF;
        m_val >>= 8;
        --i;
    }
}
