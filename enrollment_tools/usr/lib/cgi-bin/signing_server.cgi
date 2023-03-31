#! /usr/bin/env python3

##############################################################################
#  signing_server.py
#
#
#  Copyright (c) 2018-2020. Fungible, inc. All Rights Reserved.
#
##############################################################################

import sys
import os
import hashlib
import cgi

import traceback

from asn1crypto import core, algos, keys, pem

from common import *
from hsmd_common import (remote_hsm_get_modulus,
                         remote_hsm_sign_hash_with_key,
                         remote_hsm_sign_hash_with_modulus)


RESTRICTED_PORT = 4443

########################################################################
#
# Send binary bytes
#
########################################################################

def send_binary(binary_buffer, filename = None):
    if filename:
        print("Content-Disposition: attachment; filename = %s" %
              filename)
    print("Content-type: application/octet-stream")
    print("Status: 200 OK")
    print("Content-length: %d\n" % len(binary_buffer))
    sys.stdout.flush()
    sys.stdout.buffer.write(binary_buffer)

#######################################################################
#
# DER operations: digest_info, rsapublickey
#
#######################################################################

def gen_digest_info(algo_name, algo_digest):
    digest = core.OctetString()
    digest.set(algo_digest)
    digest_algorithm = algos.DigestAlgorithm()
    digest_algorithm['algorithm'] = algo_name
    digest_info = algos.DigestInfo()
    digest_info['digest_algorithm'] = digest_algorithm
    digest_info['digest'] = digest
    return digest_info.dump()


def gen_rsa_pub_key_info(modulus, exponent=0x10001):
    rsa = keys.RSAPublicKey()
    rsa['modulus'] = int.from_bytes(modulus, byteorder='big')
    rsa['public_exponent'] = exponent
    return keys.PublicKeyInfo.wrap(rsa, "rsa")


########################################################################
#
# Operations with local HSM
#
########################################################################

def hsm_get_modulus(key_label):
    # get modulus from HSM
    with get_ro_session() as session:
        return get_modulus(get_public_rsa_with_label(session, key_label))

def hsm_sign_hash_with_key(label, digest_info):
    with get_ro_session() as session:
        private = get_private_rsa_with_label(session, label)
        return private.sign(digest_info, mechanism=pkcs11.Mechanism.RSA_PKCS)

def hsm_sign_hash_with_modulus(modulus, digest_info):
    with get_ro_session() as session:
        private = get_private_rsa_with_modulus(session, modulus)
        return private.sign(digest_info, mechanism=pkcs11.Mechanism.RSA_PKCS)

########################################################################
#
# HTTP request handling
#
########################################################################


# retrieving binary form content can be problematic.
# create a function for this as a bottleneck for debugging/logging
def get_binary_from_form(form, name):
    ret = form.getfirst(name, default=b'')
    return ret


def cmd_modulus(form):

    key_label = form.getvalue("key", "fpk4")
    hsm_id = int(form.getvalue("production", 0))

    if hsm_id and key_label != "fpk4":
        modulus = remote_hsm_get_modulus(key_label, hsm_id)
    else:
        modulus = hsm_get_modulus(key_label)

    out_format = form.getvalue("format", "binary")
    if out_format == "binary":
        send_binary(modulus, "%s_%d_modulus.bin" % (key_label, hsm_id))
    elif out_format == "public_key":
        pub_key_info = gen_rsa_pub_key_info(modulus)
        pub_key_info_pem = pem.armor('PUBLIC KEY', pub_key_info.dump())
        send_binary(pub_key_info_pem, "%s_%d.pem" % (key_label, hsm_id))
    else:
        print("Content-type: text/plain")
        send_binary_buffer(modulus, form)


def process_query():

    form = cgi.FieldStorage()

    cmd = form.getvalue("cmd", "modulus")

    if cmd == "modulus":
        cmd_modulus(form)
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
            raise ValueError("Digest is %d bytes, expected %d bytes for %s" %
                             (len(algo_digest), algo.digest_size, algo_name))

    digest_info = gen_digest_info(algo_name, algo_digest)

    auth_token = form.getvalue("auth_token", None)

    # hsm_id: default to 0 but to 1 if auth_token
    # (backward compatibility with old clients)
    hsm_id = int(form.getvalue("production",
                               1 if auth_token else 0))

    key_label = form.getvalue("key", None)
    if key_label:
        if auth_token:
            signature = remote_hsm_sign_hash_with_key(key_label,
                                                      digest_info,
                                                      auth_token,
                                                      hsm_id)
        else:
            signature = hsm_sign_hash_with_key(key_label,
                                               digest_info)
    else:
        modulus = get_binary_from_form(form, "modulus")
        if len(modulus) == 0:
            raise ValueError("No key or modulus specified for sign command")
        if auth_token:
            signature = remote_hsm_sign_hash_with_modulus(modulus,
                                                          digest_info,
                                                          auth_token,
                                                          hsm_id)
        else:
            signature = hsm_sign_hash_with_modulus(modulus,
                                                   digest_info)

    # send binary signature back
    send_binary(signature)



def main_program():

    try:
        # enforce a command coming from an intranet only accessible port
        port = int(os.environ['SERVER_PORT'])

        if port != RESTRICTED_PORT:
            raise ValueError("Attempt to access signing server from port %d" % port)

        method = os.environ["REQUEST_METHOD"]
        if method not in ("GET", "POST"):
            raise ValueError("Invalid request method %s" % method)

        if method == "GET":
            process_query()
        else:
            sign()

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
    # also include ConnectionRefused etc...
        # Log
        log("Exception: %s" % err)
        # Response
        print("Status: 503 Service Unavailable")
        err_msg = str(err)
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
