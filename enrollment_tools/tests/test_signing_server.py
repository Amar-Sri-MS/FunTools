########################################################
#
# test_signing_server.py
#
# Copyright (c) Fungible,inc. 2019
# Copyright (c) Microsoft Corporation. 2023
#
########################################################

import binascii
import hashlib
import argparse
import traceback
import requests


from cryptography import exceptions
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding


HASH_ALGO_MAPPING = { 'sha224' : hashes.SHA224,
                      'sha256' : hashes.SHA256,
                      'sha384' : hashes.SHA384,
                      'sha512' : hashes.SHA512 }

def pack_binary_form_data(title, bin_data):

    return (title, bin_data, 'application/octet-stream',
                {"Content-Length" : str(len(bin_data)) })


def create_binary_form_data(infile):

    with open(infile, 'rb') as finput:
        bin_data = finput.read()
        return pack_binary_form_data(infile, bin_data)


def content(response):
    if response.status_code != requests.codes.ok:
        print("Request error: {0}".format(response.content))
    # always return the response content
    return response.content



def hash_sign(server, tls_verify, digest,
              sign_key=None, modulus=None, algo_name=None):

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

    url_str = "https://" + server + ":4443/cgi-bin/signing_server.cgi"

    params = { 'cmd' : 'modulus', 'key' : key_label, 'production' : group }
    if format:
        params['format'] = oformat

    response = requests.get(url_str, params=params, verify=tls_verify)

    return content(response)


def get_customer_cert(server, tls_verify, key_label):

    url_str = "https://" + server + ":4443/" + key_label + "_certificate.bin"

    response = requests.get(url_str, verify=tls_verify)

    return content(response)


def get_debugging_cert(server, client_cert, public_key_file,
                       tls_verify, hex_serial_nr):

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

def test_get_binary_fpk2(server, tls_verify):
    fpk2 = get_key(server, tls_verify, 'fpk2')

    fpk2_text = open('./fpk2_hex.txt', 'r').read().rstrip()

    fpk2_exp = binascii.unhexlify(fpk2_text)

    if fpk2 == fpk2_exp:
        return 0

    return 1


def test_get_customer_cert(server, tls_verify):

    customer_cert = get_customer_cert(server, tls_verify, "development/s2/cpk1")

    customer_cert_exp = open('../development_keys_certs/cpk1_certificate.bin',
                             'rb').read()

    if customer_cert == customer_cert_exp:
        return 0

    return 1


def test_hash_sign_ex(fpk2, server, tls_verify, algo_name):

    tbs = b'Between silk and cyanide'

    digest = hashlib.new(algo_name, tbs).digest()

    modulus_int = fpk2.public_numbers().n
    modulus = modulus_int.to_bytes((modulus_int.bit_length()+7) // 8,
                                   byteorder='big')

    err = 0
    # test 1: sign with key name
    server_signature1 = hash_sign(server, tls_verify, digest,
                                  algo_name=algo_name, sign_key='fpk2')

    # test 2 : sign with modulus
    server_signature2 = hash_sign(server, tls_verify, digest,
                                  algo_name=algo_name, modulus=modulus)

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

def check_value(read_bytes, expected_bytes):
    ''' compare bytes string '''
    if read_bytes != expected_bytes:
        print("Expected %s" % expected_bytes)
        print("Got      %s" % read_bytes)
        return 1
    return 0


def test_get_debugging_cert(server, client_certificate,
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
    errs += check_value(debugging_cert[0:4],   b'\xA5\x5E\x00\xB1')
    errs += check_value(debugging_cert[4:8],   b'\xFF' * 4)
    errs += check_value(debugging_cert[8:12],  b'\x00' * 4)
    errs += check_value(debugging_cert[12:16], b'\xFF' * 4)
    errs += check_value(debugging_cert[16:40], binascii.a2b_hex(hex_serial_nr))
    errs += check_value(debugging_cert[40:64], b'\xFF' * 24)

    cert_pub_key = debugging_cert[64:580]
    cert_n_len = int.from_bytes(cert_pub_key[0:4], byteorder='little')
    cert_modulus = cert_pub_key[4:4+cert_n_len]

    # check pub key matches
    with open(public_key_file, 'rb') as fd:
        pub_key = serialization.load_pem_public_key(fd.read())
    n = pub_key.public_numbers().n
    modulus = n.to_bytes((n.bit_length() + 7) // 8)
    errs += check_value(cert_modulus, modulus)

    signature_fld = debugging_cert[580:]
    signature_len = int.from_bytes(signature_fld[0:4], byteorder='little')
    signature = signature_fld[4:4+signature_len]

    # get fpk2, group 0
    fpk2_1_pem = get_key(server, tls_verify, 'fpk2',
                     group=0, oformat='public_key')

    fpk2_1_pub = serialization.load_pem_public_key(fpk2_1_pem)
    try:
        fpk2_1_pub.verify(signature, debugging_cert[:580],
                          padding.PKCS1v15(), hashes.SHA512())
    except Exception as ex:
        print("Debugging Certificate verification failed: %s" % ex)
        errs += 1

    return errs


def main_program():
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

    modulus_hex = open('fpk2_hex.txt', 'r').read().rstrip()

    fpk2 = rsa.RSAPublicNumbers(0x010001,
                                int(modulus_hex, 16)).public_key()

    try:
        errors += test_get_binary_fpk2(options.server, tls_verify)
        errors += test_get_customer_cert(options.server, tls_verify)
        for hash_algo in ("sha224", "sha256", "sha384", "sha512"):
            errors += test_hash_sign_ex(fpk2,
                                        options.server,
                                        tls_verify,
                                        hash_algo)
        errors += test_get_debugging_cert(options.server,
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
