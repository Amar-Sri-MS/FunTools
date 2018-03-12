/*
 *  prog.cpp
 *
 *  Created by Hariharan Thantry on 2018-01-26
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#include <cstring>
#include <iomanip>
#include <iostream>

//Library header file
#include "csr.h"
//Dummy backend header file
#include "dummy.h"
int main(void) {
    /*
     * Get the top level object.
     */
    auto& ns = F1NS::get(dummy_rd, dummy_wr);

    /*
     * Get a handle to a CSR by name
     */

    std::string csr_name = "prs_err_chk_en";
    auto n_instances = ns.num_inst(csr_name);
    std::cout << "CSR:"<< csr_name << std::endl;

    for (auto i = 0; i < n_instances; i ++) {
        auto csr_h = ns.get_csr(csr_name, i);
        auto n_entries = csr_h.num_entries();
        if (i == 0) {
            std::cout << "*****BEGIN PROPS*****" << std::endl;
            for (auto it = csr_h.begin(); it != csr_h.end(); it ++) {
                std::cout << "FLD_NAME: " << it->first << std::endl;
                std::cout << "FLD_PROP: " << it->second << std::endl;
            }
            std::cout << "NUM_INSTANCE:" << n_instances << std::endl;
            std::cout << "*****END*****" << std::endl;

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
        uint8_t* raw_arr = new uint8_t[csr_h.sz()]();
        for (auto it = csr_h.begin(); it != csr_h.end(); it ++) {
            uint64_t val = 1;
            if (it->first == "__rsvd") continue;
            csr_h.set(it->first, val, raw_arr); 
        }
        for (uint32_t j = 0; j < n_entries; j ++) {
            csr_h.raw_wr(raw_arr, j);
            std::memset(raw_arr, 0, csr_h.sz());
            csr_h.raw_rd(raw_arr, j);
            for (auto it = csr_h.begin(); it != csr_h.end(); it ++) {
                uint64_t val;
                if (it->first == "__rsvd") continue;
                csr_h.get(it->first, val, raw_arr); 
                assert(val == 1);
            }
        }
        delete[] raw_arr;
        csr_h.release();
    }
    return 0;
}
