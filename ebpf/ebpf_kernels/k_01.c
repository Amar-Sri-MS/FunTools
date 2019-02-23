/*
 *  k_01.c
 *
 *  Created by Hariharan Thantry on 2019-02-11
 *
 *  This is the simplest kernel. Every file should have exactly one function
 *
 *  Copyright © 2019 Fungible Inc. All rights reserved.
 *
 */

#include "ebpf_kern_args.h"

unsigned long long test_krn(k_01_arg* arg) {
    return 2;
}

