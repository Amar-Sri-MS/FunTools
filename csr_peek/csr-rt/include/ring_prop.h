/*
 *  ring_prop.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include <map>
#include <memory>
#include <vector>

#include "csr_an.h"
#include "csr_grp.h"
#include "csr_type.h"

class ring_prop_t {
   public:
       ring_prop_t(const uint64_t& base_addr);
       csr_grp_t& operator[](const std::string& name);
       void add_csr(addr_node_t* a_node,
               const std::string& name, 
               const std::shared_ptr<csr_s>& sign, 
               const uint32_t& a_off,
               const CSR_TYPE& type,
               const uint16_t& n_entries=1,
               const uint8_t& n_inst=1);

       addr_node_t* add_an(const uint8_t& n_args, ...);

   private:
       addr_node_t* _construct(const std::vector<addr_node_t>& tmp_vec);
       addr_node_t* _get(const addr_node_t& tmp_vec);
       std::map<std::string, csr_grp_t> csr_prop;
       std::vector<addr_node_t*> children;
       uint64_t base_addr;

};
