#! /usr/bin/env python3

##############################################################################
#  hsmd_common.py
#
# routines to forward request to the hsm daemon
#
#  Copyright (c) 2018-2020. Fungible, inc. All Rights Reserved.
#
##############################################################################
import struct
import socket

SERVER_ADDRESS = '/var/lib/hsmdaemon/com.fungible.hsmdaemon.socket'


########################################################################
#
# transport to daemon
#
########################################################################

def make_daemon_msg(s):
    return struct.pack('!H', len(s)) + s


def recv_daemon_msg(sock):

    data = sock.recv(2)
    if len(data) != 2:
        return None

    msg_size = struct.unpack('!H', data)[0]

    recv_size = 0
    data = b''
    while recv_size < msg_size:
        new_data = sock.recv(msg_size - recv_size)
        recv_size += len(new_data)
        data += new_data

    return data


def hsmd_rpc_call(json_payload):

    to_send = json_payload.encode('utf-8')

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SERVER_ADDRESS)

    sock.sendall(make_daemon_msg(to_send))

    received = recv_daemon_msg(sock)
    if received is None:
        raise ConnectionError("HSM Server did not send a response")
    return received.decode('utf-8')
