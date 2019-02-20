/*
 *  k_02.c
 *
 *  Created by Hariharan Thantry on 2019-02-11
 *
 *  Copyright © 2019 Fungible Inc. All rights reserved.
 *  
 *  Accept arguments, and return a member value based on arg
 *
 *
 */
#include "ebpf_kern_args.h"



unsigned long long test_krn(struct k_02_arg* arg) {
    return (arg->c) + 10;
}

