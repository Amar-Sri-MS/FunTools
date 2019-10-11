/*
*  cli_module.h
*
*  Created by Hariharan Thantry on 2019-04-01
*
*  Interface definition for any module that wants to communicate
*  with dpc proxy
*
*  Copyright © 2019 Fungible Inc. All rights reserved.
*
*/



#pragma once

/*
 * Base Module class that must be overridden by every
 * module. Every module can be expected to be called once
 */



#include <unordered_map>
#include <utility>
#include <string>

class cli_module {

  public:
    virtual std::pair<uint8_t*, size_t> create_bin_request(std::unordered_map<std::string, std::string>& params) = 0;
    virtual void* create_js_req(std::unordered_map<std::string,
		    std::string>& params) = 0;
    virtual ~cli_module(){}
};

