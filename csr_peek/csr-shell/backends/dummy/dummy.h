/*
 *  dummy.h
 *
 *  Created by Hariharan Thantry on 2018-03-03
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include <stdint.h>

void dummy_wr(uint64_t addr, uint8_t* buffer);
void dummy_rd(uint64_t addr, uint8_t* buffer);
