########################################################
#
# test_signing_server.py
#
# Copyright (c) Fungible,inc. 2019
# Copyright (c) Microsoft Corporation. 2023
#
########################################################

''' module used for testing signing server API '''

import binascii
import hashlib
import argparse
import traceback
import urllib3
import requests


from cryptography import exceptions
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils

#pylint: disable=consider-using-f-string

HASH_ALGO_MAPPING = { 'sha224' : hashes.SHA224,
                      'sha256' : hashes.SHA256,
                      'sha384' : hashes.SHA384,
                      'sha512' : hashes.SHA512 }

def pack_binary_form_data(title, bin_data):
    ''' pack request binary data '''
    return (title, bin_data, 'application/octet-stream',
                {"Content-Length" : str(len(bin_data)) })


def create_binary_form_data(infile):
    ''' pack content of file as request binary data '''
    with open(infile, 'rb') as finput:
        bin_data = finput.read()
        return pack_binary_form_data(infile, bin_data)


def content(response):
    ''' check HTTP response and return its content '''
    if response.status_code != requests.codes.ok:
        raise RuntimeError("Request error: {0}".format(response.content))
    # always return the response content
    return response.content

def pub_key_modulus_bytes(pub_key):
    ''' return the modulus bytes of a public key '''
    n = pub_key.public_numbers().n
    return n.to_bytes((n.bit_length() + 7) // 8)


def hash_sign(server, tls_verify, digest,
              sign_key=None, modulus=None, algo_name=None):
    ''' send a signing request to the server and return the signature '''
    url_str = "https://" + server + ":4443/cgi-bin/signing_server.cgi"

    multipart_form_data = { 'digest' : pack_binary_form_data("sha512", digest) }

    if modulus:
        multipart_form_data['modulus'] = pack_binary_form_data("modulus",
                                                               modulus)

    params = {}

    if sign_key:
        params['key'] = sign_key

    if algo_name:
        params['algo'] = algo_name

    response = requests.post(url_str,
                             files=multipart_form_data,
                             params=params,
                             verify=tls_verify)
    return content(response)


def get_key(server, tls_verify, key_label, group=0, oformat=None):
    ''' retrieve key from server in specified oformat '''
    url_str = "https://" + server + ":4443/cgi-bin/signing_server.cgi"

    params = { 'cmd' : 'modulus', 'key' : key_label, 'production' : group }
    if oformat:
        params['format'] = oformat

    response = requests.get(url_str, params=params, verify=tls_verify)

    return content(response)


def get_customer_cert(server, tls_verify, key_label):
    ''' retrieve customer certificate '''
    url_str = "https://" + server + ":4443/" + key_label + "_certificate.bin"

    response = requests.get(url_str, verify=tls_verify)

    return content(response)


def get_debugging_cert(server, client_cert, public_key_file,
                       tls_verify, hex_serial_nr):
    ''' retrieve new debugging certificate '''
    url_str = "https://" + server + ":4443/cgi-bin/signing_server.cgi"

    params = { 'serial_number' : hex_serial_nr }

    pem_key = open(public_key_file, 'rb').read()
    multipart_form_data = { 'key' : pack_binary_form_data(public_key_file,
                                                          pem_key) }
    response = requests.post(url_str,
                             cert=client_cert,
                             files=multipart_form_data,
                             params=params,
                             verify=tls_verify)
    return content(response)

####### tests

def check_value(msg, read_bytes, expected_bytes):
    ''' compare bytes strings '''
    if read_bytes != expected_bytes:
        print(msg)
        print("Expected %s" % expected_bytes)
        print("Got      %s" % read_bytes)
        return 1
    return 0


def test_get_binary_fpk2(server, tls_verify, exp_fpk2_modulus):
    ''' retrieve the fpk2 modulus as bytes '''
    fpk2_modulus = get_key(server, tls_verify, 'fpk2')
    return check_value("FPK2 modulus bytes", fpk2_modulus, exp_fpk2_modulus)


def test_get_customer_cert(server, tls_verify):
    ''' test customer certificate retrieval matches value in repository '''
    customer_cert = get_customer_cert(server, tls_verify, "development/s2/cpk1")

    customer_cert_exp = open('../development_keys_certs/cpk1_certificate.bin',
                             'rb').read()

    return check_value("Customer Certificate", customer_cert, customer_cert_exp)

def test_fpk4_binary_path(server, tls_verify, fpk4):
    ''' retrieve the modulus of fpk4 and verify it matches the value in PEM
    This detects a regression that broke the signing server on April 2024 '''

    fpk4_modulus = get_key(server, tls_verify, 'fpk4')
    exp_fpk4_modulus = pub_key_modulus_bytes(fpk4)
    return check_value("FPK4 modulus bytes", fpk4_modulus, exp_fpk4_modulus)


def test_fpk4_signing(server, tls_verify, fpk4):
    ''' execute the sign_test command on the server (signing 64 0x00 digest)'''

    url_str = "https://" + server + ":4443/cgi-bin/signing_server.cgi"
    params={'cmd': 'sign_test'}

    response = requests.get(url_str,
                            params=params,
                            verify=tls_verify)
    signature = content(response)

    try:
        fpk4.verify(signature,
                    b'\x00' * 64,
                    padding.PKCS1v15(),
                    utils.Prehashed(hashes.SHA512()))
    except exceptions.InvalidSignature:
        print("%d: Error: Invalid signature for FPK4 signing test")
        return 1

    return 0


def test_hash_sign_ex(fpk2, fpk2_modulus, server, tls_verify, algo_name):
    ''' signature generation/verification test using the fpk2 key '''
    tbs = b'Between silk and cyanide'

    digest = hashlib.new(algo_name, tbs).digest()

    err = 0
    # test 1: sign with key name
    server_signature1 = hash_sign(server, tls_verify, digest,
                                  algo_name=algo_name, sign_key='fpk2')

    # test 2 : sign with modulus
    server_signature2 = hash_sign(server, tls_verify, digest,
                                  algo_name=algo_name, modulus=fpk2_modulus)

    # PKCS: same signature
    if server_signature1 != server_signature2:
        print("Hash sign mismatch {2}:\n{0}\n{1}".
              format(binascii.b2a_hex(server_signature1),
                     binascii.b2a_hex(server_signature2),
                     algo_name))
        err += 1

    # verify it
    try:
        fpk2.verify(server_signature1, tbs, padding.PKCS1v15(),
                    HASH_ALGO_MAPPING[algo_name]())

    except exceptions.InvalidSignature:
        print("%d: Error: Invalid signature for algo %s" %  algo_name)
        err += 1

    return err


def test_get_debugging_cert(fpk2_pub, server, client_certificate,
                            public_key_file, tls_verify):
    ''' generate/get a debugging certificate '''
    if not client_certificate:
        print("client authentication certificate required: debugging certificate test omitted")
        return 0

    if not public_key_file:
        print("public key file required: debugging certificate test omitted")
        return 0

    errs = 0

    # test serial nr: all zeroes
    hex_serial_nr = b"00" * 8 + b"00" * 6 + b"0000" + b"00" * 8

    debugging_cert = get_debugging_cert(server, client_certificate,
                                        public_key_file, tls_verify,
                                        hex_serial_nr)
    errs += check_value("debug cert [0:4]",
                        debugging_cert[0:4],
                        b'\xA5\x5E\x00\xB1')
    errs += check_value("debug cert [4:16]",
                        debugging_cert[4:8],
                        b'\xFF' * 4 + b'\x00' * 4 + b'\xFF' * 4)
    errs += check_value("debug cert [16:40]",
                        debugging_cert[16:40],
                        binascii.a2b_hex(hex_serial_nr))
    errs += check_value("debug cert [40:64]",
                        debugging_cert[40:64],
                        b'\xFF' * 24)

    cert_pub_key = debugging_cert[64:580]
    cert_n_len = int.from_bytes(cert_pub_key[0:4], byteorder='little')
    cert_modulus = cert_pub_key[4:4+cert_n_len]

    # check pub key matches
    with open(public_key_file, 'rb') as fd:
        pub_key = serialization.load_pem_public_key(fd.read())

    modulus = pub_key_modulus_bytes(pub_key)
    errs += check_value(cert_modulus, modulus)

    signature_fld = debugging_cert[580:]
    signature_len = int.from_bytes(signature_fld[0:4], byteorder='little')
    signature = signature_fld[4:4+signature_len]

    try:
        fpk2_pub.verify(signature, debugging_cert[:580],
                        padding.PKCS1v15(), hashes.SHA512())
    except Exception as ex:
        print("Debugging Certificate verification failed: %s" % ex)
        errs += 1

    return errs


def main_program():
    ''' main test program '''
    errors = 0

    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--server", dest="server",
                        default="f1reg.fungible.com",
                        help="Ip address or DNS name of server to test")

    parser.add_argument("-c", "--certificate",
                        help="Mutual authentication certificate and key")
    parser.add_argument("-p", "--public-key-file",
                        help="Path to PEM public key file")

    options = parser.parse_args()

    tls_verify = options.server.endswith(".fungible.com")

    if not tls_verify:
        urllib3.disable_warnings()

    fpk2_data = open('../development_keys_certs/fpk2.pem', 'rb').read()
    fpk2_priv = serialization.load_pem_private_key(fpk2_data, password=None)
    fpk2 = fpk2_priv.public_key()
    fpk2_modulus = pub_key_modulus_bytes(fpk2)

    try:

        # get fpk4 (ESRP key)
        fpk4_pem = get_key(options.server, tls_verify,
                           'fpk4', oformat='public_key')
        fpk4 = serialization.load_pem_public_key(fpk4_pem)
        if not isinstance(fpk4, rsa.RSAPublicKey):
            raise RuntimeError("fpk4 retrieved not an RSA key")

        errors += test_fpk4_binary_path(options.server, tls_verify, fpk4)
        errors += test_fpk4_signing(options.server, tls_verify, fpk4)

        errors += test_get_binary_fpk2(options.server, tls_verify, fpk2_modulus)
        errors += test_get_customer_cert(options.server, tls_verify)
        for hash_algo in ("sha224", "sha256", "sha384", "sha512"):
            errors += test_hash_sign_ex(fpk2,
                                        fpk2_modulus,
                                        options.server,
                                        tls_verify,
                                        hash_algo)
        errors += test_get_debugging_cert(fpk2,
                                          options.server,
                                          options.certificate,
                                          options.public_key_file,
                                          tls_verify)

    except Exception as ex:
        print("Exception occurred: %s" % str(ex))
        traceback.print_exc()
        errors += 1

    print("Test completed on server %s with %d errors" % (options.server, errors))


if __name__=="__main__":
    main_program()
