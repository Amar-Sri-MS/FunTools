/*
 *  k_04.c
 *
 *  Created by Hariharan Thantry on 2019-02-15
 *
 *  Copyright © 2019 Fungible Inc. All rights reserved.
 */
#include "ebpf_kern_args.h"

int modify(struct k_04_arg* p) {
    p->c = 20;
    return 0;
}
