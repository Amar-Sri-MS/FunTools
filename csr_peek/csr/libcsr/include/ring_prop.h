/*
 *  ring_prop.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include <unordered_map>
#include <memory>
#include <vector>

#include "csr_an.h"
#include "csr_prop.h"
#include "csr_type.h"
#include "csr_utils.h"

class ring_node_t {
  public:
      ring_node_t(const char* _name,
              const uint8_t& _level);
      bool operator==(const ring_node_t& other) const;
      uint8_t get_level(void) const;
      const char* get_name(void) const;
  private:
      const char* name;
      uint8_t level;
};


namespace std {
    template<>
        struct hash<ring_node_t> {
            size_t operator()(const ring_node_t& rn) const {
                return (hash<const char*>()(rn.get_name()) ^ (hash<uint8_t>()(rn.get_level())));
            }
        };
};


class ring_prop_t {
   public:
       ring_prop_t(const uint64_t& base_addr);
       addr_node_t* add_an(const std::vector<const char*>& hier,
               const uint32_t& base_addr,
               const uint8_t& n_instances=1,
               const uint32_t& addr_skip=0x0);
       std::vector<addr_node_t*> get_anodes(const std::vector<const char*>& hier);

   private:
       /*
        * Keeps a map of number of instances of a particular
        * address node that have been seen so far. Keeps a global ordering
        * of all instance ids across all rings
        */

       static std::unordered_map<const char*, uint8_t,
           string_hash> an_id_map;
       uint64_t base_addr;
       std::unordered_multimap<ring_node_t, addr_node_t*> addr_tree;
};
