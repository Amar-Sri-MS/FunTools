#pragma once
#include "csr.h"
//#include "dpc_port.h"
#include <map>
#include <utility>
#include "json_util.h"
#include "tcp_cli.h"

class CsrSh {
  public:
     CsrSh():ns_h(F1NS::get()) { __init();}
     void dump_csr(const std::string& csr_name);
     void set_csr(const std::string& csr_name);
     void set_raw(const std::string& csr_name);
     void show_buffer(void);
     void fetch(const std::string& csr_name, const uint16_t& inst_num, const uint32_t& entry_num);
     void flush(const std::string& csr_name, const uint16_t& inst_num, const uint32_t& entry_num);
  private:
      F1NS& ns_h;
      tcp_cli tcp_h;
      json_util json_acc;
      std::map<std::string, std::pair<uint8_t*, uint16_t>> mp_buf;
      void __init(void);
};
