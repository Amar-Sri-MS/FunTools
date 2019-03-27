/*
 *  cli_mgr.h
 *
 *  Created by Hariharan Thantry on 2019-02-01
 *
 *  Copyright © 2019 Fungible Inc. All rights reserved.
 *  
 *  Provides a small wrapper for all modules that want to interact
 *  with the 
 *
 */

#pragma once
#include <string>
#include <unordered_map>
#include <utility>


#include "cli_module.h"
#include "tcp_cli.h"


class cli_mgr {
  public:
     explicit cli_mgr(const char* host, const uint16_t& port) { __init(host, port);}

     /*
      * Call this method to process. Can be used by multiple front ends
      */

     bool process(const std::string& mod, 
		  std::unordered_map<std::string, std::string>& params);
     ~cli_mgr();

  private:
      
      tcp_cli __tcp_h;
      bool __started{false};
      void __init(const char* host, const uint16_t& port);
};
