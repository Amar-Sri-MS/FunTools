#pragma once

/*
 * Base Module class that must be overridden by every
 * module. Every module can be expected to be called once
 */



#include <unordered_map>
#include <string>

class cli_module {

  public:
    virtual void* create_request(std::unordered_map<std::string, std::string>& params) = 0;
    virtual ~cli_module(){}  
};

