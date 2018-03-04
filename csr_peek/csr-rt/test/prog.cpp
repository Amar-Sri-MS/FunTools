/*
 *  prog.cpp
 *
 *  Created by Hariharan Thantry on 2018-01-26
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#include <cstring>
#include <iostream>
#include <tuple>

#include "csr.h"
#include "dummy.h"

int main(void) {
    auto& ns = F1NS::get(dummy_rd, dummy_wr);

    uint64_t val = 15;
    auto csr = ns.get_csr("rand_csr_0");
    uint8_t* raw_arr = new uint8_t[csr.sz()]();
    csr.set("__pad0", val, raw_arr);
    csr.set("port_blocked", 1, raw_arr);
    csr.raw_wr(raw_arr);

    std::memset(raw_arr, 0, csr.sz());
    csr.raw_rd(raw_arr);
    csr.get("__pad0", val, raw_arr);
    assert(val == 0xF);
    csr.get("port_blocked", val, raw_arr);
    assert(val == 1);

    csr.release();


    return 0;
}
