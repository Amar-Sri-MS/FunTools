/*
 *
 *  csr.cpp
 *
 *  Created by Hariharan Thantry on 2018-01-27
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#include <cstring>
#include <vector>
#include <iomanip>

#include "csr_c.h"

csr_c::csr_c(const csr_s& p, uint8_t* r_arr):
    m_sign(p), _sz(p.sz()/8), raw_arr(new uint8_t[_sz]) {
    if (r_arr) {
        std::memcpy(raw_arr, r_arr, _sz);
    }
    uint8_t* f_arr = nullptr;
    uint16_t st_off = 0;
    uint16_t width = 0;
    for (auto it = m_sign.begin(); it != m_sign.end(); it ++) {
        st_off = ((it->second).fld_off)%8;
        width = (it->second).width;
        if (r_arr) {
            f_arr = &raw_arr[st_off];
        }
        _initialize(it->first, st_off, width, f_arr);
    }
}


void csr_c::_initialize(const std::string& name, 
        const uint16_t& st_off, 
        const uint16_t& width, uint8_t* raw_val) {
    uint8_t arr_w = _get_width(st_off, width);

    auto val_arr = std::vector<uint8_t>(arr_w);
    auto mask_arr = std::vector<uint8_t>(arr_w);
    auto r_shift = std::vector<uint8_t>(arr_w);
    uint8_t l_shift = 0;

    if (width < 8 && arr_w == 1) {
        l_shift = (8 - width - st_off);
        r_shift[0] = 0;
        mask_arr[0] = 0xFF >> st_off;
        mask_arr[0] &= (0xFF << l_shift);
        if (raw_val) {
            val_arr[0] = (raw_val[0] & mask_arr[0]);
        }

    } else {
        uint8_t rem = width;
        uint8_t cons = 0;
        uint8_t idx = 0;
        uint16_t m_off = st_off;

        while ((rem > 8) || (m_off)) {
            r_shift[idx] = (rem - (8 - m_off));
            cons = 8 - m_off;
            m_off = 0;
            if (cons == 8) {
                mask_arr[idx] = 0xFF;
            } else {
                mask_arr[idx] = 0xFF >> cons; 
            }
            rem -= cons;
            if (raw_val) {
                val_arr[idx] = (raw_val[idx] & mask_arr[idx]);
            }
            idx ++;

        }
        if (rem) {
            l_shift = (8 - rem);
            mask_arr[idx] = 0xFF << l_shift;
            if (raw_val) {
                val_arr[idx] = (raw_val[idx] & mask_arr[idx]);
            }
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
    val_map[name] = val_arr;
    mask_map[name] = mask_arr;
    shift_map[name] = std::make_pair(l_shift, r_shift);

}

uint8_t* csr_c::operator()(void) {
    return raw_arr;
}

csr_c::~csr_c() {
    
    val_map.clear();
    mask_map.clear();
    shift_map.clear();

    if (raw_arr) {
         delete[] raw_arr;
         raw_arr = nullptr;
    }
}

uint8_t csr_c::_get_width(const uint8_t& st_off, const uint16_t& width) {
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


std::ostream& operator<<(std::ostream& os, csr_c& obj) {
    uint64_t val;
    for (auto it = obj.m_sign.cbegin(); it != obj.m_sign.cend(); it ++) {
        os << std::setw(2) << it->first << ":" << std::endl;
        obj.get((it->first).c_str(), val);
        os << std::setw(4) << it->second << std::endl;
        os << std::setw(4) << "v:" << std::hex << std::showbase << val << std::dec << std::endl;
        os << std::endl;
    }
    return os;
}
