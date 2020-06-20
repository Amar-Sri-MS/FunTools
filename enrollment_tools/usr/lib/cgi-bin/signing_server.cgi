#! /usr/bin/env python3

##############################################################################
#  signing_server.py
#
#
#  Copyright (c) 2018-2020. Fungible, inc. All Rights Reserved.
#
##############################################################################

import sys
import struct
import os
import hashlib
import cgi

import traceback

from asn1crypto import core,algos

from common import *

RESTRICTED_PORT = 4443

# FIXME: this should be a shared constants file
RSA_KEY_SIZE_IN_BITS = 2048
SIGNING_INFO_SIZE = 2048

HEADER_RESERVED_SIZE = SIGNING_INFO_SIZE - (4 + MAX_SIGNATURE_SIZE)

SIGNED_ATTRIBUTES_SIZE = 32
SIGNED_DESCRIPTION_SIZE = 32

SERIAL_INFO_NUMBER_SIZE = 24

CERT_PUB_KEY_POS = 64

MAX_KEYS_IN_KEYBAG = 96

MAGIC_NUMBER_CERTIFICATE = 0xB1005EA5
MAGIC_NUMBER_ENROLL_CERT = 0xB1005C1E


########################################################################
#
# Send binary bytes
#
########################################################################

def send_binary(binary_buffer):
    print("Content-type: application/octet-stream")
    print("Status: 200 OK")
    print("Content-length: %d\n" % len(binary_buffer))
    sys.stdout.flush()
    sys.stdout.buffer.write(binary_buffer)


########################################################################
#
# Return some information: key modulus
#
########################################################################

def send_binary_modulus(form, key_label):
    # get modulus from HSM
    with get_ro_session() as session:
        modulus = get_modulus(get_public_rsa_with_label(session, key_label))
        send_binary(modulus)

def gen_sha512_digest_info(sha512_hash):
    digest = core.OctetString()
    digest.set(sha512_hash)
    digest_algorithm = algos.DigestAlgorithm()
    digest_algorithm['algorithm'] = 'sha512'
    digest_info = algos.DigestInfo()
    digest_info['digest_algorithm'] = digest_algorithm
    digest_info['digest'] = digest
    return digest_info.dump()

def hsm_sign_hash_with_key(label, sha512_hash):
    digest_info_der = gen_sha512_digest_info(sha512_hash)
    with get_ro_session() as session:
        private = get_private_rsa_with_label(session, label)
        return private.sign(digest_info_der, mechanism=pkcs11.Mechanism.RSA_PKCS)

def hsm_sign_hash_with_modulus(modulus, sha512_hash):
    digest_info_der = gen_sha512_digest_info(sha512_hash)
    with get_ro_session() as session:
        private = get_private_rsa_with_modulus(session, modulus)
        return private.sign(digest_info_der, mechanism=pkcs11.Mechanism.RSA_PKCS)


# retrieving binary form content can be problematic.
# create a function for this as a bottleneck for debugging/logging
def get_binary_from_form(form, name):
    ret = form.getfirst(name, default=b'')
    return ret


def process_query():

    form = cgi.FieldStorage()
    cmd = safe_form_get(form, "cmd", "modulus")
    if cmd == "modulus":

        key_label = safe_form_get(form, "key", "fpk4")

        # send in binary format by default for this application
        # to ease transition
        out_format = safe_form_get(form, "format", "binary")
        if out_format == "binary":
            send_binary_modulus(form, key_label)
        else:
            print("Content-type: text/plain")
            send_modulus(form, key_label)

    else:
        raise ValueError("Invalid command")


def sign():
    form = cgi.FieldStorage()

    # is there a hash provided?
    sha512_hash = get_binary_from_form(form, "digest")

    if len(sha512_hash) != hashlib.sha512().digest_size:
        raise ValueError("Digest is %d bytes, expected %d" %
                        (len(sha512_hash), hashlib.sha512.digest_size))

    key_label = safe_form_get(form, "key", None)
    if key_label:
        signature = hsm_sign_hash_with_key(key_label, sha512_hash)
    else:
        modulus = get_binary_from_form(form, "modulus")
        if len(modulus) == 0:
            raise ValueError("No key or modulus specified for sign command")
        signature = hsm_sign_hash_with_modulus(modulus, sha512_hash)

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
