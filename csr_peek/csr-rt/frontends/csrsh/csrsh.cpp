#include "csrsh.h"
#include <cstring>
#include <iomanip>
#include <sstream>

/*
 * This wants to be a global variable
 */

std::map<std::string, std::pair<uint8_t*, uint16_t>> mp_buf;
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
        buf = new uint8_t[sz];
	std::memset(buf, 0, sz);
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
