/*
 *  csr.h
 *
 *  Created by Hariharan Thantry on 2018-02-26
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include <iostream>
#include <unordered_map>
#include <vector>

#include "csr_an.h"
#include "csr_prop.h"
#include "csr_s.h"

#include "ring_coll.h"


#define CREATE_ENTRY(k0, v0, v1) {k0, fld_off_t(v0, v1)}

typedef std::unordered_map<std::string, ring_coll_t, string_hash> ring_t;
class F1NS {
    public:
        static F1NS& get(rd_fptr rd_fn=nullptr, wr_fptr wr_fn=nullptr) {
             static F1NS m(rd_fn, wr_fn);
             return m;
        }
        F1NS& operator=(const F1NS& other) =delete;
        F1NS(const F1NS& other) =delete;

        typedef ring_t::iterator iterator;
        typedef ring_t::const_iterator const_iterator;
        inline iterator begin() noexcept { return sys_rings.begin(); }
        inline iterator end() noexcept { return sys_rings.end(); }
        inline const_iterator cbegin() const noexcept { return sys_rings.cbegin(); }
        inline const_iterator cend() const noexcept { return sys_rings.cend(); }

        ring_coll_t& operator[](const std::string& name);
        csr_prop_t& get_csr(const std::string& csr_name, const uint8_t& inst_num=0);
        void add_csr(addr_node_t* an, const std::string& name, csr_prop_t& csr);

    private:
        /*
         * For each ring, NU, HU, HNU etc
         */
        rd_fptr m_rd_fn{nullptr};
        wr_fptr m_wr_fn{nullptr};
        ring_t sys_rings;
        std::map<std::string, std::vector<addr_node_t*>> csr_addrs;

        F1NS(rd_fptr rd, wr_fptr wr);
};
