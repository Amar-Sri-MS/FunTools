#include "csrsh.h"
#include <cstring>
#include <iomanip>
#include <sstream>

// Get this from the DPC include files
#define DPC_PORT 40221
/*
 * Connect to the DPCSH that must already be
 * running in proxy mode
 * Add command line arg later to ignore this
 * if the server is a raw server
 */

void CsrSh::__init(void) {
    assert(tcp_h.conn("localhost", DPC_PORT));
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
    std::cin.unsetf(std::ios::dec);
    std::cin.unsetf(std::ios::hex);
    std::cin.unsetf(std::ios::oct);

    uint64_t curr_val;
    uint64_t prev_val;
    std::string curr_str;
    std::istringstream istream;

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
    std::cin.unsetf(std::ios::dec);
    std::cin.unsetf(std::ios::hex);
    std::cin.unsetf(std::ios::oct);

    uint8_t curr_val;
    std::string curr_str;
    std::istringstream istream;

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
    std::cout << "REQ: " << csr_name <<  ":ADDR: 0x" << std::hex << addr
	    << std::dec << "BYTES: " << n_bytes << std::endl;



}
void CsrSh::flush(const std::string& csr_name,
		const uint16_t& inst_num,
		const uint32_t& entry_num) {


}
