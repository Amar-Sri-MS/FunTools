/*
 *  csr_an.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include <map>
#include "csr_prop.h"


class addr_node_t {
    public:
        addr_node_t(const std::string& name,
               const uint64_t& addr,
               const uint8_t& start_id,
               const uint8_t& n_instance,
               const uint64_t& skip_addr);

        addr_node_t(const addr_node_t& other);
        addr_node_t& operator=(const addr_node_t& other);
        void add_csr(const std::string& name,
                csr_prop_t& csr,
                rd_fptr r_fn = nullptr,
                wr_fptr w_fn = nullptr);

        uint8_t get_num_nodes(void) const;
        uint8_t get_start_id(void) const;
        std::string get_name(void) const;
        csr_prop_t& get_csr(
                const std::string& csr_name,
                const uint8_t& gid);

        bool operator==(const addr_node_t& other) const;
        bool operator!=(const addr_node_t& other) const;

    private:
        std::string name;
        uint64_t base_addr{0};
        uint8_t start_id{0};
        uint8_t n_instances{1};
        uint64_t skip_addr{0};

        std::map<std::string, csr_prop_t> csr_props;

        /* For the final addr_node list of all the csrs */

};
