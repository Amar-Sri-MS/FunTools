#!/usr/bin/python
# Description: DPC Clinet Lib modified for BMC -> COMe Interaction
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

class DpcClient(object):
    def __init__(self, dpcsh_server_ip, dpcsh_server_port, verbose=False):
        self.dpcsh_server_ip = dpcsh_server_ip
        self.dpcsh_server_port = int(dpcsh_server_port)
        self.sock = None
        self.verbose = verbose
        self.connect(ensure_connect=False)

    def sendall(self, data):
        while data:
            try:
                sent = self.sock.send(data)
                data = data[sent:]
            except socket.error, e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    continue

    def _read(self):
        chunk = 4096
        output = ""
        while not output.endswith('\n'):
            try:
                buffer = self.sock.recv(chunk)
            except socket.error, e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    continue
                else:
                    # a "real" error occurred
                    print e
                    sys.exit(1)
            else:
                output += buffer
        return output.rstrip('\n')

    def connect(self, ensure_connect=False):
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.dpcsh_server_ip, self.dpcsh_server_port))
            fcntl.fcntl(self.sock, fcntl.F_SETFL, os.O_NONBLOCK)
            if ensure_connect:
                self.ensure_connect()

    def read(self):
        json = self._read()
        while (not json) or (json.count('{') != json.count('}')) or (json.count('[') != json.count(']')):
            json += self._read()
        return json

    def disconnect(self):
        if self.sock:
            self.sock.close()
        self.sock = None
        return True

    def _parse_actual_output(self, output):
        actual_output = output
        if re.search(r'.*arguments.*', output, re.MULTILINE):
            actual_output = re.sub(r'.*arguments.*', "", output, re.MULTILINE)
        return actual_output

    def _print_result(self, result):
        print("Raw DPCSH Result")
        print(result)

    def execute(self, verb, arg_list=None, tid=0):
        jdict = None
        result = None
        output = ""
        try:
            self.connect(ensure_connect=False)
            if arg_list:
                if type(arg_list) is not list:
                    jdict = {"verb": verb, "arguments": [arg_list], "tid": tid}
                elif type(arg_list) is list:
                    jdict = {"verb": verb, "arguments": arg_list, "tid": tid}
            else:
                jdict = {"verb": verb, "arguments": [], "tid": tid}

            command = "{}\n".format(json.dumps(jdict))
            self.sendall(command)
            output = self.read()
            if output:
                actual_output = self._parse_actual_output(output=output)
                try:
                    json_output = json.loads(actual_output.strip())
                except:
                    if self.verbose:
                        print("Unable to parse JSON data")
                    json_output = output
                if "result" in json_output:
                    result = json_output['result']
                else:
                    result = json_output
        except socket.error, msg:
            print msg
        except Exception as ex:
            print (str(ex))
            print ("result from read:" + str(output))
        if self.verbose:
            self._print_result(result=output)
        return result

    def ensure_connect(self):
        result = self.execute(verb="echo", arg_list=["hello"])
        if result != 'hello':
            print 'Connection to DPC server via tcp_proxy at %s:%s failed. ' % (
                    self.dpcsh_server_ip, self.dpcsh_server_port)
            sys.exit(1)
        else:
            print 'Connected to DPC server via tcp_proxy at %s:%s.' % (self.dpcsh_server_ip, self.dpcsh_server_port)
            self._set_syslog_level(level=3)

    def _set_syslog_level(self, level):
        try:
            result = self.execute(verb="poke", arg_list=["params/syslog/level", level])
        except Exception as ex:
            print "ERROR: %s" % str(ex)

    def port_mtu(self, shape, portnum, mtu=None):
        try:
            cmd_arg_dict = {"portnum": portnum, "shape": shape}
            if mtu is not None:
                mtu_dict = {"mtu": mtu}
                arg_list = ["mtuset", cmd_arg_dict, mtu_dict]
            else:
                arg_list = ["mtuget", cmd_arg_dict]
            result = self.execute(verb="port", arg_list=arg_list)
            return result
        except Exception as ex:
            print "ERROR: %s" % str(ex)

    def port_temperature(self, shape, portnum):
        try:
            cmd_arg_dict = {"portnum": portnum, "shape": shape}
            arg_list = ["temperature", cmd_arg_dict]
            result = self.execute(verb="port", arg_list=arg_list)
            return result
        except Exception as ex:
            print "ERROR: %s" % str(ex)

def main(argv):

    try:
        opts, args = getopt.getopt(argv,"hi:p:c:",["dpcsh_server_ip=","dpcsh_server_port=", "dpcsh_cmd="])

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
          dpcsh_server_port = arg
       elif opt in ("-c", "--dpcsh_cmd"):
          dpcsh_cmd = arg
       else:
          print "bmc_dpcsh_client.py -i <dpcsh_server_ip> -p <dpcsh_server_port> -c <'dpcsh_cmd'>"
          sys.exit()

    dpc_obj = DpcClient(dpcsh_server_ip, dpcsh_server_port)

    dpcsh_cmd = dpcsh_cmd.split(' ', 1)
    dpcsh_cmd_len = len(dpcsh_cmd)

    if dpcsh_cmd_len > 1: 
        dpcsh_cmd_verb = dpcsh_cmd[0]

        dpcsh_cmd_args = dpcsh_cmd[1]
        dpcsh_cmd_args = dpcsh_cmd_args.split(' ', 1)
        dpcsh_cmd_args_len = len(dpcsh_cmd_args)

        if dpcsh_cmd_args_len > 1:
           cmd_arg_dict = json.loads(dpcsh_cmd_args[1])
           arg_list = [dpcsh_cmd_args[0], cmd_arg_dict]
        else:
           arg_list = [dpcsh_cmd_args[0]]
    else:
        print "bmc_dpcsh_client.py -i <dpcsh_server_ip> -p <dpcsh_server_port> -c <'dpcsh_cmd'>"
        sys.exit()

    out = dpc_obj.execute(dpcsh_cmd_verb, arg_list)
    print json.dumps(out)
    dpc_obj.disconnect()

if __name__ == "__main__":
    main(sys.argv[1:])
