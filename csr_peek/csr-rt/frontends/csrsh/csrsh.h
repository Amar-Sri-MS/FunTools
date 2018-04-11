#pragma once
#include "csr.h"
#include <map>
#include <utility>

class CsrSh {
  public:	
     CsrSh():ns_h(F1NS::get()) { }
     void dump_csr(const std::string& csr_name);
     void set_csr(const std::string& csr_name);
  private:
      F1NS& ns_h;      
      std::map<std::string, std::pair<uint8_t*, uint16_t>> mp_buf;
};
