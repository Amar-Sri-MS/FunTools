#pragma once

/*
 * Base Module class that must be overridden by every
 * module. Every module can be expected to be called once
 */



#include <deque>
#include <string>


/*
 * All Modules must add a unique ID here
 */

enum class ModuleID {
    BPF
};

class cli_module {

  public:
    //cli_module(const ModuleID& my_id):this_id(my_id) {}
    //cli_module(void) {}
    virtual bool execute(std::deque<std::string>& params) = 0;
  
  protected:
    //ModuleID this_id;
};

