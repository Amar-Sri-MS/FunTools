/*
 *  cli_mgr.cpp
 *
 *  Created by Hariharan Thantry on 2019-02-01
 *
 *  Common cli manager for interfacing with dpc proxy
 *  Requires backend implementations for client modules (e.g. bpf)
 *  that implement/interpret client specific verbs.
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#include <algorithm>
#include <cassert>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <utility>
#include <vector>

#include "bpf_module.h"
#include "cli_mgr.h"
#include "json_factory.h"

// Get this from the DPC include files
/*
 * Connect to the DPCSH that must already be
 * running in proxy mode
 * Add command line arg later to ignore this
 * if the server is a raw server
 */

cli_mgr::~cli_mgr() {}

void cli_mgr::__init(const char *host, const uint16_t &port) {
    std::cout << "Connect:Host: " << host << ":port: " << port << std::endl;
    if (not __tcp_h.conn(host, port)) {
        std::cout
            << "!!!!WARNING: dpcsh not connected. BPF commands WILL NOT work!!"
            << std::endl;
    } else {
        __started = true;
    }
}

/*
 * Main entry function for any front end
 *
 * This function is simply a wrapper around
 *
 * vec[0] == "attach | detach"
 * vec[1] onwards, "key:value"
 *
 * key:value pairs after attach detach commands
 */

bool cli_mgr::process(const std::string &mod_name,
                      std::unordered_map<std::string, std::string> &params) {
    if (!__started) {
        std::cout << "dpcsh not started. Commands will not work, returning";
        return false;
    }
    cli_module *p{nullptr};
    json_factory __f;

    if (mod_name == "bpf") {
        p = new bpf_module();
    } else {
        std::cout << "Unknown module. Returning";
        return false;
    }
    auto send_js = p->create_js_req(params);
    /*
     * We now have a valid JSON tree
     */

    if (!send_js) {
        std::cout << "JSON not constructed for sending" << std::endl;
        delete p;
        return false;
    }
    /*
     * Stringify for network transmission
     * The daemon only accepts text JSON
     */

    auto snd_jstr = __f.stringify(send_js);

    auto snd_rval = __tcp_h.send_data(snd_jstr);

    /*
     * Get response back from FunOS
     */

    auto rx_str = __tcp_h.receive();
    std::cout << rx_str << std::endl;
    delete p;
    return (snd_rval && !rx_str.empty());
}
