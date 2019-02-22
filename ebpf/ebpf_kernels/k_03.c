/*
 *  k_03.c
 *
 *  Created by Hariharan Thantry on 2019-02-11
 *
 *  Copyright © 2019 Fungible Inc. All rights reserved.
 *  
 *  Loops, return min
 *
 */
#include "ebpf_kern_args.h"

unsigned int test_krn(struct k_03_arg* my_arr) {
    unsigned int min = my_arr->arr[0];
    unsigned int i = 1;

    while (i < my_arr->a_len) {
        if (my_arr->arr[i] < min) min = my_arr->arr[i];
        ++i; 
    }
    return min;
}

