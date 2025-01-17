/*
 *  csr.h
 *
 *  Created by Hariharan Thantry on 2018-02-26
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include <iostream>
#include <tuple>
#include <unordered_map>
#include <vector>

#include "csr_an.h"
#include "csr_prop.h"
#include "csr_s.h"

#include "ring_coll.h"


#define ADD_ENTRY(m, k0, v0, v1) m.emplace(std::piecewise_construct, std::forward_as_tuple(k0), std::forward_as_tuple(v0, v1))

typedef std::unordered_map<const char*, ring_coll_t> ring_t;
class F1NS {
    public:
        static F1NS& get() {
             static F1NS m{};
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

        ring_coll_t& operator[](const char* name);
        csr_prop_t& get_csr(const char* csr_name, const uint8_t& inst_num=0);
        void add_csr(addr_node_t* an, const char* name, csr_prop_t& csr);
        uint16_t num_inst(const char* csr_name) const;
    private:
        /*
         * For each ring, NU, HU, HNU etc
         */
        ring_t sys_rings;
        std::map<const char*, std::vector<addr_node_t*>> csr_addrs;

        F1NS(void);
};
