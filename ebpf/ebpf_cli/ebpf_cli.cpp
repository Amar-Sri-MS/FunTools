/*
 *  ebpf_cli.cpp
 *
 *  Created by Hariharan Thantry on 2019-03-20
 *
 *  Copyright © 2019 Fungible Inc. All rights reserved.
 */
#include <cassert>
#include <iostream>
#include <sstream>
#include <unordered_map>
#include <vector>

#ifdef __cplusplus
extern "C" {
#endif
/* C header files */

#include <getopt.h>

#ifdef __cplusplus
}
#endif
#include "cli_mgr.h"
#define DPC_PORT 40221
static const char *DEF_MOD = "bpf";

void help(void) {
  std::cout << std::endl;
  std::cout << std::endl;
  std::cout << "**** Commandline frontend for transfering/installing ebpf "
               "bytes to FunOS ***"
            << std::endl;
  std::cout << "-h: This help" << std::endl;
  std::cout << "-S {hostname} | --dpc_host={hostname}: remote dpc host to "
               "connect to (default: localhost)"
            << std::endl;
  std::cout << "-p {portnum}  | --dpc_port={portnum}: dpc host port to connect "
               "to (default:"
            << DPC_PORT << ")" << std::endl;

  std::cout << "-m {modulename}  | --module_name={module}: module inside FunOS "
               "to target(default:"
            << DEF_MOD << ")" << std::endl;
  std::cout << std::endl;
  std::cout << std::endl;

  std::cout << "******Set of args******" << std::endl;
  std::cout << "all of form KEY=VALUE separated by space " << std::endl;
  std::cout << "Allowed KEY=VALUE pairs" << std::endl;
  std::cout << "cmd=(attach | detach)" << std::endl;
  std::cout << "sec=(xdp) (FunOS section to attach to. [Attach & Detach]"
            << std::endl;
  std::cout << "cl_id=<client_id> (unique client id    [Attach & Detach)"
            << std::endl;
  std::cout
      << "tx_id=<tx_id> (transaction ID for this bytecode [Attach & Detach]"
      << std::endl;
  std::cout << "bpf=(location to bpf object byte code [Attach only]"
            << std::endl;
  std::cout << "qid: <QID> (XDP, QID to attach to [Attach only])" << std::endl;
  std::cout << "order: <order_num> (Relative order of execution of this bpf "
               "code, lower number gets executed first [Attach only])"
            << std::endl;

  std::cout << std::endl;
  std::cout << std::endl;
}

std::pair<std::string, std::string> __tokenize(const std::string &str) {
  std::stringstream is{str};
  std::vector<std::string> tok;
  std::string inter;
  while (getline(is, inter, '=')) {
    if (inter.empty()) continue;
    tok.emplace_back(inter);
  }
  return std::make_pair(tok[0], tok[1]);
}

/*
 * Entry point. dpcsh in tcp proxy mode must
 * already be running
 */

int main(int argc, char **argv) {
  int opt_char;
  const char *hostname{"localhost"};
  const char *mod_name{DEF_MOD};
  uint16_t port_num{DPC_PORT};
  std::unordered_map<std::string, std::string> mp;

  struct option long_opts[] = {
      {"help", no_argument, nullptr, 'h'},
      {"dpc_host", optional_argument, nullptr, 'S'},
      {"dpc_port", optional_argument, nullptr, 'p'},
      {"module_name", optional_argument, nullptr, 'm'},
      {nullptr, 0, nullptr, 0},
  };
  while ((opt_char = getopt_long(argc, argv, "hm:S:p:i", long_opts, NULL)) !=
         -1) {
    switch (opt_char) {
      case 'h':
        help();
        exit(0);
      case 'S':
        if (optarg) hostname = optarg;
        break;
      case 'p':
        if (optarg) port_num = atoi(optarg);
        break;
      case 'm':
        if (optarg) mod_name = optarg;
      default:
        break;
    }
  }
  while (optind < argc) {
    auto p = __tokenize(argv[optind]);
    mp.emplace(p);
    optind++;
  }

  // Start the cli-mgr
  cli_mgr s{hostname, port_num};
  s.process(mod_name, mp);
}
