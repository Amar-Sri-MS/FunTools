#!/usr/bin/env python2.7
# Description: DPC Command Line Interface for BMC -> COMe Interaction
#    This script will talk with DPC Server running in Proxy Mode on
#    COMe and help the BMC to fetch the data from F1s'
# Author: Karnik Jain
# Date: 20th JAN 2020
# Copyright (c) 2020 Fungible. All rights reserved.

import json, time, re
import socket, fcntl, errno
import os, sys
import sys, getopt
import subprocess

from dpc_client import DpcClient

def main(argv):

    try:
        opts, _ = getopt.getopt(argv,"hi:p:c:",["dpcsh_server_ip=","dpcsh_server_port=", "dpcsh_cmd="])

    except getopt.GetoptError:
       print "bmc_dpcsh_client.py -i <dpcsh_server_ip> -p <dpcsh_server_port> -c <'dpcsh_cmd'>"
       sys.exit(2)

    for opt, arg in opts:
       if opt == '-h':
          print "bmc_dpcsh_client.py -i <dpcsh_server_ip> -p <dpcsh_server_port> -c <'dpcsh_cmd'>"
          sys.exit()
       elif opt in ("-i", "--dpcsh_server_ip"):
          dpcsh_server_ip = arg
       elif opt in ("-p", "--dpcsh_server_port"):
          dpcsh_server_port = int(arg)
       elif opt in ("-c", "--dpcsh_cmd"):
          dpcsh_cmd = arg
       else:
          print "bmc_dpcsh_client.py -i <dpcsh_server_ip> -p <dpcsh_server_port> -c <'dpcsh_cmd'>"
          sys.exit()

    dpc_obj = DpcClient(server_address = (dpcsh_server_ip, dpcsh_server_port))
    dpcsh_cmd = dpcsh_cmd.split(' ', 1)

    if len(dpcsh_cmd) < 2:
        print "bmc_dpcsh_client.py -i <dpcsh_server_ip> -p <dpcsh_server_port> -c <'dpcsh_cmd'>"
        sys.exit()

    dpcsh_cmd_verb, dpcsh_cmd_args = dpcsh_cmd
    dpcsh_cmd_args = dpcsh_cmd_args.split(' ', 1)

    if len(dpcsh_cmd_args) > 1:
        cmd_arg_dict = json.loads(dpcsh_cmd_args[1])
        arg_list = [dpcsh_cmd_args[0], cmd_arg_dict]
    else:
        arg_list = dpcsh_cmd_args

    out = dpc_obj.execute(dpcsh_cmd_verb, arg_list)
    print json.dumps(out, indent=4)

if __name__ == "__main__":
    main(sys.argv[1:])
