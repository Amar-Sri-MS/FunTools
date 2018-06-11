/*
 *  csr.h
 *
 *  Created by Hariharan Thantry on 2018-01-27
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include <cassert>
#include <iostream>
#include <map>
#include <vector>

#include <stdint.h>

#include "csr_s.h"

class csr_c {
  public:
      explicit csr_c(const csr_s& p, uint8_t* raw_arr = nullptr);

      uint16_t sz(void) const { return _sz; }
      uint8_t* operator()(void);

      /* Getter & Setter */
      template <typename T>
      void get(const char* name, T& val);
      template <typename T>
      void set(const char* name, const T& val);

      ~csr_c(void);
  private:
      template <typename T>
          void _convert(const char*  r, const T& val);

      void _compute_shifts(const uint16_t& st_off, const uint16_t& width,
              uint8_t* mask_arr,uint8_t* r_shift, uint8_t& l_shift, uint16_t w);

      uint8_t _get_width(const uint8_t& st_off, const uint16_t& width);
      void _initialize(const char*  f_name, const uint16_t& st_off, const uint16_t& width, uint8_t* raw_arr);



      csr_s m_sign;
      /*
       * Keep caches to avoid having to recompute every time. Optimize for get, not set
       */
      std::map<const char*, std::vector<uint8_t>> val_map;
      std::map<const char*, std::vector<uint8_t>> mask_map;
      std::map<const char*, std::pair<uint8_t, std::vector<uint8_t>>> shift_map;

      uint16_t _sz{0};
      uint8_t* raw_arr{nullptr};

      friend std::ostream& operator<<(std::ostream& os, csr_c& obj);

};
/*
 * Create a byte array that exactly aligns with
 * raw array representation of the value
 * s_off represents the starting offset
 */

template <typename T>
void csr_c::_convert(const char*  fld_name, const T& val) {

   auto l_shift = shift_map[fld_name].first;
   auto r_shift = shift_map[fld_name].second;
   auto val_arr = val_map[fld_name];
   auto arr_w = val_arr.size();

   for (uint16_t i = 0; i < arr_w; i ++) {
       val_arr[i] = (val >> r_shift[i]) & 0xFF;
   }
   if (r_shift[arr_w - 1]) {
       val_arr[arr_w-1] |= (val << l_shift) & 0xFF;
   } else {
       val_arr[arr_w-1] = (val << l_shift) & 0xFF;
   }
   /*
   for (auto i = 0; i < arr_w; i ++) {
       std::cout << "i:" << i << ":0x"
           << std::hex << (uint16_t)val_arr[i] << std::endl;
   }
   */
   val_map[fld_name] = val_arr;

}

template <typename T>
void csr_c::set(const char* f_name, const T& val) {


    auto f_info = m_sign[f_name];
    auto f_start = f_info.fld_off;
    auto s_idx = f_start/8;

    _convert(f_name, val);
    auto it = val_map.find(f_name);
    assert (it != val_map.end());
    auto val_arr = val_map[f_name];
    auto mask_arr = mask_map[f_name];
    for (uint16_t i = 0; i < val_arr.size(); i ++) {
        raw_arr[i+s_idx] = ((raw_arr[i+s_idx] & ~mask_arr[i]) | (val_arr[i] & mask_arr[i]));
    }
    /*
    for (auto i = 0; i < _sz; i ++) {
        std::cout << std::dec << "raw_arr[" << i << "] = " << std::hex << (uint16_t) raw_arr[i] << std::endl;
    }
    */

}


template <typename T>
void csr_c::get(const char* f_name, T& rval) {
    rval = 0;
    auto it = val_map.find(f_name);
    assert (it != val_map.end());
    auto mask_arr = mask_map[f_name];
    auto l_shift = shift_map[f_name].second;
    auto r_shift = shift_map[f_name].first;
    auto val_arr = it->second;
    T curr_val = 0;
    uint16_t idx = 0;
    for (; idx < val_arr.size() - 1; idx ++) {
        /*
        std::cout << "idx: " << std::dec << idx
            << std::hex << "val : " << (uint16_t)val_arr[idx]
            << " mask : " << (uint16_t)mask_arr[idx] << std::endl;
        std::cout << "l_shift: " << std::dec << (uint16_t) l_shift[idx] << std::endl;
        */
        curr_val = (val_arr[idx] & mask_arr[idx]);
        curr_val <<= l_shift[idx];
        rval |= curr_val;
        //std::cout << "rval = " << std::hex << rval << std::endl;
    }
    //std::cout << "r_shift: " << (uint16_t) r_shift << std::endl;
    curr_val = (val_arr[idx] & mask_arr[idx]) >> r_shift;
    rval |= curr_val;
    //std::cout << "rval = " << std::hex << rval << std::endl;
}

