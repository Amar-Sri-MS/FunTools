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
import binascii
import hashlib

import cgi

import traceback

from subprocess import CalledProcessError

from asn1crypto import pem, keys

from common import (log,
                    send_binary_buffer)

from db_helper import (SN_DESC,
                       SN_LEN,
                       ID_FLD,
                       insert_select_chip_id,
                       get_sn_values,
                       pack_bytes_with_len_prefix,
                       db_func)

from openssl_esrp import (esrp_signer_cert,
                          esrp_get_public_key,
                          esrp_get_modulus,
                          esrp_sign_hash_with_key,
                          esrp_sign_hash_with_modulus)

####
# Constants
#

RESTRICTED_PORT = 4443

# SERIAL_NUMBER_DESCS = (
#     ('serial_info', 8),
#     ('family', 1),
#     ('device', 1),
#     ('revision', 1),
#     ('foundry_fab' 1),
#     ('year', 1),
#     ('iso_week', 1),
#     ('security_group', 2),
#     ('reserved', 4),
#     ('sn', 4))


#################################################################################
#
# Database routines
#
#################################################################################

CERT_DESCS = (
    ('magic', 4, b'\xa5\x5e\x00\xb1'),
    ('debug_locks', 4, 4 * b'\xff'),
    ('auth', 1, b'\x00'),
    ('key_index', 1, b'\x00'),
    ('reserved', 2, 2 * b'\x00'),
    ('tamper_locks', 4, 4 * b'\xff'),
) + SN_DESC + (
    ('serial_info_mask', 8, 8 * b'\xff'),
    ('serial_nr_mask', 16, 16 * b'\xff'),
    ('modulus', 516),
    ('rsa_signature', 516)
)

FIELDS = [desc[0] for desc in CERT_DESCS]
FIELDS_CONCAT = " || ".join(FIELDS)

# psycopg2 parameters are always represented by %s
# retrieve from the view
RETRIEVE_STMT_ROOT = "SELECT " + FIELDS_CONCAT + " FROM debug_certs_v "
RETRIEVE_STMT = RETRIEVE_STMT_ROOT + "WHERE serial_info = %s AND serial_nr = %s"

# insertion
# only a few fields -- others have default values
INS_CERT_FIELDS = [ID_FLD] + [desc[0] for desc in CERT_DESCS
                                  if not desc in SN_DESC] + ["pub_key_pem"]

INS_CERT_FIELDS_LIST = ",".join(INS_CERT_FIELDS)
INS_CERT_ARGS_LIST = ",".join([f"%({fld})s" for fld in INS_CERT_FIELDS])

INSERT_CERT_STMT  = "INSERT INTO debug_certs (" + \
    INS_CERT_FIELDS_LIST + ") VALUES (" + INS_CERT_ARGS_LIST + " ) "

def db_store_cert(conn, values):
    ''' store the full certificate in the database '''
    with conn.cursor() as cur:
        values[ID_FLD] = insert_select_chip_id(cur,
                                               values['serial_info'],
                                               values['serial_nr'])
        cur.execute(INSERT_CERT_STMT, values)
    conn.commit()


def db_retrieve_cert_with_sn(conn, values):
    ''' retrieve the certificate based on serial number '''
    with conn.cursor() as cur:
        cur.execute(RETRIEVE_STMT,
                    (values['serial_info'],
                     values['serial_nr']))
        row = cur.fetchone()
        if row:
            return row[0]
        return None


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


def cmd_sign_test(form):

    key_label = form.getvalue("key", "fpk4")
    key_set = int(form.getvalue("production", 0))
    out_format = form.getvalue("format", "binary")

    signature = esrp_sign_hash_with_key(key_set,
                                            key_label,
                                            "sha512",
                                            b'\x00' * 64)
    if out_format == "binary":
        send_binary(signature, f"{key_label}_{key_set}_test_signature.bin")
    else:
        print("Content-type: text/plain")
        send_binary_buffer(signature, form)


def process_query():
    ''' process a modulus query '''
    form = cgi.FieldStorage()

    cmd = form.getvalue("cmd", "modulus")

    if cmd == "modulus":
        cmd_modulus(form)
    elif cmd == "esrp_signer_cert":
        pem_cert = esrp_signer_cert()
        send_binary(pem_cert, "esrp_signer_cert.pem")
    elif cmd == "sign_test":
        cmd_sign_test(form)
    else:
        raise ValueError("Invalid command")


def rsa_pub_key_components(rsa_pub_key):
    ''' return the public exponent (integer) and modulus (binary str) of
    a rsa public key '''
    pub_exp_integer = rsa_pub_key['public_exponent']
    pub_exp = int.from_bytes(pub_exp_integer.contents,
                             byteorder='big')
    modulus_integer = rsa_pub_key['modulus']
    raw_modulus = modulus_integer.contents
    # the raw modulus might have an extra 0 (ASN.1 integer encoding)
    if raw_modulus[0] == 0:
        return pub_exp, raw_modulus[1:]
    return pub_exp, raw_modulus


def read_rsa_public_key(pub_info_der):
    rsa_pub_key = keys.RSAPublicKey.load(pub_info_der)
    return rsa_pub_key_components(rsa_pub_key)


def read_public_key(pub_info_der):
    ''' extract the modulus from the ASN.1 structure '''
    pub_key_info = keys.PublicKeyInfo.load(pub_info_der)
    if pub_key_info.algorithm != 'rsa':
        raise ValueError("Not an RSA key")
    rsa_pub_key = pub_key_info['public_key'].parsed
    return rsa_pub_key_components(rsa_pub_key)


def read_public_key_file(contents):
    # if PEM file, decode it
    if pem.detect(contents):
        obj_name, _, der_bytes = pem.unarmor(contents)
        if obj_name == 'RSA PUBLIC KEY':
            pub_exp,modulus = read_rsa_public_key(der_bytes)
        elif obj_name == 'PUBLIC KEY':
            pub_exp, modulus = read_public_key(der_bytes)
        else:
            raise ValueError(f"Cannot use PEM file with f{obj_name} for key")
    else:
        raise ValueError("Invalid PEM file provided")

    if pub_exp != 0x10001:
        raise ValueError("Key must have 0x010001 as public exponent")

    return modulus


def auth_log(msg):
    user_DN = os.environ.get('SSL_CLIENT_S_DN')
    if os.environ.get('SSL_CLIENT_VERIFY') != 'SUCCESS' or not user_DN:
        raise PermissionError(401, "Authentication required")

    # log the operation
    log(f"Signing by {user_DN}: {msg}")


def get_debugging_certificate(form, hex_serial_nr):
    ''' generate retrieve a debugging certificate for that serial nr '''
    try:
        serial_nr = binascii.a2b_hex(hex_serial_nr)
    except binascii.Error as exc:
        raise ValueError("Invalid format for serial number") from exc

    if len(serial_nr) != SN_LEN:
        raise ValueError("Invalid length for serial number")

    values = get_sn_values(serial_nr)
    # trying getting cert from/in db
    cert = db_func(db_retrieve_cert_with_sn, values)
    if cert:
        send_binary(cert, filename=f"debug_cert_{hex_serial_nr}.bin")
        return

    # otherwise try to insert a new debugging cert
    # get security group
    key_set = int.from_bytes(serial_nr[14:16], byteorder='big')
    if key_set == 0:
        raise ValueError("Use debugging certficate for group 0")

    # mutual authentication required for production signing FWIW
    auth_log(f"debugging certificate for {hex_serial_nr}")

    # retrieve the PEM key ensuring str type
    values['pub_key_pem'] = form.getvalue('key', None)

    modulus = read_public_key_file(values['pub_key_pem'])
    # build the TBS
    for desc in CERT_DESCS:
        if len(desc) > 2:
            values[desc[0]] = desc[2]
    values['modulus'] = pack_bytes_with_len_prefix(modulus, 516)
    values['rsa_signature'] = b'' # no signature in TBS
    # TBS is the concatenation of all values in CERT DESCS so far
    tbs = b''.join([values[desc[0]] for desc in CERT_DESCS])
    # sign with 'fpk2'
    dgst = hashlib.sha512(tbs).digest()
    signature = esrp_sign_hash_with_key(key_set,
                                        'fpk2',
                                        'sha512',
                                        dgst)
    values['rsa_signature'] = pack_bytes_with_len_prefix(signature, 516)
    db_func(db_store_cert, values)

    send_binary(tbs + values['rsa_signature'],
                filename=f"debug_cert_{hex_serial_nr}.bin")


def digest_sign(form):
    ''' send the response to a signing request '''
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
        auth_log(f"set ({key_set}), key = {key_label}, digest = {algo_digest}")

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



def process_post():
    form = cgi.FieldStorage()

    # is there a serial number provided?
    serial_nr = form.getvalue("serial_number", None)
    if serial_nr:
        get_debugging_certificate(form, serial_nr)
    else:
        digest_sign(form)


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
            # either a sign request or debugging certificate request
            process_post()

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
        log(f"Exception: {err}\n{traceback.format_exc()}")
        # Response
        print("Status: 400 Bad Request")
        err_msg = str(err)
        print(f"Content-Length: {len(err_msg)}\n")
        print(err_msg)

    except ConnectionError as err:
    # also include ConnectionRefused etc...
        # Log
        log(f"Exception: {err}\n{traceback.format_exc()}")
        # Response
        print("Status: 503 Service Unavailable")
        err_msg = str(err)
        print(f"Content-Length: {len(err_msg)}\n")
        print(err_msg)

    except PermissionError as err:
        # Log
        log(f"Exception: {err}\n{traceback.format_exc()}")
        # Response
        print("Status: 401 Unauthorized")
        err_msg = str(err)
        print(f"Content-Length: {len(err_msg)}\n")
        print(err_msg)

    # all other errors are reported as 500 Internal Server Error
    except Exception as err: # pylint: disable=broad-exception-caught
        # Log
        log(f"Exception: {err}\n{traceback.format_exc()}")
        # Response
        print("Status: 500 Internal Server Error")
        err_msg = str(err) + "\n" + traceback.format_exc()
        print(f"Content-Length: {len(err_msg)}\n")
        print(err_msg)


main_program()
