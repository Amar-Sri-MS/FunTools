/*
 *  csrsh.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#pragma once
#include "csr.h"
//#include "dpc_port.h"
#include <map>
#include <utility>
#include "json_util.h"
#include "tcp_cli.h"

class CsrSh {
  public:
     CsrSh(const std::string& host, const uint16_t& port):ns_h(F1NS::get()) { __init(host, port);}
     void dump_csr(const std::string& csr_name);
     void set_csr(const std::string& csr_name);
     void set_raw(const std::string& csr_name);
     void show_buffer(void);
     void fetch(const std::string& csr_name, const uint16_t& inst_num, const uint32_t& entry_num);
     void flush(const std::string& csr_name, const uint16_t& inst_num, const uint32_t& entry_num);
     ~CsrSh();
  private:
      F1NS& ns_h;
      tcp_cli tcp_h;
      json_util json_acc;
      std::map<std::string, std::pair<uint8_t*, uint16_t>> mp_buf;
      void __init(const std::string& host, const uint16_t& port);
      void __interpret(const std::string& csr_name, uint8_t* buf);
};