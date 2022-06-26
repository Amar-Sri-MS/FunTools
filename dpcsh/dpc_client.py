##
##  dpc_client.py
##
##  Created by Dan Picken on 2017-06-20
##  Copyright (C) 2017 Fungible. All rights reserved.
##
## Example usage dpctest.py

from __future__ import print_function
from abc import abstractmethod
import json
import select
import socket
import sys
import time

try:
    from typing import Any, Tuple, Union
except ImportError:
    pass # since types are comments it is ok to miss the module

class DpcExecutionError(Exception):
    pass


class DpcExecutionException(Exception):
    pass


class DpcProxyError(Exception):
    pass


class DpcTimeoutError(Exception):
    pass


class DpcEncoder():
    @abstractmethod
    def enable_command(self):
        # type: (Any) -> Union[bytes(), None]
        pass

    @abstractmethod
    def serialization_size(self, buffer):
        # type: (Any, bytes()) -> int
        pass

    @abstractmethod
    def decode(self, buffer):
        # type: (Any, bytes()) -> Any
        pass

    @abstractmethod
    def encode(self, data):
        # type: (Any, Any) -> bytes()
        pass

    @abstractmethod
    def blob_from_string(data):
        # type: (bytes()) -> Any
        """
        makes blob suitable to use with FunOS blob services from a given string
        """
        pass

    @abstractmethod
    def blob_to_string(data):
        # type: (Any) -> bytes()
        """
        makes binary from blob returned by FunOS blob services, see dpctest.py for details
        """
        pass


class TextJSONEncoder(DpcEncoder):
    def enable_command(self):
        # type: (Any) -> Union[bytes(), None]
        return None

    def serialization_size(self, buffer):
        # type: (Any, bytes()) -> int
        return buffer.find(b'\n')

    def decode(self, buffer):
        # type: (Any, bytes()) -> Any
        try:
            return json.loads(buffer, strict=False)
        except:
            raise DpcExecutionError("Unable to parse to JSON. data: %s" % buffer)

    def encode(self, data):
        # type: (Any, Any) -> bytes()
        return json.dumps(data).encode('utf8') + b'\n'

    def blob_from_string(self, data):
        # type: (bytes()) -> Any
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

    def blob_to_string(self, data):
        # type: (Any) -> bytes()
        result = b''
        for chunk in data:
            result += bytes(bytearray(chunk))
        return result


class DpcSocket:
    def __init__(self, unix_sock, server_address, encoder):
        # type: (Any, bool, Union[None, str, Tuple[str, int]], DpcEncoder) -> None
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
        self.__encoder = encoder
        self.__buffer = b''
        self.__chunk_size = 32*1024
        if self.__encoder.enable_command() is not None:
            self.__write(self.__encoder.enable_command(), None)

    def __write(self, data, timeout_seconds):
        # type: (Any, bytes, Union[float, None]) -> Tuple[Union[float, None], int]

        start_time = time.time()
        ready = select.select([], [self.__sock], [], timeout_seconds)
        if ready[1]:
            bytes_sent = self.__sock.send(data)
        else:
            raise DpcTimeoutError('receive() timeout')

        if timeout_seconds is None:
            return None, bytes_sent

        remaining_time = timeout_seconds - start_time + time.time()
        if remaining_time is not None and remaining_time < 0:
            raise DpcTimeoutError('receive() timeout')

        return remaining_time, bytes_sent

    def send(self, data, timeout_seconds):
        # type: (Any, Any, Union[float, None]) -> None
        data_bytes = self.__encoder.encode(data)
        while len(data_bytes) > 0:
            timeout_seconds, bytes_sent = self.__write(data_bytes, timeout_seconds)
            data_bytes = data_bytes[bytes_sent:]

    def __read(self, timeout_seconds):
        # type: (Any, Union[float, None]) -> None
        start_time = time.time()
        ready = select.select([self.__sock], [], [], timeout_seconds)
        if ready[0]:
            self.__buffer += self.__sock.recv(self.__chunk_size)
            remaining_time = timeout_seconds - start_time + time.time() if timeout_seconds is not None else None
            if remaining_time is not None and remaining_time < 0:
                raise DpcTimeoutError('receive() timeout')
            return remaining_time
        raise DpcTimeoutError('receive() timeout')

    def receive(self, timeout_seconds):
        # type: (Any, Union[float, None]) -> Any
        position = self.__encoder.serialization_size(self.__buffer)

        if position == -1:
            remaining_time_seconds = self.__read(timeout_seconds)
            return self.receive(remaining_time_seconds)

        line = self.__buffer[:position]
        self.__buffer = self.__buffer[position + 1:]

        return self.__encoder.decode(line)

    def close(self):
        # type: (Any) -> None
        self.__sock.close()


class DpcClient(object):
    def __init__(self, legacy_ok = True, unix_sock = False, server_address = None, encoder = TextJSONEncoder()):
        # type: (Any, bool, bool, Union[None, str, Tuple[str, int]]) -> None
        self.__verbose = False
        self.__truncate_long_lines = False
        self.__async_queue = []
        self.__next_tid = 1
        self.__execute_timeout_seconds = None
        self.__sock = DpcSocket(unix_sock, server_address, encoder)
        self.blob_from_string = encoder.blob_from_string
        self.blob_to_string = encoder.blob_to_string

    def close(self):
        self.__sock.close()

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    # main interface for running DPC commands
    def execute(self, verb, arg_list, tid = None, custom_timeout = False, timeout_seconds = None):
        # type: (Any, str, list[Any], Union[None, int], bool, Union[float, None]) -> Any

        if " " in verb:
            raise RuntimeError("no spaces allowed in verbs")
        # make it a string and send it & get results
        tid = self.async_send(verb, arg_list, tid, custom_timeout, timeout_seconds)
        results = self.async_recv_wait(tid, custom_timeout, timeout_seconds)

        return results

    # Whether to print each command line and its result
    def set_verbose(self, verbose = True):
        # type: (Any, bool) -> None
        self.__verbose = verbose

    def set_truncate_long_lines(self, truncate = True):
        # type: (Any, bool) -> None
        self.__truncate_long_lines = truncate

    # passing None disables timeout
    def set_timeout(self, timeout_seconds):
        # type: (Any,  Union[float, None]) -> None
        self.__execute_timeout_seconds = timeout_seconds

    def async_send(self, verb, args, tid = None, custom_timeout = False, timeout_seconds = None):
        # type: (Any,  str, Any, Union[int, None], bool, Union[float, None]) -> int

        if tid is None:
            tid = self.__get_next_tid()

        # make the args a list if it's just a dict or int or something
        arg_list = args if type(args) is list else [args]

        if not custom_timeout:
            timeout_seconds = self.__execute_timeout_seconds

        # make a json request in dict from
        self.__sock.send({ "verb": verb, "arguments": arg_list, "tid": tid }, timeout_seconds)

        return tid

    def async_wait(self, custom_timeout = False, timeout_seconds = None):
        # type: (Any,  bool, Union[float, None]) -> Any
        # just pull the first thing off the wire and return it
        if not custom_timeout:
            timeout_seconds = self.__execute_timeout_seconds
        result = self.__sock.receive(timeout_seconds)
        self.__print(result)
        return result

    def async_recv_any_raw(self, custom_timeout = False, timeout_seconds = None):
        # type: (Any,  bool, Union[float, None]) -> Any
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

    def blob_from_file(self, filename):
        """
        makes blob suitable to use with FunOS blob services from a given string
        """
        with open(filename, 'rb') as f:
            return self.blob_from_string(f.read())

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
