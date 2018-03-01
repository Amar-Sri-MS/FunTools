/*
 *  signature.cpp
 *
 *  Created by Hariharan Thantry on 2018-01-27
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#include <cassert>
#include "csr_s.h"
#include <iostream>
#include <iomanip>

fld_off_t::fld_off_t(const uint16_t& off, const uint16_t& w):fld_off(off), width(w) {}

std::ostream& operator<<(std::ostream& os, const fld_off_t& obj) {
    os << "o: " << obj.fld_off << std::endl;
    os << "w: " << obj.width << std::endl;
    return os;
}

csr_s::csr_s(const csr_s& other):
    fld_map(other.fld_map) {}

csr_s& csr_s::operator=(const csr_s& other) {
    if (this != &other) {
        fld_map.insert(other.fld_map.begin(), other.fld_map.end());
    }
    return (*this);
}
csr_s::csr_s(void){}


const fld_off_t& csr_s::operator[](const std::string& key) const {
    auto it = fld_map.find(key);
    assert (it != fld_map.end());
    return it->second;
}

csr_s::csr_s(const fld_map_t& i_fld_map) {
    fld_map.insert(i_fld_map.begin(), i_fld_map.end());
}

uint16_t csr_s::sz(void) const {
    uint16_t sz = 0;
    for(auto elem: fld_map) {
        sz += elem.second.width;
    }
    return sz;
}

std::ostream& operator<<(std::ostream& os, const csr_s& obj) {
    for (auto& elem: obj.fld_map) {
        os <<  elem.first << ":" << std::endl;
        os << std::setw(2) << elem.second << std::endl;
    }
    return os;
}
