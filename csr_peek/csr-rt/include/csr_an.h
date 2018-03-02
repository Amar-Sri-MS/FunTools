/*
 *  csr_an.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include "csr_grp.h"

class addr_node_t {
    public:
        addr_node_t(const std::string& name = "");
        addr_node_t(const addr_node_t& other);
        addr_node_t& operator=(const addr_node_t& other);
        void append_csr(const csr_grp_t& csr);
        bool operator==(const addr_node_t& other) const;
        bool operator!=(const addr_node_t& other) const;
        addr_node_t* get(const addr_node_t& elem);

    private:
        std::string name;
        std::vector<addr_node_t*> children;

        /* For the final addr_node, a list of all the csrs */
        std::vector<csr_grp_t> csrs;
        
};
