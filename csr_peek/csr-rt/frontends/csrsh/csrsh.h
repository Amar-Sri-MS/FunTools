#pragma once
#include "csr.h"
#include <map>
#include <utility>

class CsrSh {
  public:	
     CsrSh():ns_h(F1NS::get()) { }
     void dump_csr(const std::string& csr_name);
     void set_csr(const std::string& csr_name);
     void set_raw(const std::string& csr_name);
     void show_buffer(void);
     void fetch(const std::string& csr_name, const uint16_t& inst_num, const uint32_t& entry_num);
     void flush(const std::string& csr_name, const uint16_t& inst_num, const uint32_t& entry_num);
  private:
      F1NS& ns_h;      
};
