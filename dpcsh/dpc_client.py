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
# Example usage dpctest.py

class DpcClient(object):
    def __init__(self, legacy_ok = True, unix_sock = False, server_address = None):
        self.__legacy_ok = legacy_ok
        self.__verbose = True
        self.__truncate_long_lines = False
        self.__async_queue = []
        self.__next_tid = 1
        
        if (unix_sock):
            if (server_address is None):
                server_address = '/tmp/funos-dpc-text.sock'
            self.__sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        else:
            if (server_address is None):
                server_address = ('127.0.0.1', 40221)
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
            if (not json) :
                break
        return json

    def __send_line(self, line):
        self.__sock.sendall(line + '\n')

    # Whether to print each command line and its result
    def set_verbose(self, verbose = True):
        self.__verbose = verbose

    def set_truncate_long_lines(self, truncate = True):
        self.__truncate_long_lines = truncate

    def __print(self, text, end = '\n'):
        if self.__verbose != True:
            return
        if self.__truncate_long_lines and len(text) > 255:
            print(text[:252] + '...', end=end)
        else:
            print(text, end=end)

    def next_tid(self):
        tid = self.__next_tid
        self.__next_tid += 1
        return tid
            
    def send_raw(self, jstr):
        self.__print(jstr, ' -> ')
        self.__send_line(jstr)
        
    def async_send(self, verb, arg_list, tid = None):

        if (tid is None):
            tid = self.next_tid()
            
        # make the args a list if it's just a dict or int or something
        if (type(arg_list) is not list):
            arg_list = [arg_list]

        # make a json request in dict from
        jdict = { "verb": verb, "arguments": arg_list, "tid": tid }

        # stringify and send it
        jstr = json.dumps(jdict)
        self.send_raw(jstr)

        return tid
        
    def async_wait(self):
        # just pull the first thing off the wire and return it
        result = self.__recv_json()
        self.__print(result)

        # decode the raw json and return
        try:
            decoded_results = json.loads(result)
        except:
            print("ERROR: Unable to parse to JSON. data: %s" % result)
            decoded_results = {"result" : None, "tid" : "-1"} # "an error happened"
        return decoded_results
    
    def async_recv_any_raw(self):
        # try and dequeue the first queued
        if (len(self.__async_queue) > 0):
            r = self.__async_queue.pop(0)
            return r
        
        # wait for something else        
        return self.async_wait()

    def async_recv_any(self):
        return self.async_recv_any_raw()['result']

    def async_recv_wait_raw(self, tid):

        # see if it's already pending
        for r in self.__async_queue:
            if (r['tid'] == tid):
                self.__async_queue.remove(r)
            return r
        
        # wait and dequeue until we find the one we want
        while (True):
            r = self.async_wait()
            print("found: %s" % r)
            if (r['tid'] == tid):
                return r

            self.__async_queue.append(r)

    def async_recv_wait(self, tid):
        return self.async_recv_wait_raw(tid)['result']


    # preferred interface
    def execute(self, verb, arg_list, tid = None):

        # make sure verb is just a verb
        if (" " in verb):
            raise RuntimeError("no spaces allowed in verbs")

        # make it a string and send it & get results
        tid = self.async_send(verb, arg_list, tid)
        results = self.async_recv_wait(tid)

        return results

    # XXX: legacy interface. Avoid using this
    def execute_command(self, command, args):

        if (not self.__legacy_ok):
            raise RuntimeError("Attempted legacy command on non-legacy client instance")

        encoded_args = json.dumps(args)
        
        # #!sh prefix to ensure it's parsed as legacy input
        cmd_line = "#!sh " + command + ' ' + encoded_args

        # send the request 
        self.send_raw(cmd_line)

        # XXX: we know what dpcsh will always stuff a zero tid for
        # legacy commands
        results = self.async_recv_wait(0)

        if (command == 'execute'):
            # XXX: flatten it back down for legacy clients
            return json.dumps(results)
        return results
