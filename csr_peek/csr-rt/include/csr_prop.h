/*
 *  csr_prop.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include <iostream>
#include <memory>
#include <vector>

#include "csr_type.h"
#include "csr_s.h"

class csr_prop_t {
    public:
        explicit csr_prop_t(const std::shared_ptr<csr_s>& sign,
                const uint64_t& addr,
                const CSR_TYPE& type,
                const uint16_t& addr_w,
                const uint32_t& n_entries=1);
        /*
         * Here you need to have set/get (Field) 
         * read/write with flags
         */
        template <typename T>
            void set(const char* fld_name, const T& val);
        template <typename T>
            void get(const char* fld_name, T& val);

         void write(const uint32_t& e_idx = 0){};
         void set_base(const uint64_t& base_addr);

    private:
        std::shared_ptr<csr_s> sign;
        uint64_t m_addr;
        CSR_TYPE type;
        uint32_t addr_w{0};
        uint32_t n_entries{1};
};

template <typename T>
void csr_prop_t::set(const char* fld_name, const T& val) {
    std::cout << "ADDR:0x" << std::hex << m_addr << ":FLD: " << fld_name << ":VAL: " << val << std::endl;

}

template <typename T>
void csr_prop_t::get(const char* fld_name, T& val) {

}
