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
     CsrSh(const char* host, const uint16_t& port):ns_h(F1NS::get()) { __init(host, port);}
     void dump_csr(const char* csr_name);
     void set_csr(const char* csr_name);
     void set_raw(const char* csr_name);
     void show_buffer(void);
     void fetch(const char* csr_name, const uint16_t& inst_num, const uint32_t& entry_num);
     void flush(const char* csr_name, const uint16_t& inst_num, const uint32_t& entry_num);
     ~CsrSh();
  private:
      F1NS& ns_h;
      tcp_cli tcp_h;
      json_util json_acc;
      std::map<const char*, std::pair<uint8_t*, uint16_t>> mp_buf;
      void __init(const char* host, const uint16_t& port);
      void __interpret(const char* csr_name, uint8_t* buf);
};
