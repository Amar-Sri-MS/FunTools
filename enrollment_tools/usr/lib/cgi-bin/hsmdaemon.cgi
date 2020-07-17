#! /usr/bin/env python3

##############################################################################
#  hsmdaemon.py
#
# simple cgi-script that extract a message from the request and
# sends it
#
#  Copyright (c) 2018-2020. Fungible, inc. All Rights Reserved.
#
##############################################################################
import struct
import socket
import traceback
import os

from common import *

RESTRICTED_PORT = 4443

SERVER_ADDRESS = '/var/lib/hsmdaemon/com.fungible.hsmdaemon.socket'

########################################################################
#
# Send json
#
########################################################################

def send_json(json):
    print("Content-type: application/json")
    print("Status: 200 OK")
    print("Content-length: %d\n" % len(json))
    print(json)


########################################################################
#
# process POST
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

def call_rpc():
    ''' just package the content into a RPC message '''
    len = int(os.environ['CONTENT_LENGTH'])
    to_send = sys.stdin.read(len).encode('utf-8')

    log("Connecting to %s " % SERVER_ADDRESS)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SERVER_ADDRESS)

    sock.sendall(make_daemon_msg(to_send))

    received = recv_daemon_msg(sock)
    if received is None:
        raise ConnectionError("Server did not send a response")
    send_json(received.decode('utf-8'))


def main_program():

    try:
        # enforce a command coming from an intranet only accessible port
        port = int(os.environ['SERVER_PORT'])

        if port != RESTRICTED_PORT:
            raise ValueError("Attempt to access signing server from port %d" % port)

        method = os.environ["REQUEST_METHOD"]
        if method not in ("POST"):
            raise ValueError("Invalid request method %s" % method)

        call_rpc()

    # key errors (missing form entries) as well as
    # value errors are translated as 400 Bad Request
    except (ValueError, KeyError) as err:
        # Log
        log("Exception: %s" % err)
        # Response
        print("Status: 400 Bad Request")
        err_msg = str(err)
        print("Content-Length: %d\n" % len(err_msg))
        print(err_msg)

    except ConnectionError as err:
         # Log
        log("Exception: %s" % err)
        traceback.print_exc()
        # Response
        print("Status: 503 Service Unavalaible")
        err_msg = str(err) + "\n" + traceback.format_exc()
        print("Content-Length: %d\n" % len(err_msg))
        print(err_msg)

        # all other errors are reported as 500 Internal Server Error
    except Exception as err:
        # Log
        log("Exception: %s" % err)
        traceback.print_exc()
        # Response
        print("Status: 500 Internal Server Error")
        err_msg = str(err) + "\n" + traceback.format_exc()
        print("Content-Length: %d\n" % len(err_msg))
        print(err_msg)


main_program()
