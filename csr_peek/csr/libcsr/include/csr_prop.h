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

class csr_prop_t {
    public:
        typedef fld_map_t::iterator iterator;
        typedef fld_map_t::const_iterator const_iterator;

        explicit csr_prop_t(csr_s* sign,
                const uint64_t& addr,
                const uint32_t& n_entries=1);
	~csr_prop_t(void);
        /*
         *
         */
        template <typename T>
            void set(const char *fld_name, const T& val, uint8_t* raw_buf);
        template <typename T>
            void get(const char *fld_name, T& val, uint8_t* raw_buf);

        void set_an_props(const uint64_t& base_addr,
                const uint8_t& num_an,
                const uint64_t& skip_addr);
        csr_prop_t& get_csr(const uint8_t& e_num);
         /*
          * Get the address given an instance number
          */
         uint64_t addr(const uint32_t& e_num=0) const;
         uint32_t num_entries(void) const;

         uint16_t sz() const;
         inline iterator begin() noexcept { return sign->begin(); }
         inline iterator end() noexcept { return sign->end(); }
         inline const_iterator cend() noexcept { return sign->cend(); }
         inline const_iterator cbegin() noexcept { return sign->cbegin(); }

    private:
        csr_s* sign{nullptr};
        uint64_t m_addr;
        uint32_t n_entries{1};
        uint8_t num_an_nodes{1};
        uint64_t skip_addr{0};
        uint16_t buf_sz{0};
        uint32_t addr_w{0};
        uint8_t curr_inst{0};

};

template <typename T>
void csr_prop_t::set(const char *fld_name, const T& val, uint8_t* raw_buf) {
    //std::cout << "FLD: " << fld_name << ":VAL: " << val << std::endl;
    sign->set(fld_name, val, raw_buf);

}

template <typename T>
void csr_prop_t::get(const char *fld_name, T& val, uint8_t* raw_buf) {
    assert(raw_buf != nullptr);
    sign->get(fld_name, val, raw_buf);
}
