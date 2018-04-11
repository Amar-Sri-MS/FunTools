#pragma once
#include "csr.h"

class CsrSh {
  public:	
     CsrSh():ns_h(F1NS::get()) { }
     void dump_csr(const std::string& csr_name);
  private:
      F1NS& ns_h;      

};
