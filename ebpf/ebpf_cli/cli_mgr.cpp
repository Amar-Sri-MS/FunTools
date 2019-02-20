/*
 *  cli.cpp
 *
 *  Created by Hariharan Thantry on 2019-02-01
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

#include "cli_mgr.h"
#include "bpf_module.h"

// Get this from the DPC include files
/*
 * Connect to the DPCSH that must already be
 * running in proxy mode
 * Add command line arg later to ignore this
 * if the server is a raw server
 */

cli_mgr::~cli_mgr() {


}

void cli_mgr::__init(const char* host, const uint16_t& port) {
    std::cout << "Connect:Host: " << host << ":port: " << port << std::endl;
    if (not tcp_h.conn(host, port)) {
        std::cout << "!!!!WARNING: dpcsh not connected. BPF commands WILL NOT work!!" << std::endl;
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


bool cli_mgr::process(const ModuleID& mod, 
		std::deque<std::string>& params) {
        
        auto idx = static_cast<int>(mod);
	auto it = mod_map.find(idx);
	cli_module* p = nullptr;
        if (it == mod_map.end()) {
           if (mod == ModuleID::BPF) {
               p = new bpf_module();
	   }
	   mod_map[idx] = p;
	} else {
            p = it->second;

	}
	return p->execute(params);

}

#if 0
void bpf_cli::set_csr(const char* csr_name) {
	/*
    auto csr_h = ns_h.get_csr(csr_name);
    auto it = mp_buf.find(csr_name);
    uint8_t* buf = nullptr;
    bool is_set = false;
    uint16_t sz = csr_h.sz();
    if (it != mp_buf.end()) {
        buf = (it->second).first;
	is_set = true;
    } else {
        buf = new uint8_t[sz]();
    }

    uint64_t curr_val;
    uint64_t prev_val;
    std::string curr_str;
    std::istringstream istream;
    istream.unsetf(std::ios::dec);
    istream.unsetf(std::ios::hex);
    istream.unsetf(std::ios::oct);

    for (auto it = csr_h.begin(); it != csr_h.end(); it ++) {
       std::cout << "FLD: " << it->first << ":";
       if (is_set) {
          csr_h.get(it->first, prev_val, buf);
	  std::cout << std::hex << "(0x" << prev_val << "):";
       }

       while(std::getline(std::cin, curr_str)) {
           istream.clear();
	   if (curr_str.empty()) {
              if (!is_set) {
                  curr_val = 0;
	      } else {
                  curr_val = prev_val;
	      }
	      break;
	   }
	   istream.str(curr_str);
	   if (istream >> curr_val) break;
	   std::cout << "Incorrect input: " << curr_str << std::endl;
           std::cout << "FLD: " << it->first << ": ";
           if (is_set) {
	      std::cout << std::hex << "(0x" << prev_val << "):";
           }
       }
       csr_h.set(it->first, curr_val, buf);
    }
    for (auto i = 0; i < sz; i ++) {
       std::cout << "[" << i << "] = 0x" << std::hex << static_cast<uint16_t>(buf[i]) << std::endl;
    }

    mp_buf.emplace(std::piecewise_construct,
		   std::forward_as_tuple(csr_name),
		   std::forward_as_tuple(buf, sz));
		   */
}

void bpf_cli::set_raw(const char* csr_name) {
	/*
    auto it = mp_buf.find(csr_name);
    auto csr_h = ns_h.get_csr(csr_name);
    uint8_t* buf = nullptr;
    uint16_t sz = 0;
    bool is_set = false;
    if (it != mp_buf.end()) {
        buf = (it->second).first;
        sz = (it->second).second;
	is_set = true;
    } else {
        sz = csr_h.sz();
	buf = new uint8_t[sz]();
    }

    uint16_t curr_val;
    std::string curr_str;
    std::istringstream istream;
    istream.unsetf(std::ios::dec);
    istream.unsetf(std::ios::hex);
    istream.unsetf(std::ios::oct);

    for (auto i = 0; i < sz; i ++) {
        std::cout << "BYTE[" << i << "]:";
        if(is_set) {
            std::cout << "(" << static_cast<uint16_t>(buf[i]) << "):";
	}
       while(std::getline(std::cin, curr_str)) {
           istream.clear();
	   if (curr_str.empty()) {
              if (!is_set) {
                  curr_val = 0;
	      } else {
                  curr_val = buf[i];
	      }
	      break;
	   }
	   istream.str(curr_str);
	   if (istream >> curr_val) break;
	   std::cout << "Incorrect input: " << curr_str << std::endl;
           std::cout << "BYTE[" << i << "]:";
           if (is_set) {
	      std::cout << "(" << static_cast<uint16_t>(buf[i])<< "):";
           }

       }
       buf[i] = curr_val;
    }

    mp_buf.emplace(std::piecewise_construct,
		   std::forward_as_tuple(csr_name),
		   std::forward_as_tuple(buf, sz));
		   */
}

void bpf_cli::show_buffer(void) {
/*
    uint8_t* buf = nullptr;
    for (auto& elem : mp_buf) {
	    std::cout << "CSR:" << elem.first << std::endl;
	    auto sz = elem.second.second;
	    std::cout << "VAL:" << std::endl;
	    buf = (elem.second).first;
	    for (auto i = 0; i < sz; i ++) {
		    std::cout << "[" << i << "] = 0x";
		    std::cout << std::hex << static_cast<uint16_t>(buf[i]) << std::endl;
	    }
    }
    */
}

void bpf_cli::__interpret(const char* csr_name, uint8_t* buf) {
    assert(buf != nullptr);
}


/*
 * The ones below interact with real hardware
 * either through dpcsh or otherwise
 */

void bpf_cli::fetch(const char* csr_name,
		const uint16_t& inst_num,
		const uint32_t& entry_num) {
/*
    auto csr_h = ns_h.get_csr(csr_name, inst_num);
    auto n_entries = csr_h.num_entries();
    assert(entry_num < n_entries);
    auto addr = csr_h.addr(entry_num);
    auto n_bytes = csr_h.sz();
    std::cout << "FETCH: " << csr_name <<  ":ADDR: 0x" << std::hex << addr
	    << std::dec << ":BYTES: " << n_bytes << std::endl;

    auto json = json_acc.peek(addr, n_bytes);
    auto json_str = json_acc.stringify(json);
    json_str.append("\n");
    assert(tcp_h.send_data(json_str));
    std::cout << "SEND_JSON: " << json_str << std::endl;
    auto r_json = tcp_h.receive();
    std::cout << "RCV_JSON: " << r_json << std::endl;
    r_json.erase(std::remove(r_json.begin(), r_json.end(), '\n'), r_json.end());
    r_json.erase(std::remove(r_json.begin(), r_json.end(), '\r'), r_json.end());
    uint8_t* bin_arr = json_acc.peek_rsp(r_json);
    for (auto i = 0; i < n_bytes; i ++) {
        std::cout << "raw[" << i << "] = 0x" << std::hex << static_cast<uint16_t>(bin_arr[i]) << std::endl;
    }
    mp_buf.insert(std::make_pair(csr_name,
                   std::make_pair(bin_arr, n_bytes)));
    __interpret(csr_name, bin_arr);
    */

}
void bpf_cli::flush(const char* csr_name,
		const uint16_t& inst_num,
		const uint32_t& entry_num) {
/*
    auto it = mp_buf.find(csr_name);
    assert (it != mp_buf.end());
    auto n_inst = ns_h.num_inst(csr_name);
    assert(inst_num < n_inst);
    auto csr_h = ns_h.get_csr(csr_name, inst_num);
    auto n_entries = csr_h.num_entries();
    assert(entry_num < n_entries);
    auto addr = csr_h.addr(entry_num);
    auto n_bytes = csr_h.sz();
    uint8_t* buf = (it->second).first;
    std::cout << "FLUSH: " << csr_name << ": ADDR: 0x" << std::hex << addr << std::endl;
    for (auto i = 0; i < n_bytes; i ++) {
        std::cout << "[" << i << "] = 0x" << std::hex
		<< static_cast<uint16_t>(buf[i]) << std::endl;
    }


    auto json = json_acc.poke(addr, buf, n_bytes);
    auto json_str = json_acc.stringify(json);
    json_str.append("\n");
    assert(tcp_h.send_data(json_str));
    std::cout << "SEND_JSON: " << json_str << std::endl;
    auto r_json = tcp_h.receive();
    std::cout << "RCV_JSON: " << r_json ;
    r_json.erase(std::remove(r_json.begin(), r_json.end(), '\n'), r_json.end());
    assert(json_acc.poke_rsp(r_json));
    delete[] buf;
    buf = nullptr;
    mp_buf.erase(it);
*/
}


#endif
