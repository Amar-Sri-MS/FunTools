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



class csr_grp_t;
class csr_prop_t {
    public:
        explicit csr_prop_t(const std::shared_ptr<csr_s>& sign,
                const uint64_t& addr,
                const CSR_TYPE& type,
                const uint16_t& addr_w,
                const uint32_t& n_entries=1);
        /*
         *
         */
        template <typename T>
            void set(const std::string& fld_name, const T& val);
        template <typename T>
            void get(const std::string& fld_name, T& val);
         /*
          * Returns the current raw buffer
          */
         uint8_t* get(void);

         /*
          * Clears up the buffer
          */
         void reset(void);

         /*
          * Flush/Read from a lower level agent.
          * Ideally, this should be a previously registered handler.
          */

         void flush(const uint32_t& e_idx = 0);
         uint8_t* read_raw(const uint32_t& e_idx = 0);

         void release();

    private:
        std::shared_ptr<csr_s> sign;
        uint64_t m_addr;
        CSR_TYPE type;
        uint32_t addr_w{0};
        uint32_t n_entries{1};
        bool is_init{false};
        uint8_t* raw_buf{nullptr};

        void __init(void);
        void set_base(const uint64_t& base_addr);
        friend class csr_grp_t;
};

template <typename T>
void csr_prop_t::set(const std::string& fld_name, const T& val) {
    std::cout << "ADDR:0x" << std::hex << m_addr << ":FLD: " << fld_name << ":VAL: " << val << std::endl;
    __init();
    sign->_set(fld_name, val, raw_buf);

}

template <typename T>
void csr_prop_t::get(const std::string& fld_name, T& val) {
    assert(raw_buf != nullptr);
    sign->_get(fld_name, val, raw_buf);
}
