/*
 *  csr_s.h
 *
 *  Created by Hariharan Thantry on 2018-01-27
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

/*
 * Defines a signature class that must be passed in as a
 * parameter to each container created.
 */
#include <cassert>
#include <functional>
#include <map>
#include <memory>
#include <string>
#include <unordered_map>
#include <tuple>
#include <vector>

#include "stdint.h"
#include "csr_utils.h"

/* start off, width */
//typedef std::tuple<uint16_t, uint16_t> fld_off_t;

struct fld_off_t {

    uint16_t fld_off{0};
    uint16_t width{0};
    fld_off_t(const fld_off_t& other) = default;
    fld_off_t& operator=(const fld_off_t& other) = default;
    fld_off_t(const uint16_t& fld, const uint16_t& w);
    friend std::ostream& operator<<(std::ostream& os, const fld_off_t& obj);

};

typedef std::unordered_map<std::string, fld_off_t, string_hash> fld_map_t;

class csr_prop_t;
class csr_grp_t;

class csr_s {
    public:
        csr_s(void);
        csr_s(const fld_map_t& fld_map);
        const fld_off_t& operator[](const std::string& fld_name) const;
        csr_s(const csr_s& other);
        csr_s& operator=(const csr_s&);
        uint16_t sz(void) const;
        typedef fld_map_t::iterator iterator;
        typedef fld_map_t::const_iterator const_iterator;
        inline iterator begin() noexcept { return fld_map.begin(); }
        inline iterator end() noexcept { return fld_map.end(); }
        inline const_iterator cbegin() const noexcept { return fld_map.cbegin(); }
        inline const_iterator cend() const noexcept { return fld_map.cend(); }
    private:
        fld_map_t fld_map;
        std::map<std::string, std::vector<uint8_t>> mask_map;
        std::map<std::string, std::pair<uint8_t, std::vector<uint8_t>>> shift_map;

        void __init(const std::string& name, const uint16_t& st_off, const uint16_t& w);
        uint8_t __get_w(const uint8_t& st_off, const uint16_t& w);

        friend class csr_prop_t;
        void _initialize(void);
        void _deinit(void);
        template <typename T>
            void _set(const std::string& fld_name, const T& val, uint8_t* buf);

        template <typename T>
            void _get(const std::string& fld_name, T& val, uint8_t* buf);

        template <typename T>
            void __convert(const std::string& f_name, const T& val, uint8_t* val_arr);

        uint16_t __get_addr_w(const uint16_t& width) const;
        uint16_t _get_addr_w(void) const;


        friend std::ostream& operator<<(std::ostream& os, const csr_s& obj);
};

template <typename T>
void csr_s::__convert(const std::string& fld_name, const T& val, uint8_t* val_arr) {

   auto l_shift = shift_map[fld_name].first;
   auto r_shift = shift_map[fld_name].second;
   auto arr_w = r_shift.size();

   for (uint16_t i = 0; i < arr_w; i ++) {
       val_arr[i] = (val >> r_shift[i]) & 0xFF;
   }
   if (r_shift[arr_w - 1]) {
       val_arr[arr_w-1] |= (val << l_shift) & 0xFF;
   } else {
       val_arr[arr_w-1] = (val << l_shift) & 0xFF;
   }
}

template <typename T>
void csr_s::_set(const std::string& f_name, const T& val, uint8_t* raw_arr) {
    auto it = fld_map.find(f_name);
    assert(it != fld_map.end());

    auto s_idx = ((it->second).fld_off)/8;
    auto mask_arr = mask_map[f_name];
    uint8_t* val_arr = new uint8_t[mask_arr.size()];

    __convert(f_name, val, val_arr);
    for (uint16_t i = 0; i < mask_arr.size(); i ++) {
        raw_arr[i+s_idx] = ((raw_arr[i+s_idx] & ~mask_arr[i]) | (val_arr[i] & mask_arr[i]));
    }
    delete[] val_arr;
    /*
    for (auto i = 0; i < _sz; i ++) {
        std::cout << std::dec << "raw_arr[" << i << "] = " << std::hex << (uint16_t) raw_arr[i] << std::endl;
    }
    */
}

template <typename T>
void csr_s::_get(const std::string& f_name, T& rval, uint8_t* raw_arr) {

    rval = 0;
    auto it = fld_map.find(f_name);
    assert(it != fld_map.end());
    auto s_idx = ((it->second).fld_off)/8;
    auto mask_arr = mask_map[f_name];
    auto l_shift = shift_map[f_name].second;
    auto r_shift = shift_map[f_name].first;
    T curr_val = 0;
    uint16_t idx = 0;

    for (; idx < mask_arr.size() - 1; idx ++) {
        /*
        std::cout << "idx: " << std::dec << idx
            << std::hex << "val : " << (uint16_t)val_arr[idx]
            << " mask : " << (uint16_t)mask_arr[idx] << std::endl;
        std::cout << "l_shift: " << std::dec << (uint16_t) l_shift[idx] << std::endl;
        */
        curr_val = (raw_arr[s_idx+idx] & mask_arr[idx]);
        curr_val <<= l_shift[idx];
        rval |= curr_val;
        //std::cout << "rval = " << std::hex << rval << std::endl;
    }
    //std::cout << "r_shift: " << (uint16_t) r_shift << std::endl;
    curr_val = (raw_arr[s_idx+idx] & mask_arr[idx]) >> r_shift;
    rval |= curr_val;
}

