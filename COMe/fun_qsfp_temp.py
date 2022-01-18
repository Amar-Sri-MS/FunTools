#!/usr/bin/env python2.7
# Description: Script to Read All NU Ports' Temp of FS-1600 and Print Max Temp out of all
# Author: Karnik Jain
# Date: 20th JAN 2020
# Copyright (c) 2020 Fungible. All rights reserved.

import json, time
import argparse
import subprocess
from   bmc_dpc_client import DpcClient


def main(args):

    if args.dpcsh_server_ip:
        dpcsh_server_ip = args.dpcsh_server_ip

    if args.dpcsh_server_f1_0_port:
        dpcserver_f1_0_port = args.dpcsh_server_f1_0_port

    if args.dpcsh_server_f1_1_port:
        dpcserver_f1_1_port = args.dpcsh_server_f1_1_port
    
    f1_0_nu_port_temp = {0:"na", 4:"na", 8:"na", 12:"na", 16:"na", 20:"na"}
    f1_1_nu_port_temp = {0:"na", 4:"na", 8:"na", 12:"na", 16:"na", 20:"na"}
    max_temp = -1
    max_temp_port = -1
    max_temp_f1 = -1
    index = 0
    dpcsh_server_port = dpcserver_f1_0_port
    f1_nu_port_temp_list = [f1_0_nu_port_temp, f1_1_nu_port_temp]

    for f1_nu_port_temp in f1_nu_port_temp_list:
        if index == 1:
           dpcsh_server_port = dpcserver_f1_1_port
        for key,val in f1_nu_port_temp.items():
            dpc_obj = DpcClient(dpcsh_server_ip, dpcsh_server_port)
            result = dpc_obj.port_temperature(0, key) 
            if result != "false":
               f1_nu_port_temp[key] = "%.2f" % result
               print ("FS-1600 F1_%d: NU-Port:%d, Temp:%.2f" % (index, key, result))
               if result > max_temp:
                   max_temp = result
                   max_temp_port = key
                   max_temp_f1 = index
            del dpc_obj
        index = index + 1

    print "\n===================================="
    print ("FS1600 F1_%d NU-Port:%d Max Temp:%.2f" % (max_temp_f1, max_temp_port, max_temp))
    print "===================================="

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('-i',
                            "--dpcsh_server_ip",
                            help="COMe IP Address",
                            type=str, default="",
                            required=True)
    arg_parser.add_argument('-p0',
                            "--dpcsh_server_f1_0_port",
                            help="DPCSH Server TCP Port for F1_0",
                            type=str, default="43101",
                            required=False)
    arg_parser.add_argument('-p1',
                            "--dpcsh_server_f1_1_port",
                            help="DPCSH Server TCP Port for F1_1",
                            type=str, default="43102",
                            required=False)
    arg_parser.add_argument('-v',
                            '--version', action='version',
                             version='version=0.1')

    args = arg_parser.parse_args()
    main(args)
