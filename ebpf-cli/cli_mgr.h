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
#include <deque>
#include <map>
#include <string>
#include <utility>


#include "cli_module.h"
#include "json_util.h"
#include "tcp_cli.h"


class cli_mgr {
  public:
     explicit cli_mgr(const char* host, const uint16_t& port) { __init(host, port);}
     bool process(const ModuleID& mod, std::deque<std::string>& params);
     ~cli_mgr();

  private:
      
      tcp_cli tcp_h;
      json_util json_acc;
      std::map<int, cli_module*> mod_map;
      void __init(const char* host, const uint16_t& port);
};
