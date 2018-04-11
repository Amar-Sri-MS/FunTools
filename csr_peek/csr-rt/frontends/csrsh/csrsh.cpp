#include "csrsh.h"
#include <iomanip>

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
