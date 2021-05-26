########################################################
#
# test_prod_signing_server.py
#
# Copyright (c) Fungible,inc. 2021
#
# This is a test of the production signing server API
#
# As the real production signing server is protected
# this test should be run on a local clone -- which of
# course does not have the real keys.
#
########################################################

import os
import binascii
import hashlib
import argparse
import requests
import traceback


from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


from cryptography import exceptions
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


HASH_ALGO_MAPPING = { 'sha1' : hashes.SHA1,
                      'sha224' : hashes.SHA224,
                      'sha256' : hashes.SHA256,
                      'sha384' : hashes.SHA384,
                      'sha512' : hashes.SHA512 }


def pack_binary_form_data(title, bin_data):

    return (title, bin_data, 'application/octet-stream',
                {"Content-Length" : str(len(bin_data)) })


def create_binary_form_data(infile):

    with open(infile, 'rb') as input:
        bin_data = input.read()
        return pack_binary_form_data(infile, bin_data)


def content(response):
    if response.status_code != requests.codes.ok:
        print("Request error: {0}".format(response.content))
    # always return the response content
    return response.content



def hash_sign(server, tls_verify, digest, auth_token,
              sign_key=None, modulus=None, algo_name=None):

    url_str = "https://" + server + ":4443/cgi-bin/signing_server.cgi"

    multipart_form_data = { 'digest' : pack_binary_form_data("sha512", digest),
                            'auth_token' : pack_binary_form_data("auth", auth_token) }

    if modulus:
        multipart_form_data['modulus'] = pack_binary_form_data("modulus", modulus)

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


def get_key(server, tls_verify, key_label):

    url_str = "https://" + server + ":4443/cgi-bin/signing_server.cgi"

    params = { 'cmd' : 'modulus', 'key' : key_label, 'production' : 1 }

    response = requests.get(url_str, params=params, verify=tls_verify)

    return content(response)


####### tests

def test_hash_sign_ex(key_label, server, tls_verify, algo_name, auth_token):

    tbs = b'Between silk and cyanide'

    digest = hashlib.new(algo_name, tbs).digest()

    # get the modulus
    modulus = get_key(server, tls_verify, key_label)

    # generate the public key
    key = rsa.RSAPublicNumbers(0x010001,
                               int.from_bytes(modulus, byteorder='big')
                               ).public_key()

    err = 0
    # test 1: sign with key name
    server_signature1 = hash_sign(server, tls_verify, digest, auth_token,
                                  algo_name=algo_name, sign_key=key_label)

    # test 2 : sign with modulus
    server_signature2 = hash_sign(server, tls_verify, digest, auth_token,
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
        key.verify(server_signature1, tbs, padding.PKCS1v15(),
                    HASH_ALGO_MAPPING[algo_name]())

    except exceptions.InvalidSignature:
        print("%d: Error: Invalid signature for algo %s" %  algo_name)
        err += 1

    return err


def main_program():
    errors = 0

    parser = argparse.ArgumentParser()

    parser.add_argument("-k", "--key", dest="key_label",
                        default="hkey1",
                        help="Name of HSM key to use for signing test")
    parser.add_argument("-s", "--server", dest="server",
                        required=True,
                        help="Ip address or DNS name of server to test")
    parser.add_argument("-t", "--token-file", dest="auth_token_file",
                        default=os.environ.get('FUN_HSM_TOKEN'),
                        help="Auth token file if not specified via environment FUN_HSM_TOKEN")

    options = parser.parse_args()

    if options.auth_token_file is None:
        print("No auth token file specified. Terminating.")

    with open(options.auth_token_file, "r") as fp:
        auth_token = fp.read()

    try:
        for hash_algo in ("sha1", "sha224", "sha256", "sha384", "sha512"):
            errors += test_hash_sign_ex(options.key_label, options.server,
                                        False, hash_algo, auth_token)

    except Exception as ex:
        print("Exception occurred %s" % str(ex))
        traceback.print_tb(ex.__traceback__)
        errors += 1

    print("Test completed on server %s with %d errors" % (options.server, errors))


if __name__=="__main__":
    main_program()
