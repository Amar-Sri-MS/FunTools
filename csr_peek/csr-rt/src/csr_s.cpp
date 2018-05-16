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
#include <vector>

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

uint16_t csr_s::_get_addr_w(void) const {
    return __get_addr_w(sz());

}

uint16_t csr_s::__get_addr_w(const uint16_t& w) const {
    if (w <= 64) return 8;
    return (__get_addr_w(w >> 1) << 1);
}

void csr_s::_initialize(void) {
    uint16_t st_off = 0;
    uint16_t w = 0;
    for (auto it = fld_map.begin(); it != fld_map.end(); it ++) {
        st_off = ((it->second).fld_off)%8;
        w = (it->second).width;
        __init(it->first, st_off, w);
    }
}
void csr_s::_deinit(void) {
    mask_map.clear();
    shift_map.clear();
}


uint8_t csr_s::__get_w(const uint8_t& st_off, const uint16_t& width) {
   uint16_t w = 0;
   int16_t t_w = width;
   if (st_off) {
       w += 1;
       t_w -= (8 - st_off);
   }
   if (t_w > 0) {
       w += (t_w / 8);
       if (t_w % 8) {
           w += 1;
       }
   }
   return w;
}

void csr_s::__init(const std::string& name,
        const uint16_t& st_off,
        const uint16_t& width) {
    uint16_t arr_w = __get_w(st_off, width);
    auto mask_arr = std::vector<uint8_t>(arr_w);
    auto r_shift = std::vector<uint8_t>(arr_w);
    uint8_t l_shift = 0;

    if (width < 8 && arr_w == 1) {
        l_shift = (8 - width - st_off);
        r_shift[0] = 0;
        mask_arr[0] = 0xFF >> st_off;
        mask_arr[0] &= (0xFF << l_shift);

    } else {
        uint8_t rem = width;
        uint8_t cons = 0;
        uint8_t idx = 0;
        uint16_t m_off = st_off;

        while ((rem > 8) || (m_off)) {
            r_shift[idx] = (rem - (8 - m_off));
            cons = 8 - m_off;
            if (cons == 8) {
                mask_arr[idx] = 0xFF;
            } else {
                mask_arr[idx] = 0xFF >> m_off;
            }
            m_off = 0;
            rem -= cons;
            idx ++;
        }
        if (rem) {
            l_shift = (8 - rem);
            mask_arr[idx] = 0xFF << l_shift;
        }
    }
    /*
    std::cout << "fld: " << name << ":st_off: " << st_off << ":width: " << width << std::endl;
    for (uint8_t i = 0; i < arr_w; i ++) {
        std::cout << "r_shift[ " << (uint16_t)i << "] = "
            << (uint16_t)r_shift[i] << " mask = " << std::hex << (uint16_t) mask_arr[i] << std::endl;

    }
    std::cout << std::dec << "l_shift: " << (uint16_t)l_shift << std::endl;
    */
    /* Finally set the name -> maps mapping */


    mask_map.emplace(std::make_pair(name, mask_arr));
    shift_map.emplace(std::make_pair(name, std::make_pair(l_shift, r_shift)));
}


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
