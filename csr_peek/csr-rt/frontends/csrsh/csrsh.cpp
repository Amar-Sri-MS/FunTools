/*
 *  csrsh.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#include "csrsh.h"
#include <algorithm>
#include <cstring>
#include <iomanip>
#include <sstream>
#include <utility>

// Get this from the DPC include files
#define DPC_PORT 40221
/*
 * Connect to the DPCSH that must already be
 * running in proxy mode
 * Add command line arg later to ignore this
 * if the server is a raw server
 */
CsrSh::~CsrSh(void) {
    for (auto& elem: mp_buf) {
        delete elem.second.first;
	elem.second.first=nullptr;
    }
    mp_buf.clear();


}
void CsrSh::__init(void) {
    if (not tcp_h.conn("localhost", DPC_PORT)) {
        std::cout << "!!!!WARNING: dpcsh not connected. Fetch/Flush commands WILL NOT work!!" << std::endl;
    }
}

void CsrSh::dump_csr(const std::string& csr_name) {
    auto n_inst = ns_h.num_inst(csr_name);
    std::cout << "CSR:"<< csr_name << std::endl;
    for (auto i = 0; i < n_inst; i ++) {
        auto csr_h = ns_h.get_csr(csr_name, i);
        auto n_entries = csr_h.num_entries();
        if (i == 0) {
            for (auto it = csr_h.begin(); it != csr_h.end(); it ++) {
                std::cout << "f_name: " << it->first << std::endl;
                std::cout << "f_prop: " << std::dec << it->second << std::endl;
            }
            std::cout << "n_inst:" << std::dec << n_inst << std::endl;
        }

        std::cout <<"   I#: " << i << std::endl;
        std::cout <<"   N_E:" << n_entries << std::endl;
        for (uint32_t j = 0; j < n_entries; j ++) {
            auto addr = csr_h.addr(j);
            std::cout << "      :E#: " << j << std::endl;
            std::cout << "      :ADDR:0x"
                << std::hex << std::setfill('0')
                << std::setw(10) << addr << std::endl;
        }
    }
}
void CsrSh::set_csr(const std::string& csr_name) {
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
       if (it->first == "__rsvd") continue;
       std::cout << "FLD: " << it->first << ":";
       if (is_set) {
          csr_h.get(it->first, prev_val, buf);
	  std::cout << "(" << prev_val << "):";
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
	      std::cout << "(" << prev_val << "):";
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
}

void CsrSh::set_raw(const std::string& csr_name) {
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
}

void CsrSh::show_buffer(void) {
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
}

void CsrSh::__interpret(const std::string& csr_name, uint8_t* buf) {
    auto csr_h = ns_h.get_csr(csr_name);
    uint64_t val = 0;
    assert(buf != nullptr);
    for (auto& elem: csr_h) {
        csr_h.get(elem.first, val, buf);
	std::cout << "FLD: " << elem.first
		<< ":0x" << std::hex
		<< static_cast<uint16_t>(val) << std::endl;
    }
}


/*
 * The ones below interact with real hardware
 * either through dpcsh or otherwise
 */

void CsrSh::fetch(const std::string& csr_name,
		const uint16_t& inst_num,
		const uint32_t& entry_num) {
    auto n_inst = ns_h.num_inst(csr_name);
    assert(inst_num < n_inst);
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
    r_json.erase(std::remove(r_json.begin(), r_json.end(), '\n'), r_json.end());
    r_json.erase(std::remove(r_json.begin(), r_json.end(), '\r'), r_json.end());
    std::cout << "RCV_JSON: " << r_json << std::endl;
    uint8_t* bin_arr = json_acc.peek_rsp(r_json);
    for (auto i = 0; i < n_bytes; i ++) {
        std::cout << "raw[" << i << "] = 0x" << std::hex << static_cast<uint16_t>(bin_arr[i]) << std::endl;
    }
    mp_buf.insert(std::make_pair(csr_name,
                   std::make_pair(bin_arr, n_bytes)));
    __interpret(csr_name, bin_arr);

}
void CsrSh::flush(const std::string& csr_name,
		const uint16_t& inst_num,
		const uint32_t& entry_num) {
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
    r_json.erase(std::remove(r_json.begin(), r_json.end(), '\n'), r_json.end());
    std::cout << "RCV_JSON: " << r_json << std::endl;
    assert(json_acc.poke_rsp(r_json));
}
