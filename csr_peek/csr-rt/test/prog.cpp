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
     * If part of layered stack, pass the raw_rd & raw_wr functions
     */
    auto& ns = F1NS::get(dummy_rd, dummy_wr);

    /*
     * Get a handle to a CSR by name
     * The second parameter (optional) is the instance id
     * if the CSR has multiple instances
     */
    auto csr = ns.get_csr("rand_csr_0", 1);
    auto addr = csr.addr(3);

    std::cout << "LKUP_ADDR: 0x"
        << std::hex << std::setfill('0')
        << std::setw(10) << addr << std::endl;


    //Raw byte array to hold CSR contents
    uint8_t* raw_arr = new uint8_t[csr.sz()]();

    //Set some fields in the CSR
    uint64_t val = 15;
    csr.set("__pad0", val, raw_arr);
    csr.set("port_blocked", 1, raw_arr);

    /*
     * Call the raw write. Second parameter (optional) is the entry index, in case of a table
     * Successful if part of layered stack
     */
    csr.raw_wr(raw_arr, 3);
    std::memset(raw_arr, 0, csr.sz());
    //Read back, Second parameter(optional) is the entry index, in case of table
    csr.raw_rd(raw_arr, 3);

    //Decode the individual field values
    csr.get("__pad0", val, raw_arr);
    assert(val == 0xF);
    csr.get("port_blocked", val, raw_arr);
    assert(val == 1);

    //Release the CSR resources, if no longer in use
    csr.release();
    return 0;
}
