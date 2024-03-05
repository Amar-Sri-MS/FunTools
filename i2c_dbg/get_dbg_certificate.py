#!/usr/bin/env python3
#
# Copyright (c) 2024. Microsoft Corporation,inc.
# All Rights Reserved.
#
#
# pylint: disable=consider-using-f-string


r'''
get_dbg_certificate:

generates or retrieve a debugging certificate for the specified serial number.

The debugging certificate can always be retrieved --if it exists -- using only
the serial number. If it does not exist, then it will be generated if and only
if the following additional information is provided:

1-an RSA key (PEM file format)
2-a client authentication X.509 certificate accepted by the server
3-the RSA private key for the certificate above

Once a debugging certificate is generated for a serial number, it will always
be the one returned even if a public key and X.509 authentication material
are presented.

The certificate is written to a file name "dbg_cert_<serial_number>.bin"

Examples:

python3 get_dbg_certificate.py --sn '00:00:00:....:63:'

(Retrieve the debugging certificate for the serial number)

python3 get_dbg_certificate.py -s '00:00:00:....:63:' -d rsapub.pem \
-c mycert.pem -k mykey.pem

(Retrieve and possibly generate the debugging certificate for the serial number)

'''

import sys
import argparse
import requests
import string
from asn1crypto import pem, keys


PROD_SERVER = "f1reg.fungible.com"
SERVER = PROD_SERVER
#SERVER = "sjc-f1regdev-01.fungible.local"

def pack_binary_form_data(title, bin_data):
    ''' utility to pack binary data in POST form '''
    return (title, bin_data, 'application/octet-stream',
                {"Content-Length" : str(len(bin_data)) })


def content(response):
    ''' return response content '''
    if response.status_code != requests.codes.ok:
        print("Request error: {0}".format(response.content))
    # always return the response content
    return response.content


def get_public_key_pem(key_file):
    ''' return PEM public key contents from file '''
    with open(key_file, 'rb') as fp:
        contents = fp.read()

    if pem.detect(contents):
        obj_name, _, der_bytes = pem.unarmor(contents)
        if 'PUBLIC KEY' in obj_name:
            return contents

        if obj_name == 'RSA PRIVATE KEY':
            private_key =  keys.RSAPrivateKey.load(der_bytes)
            public_key = keys.RSAPublicKey()
            public_key['modulus'] = private_key['modulus']
            public_key['public_exponent'] = private_key['public_exponent']
            contents = pem.armor('RSA PUBLIC KEY',
                                public_key.dump())
            return contents

    raise RuntimeError("%s: not a valid PEM file" % key_file)


def get_generate_certificate(args):
    ''' contact the signing server to get or generate a certificate '''
    post_args= {}

    # add debugging key if provided
    if args.debug_key:
        pub_pem_content = get_public_key_pem(args.debug_key)
        post_args['files'] = {'key' : pack_binary_form_data("pubkey.pem",
                                                            pub_pem_content) }

    # add TLS mutual aut
    if args.cert and args.key:
        post_args['cert'] = (args.cert, args.key)

    # TLS verify (allow testing with other server)
    post_args['verify'] = SERVER==PROD_SERVER

    post_args['params'] = { 'serial_number' : args.sn }

    url = "https://" + SERVER + ":4443/cgi-bin/signing_server.cgi"
    response = requests.post(url, **post_args)

    return content(response)


def main():
    ''' main entry point to the script '''
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=sys.modules['__main__'].__doc__)

    parser.add_argument("-s", "--sn", metavar="HEXADECIMAL_STRING",
                        required=True,
                        help= "Full 24 byte Serial Number of the chip in "\
                        "hex format;bytes or byte groups can be separated "\
                        "by a delimiter character (':', ''', '_', '-')")

    parser.add_argument("-d", "--debug-key", metavar="RSA_KEY_PEM_FILE",
                        help="RSA Key file in PEM format; only the public part "\
                        "will be sent to the signing server")

    parser.add_argument("-c", "--cert",
                        metavar="X.509_CERTIFICATE_PEM_FILE",
                        help="X.509 certificate with your identity")

    parser.add_argument("-k", "--key",
                        metavar="PRIVATE_KEY_PEM_FILE",
                        help="Private key for your identity")

    args = parser.parse_args()

    args.sn = ''.join(c for c in args.sn if c in string.hexdigits)
    debug_cert = get_generate_certificate(args)

    with open("dbg_cert_%s.bin" % args.sn, 'wb') as fp:
        fp.write(debug_cert)


if __name__ == "__main__":
    main()
