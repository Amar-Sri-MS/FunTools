/*
 *  csr_an.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include <map>
#include "csr_grp.h"


class addr_node_t {
    public:
        addr_node_t(const std::string& name, const uint64_t& addr);

        addr_node_t(const addr_node_t& other);
        addr_node_t& operator=(const addr_node_t& other);
        void add_csr(const std::string& name,
                csr_grp_t& csr,
                rd_fptr r_fn = nullptr,
                wr_fptr w_fn = nullptr);


        csr_prop_t& get_csr(
                const std::string& csr_name,
                const uint8_t& gid);

        bool operator==(const addr_node_t& other) const;
        bool operator!=(const addr_node_t& other) const;
        addr_node_t* get(const addr_node_t& elem);

    private:
        std::string name;
        std::vector<addr_node_t*> children;
        std::map<std::string, csr_grp_t> csr_props;
        uint64_t base_addr{0};
        /* For the final addr_node list of all the csrs */

};
