/*
 *  ebpf_kern.h
 *
 *  Created by Hariharan Thantry on 2019-02-20
 *
 *  Copyright © 2019 Fungible Inc. All rights reserved.
 */

/*
 * This header file contains the defintions for runtime args 
 * The same layout must be used by any host for the respective
 * kernels being attached.
 * This utility file needs to be copied over to FunOS
 */

#pragma once

typedef unsigned long long k_01_arg;

struct k_02_arg {
    unsigned long long a;
    unsigned long b;
    unsigned int c;
};
struct k_03_arg {
    unsigned int* arr;
    unsigned int a_len;
};
struct k_04_arg {
    int a;
    int b;
    int c;
};
