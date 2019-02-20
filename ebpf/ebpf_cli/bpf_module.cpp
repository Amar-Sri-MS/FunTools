

#include "cli_module.h"
#include "bpf_module.h"

#include <deque>
#include <iostream>
#include <sstream>
#include <string>

bpf_module::bpf_module(void) {}
bpf_module::~bpf_module(){}

std::deque<std::string> bpf_module::__tokenize(const std::string& str) {
    std::istringstream ss(str);
    std::deque<std::string> v;
    std::string token;
    while(std::getline(ss, token, _KV_TOKEN)) {
        v.emplace_back(token);
    }
    assert(v.size() == 2);
    return v;
}


bool bpf_module::__process(std::deque<std::string>& params) {
   for (auto& p: params) {
      auto m_pair = __tokenize(p);
      auto key = m_pair[0];
      auto val = m_pair[1];
      if (key == "sec") {
          assert(val == "xdp");
             

      }






   }
   return false;



}


bool bpf_module::execute(std::deque<std::string>& params) {
    auto rval = true;
    auto cmd = params.front();
    params.pop_front();
    rval &= (cmd == "attach" || cmd == "detach");
    if (cmd == "attach") {
        rval &= (params.size() == _ATTACH_NUM_KEYS);
    } else if (cmd == "detach") {
        rval &= (params.size() == _DETACH_NUM_KEYS);
    }
    if (!rval) return rval;
    return __process(params); 
}

