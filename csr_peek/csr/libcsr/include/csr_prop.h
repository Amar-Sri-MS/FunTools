/*
 *  csr_prop.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include <iostream>
#include <iterator>
#include <memory>
#include <vector>

#include "csr_type.h"
#include "csr_s.h"

typedef void (*rd_fptr)(uint64_t addr, uint8_t* arr);
typedef void (*wr_fptr)(uint64_t addr, uint8_t* arr);


class csr_prop_t {
    public:
        typedef fld_map_t::iterator iterator;
        typedef fld_map_t::const_iterator const_iterator;

        explicit csr_prop_t(const std::shared_ptr<csr_s>& sign,
                const uint64_t& addr,
                const CSR_TYPE& type,
                const uint32_t& n_entries=1);
        /*
         *
         */
        template <typename T>
            void set(const char *fld_name, const T& val, uint8_t* raw_buf);
        template <typename T>
            void get(const char *fld_name, T& val, uint8_t* raw_buf);

         /*
          * Flush/Read from a lower level agent.
          * Ideally, this should be a previously registered handler.
          */

         void raw_wr(uint8_t* raw_buf, const uint32_t& e_idx = 0);
         void raw_rd(uint8_t* raw_buf, const uint32_t& e_idx = 0);


         /*
          * Get the address given an instance number
          */
         uint64_t addr(const uint32_t& e_num=0) const;
         uint32_t num_entries(void) const;

         uint16_t sz() const;
         void release();
         inline iterator begin() noexcept { return sign->begin(); }
         inline iterator end() noexcept { return sign->end(); }
         inline const_iterator cend() noexcept { return sign->cend(); }
         inline const_iterator cbegin() noexcept { return sign->cbegin(); }

    private:
        std::shared_ptr<csr_s> sign;
        uint64_t m_addr;
        CSR_TYPE type;
        uint32_t n_entries{1};
        uint8_t num_an_nodes{1};
        uint64_t skip_addr{0};
        uint16_t buf_sz{0};
        uint32_t addr_w{0};
        uint8_t start_id{0};
        uint8_t curr_inst{0};
        bool is_init{false};
        rd_fptr r_fn{nullptr};
        wr_fptr w_fn{nullptr};

        void __init(void);

        friend class addr_node_t;
        void _set_an_props(const uint64_t& base_addr,
                const uint8_t& num_an,
                const uint64_t& skip_addr);
        csr_prop_t& _get_csr(const uint8_t& e_num);

        void _set_rd_cb(rd_fptr r_fn = nullptr);
        void _set_wr_cb(wr_fptr w_fn = nullptr);
};

template <typename T>
void csr_prop_t::set(const char *fld_name, const T& val, uint8_t* raw_buf) {
    //std::cout << "FLD: " << fld_name << ":VAL: " << val << std::endl;
    __init();
    sign->_set(fld_name, val, raw_buf);

}

template <typename T>
void csr_prop_t::get(const char *fld_name, T& val, uint8_t* raw_buf) {
    assert(raw_buf != nullptr);
    sign->_get(fld_name, val, raw_buf);
}
