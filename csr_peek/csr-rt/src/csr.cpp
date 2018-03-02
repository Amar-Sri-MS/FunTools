/*
 *  csr.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-26
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#include <cassert>
#include <iostream>
#include "csr.h"

ring_coll_t& F1NS::operator[](const std::string& name) {
    auto it = sys_rings.find(name);
    assert(it != sys_rings.end());
    return it->second;
}






