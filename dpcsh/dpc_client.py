##
##  dpc_client.py
##
##  Created by Dan Picken on 2017-06-20
##  Copyright (C) 2017 Fungible. All rights reserved.
##

import json
import select
import socket
import sys
import time
from typing import Any, Tuple, Union

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

class DpcSocket:
    def __init__(self, unix_sock: bool, server_address: Union[None, str, Tuple[str, int]]) -> None:
        if unix_sock:
            if server_address is None:
                server_address = '/tmp/dpc.sock'
            self.__sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        else:
            if (server_address is None):
                server_address = ('127.0.0.1', 40221)
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__sock.connect(server_address)
        self.__sock.setblocking(False)
        self.__buffer = b''
        self.__chunk_size = 32*1024

    def __write(self, data: bytes, timeout_seconds: Union[float, None]) -> Tuple[Union[float, None], int]:
        if timeout_seconds is None:
            bytes_sent = self.__sock.send(data)
            return None, bytes_sent

        start_time = time.time()
        ready = select.select([], [self.__sock], [], timeout_seconds)
        if ready[1]:
            bytes_sent = self.__sock.send(data)
        else:
            raise DpcTimeoutError('receive() timeout')

        remaining_time = timeout_seconds - start_time + time.time()
        if remaining_time is not None and remaining_time < 0:
            raise DpcTimeoutError('receive() timeout')

        return remaining_time, bytes_sent

    def send(self, data: Any, timeout_seconds: Union[float, None]) -> None:
        data_bytes = json.dumps(data).encode('utf8') + b'\n'
        while len(data_bytes) > 0:
            timeout_seconds, bytes_sent = self.__write(data_bytes, timeout_seconds)
            data_bytes = data_bytes[bytes_sent:]

    def __read(self, timeout_seconds: Union[float, None]) -> None:
        start_time = time.time()
        ready = select.select([self.__sock], [], [], timeout_seconds)
        if ready[0]:
            self.__buffer += self.__sock.recv(self.__chunk_size)
            remaining_time = timeout_seconds - start_time + time.time() if timeout_seconds is not None else None
            if remaining_time is not None and remaining_time < 0:
                raise DpcTimeoutError('receive() timeout')
            return remaining_time
        raise DpcTimeoutError('receive() timeout')

    def receive(self, timeout_seconds: Union[float, None]) -> Any:
        position = self.__buffer.find(b'\n')

        if position == -1:
            remaining_time_seconds = self.__read(timeout_seconds)
            return self.receive(remaining_time_seconds)

        line = self.__buffer[:position]
        self.__buffer = self.__buffer[position + 1:]

        # decode the raw json and return
        try:
            decoded_results = json.loads(line, strict=False)
        except:
            raise DpcExecutionError("Unable to parse to JSON. data: %s" % result)

        return decoded_results

class DpcClient(object):
    def __init__(self, legacy_ok: bool = True, unix_sock: bool = False, server_address = None):
        self.__legacy_ok = legacy_ok
        self.__verbose = False
        self.__truncate_long_lines = False
        self.__async_queue = []
        self.__next_tid = 1
        self.__execute_timeout_seconds = None
        self.socket = DpcSocket(unix_sock, server_address)

    # main interface for running DPC commands
    def execute(self, verb: str, arg_list: list[Any], tid: Union[None, int] = None, custom_timeout: bool = False, timeout_seconds: Union[float, None] = None) -> Any:

        # make sure verb is just a verb
        if (" " in verb):
            raise RuntimeError("no spaces allowed in verbs")
        # make it a string and send it & get results
        tid = self.async_send(verb, arg_list, tid, custom_timeout, timeout_seconds)
        results = self.async_recv_wait(tid, custom_timeout, timeout_seconds)

        return results

    # Whether to print each command line and its result
    def set_verbose(self, verbose: bool = True) -> None:
        self.__verbose = verbose

    def set_truncate_long_lines(self, truncate: bool = True) -> None:
        self.__truncate_long_lines = truncate

    # passing None disables timeout
    # passing 0 makes socket Non-blocking and not supported
    # complete time spend in execute may be 2x higher
    # because send and receive timeouts add
    def set_timeout(self, timeout_seconds: Union[float, None]) -> None:
        self.__execute_timeout_seconds = timeout_seconds

    def async_send(self, verb: str, args: Any, tid: Union[int, None] = None, custom_timeout: bool = False, timeout_seconds: Union[float, None] = None) -> int:

        if tid is None:
            tid = self.__get_next_tid()

        # make the args a list if it's just a dict or int or something
        arg_list = args if type(args) is list else [args]

        if not custom_timeout:
            timeout_seconds = self.__execute_timeout_seconds

        # make a json request in dict from
        self.socket.send({ "verb": verb, "arguments": arg_list, "tid": tid }, timeout_seconds)

        return tid

    def async_wait(self, custom_timeout: bool = False, timeout_seconds: Union[float, None] = None) -> Any:
        # just pull the first thing off the wire and return it
        if not custom_timeout:
            timeout_seconds = self.__execute_timeout_seconds
        result = self.socket.receive(timeout_seconds)
        self.__print(result)
        return result

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

    @staticmethod
    def blob_from_string(data):
        """
        makes blob suitable to use with FunOS blob services from a given string
        """
        if sys.version_info[0] != 2 and not isinstance(data, bytes):
            raise RuntimeError("wrong datatype passed to blob_from_string, expecting bytes, got ", type(data))
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
