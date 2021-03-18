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
import json
import binascii

SERVER_ADDRESS = '/var/lib/hsmdaemon/com.fungible.hsmdaemon.socket'

# maps hsmid to suffix to server address
# 0 is invalid (development)
# 1 is SmartCard HSM (DPU)
# 2 is SoftHSM (AST2600)

HSM_ID_TO_SUFFIX = {
    1: "",
    2: ".softhsm"
}

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



def hsmd_rpc_call(json_payload, hsm_id):
    ''' send the json paylod to the server socket '''
    to_send = json_payload.encode('utf-8')

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SERVER_ADDRESS + HSM_ID_TO_SUFFIX[hsm_id])

    sock.sendall(make_daemon_msg(to_send))

    received = recv_daemon_msg(sock)
    if received is None:
        raise ConnectionError("HSM Server did not send a response")
    return received.decode('utf-8')


#######################################################################
#
# higher level routines
#
# these routines used to be in the signing_server but contributed
# instability (were changed often), so they are moved here.
#
#######################################################################

########################################################################
#
# Operation with remote HSM
#
########################################################################

################################################################
# Base64 helpers
def to_b64(some_bytes):
    return binascii.b2a_base64(some_bytes).rstrip().decode('utf-8')

def from_b64(b64):
    return binascii.a2b_base64(b64)


def make_json_rpc_call(cmd, params=None, **kwargs):
    if not params:
        params = kwargs
    json_cmd = {'jsonrpc': '2.0', 'method': cmd, 'params': params, 'id': 1}
    return json.dumps(json_cmd)

def get_result(json_rpc_return):
    response = json.loads(json_rpc_return)
    # look for an error
    if "error" in response:
        err = response["error"]
        raise ValueError("HSM returned error %d: %s" %
                         (err.get("code", 0), err.get("message", "")))
    return response["result"]

def get_auth_token(auth_token_str):
    auth_token_dict = json.loads(auth_token_str)
    return auth_token_dict['auth_token']


def remote_hsm_get_modulus(key_label, hsm_id):
    # package the request into json
    json_rpc_call = make_json_rpc_call("pubkey", key=key_label)
    json_rpc_return = hsmd_rpc_call(json_rpc_call, hsm_id)

    modulus_b64 = get_result(json_rpc_return)
    if modulus_b64 is None:
        raise ValueError("Key \"%s\" not found on remote HSM" %
                         key_label)

    return from_b64(modulus_b64)


def remote_hsm_sign_hash_with_key(key_label, digest_info, auth, hsm_id):
    # package the request into json
    json_rpc_call = make_json_rpc_call("sign",
                                       auth_token=get_auth_token(auth),
                                       digest_info=to_b64(digest_info),
                                       key=key_label)
    json_rpc_return = hsmd_rpc_call(json_rpc_call, hsm_id)

    signature_b64 = get_result(json_rpc_return)
    return from_b64(signature_b64)


def remote_hsm_sign_hash_with_modulus(modulus, digest_info, auth, hsm_id):
    # package the request into json
    json_rpc_call = make_json_rpc_call("sign",
                                       auth_token=get_auth_token(auth),
                                       digest_info=to_b64(digest_info),
                                       modulus=to_b64(modulus))
    json_rpc_return = hsmd_rpc_call(json_rpc_call, hsm_id)

    signature_b64 = get_result(json_rpc_return)
    return from_b64(signature_b64)
