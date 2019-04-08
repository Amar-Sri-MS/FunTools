/*
*  k_05.c
*
*  Created by Hariharan Thantry on 2019-04-08
*
*  Copyright © 2019 Fungible Inc. All rights reserved.
*/
#include "ebpf_kern_args.h"
int drop(struct k_05_arg *arg)
{
	return 1;

}
