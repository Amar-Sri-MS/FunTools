#! /usr/bin/env python3

##############################################################################
#  signing_server.py
#
#  A skeleton implementation of the Fungible Signing Server using
#  PEM key files.
#
#  THIS SHOULD BE USED FOR DEVELOPMENT PURPOSES ONLY. THE KEYS USED ARE NOT
#  PROPERLY PROTECTED (PEM FILES W/O PASSWORD). IT IS STRONGLY RECOMMENDED
#  TO USE A HSM FOR PRODUCTION SIGNING BY MODIFYING THE FUNCTIONS IN THE
#  "Operations with keys" CODE SECTION BELOW.
#
#  The PEM Key files should be readable by the Apache user account
#  (typically www-data). These files can be located anywhere by
#  populating the KEY_PATHS dictionary. Otherwise, they need to be
#  placed in /usr/lib/cgi-bin.
#
#  Copyright (c) 2021. Fungible, inc. All Rights Reserved.
#
##############################################################################

import sys
import os
import binascii
import textwrap
import hashlib
import cgi
import datetime

import traceback

from asn1crypto import keys, pem

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.hazmat.primitives.serialization import (load_der_private_key,
                                                          load_der_public_key)

# optional key_label -> key_file_path. Files in the current directory will be used
# if the required key name or modulus is not found using the labels or paths
# in this dictionary.
KEY_PATHS = { }



#################################################################################
#
# Logging Apache style
#
#################################################################################
def log(msg):
    dt_stamp = datetime.datetime.now().strftime("%c")
    print("[%s] [signing] %s" % (dt_stamp, msg), file=sys.stderr)


###########################################################################
#
# HTTP common routines
#
###########################################################################

def send_response_body(body):
    print("Status: 200 OK")
    print("Content-length: %d\n" % len(body))
    print("%s\n" % body)


def send_binary_buffer(bin_buffer, form):
    format = form.getvalue("format", "hex")
    if format == "hex":
        bin_str = binascii.b2a_hex(bin_buffer).decode('ascii')
    elif format == "base64":
        bin_str = textwrap.fill(
            binascii.b2a_base64(bin_buffer).decode('ascii'),
            width=57)
    elif format == "c_struct":
        bin_c_struct = "%d,\n{\n" % len(bin_buffer)

        for pos in range(0, len(bin_buffer)):
            bin_c_struct += "0x%02x, " % bin_buffer[pos]
            if pos % 8 == 7:
                bin_c_struct += "\n"
        if len(bin_buffer) %8 != 0:
            bin_c_struct += "\n"
        bin_c_struct += "}"
        bin_str = bin_c_struct
    else:
        raise ValueError("Unsupported format: %s" % format)

    send_response_body(bin_str)


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
# DER operations: rsapublickey
#
#######################################################################

def gen_rsa_pub_key_info(modulus, exponent=0x10001):
    rsa = keys.RSAPublicKey()
    rsa['modulus'] = int.from_bytes(modulus, byteorder='big')
    rsa['public_exponent'] = exponent
    return keys.PublicKeyInfo.wrap(rsa, "rsa")


########################################################################
#
# Operations with keys using PEM files (development)
# The same operations should be implemented using a HSM for production
#
########################################################################

# maps the hashlib nams to the cryptolib hash algorithm
HASH_ALGO_NAMES = {
    "sha512" : hashes.SHA512,
    "sha256" : hashes.SHA256,
    "sha224" : hashes.SHA224,
    "sha384" : hashes.SHA384,
}


def load_key_from_path(fname):
    try:
        with open(fname, 'rb') as fd:
            data = fd.read()
        if not pem.detect(data):
            return None # only support PEM

        data_type, _, der_data = pem.unarmor(data)

        if 'PRIVATE' in data_type:
            return load_der_private_key(der_data,
                                        password=None,
                                        backend=default_backend())
        elif 'PUBLIC' in data_type:
            # this can load both PUBLIC KEY and RSA PUBLIC KEY
            return load_der_public_key(der_data,
                                       backend=default_backend())
        else:
            return None

    except Exception as exc:
        log("Error: %s" % str(exc))
        return None

def key_n(key):
    #deal with public and private keys
    try:
        key = key.public_key()
    except:
        pass
    return key.public_numbers().n


def key_has_modulus(key, n):
    return n == key_n(key)

def search_paths_for_modulus( paths, n):
    for fname in paths:
        key = load_key_from_path(fname)
        if key and key_has_modulus(key, n):
            return key


def get_key_with_label(key_label):
    key_path = KEY_PATHS.get(key_label)
    if not key_path:
        key_path = key_label + ".pem"

    key = load_key_from_path(key_path)
    if not key:
        raise ValueError("No key found for the label %s (%s)" %
                         (key_label, os.getcwd()))
    return key


def get_key_with_modulus(modulus):
    # find key with that modulus
    # modulus to int
    target_n = int.from_bytes(modulus, byteorder='big')

    # iterate through KEY_PATHS first
    key = search_paths_for_modulus(KEY_PATHS.values(), target_n)

    if not key:
    # iterate through the current directory
        key = search_paths_for_modulus([path for path in os.listdir('./')
                                        if path.endswith('.pem')],
                                       target_n)
    if not key:
        raise ValueError("No key found for the modulus %s (%s)" %
                         (hex(target_n), os.getcwd()))

    return key

def get_modulus_of_key(key_label):
    # get modulus from key
    key = get_key_with_label(key_label)

    n = key_n(key)
    modulus = n.to_bytes((n.bit_length()+7)//8, byteorder='big')
    return modulus


def sign_hash(key, digest, digest_name):
    hash_algo = HASH_ALGO_NAMES[digest_name]()
    return key.sign(digest,
                    padding.PKCS1v15(),
                    utils.Prehashed(hash_algo))

def sign_hash_with_label(key_label, digest, digest_name):
    key = get_key_with_label(key_label)
    return sign_hash(key, digest, digest_name)


def sign_hash_with_modulus(modulus, digest, digest_name):
    key = get_key_with_modulus(modulus)
    return sign_hash(key, digest, digest_name)


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

    modulus = get_modulus_of_key(key_label)

    out_format = form.getvalue("format", "binary")
    if out_format == "binary":
        send_binary(modulus, "%s_modulus.bin" % (key_label))
    elif out_format == "public_key":
        pub_key_info = gen_rsa_pub_key_info(modulus)
        pub_key_info_pem = pem.armor('PUBLIC KEY', pub_key_info.dump())
        send_binary(pub_key_info_pem, "%s.pem" % (key_label))
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
    digest = get_binary_from_form(form, "digest")
    algo_name = form.getvalue("algo", "sha512") # default and back ward compatible

    if algo_name in hashlib.algorithms_available:
        algo = hashlib.new(algo_name)
        if len(digest) != algo.digest_size:
            raise ValueError("Digest is %d bytes, expected %d bytes for %s" %
                             (len(digest), algo.digest_size, algo_name))

    key_label = form.getvalue("key", None)
    if key_label:
        signature = sign_hash_with_label(key_label,
                                         digest,
                                         algo_name)
    else:
        modulus = get_binary_from_form(form, "modulus")
        if len(modulus) == 0:
            raise ValueError("No key or modulus specified for sign command")
        signature = sign_hash_with_modulus(modulus,
                                           digest,
                                           algo_name)

    # send binary signature back
    send_binary(signature)


def main_program():

    try:
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
