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
       //csr_grp_t& operator[](const std::string& name);

       //addr_node_t* add_an(const uint8_t& n_args, ...);
       addr_node_t* add_an(const std::vector<std::string>& hier,
               const uint32_t& n_addr);

   private:
       addr_node_t* _construct(const std::vector<addr_node_t>& tmp_vec);
       addr_node_t* _get(const addr_node_t& tmp_vec);
       std::vector<addr_node_t*> children;
       uint64_t base_addr;

};
