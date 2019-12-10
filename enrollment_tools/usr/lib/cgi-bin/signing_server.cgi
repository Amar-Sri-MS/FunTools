#! /usr/bin/env python3

##############################################################################
#  enrollment_server.py
#
#
#  Copyright (c) 2018-2019. Fungible, inc. All Rights Reserved.
#
##############################################################################

import sys
import struct
import os
import cgi

import traceback

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


########################################################################
#
# sign images
#
########################################################################

def add_cert_and_signature_to_binary(binary, cert, signature):
    ''' add certificate and signature to a buffer '''
    binary += cert
    binary += b'\x00' * (HEADER_RESERVED_SIZE - len(cert))
    return append_signature_to_binary(binary, signature)

def get_cert_modulus(cert):
    ''' get the modulus from a certificate '''
    cert_key_modulus_len = struct.unpack('<I',
                                         cert[CERT_PUB_KEY_POS:CERT_PUB_KEY_POS+4])
    start = CERT_PUB_KEY_POS+4
    end = start + cert_key_modulus_len[0]
    return cert[start:end]


def hsm_sign_with_key(label, data):
    with get_ro_session() as session:
        private = get_private_rsa_with_label(session, label)
        return private.sign(data, mechanism=pkcs11.Mechanism.SHA512_RSA_PKCS)


def hsm_sign_with_cert(cert, data):
    modulus = get_cert_modulus(cert)
    with get_ro_session() as session:
        private = get_private_rsa_with_modulus(session, modulus)
        return private.sign(cert+data, mechanism=pkcs11.Mechanism.SHA512_RSA_PKCS)


def image_gen(binary, ftype, version, description,
              sign_key, cert, customer_cert, key_index):
    ''' generate signed firmware image '''

    to_be_signed = struct.pack('<2I', len(binary), version)
    to_be_signed += struct.pack('4s', ftype.encode())
    to_be_signed += b'\x00' * SIGNED_ATTRIBUTES_SIZE
    if description:
        # Max allowed size is (block size - 1) to allow for terminating null
        if len(description) > SIGNED_DESCRIPTION_SIZE - 1:
            raise ValueError("Image description too long, max is {}".format(SIGNED_DESCRIPTION_SIZE-1))
        to_be_signed += description.encode() + b'\x00' * (SIGNED_DESCRIPTION_SIZE - len(description))
    else:
        to_be_signed += b'\x00' * SIGNED_DESCRIPTION_SIZE

    to_be_signed += binary

    signature = b''
    # sign_key and cert_file are mutually exclusive with sign_key taking priority
    # if there is a key_index, then encode it as a pseudo-certificate'
    if sign_key:
        if key_index is not None:
            cert = struct.pack("<I", (key_index | 0x80000000))
        else:
            cert = b''
        signature = hsm_sign_with_key(sign_key, to_be_signed)
    elif cert:
        signature = hsm_sign_with_cert(cert, to_be_signed)
    elif not customer_cert:
        raise ValueError("A certificate (customer or fungible) or a key label is needed "+
                         "to identify the key used to sign a firmware image")

    customer_to_be_signed = add_cert_and_signature_to_binary(b'', cert, signature)
    customer_to_be_signed += to_be_signed

    if customer_cert:
        customer_signature = hsm_sign_with_cert(customer_cert,
                                                customer_to_be_signed)
    else:
        customer_cert = b''
        customer_signature = b''

    image = add_cert_and_signature_to_binary(b'', customer_cert,
                                             customer_signature)
    image += customer_to_be_signed
    return image

# retrieving binary form content can be problematic.
# create a function for this as a bottleneck for debugging/logging
def get_binary_from_form(form, name):
    ret = form.getfirst(name, default=b'')
    return ret


def sign_image():
    form = cgi.FieldStorage()

    # we need a type ...
    image_type = safe_form_get(form, "type", None)
    if not image_type:
        raise ValueError("No type specified")

    if len(image_type) != 4:
        raise ValueError("Invalid type '" + image_type + "' specified")

    # ... and a version ...
    image_version = safe_form_get(form, "version", None)
    if not image_version:
        raise ValueError("No version specified")

    # convert to number
    image_version = int(image_version, 0)

    # ...and optionally a description
    description = safe_form_get(form, "description", '')

    # image
    image = get_binary_from_form(form, "img")

    # we need a key label, a certificate or a customer certificate
    # a customer certificate can be in addition to a key label or a certificate
    key_label = safe_form_get(form, "key", None)

    #  key can be marked as index into key bag
    key_index = None
    if key_label is not None:
        key_index_str = safe_form_get(form, "key_index", None)
        if key_index_str is not None:
            key_index = int(key_index_str, 0)

    certificate = get_binary_from_form(form, "cert")

    customer_certificate = get_binary_from_form(form, "customer_cert")

    # log the request
    log("Signing request version = %d type = %s description = %s " %
        (image_version, image_type, description))
    log("Key = %s Certificate = %s Customer Certificate = %s " %
        (key_label if key_label else 'None',
         'Present' if certificate else 'None',
         'Present' if customer_certificate else 'None'))

    signed_image = image_gen(image, image_type, image_version, description,
                             key_label, certificate, customer_certificate,
                             key_index)
    send_binary(signed_image)


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
            sign_image()

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
