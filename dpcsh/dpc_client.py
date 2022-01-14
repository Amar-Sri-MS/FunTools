##
##  dpc_client.py
##
##  Created by Dan Picken on 2017-06-20
##  Copyright (C) 2017 Fungible. All rights reserved.
##

from __future__ import print_function
import json
import socket
import time
import sys


# N.B. The user must start a dpcsh in text proxy mode before
# creating a DpcClient, e.g.
#
# $WORKSPACE/FunTools/dpcsh/dpcsh --text_proxy
#
# Example usage dpctest.py
class DpcExecutionError(Exception):
    pass

class DpcExecutionException(Exception):
    pass

class DpcProxyError(Exception):
    pass

class DpcTimeoutError(Exception):
    pass

class DpcClient(object):
    def __init__(self, legacy_ok = True, unix_sock = False, server_address = None):
        self.__legacy_ok = legacy_ok
        self.__verbose = False
        self.__truncate_long_lines = False
        self.__async_queue = []
        self.__next_tid = 1
        self.__execute_timeout_seconds = None

        if (unix_sock):
            if (server_address is None):
                server_address = '/tmp/dpc.sock'
            self.__sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        else:
            if (server_address is None):
                server_address = ('127.0.0.1', 40221)
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__sock.connect(server_address)
        self.__sock_file = self.__sock.makefile(mode='rb')

    # main interface for running DPC commands
    def execute(self, verb, arg_list, tid = None, custom_timeout = False, timeout_seconds = None):

        # make sure verb is just a verb
        if (" " in verb):
            raise RuntimeError("no spaces allowed in verbs")
        # make it a string and send it & get results
        tid = self.async_send(verb, arg_list, tid, custom_timeout, timeout_seconds)
        results = self.async_recv_wait(tid, custom_timeout, timeout_seconds)

        return results

    # XXX: legacy interface. Avoid using this
    def execute_command(self, command, args, custom_timeout = False, timeout_seconds = None):

        if (not self.__legacy_ok):
            raise RuntimeError("Attempted legacy command on non-legacy client instance")

        encoded_args = json.dumps(args)

        # #!sh prefix to ensure it's parsed as legacy input
        cmd_line = "#!sh " + command + ' ' + encoded_args

        # send the request
        self.__send_raw(cmd_line, custom_timeout, timeout_seconds)

        # XXX: we know what dpcsh will always stuff a zero tid for
        # legacy commands
        results = self.async_recv_wait()

        if (command == 'execute'):
            # XXX: flatten it back down for legacy clients
            return json.dumps(results)
        return results

    # Whether to print each command line and its result
    def set_verbose(self, verbose = True):
        self.__verbose = verbose

    def set_truncate_long_lines(self, truncate = True):
        self.__truncate_long_lines = truncate

    # passing None disables timeout
    # passing 0 makes socket Non-blocking and not supported
    # complete time spend in execute may be 2x higher
    # because send and receive timeouts add
    def set_timeout(self, timeout_seconds):
        self.__execute_timeout_seconds = timeout_seconds
        self.__sock.settimeout(timeout_seconds)

    def async_send(self, verb, arg_list, tid = None, custom_timeout = False, timeout_seconds = None):

        if (tid is None):
            tid = self.__get_next_tid()

        # make the args a list if it's just a dict or int or something
        if (type(arg_list) is not list):
            arg_list = [arg_list]

        # make a json request in dict from
        json_dict = { "verb": verb, "arguments": arg_list, "tid": tid }

        # stringify and send it
        json_str = json.dumps(json_dict)
        self.__send_raw(json_str, custom_timeout, timeout_seconds)

        return tid

    def async_wait(self, custom_timeout = False, timeout_seconds = None):
        # just pull the first thing off the wire and return it
        result = self.__recv_json(custom_timeout, timeout_seconds)
        self.__print(result)

        if not result:
            return None

        # decode the raw json and return
        try:
            decoded_results = json.loads(result, strict=False)
        except:
            raise DpcExecutionError("Unable to parse to JSON. data: %s" % result)

        return decoded_results

    def async_recv_any_raw(self, custom_timeout = False, timeout_seconds = None):
        # try and dequeue the first queued
        if (len(self.__async_queue) > 0):
            r = self.__async_queue.pop(0)
            return r

        # wait for something else
        return self.async_wait(custom_timeout, timeout_seconds)

    def async_recv_any(self):
        return DpcClient.__handle_response(self.async_recv_any_raw())

    def async_recv_wait_raw(self, tid = None, custom_timeout = False, timeout_seconds = None):
        # see if it's already pending
        for r in self.__async_queue:
            if (tid is None or r['tid'] == tid or r['tid'] == -1):
                self.__async_queue.remove(r)
                return r

        effective_timeout = self.__execute_timeout_seconds if custom_timeout == False else timeout_seconds
        start_time = time.time() if effective_timeout is not None else None

        # wait and dequeue until we find the one we want
        while True:
            if start_time is not None and time.time() - start_time > effective_timeout:
                raise DpcTimeoutError('async_recv_wait_raw() timeout')

            r = self.async_wait(custom_timeout, timeout_seconds)
            if r is None:
                return r
            if tid is None or r['tid'] == tid or r['tid'] == -1:
                return r

            self.__async_queue.append(r)

    def async_recv_wait(self, tid = None, custom_timeout = False, timeout_seconds = None):
        r = self.async_recv_wait_raw(tid, custom_timeout, timeout_seconds)

        return DpcClient.__handle_response(r)

    def __recv_one_line(self, custom_timeout, timeout_seconds):
        old_timeout = self.__sock.gettimeout()
        if custom_timeout:
            self.__sock.settimeout(timeout_seconds)
        try:
            return self.__sock_file.readline().rstrip()
        except socket.timeout:
            raise DpcTimeoutError('readline() timeout(cur timeout: {}(custom {}, new to {}))'.format(old_timeout, custom_timeout, timeout_seconds))
        finally:
            if custom_timeout:
                self.__sock.settimeout(old_timeout)

    def __recv_json(self, custom_timeout, timeout_seconds):
        return self.__recv_one_line(custom_timeout, timeout_seconds)

    def __send_line(self, line, custom_timeout, timeout_seconds):
        old_timeout = self.__sock.gettimeout()
        if custom_timeout:
            self.__sock.settimeout(timeout_seconds)
        try:
            self.__sock.sendall((line + '\n').encode())
        except socket.timeout:
            raise DpcTimeoutError('sendall() timeout(cur timeout: {}(custom {}, new to {}))'.format(old_timeout, custom_timeout, timeout_seconds))
        finally:
            if custom_timeout:
                self.__sock.settimeout(old_timeout)

    def __print(self, text, end = '\n'):
        if self.__verbose != True:
            return
        if self.__truncate_long_lines and len(text) > 255:
            print(text[:252] + '...', end=end)
        else:
            print(text, end=end)

    def __get_next_tid(self):
        tid = self.__next_tid
        self.__next_tid += 1
        return tid

    def __send_raw(self, json_str, custom_timeout, timeout_seconds):
        self.__print(json_str, ' -> ')
        self.__send_line(json_str, custom_timeout, timeout_seconds)

    @staticmethod
    def blob_from_string(data):
        """
        makes blob suitable to use with FunOS blob services from a given string
        """
        BLOB_CHUNK_SIZE = 32 * 1024
        blob_array = []
        position = 0
        while position < len(data):
            next_position = position + BLOB_CHUNK_SIZE
            if sys.version_info[0] == 2:
                blob_array.append(map(ord, data[position:next_position]))
            else:
                blob_array.append(list(data[position:next_position]))
            position = next_position
        return blob_array

    @staticmethod
    def blob_from_file(filename):
        """
        makes blob suitable to use with FunOS blob services from a given string
        """
        with open(filename, 'rb') as f:
            return DpcClient.blob_from_string(f.read())

    @staticmethod
    def blob_to_string(data):
        """
        makes binary from blob returned by FunOS blob services, see dpctest.py for details
        """
        result = b''
        for chunk in data:
            result += bytes(bytearray(chunk))
        return result

    @staticmethod
    def __handle_response(r):
        """
        the response returned by dpcsh should contain either an 'error' key, or
        a 'result' key if the JSON is parsable.
        """

        if not r:
            return r

        if 'proxy-msg' in r:
            raise DpcProxyError(r['proxy-msg'])

        if 'error' in r:
            raise DpcExecutionError(r['error'])

        if 'exception' in r:
            raise DpcExecutionException(r['exception'])

        return r['result']
