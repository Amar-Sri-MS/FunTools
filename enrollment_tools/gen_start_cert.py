#!/usr/bin/env python3
# HSM Key management for SBP
# Copyright (c) 2018-2020 Fungible,inc. All Rights reserved.
#
# Implements the following commands:
#
# list: list all RSA keys in the HSM for the token
# modulus: export the modulus of a RSA key, in binary or in C source code format
# certificate: generate a certificate
# remove: remove the key from the HSM
# pem2c: convert a PEM file into C format


import os
import struct
import binascii
import argparse
import sys
import getpass
import json
import string

from asn1crypto import pem, keys

import pkcs11
import pkcs11.util.rsa
import pkcs11.util.ec

MAX_SIGNATURE_SIZE = 512
SIGNED_ATTRIBUTES_SIZE = 32
SIGNED_DESCRIPTION_SIZE = 32
SERIAL_INFO_NUMBER_SIZE = 24
CERT_PUB_KEY_POS = 64
MAX_KEYS_IN_KEYBAG = 96

MAGIC_NUMBER_CERTIFICATE = 0xB1005EA5
MAGIC_NUMBER_ENROLL_CERT = 0xB1005C1E


def get_from_user(prompt):
    ''' a slighty fancier to get the user to enter data '''
    while True:
        res = input(prompt)
        ok = input("You entered '{0}'\nIs this correct? (Y/n) ".format(res))
        if ok in ['', 'Y', 'y']:
            break

    return res


##############################################################################
# File access -- utils.py ported to Python 3
##############################################################################

def read(filename, nbytes=None, verbose=False):
    if filename is None:
        return ""
    if verbose:
        print("Reading %s" % filename)
    try:
        if filename == '-':
            txt = sys.stdin.buffer.read()
        else:
            txt = open(filename, "rb").read()
    except:
        raise Exception("Cannot open file '%s' for read" % filename)
    if nbytes and len(txt) != nbytes:
        raise Exception("File '%s' has invalid length. Expected %d, got %d"
                        % (filename, nbytes, len(txt)))
    return txt

def write(filename, content, overwrite=True, tohex=False, tobyte=False,
          verbose=False):
    if not filename:
        filename = '-'
    if verbose:
        print("Writing %s" % filename)
    # Overwrite
    if not overwrite and os.path.exists(filename):
        raise Exception("File '%s' already exists" % filename)
    # Open
    try:
        if filename == '-':
            f = sys.stdout.buffer
        else:
            f = open(filename, "wb")
    except:
        raise Exception("Cannot open file '%s' for write" % filename)
    # Write
    if tohex:
        assert len(content)%4 == 0
        for pos in range(0, len(content), 4):
            f.write("%08X\n" % struct.unpack("<I", content[pos:pos+4]))
    elif tobyte:
        for pos in range(0, len(content)):
            f.write("%s\n" % binascii.hexlify(content[pos]))
    else:
        f.write(content)

##############################################################################
# HSM

# libraries in order of preference -- second argument: prompt for password
LIBSOFTHSM2_PATHS = [
    ("/usr/safenet/lunaclient/lib/libCryptoki2_64.so", True), # Safenet ubuntu 14/16
    ("/usr/lib/softhsm/libsofthsm2.so", True), # Ubuntu-17, 18
    ("/usr/lib/x86_64-linux-gnu/softhsm/libsofthsm2.so", True), # Ubuntu-16
    ("/usr/local/lib/softhsm/libsofthsm2.so", True), # macOS brew
    ("/project/tools/softhsm-2.3.0/lib/softhsm/libsofthsm2.so", True), # shared vnc machines for verification team
]

def get_token_label():
    return get_from_user("Token Label = ")

def get_pkcs11_lib():

    lib = None
    prompt = False

    for entry in LIBSOFTHSM2_PATHS:
        if os.path.exists(entry[0]):
            try:
                lib = pkcs11.lib(entry[0])
            except:
                pass

            if lib is not None:
                prompt = entry[1]
                break

    if lib is None:
        raise RuntimeError("Could not find PKCS#11 library")

    return lib, prompt


def get_token():
    lib, prompt = get_pkcs11_lib()

    if prompt:
        token_label = get_token_label()
        password = getpass.getpass()
    else:
        token_label = 'fungible'
        password = 'fungible'

    # look into the slots with token
    # the old lib.get_token does not work well with Safenet PKCS#11
    for slot in lib.get_slots(True):
        token = slot.get_token()
        if token.label == token_label:
            return token, password
    return None, ''

class HSM:

    __session = None

    def __init__(self):
        pass

    def __del__(self):
        pass

    def __getattr__(self, name):
        if name == 'session':
            if not HSM.__session:
                token, password = get_token()
                # Open a session on our token -- use rw (singleton used all overwrite)
                HSM.__session = token.open(user_pin=password, rw=True)

            return HSM.__session
        return None


def get_private_key_with_label(ro_session, label):
    return ro_session.get_key(
        object_class=pkcs11.constants.ObjectClass.PRIVATE_KEY,
        label=label)


def get_public_key_with_label(ro_session, label):
    ''' Returns public key '''
    return ro_session.get_key(
        object_class=pkcs11.constants.ObjectClass.PUBLIC_KEY,
        label=label)

## RSA

def get_modulus(pub):
    return pub[pkcs11.Attribute.MODULUS]

def get_exponent(pub):
    return pub[pkcs11.Attribute.PUBLIC_EXPONENT]


def generate_rsa_key_pair(rw_session, label, key_size_in_bits):
    ''' Create and returns a new RSA key pair in the store '''
    return rw_session.generate_keypair(key_type=pkcs11.KeyType.RSA,
                                       key_length=key_size_in_bits,
                                       id=binascii.hexlify(label.encode()),
                                       label=label,
                                       store=True)

def get_create_rsa(label, key_size_in_bits):
    public = None

    hsm = HSM()
    try:
        public = get_public_key_with_label(hsm.session, label)
    except Exception as err:
        print(err)

    if public is None:
        print("Generating key " + label)
        public, _ = generate_rsa_key_pair(hsm.session, label, key_size_in_bits)

    return public


def get_all_rsa_keys(session):
    all_rsa_pubs = list(session.get_objects(
        {pkcs11.Attribute.CLASS: pkcs11.ObjectClass.PUBLIC_KEY,
         pkcs11.Attribute.KEY_TYPE: pkcs11.KeyType.RSA}))

    return all_rsa_pubs


def sign_with_key(label, data):

    hsm = HSM()
    try:
        private = get_private_key_with_label(hsm.session, label)
    except Exception as err:
        print(err)
        print("Keys can be created  with the 'modulus' command")
        raise

    key_type = private[pkcs11.Attribute.KEY_TYPE]
    if key_type == pkcs11.KeyType.RSA:
        mechanism = pkcs11.Mechanism.SHA512_RSA_PKCS
    elif key_type == pkcs11.KeyType.EC:
        #most HSMs do not support ECDSA_SHAxyz
        data = hsm.session.digest(data, mechanism=pkcs11.Mechanism.SHA256)
        mechanism = pkcs11.Mechanism.ECDSA
    else:
        raise ValueError("Unsupported key type")

    return private.sign(data, mechanism=mechanism)

def append_signature_to_binary(binary, signature):
    binary += struct.pack('<I', len(signature))
    binary += signature
    # pad to MAX_SIGNATURE_SIZE with 0
    binary += b'\x00' * (MAX_SIGNATURE_SIZE - len(signature))
    return binary

def append_modulus_to_binary(binary, modulus):
    # same structure as signature and MAX_SIGNATURE_SIZE == MAX_MODULUS_SIZE
    return append_signature_to_binary(binary, modulus)


##############################################################################
# ASN1crypto

def get_modulus_from_public_key_bytes(pub_info_der):
    ''' extract the modulus from the ASN.1 structure '''
    pub_key_info = keys.PublicKeyInfo.load(pub_info_der)

    if pub_key_info.algorithm != 'rsa':
        raise Exception("Not an RSA key")

    rsa_pub_key = pub_key_info['public_key'].parsed
    modulus_integer = rsa_pub_key['modulus']
    raw_modulus = modulus_integer.contents
    # the raw modulus might have an extra 0 (ASN.1 integer encoding)
    if raw_modulus[0] == 0:
        return raw_modulus[1:]
    return raw_modulus

def encode_public_key(pub_key):
    ''' generate a public key '''
    modulus = get_modulus(pub_key)
    pub_exp = get_exponent(pub_key)
    rsa_pub_key = keys.RSAPublicKey()
    rsa_pub_key['modulus'] = int.from_bytes(modulus, byteorder='big')
    rsa_pub_key['public_exponent'] = int.from_bytes(pub_exp, byteorder='big')

    public_key_algo = keys.PublicKeyAlgorithm()
    public_key_algo['algorithm'] = 'rsa'

    public_key_info = keys.PublicKeyInfo()
    public_key_info['algorithm'] = public_key_algo
    public_key_info['public_key'] = rsa_pub_key

    return public_key_info.dump()


##############################################################################
# Commands

def list_all_keys():
    ''' list all the keys in the session '''
    hsm = HSM()

    for rsa_key in get_all_rsa_keys(hsm.session):
        print(rsa_key)


def remove_key_aux(session, label):
    ''' delete key from the HSM using session'''
    try:
        private = get_private_key_with_label(session, label)
        if private:
            private.destroy()
    except:
        pass

    try:
        public = get_public_key_with_label(session, label)
        if public:
            public.destroy()
    except:
        pass


def remove_key(label):
    ''' delete that key from the HSM '''
    hsm = HSM()
    remove_key_aux(hsm.session, label)


def export_pub_key(outfile, label, key_size_in_bits):
    ''' export a PEM file with key; create it if it does not exists '''
    pub = get_create_rsa(label, key_size_in_bits)

    # export as PEM file: the PKCS11 library exports as RSA PUBLIC KEY
    # using the PUBLIC KEY format makes the file more useful
    der_bytes = encode_public_key(pub)
    pem_content = pem.armor('PUBLIC KEY', der_bytes)

    write(outfile, pem_content)


def sign_binary(binary, sign_key):
    ''' sign a binary and appends the signature to it '''
    signature = sign_with_key(sign_key, binary)
    return append_signature_to_binary(binary, signature)


def read_public_key_file(pub_key_file):
    # READ modulus from file
    contents = read(pub_key_file)
    # if PEM file, decode it
    if pem.detect(contents):
        obj_name, _, der_bytes = pem.unarmor(contents)
        if obj_name == 'RSA PRIVATE KEY':
            cert_rsa_key = pkcs11.util.rsa.decode_rsa_private_key(der_bytes)
            modulus = get_modulus(cert_rsa_key)
        elif obj_name == 'RSA PUBLIC KEY':
            cert_rsa_key = pkcs11.util.rsa.decode_rsa_public_key(der_bytes)
            modulus = get_modulus(cert_rsa_key)
        elif obj_name == 'PUBLIC KEY':
            modulus = get_modulus_from_public_key_bytes(der_bytes)
        else:
            raise RuntimeError("Cannot use PEM file with '%s' as modulus source" %
                               obj_name)
    elif all(chr(c) in string.hexdigits for c in contents.strip()):
        modulus = binascii.a2b_hex(contents.strip())
    else:
        raise RuntimeError("Not a valid PEM file: %s" % pub_key_file)

    return modulus


def pem_to_c(pub_key_file, outfile):

    modulus = read_public_key_file(pub_key_file)
    len_modulus = len(modulus)

    c_modulus = "%d,\n{\n" % len_modulus

    for pos in range(0, len_modulus):
        c_modulus += "0x%02x, " % modulus[pos]
        if pos % 8 == 7:
            c_modulus += "\n"
    if len_modulus % 8 != 0:
        c_modulus += "\n"
    c_modulus += "}"
    write(outfile, c_modulus.encode())



def cert_gen(outfile, sign_key, pub_key_file,
             serial_number, serial_number_mask, debugger_flags):

    # MAGIC NUMBER, DEBUG FLAGS, 0, TAMPER FLAGS=0
    dflags = int(debugger_flags, 0)
    to_be_signed = struct.pack('<4I', MAGIC_NUMBER_CERTIFICATE, dflags, 0, 0)

    # SERIAL NUMBER
    s_num = binascii.a2b_hex(serial_number)
    if len(s_num) != SERIAL_INFO_NUMBER_SIZE:
        raise ValueError("Serial Number length must be exactly " +
                         str(SERIAL_INFO_NUMBER_SIZE) + " bytes long")
    to_be_signed += s_num

    # SERIAL NUMBER MASK
    s_num_mask = binascii.a2b_hex(serial_number_mask)
    if len(s_num_mask) != SERIAL_INFO_NUMBER_SIZE:
        raise ValueError("Serial Number Mask length must be exactly " +
                         str(SERIAL_INFO_NUMBER_SIZE) + " bytes long")
    to_be_signed += s_num_mask

    # READ modulus from file
    modulus = read_public_key_file(pub_key_file)

    assert len(to_be_signed) == CERT_PUB_KEY_POS
    to_be_signed = append_modulus_to_binary(to_be_signed, modulus)

    # SIGNATURE
    if sign_key:
        cert = sign_binary(to_be_signed, sign_key)
    else:
        return to_be_signed

    write(outfile, cert)
    return None


def parse_and_execute():
    parser = argparse.ArgumentParser()

    parser.add_argument("command",
                        help="command to execute: list, remove, modulus, pem2c, certificate")

    parser.add_argument("-c", "--certificate-values-file", metavar="FILE",
                        help="file with the certificate values (certificate)")

    parser.add_argument("-k", "--key", dest="sign_key",
                        help="key name (remove, modulus, certificate)")

    parser.add_argument("-o", "--output", dest="out_path", metavar="FILE",
                        help="location to output to (modulus, pem2c, certificate)")

    parser.add_argument("-p", "--public-key-file", metavar="FILE",
                        help="public key file in PEM or binary format (pem2c, certificate)")

    parser.add_argument("-s", "--size_in_bits", dest="key_size_in_bits", default="4096",
                        help="key size in bits if key has to be created (modulus)")

    options = parser.parse_args()

    if options.command == 'pem2c':
        if options.public_key_file is None:
            err_msg += '\nPublic key file required for certificate command.'

        pem_to_c(options.public_key_file, options.out_path)
        sys.exit(0)

    elif options.command == 'list':

        list_all_keys()
        sys.exit(0)

    elif options.command == 'remove':

        if options.sign_key is None:
            parser.print_help()
            print('\nKey name required.')
            sys.exit(1)

        remove_key(options.sign_key)
        sys.exit(0)

    elif options.command == 'modulus':

        if options.sign_key is None:
            parser.print_help()
            print('\nKey name required.')
            sys.exit(1)

        export_pub_key(options.out_path,
                       options.sign_key,
                       int(options.key_size_in_bits, 0))
        sys.exit(0)

    elif options.command == 'certificate':

        err_msg = ''
        if options.sign_key is None:
            err_msg += '\nKey name required for certificate command.'
        if options.public_key_file is None:
            err_msg += '\nPublic key file required for certificate command.'
        if options.certificate_values_file is None:
            err_msg += '\nCertificate value file required for certificate  command.'

        if len(err_msg):
            parser.print_help()
            print(err_msg)
            sys.exit(1)

        # parse the value file
        with open(options.certificate_values_file, "r") as fp:
            values = json.load(fp)

        cert_gen(options.out_path, options.sign_key,
                 options.public_key_file, values["serial_number"],
                 values["serial_number_mask"], values["debugger_flags"])


if __name__ == "__main__":
    # Do important stuff that needs to be synchronized
    parse_and_execute()
