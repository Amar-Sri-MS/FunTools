#! /usr/bin/env python3
#
# wrap_tenant_key.py
#
# Copyright (c) 2023. Microsoft
# All Rights Reserved
#
'''
Script to help test the packaging a Master Tenant Key.

>>>> generate: generate a test vector.
  the test vector consists of a randomly generated AES 256 bit key to import
  and the resulting "package" to send to the DPU to import.  The code provides
  a functional description of the steps to package the key securely so that
  only SBP can see that key,

> Examples:

python3 wrap_tenant_key.py generate posix

python3 wrap_tenant_key.py generate 01010000190000000000000000000043

>>>> dpc: will import a key into the DPU using the DPC interface.
  an extension of "generate", it will send the generated package to the DPU
  for import using the test function in FunOS. FunOS will return the content
  of the wrapped key by SBP. Again, the code provides a functional
  description of the steps necessary to securely import a master key into a DPU.

> Examples:

python3 wrap_tenant_key.py dpc -p 40221  # POSIX

python3 wrap_tenant_key.py dcp            # FunOnDemand

>>>> verify: recover the key printed in the FunOS log when using the dpc command.
  if the DPU is using a debugging version of SBP that prints its encryption key
  in its log or the run was on Posix, this can be used to recover the key.


> Example:

A DPC run returned the following:

Serial Number = 000000000000000001010000190000000000000000000044

const uint8_t Generated key[32] = {
0xa1, 0x60, 0xf5, 0x10, 0xb1, 0x02, 0x5b, 0xc3, 0x8e, 0x77,
0xe2, 0xec, 0x04, 0x26, 0xd2, 0xde, 0x54, 0x06, 0x03, 0x48,
0xa5, 0xf4, 0x7e, 0x78, 0xe9, 0xdb, 0xde, 0xcf, 0x9b, 0xf9,
0x83, 0x6c,
};
Imported key: 137D2485E7CFE5B61A26BDE6EAA89D7053AB291749D638A12F341BFB60C743C187B8C9EAAD1FE01211AEE74B0D1C4995D0A72362071EF85EE6345110

The SBP log (special version of SBP firmware) show the line:

m_sec_kek_blk@(0x1002D464 | 32 | incremental) 3046EC8757DEDE4AEF46837C9066E8B487970C8D494A4330E796CB4D5F4D4F6A

(This line will appear in the FunOS log on Posix)

python3 wrap_tenant_key.py verify -k \
 3046EC8757DEDE4AEF46837C9066E8B487970C8D494A4330E796CB4D5F4D4F6A\
 137D2485E7CFE5B61A26BDE6EAA89D7053AB291749D638A12F341BFB60C743C187B8C9EAAD1FE01211AEE74B0D1C4995D0A72362071EF85EE6345110

outputs:

const uint8_t recovered_key[32] = {
0xa1, 0x60, 0xf5, 0x10, 0xb1, 0x02, 0x5b, 0xc3, 0x8e, 0x77,
0xe2, 0xec, 0x04, 0x26, 0xd2, 0xde, 0x54, 0x06, 0x03, 0x48,
0xa5, 0xf4, 0x7e, 0x78, 0xe9, 0xdb, 0xde, 0xcf, 0x9b, 0xf9,
0x83, 0x6c,
};


'''

import os
import sys
import time
import binascii
import argparse
import json
from pathlib import Path

import requests

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash




VERBOSE=0

def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')

def bytes_to_int(b):
    return int.from_bytes(b, byteorder='big')


def print_c_bytes(barr, var_name):
    print("\nconst uint8_t %s[%d] = {" % (var_name, len(barr)))
    i = 0
    for b in barr:
        print("0x%02x, " % b, end='')
        i = i + 1
        if i == 10:
            print()
            i = 0

    print("\n};")



## Crypto Routines

def make_ec_key(x, y, curve):
    pt = ec.EllipticCurvePublicNumbers(x, y, curve)
    return pt.public_key(default_backend())


def generate_shared_secret(curve, peer_x, peer_y):

    peer_key = make_ec_key(bytes_to_int(peer_x), bytes_to_int(peer_y), curve)
    # Generate a private key for use in the exchange.
    eph_key = ec.generate_private_key(curve, default_backend())

    eph_x_y = eph_key.public_key().public_numbers()
    x_bin = int_to_bytes(eph_x_y.x)
    y_bin = int_to_bytes(eph_x_y.y)

    shared_key = eph_key.exchange(ec.ECDH(), peer_key)

    if VERBOSE:
        print_c_bytes(shared_key, "shared_secret")

    return x_bin, y_bin, shared_key


def wrap_with_kdf(shared_secret, plain_text):

    AES_256_LEN = 32

    ckdf = ConcatKDFHash(algorithm=hashes.SHA256(),
                length=AES_256_LEN + 4,  # AES Key + Implicit IV
                otherinfo=None,
                backend=default_backend())

    key_material = ckdf.derive(shared_secret)

    # AES 256 key
    aes_key = key_material[0:AES_256_LEN]
    # GMC IV 12 bytes
    iv = key_material[AES_256_LEN:AES_256_LEN+4] + os.urandom(8)

    if VERBOSE:
        print_c_bytes(aes_key, "kek")
        print_c_bytes(iv, "IV")


    aesgcm = AESGCM(aes_key)

    wrapped = aesgcm.encrypt(iv, plain_text, None)

    return iv + wrapped


## Wrap Secret curve is either ec.SECP256R1() (testing on F1) or ec.SECP384R1() (F2)
def wrap_secret(curve, peer_x, peer_y, plain_text):

    x_bin, y_bin, shared_key = generate_shared_secret(curve, peer_x, peer_y)

    wrapped = wrap_with_kdf(shared_key, plain_text)

    return x_bin, y_bin, wrapped

def get_enroll_cert(chip_serial_nr):

    ''''retrieve the enrollment certificate for the serial nr
    serial nr should be an hexadecimal string like: 1236.
    code will left pad to 48 with zeroes
    '''

    padding_len = 48 - len(chip_serial_nr)
    chip_serial_nr = '0' * padding_len + chip_serial_nr

    response = requests.get(
        "https://f1reg.fungible.com/cgi-bin/enrollment_server.cgi",
        params={'cmd':'cert', 'sn': chip_serial_nr})

    return binascii.a2b_base64(response.text)



def wrap_key_for_import(aes_key, chip_serial_nr):

    P256_CERT_LEN = 1548
    P384_CERT_LEN = 1580
    KEY_OFFSET = 32 #offset of public key in certificate

    cert_bin = get_enroll_cert(chip_serial_nr)
    cert_bin_len = len(cert_bin)
    curve = None
    # based on its length, the key is either P256 or P384
    if cert_bin_len == P256_CERT_LEN:
        curve = ec.SECP256R1()
        key_size = 32
    elif cert_bin_len == P384_CERT_LEN:
        curve = ec.SECP384R1()
        key_size = 48
    else:
        raise RuntimeError("Invalid certificate length: %d" % cert_bin_len)

    chip_x = cert_bin[KEY_OFFSET:KEY_OFFSET+key_size]
    chip_y = cert_bin[KEY_OFFSET+key_size:KEY_OFFSET+ 2* key_size]
    return wrap_secret(curve, chip_x, chip_y, aes_key)


def generate_test_vector(aes_key, chip_serial_nr):

    if chip_serial_nr == 'posix':
        chip_serial_nr = '01010011172400000000000012345678'

    x,y,wrapped = wrap_key_for_import(aes_key, chip_serial_nr)
    return x,y,wrapped


##############################################
# Print Test Vector for serial nr
def print_test_vector(args):

    aes_key = os.urandom(32)

    x,y,wrapped = generate_test_vector(aes_key, args.serial_nr[0])
    # print in C format
    print_c_bytes(aes_key, "key")

    package = b''.join([x,y,wrapped])
    print_c_bytes(package, "packed")


##############################################
# Verification
def verify_wrapped_key(args):

    kek_bin = binascii.a2b_hex(args.kek)
    wrapped_bin = binascii.a2b_hex(args.wrapped[0])

    aesgcm = AESGCM(kek_bin)

    try:
        recovered_key = aesgcm.decrypt(wrapped_bin[:12], wrapped_bin[12:], None)
    except Exception as e:
        print("Key recovery failed: ", e)
        return

    print_c_bytes(recovered_key, "recovered_key")

##############################################
# DPC testing -- cf. cavp.py

def load_env_file(env_file):

    with open(env_file, 'r') as f:
        env_dict = json.load(f)

    print(json.dumps(env_dict, indent=4))

    dpc_host = env_dict['dpc_hosts'][0]
    return dpc_host['host'], dpc_host['tcp_port']


class DPCTester:
    ''' tester using DPC function '''

    def __init__(self, dpc_client, arg_dict):

        if arg_dict.get('dpc_port'):
            host = 'localhost'
            port = int(arg_dict['dpc_port'],0)
        elif arg_dict.get('env_file'):
            host,port = load_env_file(arg_dict['env_file'])
        else:
            host,port = load_env_file('./env.json')

        dpc = None

        print("Connecting to %s:%s" % (host, port))
        for _ in range(0, 100):
            try:
                dpc = dpc_client.DpcClient(server_address=(host, port))
                break
            except Exception as e:
                print('Still waiting for DPC proxy:', e)
                time.sleep(10)
        if not dpc:
            print('Problems setting up dpc connection.')
            raise RuntimeError('Could not connect to DPC proxy')
        self.dpc_client = dpc

    def get_serial_number(self):
        args = ['config/chip_info/chip_serial_number/raw_serial_number']
        serial_number = self.dpc_client.execute('peek', args)
        return serial_number

    def import_package(self, package):
        json_package = binascii.b2a_hex(package).decode('ascii')
        args = ['pketest_wrap_sec_key_test',
                {"package": json_package}]
        import_res = self.dpc_client.execute('execute', args)
        return import_res['wrapped_key']

    def run_test(self):
        serial_number = self.get_serial_number()
        print("Serial Number = %s" % serial_number)
        aes_key = os.urandom(32)
        print_c_bytes(aes_key, "Generated key")
        x,y,wrapped = wrap_key_for_import(aes_key, serial_number)
        package = b''.join([x,y,wrapped])
        imported_key = self.import_package(package)
        print("Imported key: %s" % imported_key)


def test_with_dpc(args):

    if "WORKSPACE" in os.environ:
        search_path = os.path.join(os.environ["WORKSPACE"], "FunSDK", "bin")
        dpc_client_paths = [os.path.dirname(p)
                            for p in Path(search_path).rglob("dpc_client.py")]
        if dpc_client_paths:
            sys.path.append(dpc_client_paths[0])
    try:
        import dpc_client
    except:
        print("No dpc_client module")
        return

    dpc_tester = DPCTester(dpc_client, vars(args))
    dpc_tester.run_test()



def parse_args():

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')

    # verify sub command
    parser_verify = subparsers.add_parser('verify', help="verify DEBUG output")
    parser_verify.add_argument('wrapped', metavar='WRAPPED_KEY', nargs=1,
                               help='wrapped key in hexadecimal')
    parser_verify.add_argument('-k', '--kek', required=True,
                               help="KEK to decrypt an encrypted key (POSIX)")
    parser_verify.set_defaults(func=verify_wrapped_key)

    # dpc sub command
    parser_dpc = subparsers.add_parser('dpc', help="generate and import a key using DPC")
    parser_dpc.add_argument('-k', '--kek',
                            help="KEK to verify the encrypted key (POSIX)")
    opt_grp = parser_dpc.add_mutually_exclusive_group()
    opt_grp.add_argument('-p', '--dpc-port',
                         help="Port returned by localhost dpcsh -T (POSIX)")
    opt_grp.add_argument('-e', '--env-file',
                         help="Alternative env file (default = ./env.json)")
    parser_dpc.set_defaults(func=test_with_dpc)

    # generate sub command
    parser_generate = subparsers.add_parser('generate', help="generate a test vector")
    parser_generate.add_argument('serial_nr', metavar='SERIAL_NUMBER', nargs=1,
                                 help='Serial Number of the chip')
    parser_generate.set_defaults(func=print_test_vector)

    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
