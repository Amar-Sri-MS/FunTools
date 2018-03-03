/*
 *  prog.cpp
 *
 *  Created by Hariharan Thantry on 2018-01-26
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */

#include <iostream>
#include <tuple>

#include "csr.h"

int main(void) {
    auto& ns = F1NS::get();
    
    uint64_t val = 15;
    auto csr = ns.get_csr("rand_csr_0");
    csr.set("__pad0", val);

    return 0;
}
