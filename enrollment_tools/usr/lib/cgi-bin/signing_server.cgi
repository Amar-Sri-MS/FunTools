#!/usr/bin/env python3.9

##############################################################################
#  esrp_signing_server.cgi
#
#  signing routines using ESRP
#
#  Copyright (c) 2018-2020. Fungible, inc. All Rights Reserved.
#  Copyright (c) 2023. Microsoft Corporation. All Rights Reserved.
#
##############################################################################

# simplest thing that works: invoke openssl for each operation
# optimize later if necessary

import os
import sys
import hashlib

import cgi

import traceback

from subprocess import CalledProcessError

from common import log, send_binary_buffer

from openssl_esrp import (esrp_signer_cert,
                          esrp_get_public_key,
                          esrp_get_modulus,
                          esrp_sign_hash_with_key,
                          esrp_sign_hash_with_modulus)

####
# Constants
#

RESTRICTED_PORT = 4443


###
#
# Send binary bytes
#

def send_binary(binary_buffer, filename = None):
    if filename:
        print(f"Content-Disposition: attachment; filename = {filename}")

    print("Content-type: application/octet-stream")
    print("Status: 200 OK")
    print(f"Content-length: {len(binary_buffer)}\n")
    sys.stdout.flush()
    sys.stdout.buffer.write(binary_buffer)



###
#
# HTTP request handling
#

# retrieving binary form content can be problematic.
# create a function for this as a bottleneck for debugging/logging
def get_binary_from_form(form, name):
    return form.getfirst(name, default=b'')

def cmd_modulus(form):

    key_label = form.getvalue("key", "fpk4")
    key_set = int(form.getvalue("production", 0))
    out_format = form.getvalue("format", "binary")

    if out_format == "public_key":
        pub_key_pem = esrp_get_public_key(key_set, key_label)
        send_binary(pub_key_pem, f"{key_label}_{key_set}_pub.pem")
        return

    modulus = esrp_get_modulus(key_set, key_label)
    if out_format == "binary":
        send_binary(modulus, f"{key_label}_{key_set}_modulus.bin")
    else:
        print("Content-type: text/plain")
        send_binary_buffer(modulus, form)


def process_query():

    form = cgi.FieldStorage()

    cmd = form.getvalue("cmd", "modulus")

    if cmd == "modulus":
        cmd_modulus(form)
    elif cmd == "esrp_signer_cert":
        pem_cert = esrp_signer_cert()
        send_binary(pem_cert, "esrp_signer_cert.pem")
    else:
        raise ValueError("Invalid command")


def sign():
    form = cgi.FieldStorage()

    # is there a hash provided?
    algo_digest = get_binary_from_form(form, "digest")
    algo_name = form.getvalue("algo", "sha512") # default and back ward compatible

    if algo_name in hashlib.algorithms_available:
        algo = hashlib.new(algo_name)
        if len(algo_digest) != algo.digest_size:
            raise ValueError(f"Digest is {len(algo_digest)} bytes, " +
                             f"expected {algo.digest_size} bytes for {algo_name}")

    # key set: default to 0 : development
    # (backward compatibility with old clients)
    key_set = int(form.getvalue("production",0))
    key_label = form.getvalue("key", None)
    
    # mutual authentication required for production signing FWIW
    if key_set != 0:
        user_DN = os.environ.get('SSL_CLIENT_S_DN')
        if os.environ.get('SSL_CLIENT_VERIFY') != 'SUCCESS' or not user_DN:
            raise PermissionError(401, "Authentication required")

        # log the operation
        log(f"Production ({key_set}) signing by {user_DN}, key = {key_label}, digest = {algo_digest}")
    
    if key_label:
        signature = esrp_sign_hash_with_key(key_set,
                                            key_label,
                                            algo_name,
                                            algo_digest)
    else:
        modulus = get_binary_from_form(form, "modulus")
        if len(modulus) == 0:
            raise ValueError("No key or modulus specified for sign command")
        signature = esrp_sign_hash_with_modulus(key_set,
                                                modulus,
                                                algo_name,
                                                algo_digest)

    # send binary signature back
    send_binary(signature)



def main_program():

    try:
        # enforce a command coming from an intranet only accessible port
        port = int(os.environ['SERVER_PORT'])

        if port != RESTRICTED_PORT:
            raise ValueError(f"Attempt to access signing server from port {port}")

        method = os.environ["REQUEST_METHOD"]
        if method not in ("GET", "POST"):
            raise ValueError(f"Invalid request method {method}")

        if method == "GET":
            process_query()
        else:
            sign()

    # OpenSSL error: usually something wrong with ESRP
    except CalledProcessError as err:
        err_msg = "OpenSSL Error:" + err.stdout
        log(err_msg)
        # Response
        print("Status: 500 Internal Server Error")
        print(f"Content-Length: {len(err_msg)}\n")
        print(err_msg)


    # key errors (missing form entries) as well as
    # value errors are translated as 400 Bad Request
    except (ValueError, KeyError) as err:
        # Log
        log(f"Exception: {err}")
        # Response
        print("Status: 400 Bad Request")
        err_msg = str(err)
        print(f"Content-Length: {len(err_msg)}\n")
        print(err_msg)

    except ConnectionError as err:
    # also include ConnectionRefused etc...
        # Log
        log(f"Exception: {err}")
        # Response
        print("Status: 503 Service Unavailable")
        err_msg = str(err)
        print(f"Content-Length: {len(err_msg)}\n")
        print(err_msg)

    except PermissionError as err:
        # Log
        log(f"Exception: {err}")
        # Response
        print("Status: 401 Unauthorized")
        err_msg = str(err)
        print(f"Content-Length: {len(err_msg)}\n")
        print(err_msg)

    # all other errors are reported as 500 Internal Server Error
    except Exception as err:
        # Log
        log(f"Exception: {err}")
        traceback.print_exc()
        # Response
        print("Status: 500 Internal Server Error")
        err_msg = str(err) + "\n" + traceback.format_exc()
        print(f"Content-Length: {len(err_msg)}\n")
        print(err_msg)


main_program()
