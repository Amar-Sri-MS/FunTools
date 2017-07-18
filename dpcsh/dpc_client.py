##
##  dpc_client.py
##
##  Created by Dan Picken on 2017-06-20
##  Copyright (C) 2017 Fungible. All rights reserved.
##

from __future__ import print_function
import json
import socket


# N.B. The user must start a dpcsh in text proxy mode before
# creating a DpcClient, e.g.
#
# $WORKSPACE/FunTools/dpcsh/dpcsh --text_proxy
#
# Example usage:
#
# import os
# import sys
# sys.path.append(os.environ['WORKSPACE'] + '/FunTools/dpcsh')
# import dpc_client
#
# client = dpc_client.DpcClient()
#
# result = client.execute_command('echo', 'Hello dpc')
# print result
#
# result = client.execute_command('ikv lvs_create', {
#     'volume_id': 1,
#     'volume_lba_bytes': 4096,
#     'volume_lbas': 1024,
#     'allocator_volume_id': 2,
#     'allocator_volume_lba_bytes': 4096,
#     'allocator_volume_lbas': 256
#     })
# print result

class DpcClient(object):
    def __init__(self):
        self.__sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.__verbose = False

        server_address = '/tmp/funos-dpc-text.sock'
        self.__sock.connect(server_address)

    def __recv_lines(self):
        recv_size = 1024
        lines = ""
        while lines.find('\n') == -1:
            buf = self.__sock.recv(recv_size)
            if not buf:
                break
            lines += buf
        return lines.rstrip('\n')

    def __recv_json(self):
        json = self.__recv_lines()
        while (not json) or (json.count('{') != json.count('}')) or (json.count('[') != json.count(']')):
            json += self.__recv_lines()
        return json

    def __send_line(self, line):
        self.__sock.sendall(line + '\n')

    # Whether to print each command line and its result
    def set_verbose(self, verbose = True):
        self.__verbose = verbose

    def execute_command_line(self, command_line):
        if self.__verbose == True:
            print(command_line + ' -> ', end='')
        self.__send_line(command_line)
        result = self.__recv_json()
        if self.__verbose == True:
            print(result)
        return result

    def execute_command(self, command, args):
        encoded_args = json.dumps(args)
        results = self.execute_command_line(command + ' ' + encoded_args)
        decoded_results = json.loads(results)
        return decoded_results
