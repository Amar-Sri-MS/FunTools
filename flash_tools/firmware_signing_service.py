#!/usr/bin/env python3

'''
Copyright (c) 2017-2020 Fungible, inc.
All Rights Reserved.
'''

import os
import sys
import struct
import binascii
import hashlib

import requests


# image file format description
# https://docs.google.com/document/d/1wb34TuVJmPlikeVjvE0tdCQxP8ZgzLc0RSMbyd1prwM

RSA_KEY_SIZE_IN_BITS = 2048
SIGNING_INFO_SIZE = 2048
MAX_SIGNATURE_SIZE = 512
HEADER_RESERVED_SIZE = SIGNING_INFO_SIZE - (4 + MAX_SIGNATURE_SIZE)
SIGNED_ATTRIBUTES_CHIP_ID = 3
SIGNED_ATTRIBUTES_SIZE = 29 # currently undefined/unused
SIGNED_DESCRIPTION_SIZE = 32
SERIAL_INFO_NUMBER_SIZE = 24
CERT_PUB_KEY_POS = 64
MAX_KEYS_IN_KEYBAG = 96
SEC_GRP_POS = 14
SEC_GRP_SIZE = 2

MAGIC_NUMBER_CERTIFICATE = 0xB1005EA5
MAGIC_NUMBER_ENROLL_CERT = 0xB1005C1E

SIGNING_SERVER_URL = "https://f1reg.fungible.com:4443"
SIGNING_SERVICE_URL = SIGNING_SERVER_URL + "/cgi-bin/signing_server.cgi"
CERTIFICATE_SERVICE_URL = SIGNING_SERVER_URL + "/"
PRODUCTION_CERTIFICATE_SERVICE_URL = SIGNING_SERVER_URL + "/production/"

DEFAULT_HTTP_TIMEOUT = 180

# environment variable: if it is set and points to a file, it triggers the use
# of the production keys and certificates
HSM_AUTH_TOKEN_ENV_VAR = "FUN_HSM_TOKEN"

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
        return
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


#########################################################################
# Environment Variable -- lazy singleton

class SigningEnv:

    __auth_token = None
    __done = False

    def __init__(self):
        pass

    def __del__(self):
        pass


    def __lazy_init(self):
        if not SigningEnv.__done:
            auth_token_file_name = os.environ.get(HSM_AUTH_TOKEN_ENV_VAR)
            if auth_token_file_name:
                self.__read_auth_token(auth_token_file_name)
            else:
                print("<<<<<<< NO '%s' IN ENVIRONMENT ==> DEVELOPMENT BUILD >>>>>>>" %
                      HSM_AUTH_TOKEN_ENV_VAR,
                      file=sys.stderr)

            if SigningEnv.__auth_token:
                print("<<<<<< USING '%s' AS AUTH.TOKEN ==> PRODUCTION BUILD >>>>>>>" %
                      auth_token_file_name,
                      file=sys.stderr)
                print("<<<<<< AUTH.TOKEN = %s >>>>>>>" %
                      SigningEnv.__auth_token,
                      file=sys.stderr)
                SigningEnv.__done = True


    def __getattr__(self, name):
        if name == 'auth_token':
            self.__lazy_init()
            return SigningEnv.__auth_token

        return None


    def __read_auth_token(self, auth_token_file_name):
        try:
            with open(auth_token_file_name, "r") as fp:
                SigningEnv.__auth_token = fp.read()

        except OSError:
            print("<<<<<<< UNABLE TO OPEN '%s' ==> DEVELOPMENT BUILD >>>>>>>" %
                  auth_token_file_name,
                  file=sys.stderr)
        except Exception as ex:
            print("<<<<<<< EXCEPTION %s READING '%s' ==> DEVELOPMENT BUILD >>>>>>>" %
                  (ex, auth_token_file_name),
                  file=sys.stderr)

################################################################
# Base64 helpers for production server methods
def to_b64(some_bytes):
    return binascii.b2a_base64(some_bytes).rstrip().decode('utf-8')

def from_b64(b64):
    return binascii.a2b_base64(b64)

def get_result(reply):
    result = reply.get('result')
    if result is None:
        raise RuntimeError("No result from the server: %s" % reply)
    return result


#########################################################################
# Production server access

def production_get_cert(outfile, cert_key, cert_key_file, sign_key, serial_number,
                        serial_number_mask, debugger_flags):

    # There are several production security certificates, one for
    # each security group in the serial number. All these quantities are
    # passed as hex strings so double the coordinates 1 byte=2 hexadecimal chars
    security_group = serial_number[SEC_GRP_POS*2:
                                   (SEC_GRP_POS+SEC_GRP_SIZE)*2]

    response = requests.get(PRODUCTION_CERTIFICATE_SERVICE_URL + cert_key +
                            "_certificate_" + security_group + ".bin",
                            timeout=DEFAULT_HTTP_TIMEOUT)

    if response.status_code == requests.codes.ok:
        write(outfile, response.content)
    else:
        raise(Exception("Failed to obtain certificate for security group {}, key {}, err {}".
                        format(security_group, cert_key, response.status_code)))


#########################################################################
# Signing server access

def get_modulus(name):

    params = {
        'cmd' : 'modulus',
        'format' : 'binary',
        'key' : name
    }

    # if production, use typical URL with production=1
    if SigningEnv().auth_token:
        params['production'] = '1'

    response = requests.get(SIGNING_SERVICE_URL, params=params, timeout=DEFAULT_HTTP_TIMEOUT)
    return response.content

def pack_binary_form_data(title, bin_data):
    return (title, bin_data, 'application/octet-stream',
            {"Content-Length" : str(len(bin_data))})


def hash_sign(digest, sign_key=None, modulus=None):
    ''' send a POST sign request with digest '''

    auth_token = SigningEnv().auth_token

    multipart_form_data = {'digest' : pack_binary_form_data("sha512", digest)}

    if modulus:
        multipart_form_data['modulus'] = pack_binary_form_data("modulus", modulus)

    if auth_token:
        multipart_form_data['auth_token'] = pack_binary_form_data("auth", auth_token)


    params = {}
    if sign_key:
        params['key'] = sign_key

    response = requests.post(SIGNING_SERVICE_URL,
                             files=multipart_form_data,
                             params=params,
                             timeout=DEFAULT_HTTP_TIMEOUT)
    if response.status_code != requests.codes.ok:
        raise RuntimeError("Server responded with [{}]:\n{}\n".format(
            response.status_code, response.content).replace("\\n", "\n"))

    return response.content


def server_sign_with_key(label, data):
    ''' for speed, only pass the SHA512 hash of the data to the server to generate a signature '''
    digest = hashlib.sha512(data).digest()
    return hash_sign(digest, sign_key=label)


def server_sign_with_cert(cert, data):
    ''' when signing with certificate, the certificate is part of the digest '''
    m = hashlib.sha512()
    m.update(cert)
    m.update(data)
    digest = m.digest()
    modulus = get_cert_modulus(cert)
    return hash_sign(digest, modulus=modulus)


########################################################################
# File Format

def get_cert_modulus(cert):
    cert_key_modulus_len = struct.unpack('<I',
                                         cert[CERT_PUB_KEY_POS:CERT_PUB_KEY_POS+4])
    start = CERT_PUB_KEY_POS+4
    end = start + cert_key_modulus_len[0]
    return cert[start:end]


def append_signature_to_binary(binary, signature):
    binary += struct.pack('<I', len(signature))
    binary += signature
    # pad to MAX_SIGNATURE_SIZE with 0
    binary += b'\x00' * (MAX_SIGNATURE_SIZE - len(signature))
    return binary


def add_cert_and_signature_to_image(image, cert, signature):
    image += cert
    image += b'\x00' * (HEADER_RESERVED_SIZE - len(cert))
    return append_signature_to_binary(image, signature)

def image_gen(outfile, infile, ftype, version, description, sign_key,
              certfile, customer_certfile, key_index, chip_type=None, pad=1):
    ''' generate signed firmware image '''

    chip_type_map = {
        # chip name : [ family, device, revision ]
        # see https://docs.google.com/document/d/1qojY63VZvkhmbDenbl6J2j51yeA_9FfhU8s_aTUhvJs
        'f1'   : [1, 1, 0],
        's1'   : [2, 1, 0],
        'f1d1' : [1, 1, 1],
        's2'   : [2, 2, 0]
    }

    if ((pad == 0) or (pad is None)):
        pad = 1 # make the lazy thing work
    binary = read(infile)
    to_be_signed = struct.pack('<2I', len(binary), version)
    to_be_signed += struct.pack('4s', ftype.encode())
    if chip_type:
        to_be_signed += struct.pack('3B', *chip_type_map[chip_type])
    else:
        to_be_signed += b'\x00' * SIGNED_ATTRIBUTES_CHIP_ID
    to_be_signed += b'\x00' * SIGNED_ATTRIBUTES_SIZE
    if description:
        # Max allowed size is (block size - 1) to allow for terminating null
        if len(description) > SIGNED_DESCRIPTION_SIZE - 1:
            raise ValueError("Image description too long, max is {}".
                             format(SIGNED_DESCRIPTION_SIZE-1))
        to_be_signed += description.encode() + b'\x00' * (SIGNED_DESCRIPTION_SIZE -
                                                          len(description))
    else:
        to_be_signed += b'\x00' * SIGNED_DESCRIPTION_SIZE

    to_be_signed += binary

    signature = b''
    cert = b''
    # sign_key and cert_file are mutually exclusive
    if sign_key:
        if key_index is not None:
            if key_index < 0 or key_index >= MAX_KEYS_IN_KEYBAG:
                raise ValueError("Key Index should between 0 and {0}".
                                 format(MAX_KEYS_IN_KEYBAG))

            cert = struct.pack("<I", (key_index | 0x80000000))
        signature = server_sign_with_key(sign_key, to_be_signed)
    elif certfile:
        cert = read(certfile)
        signature = server_sign_with_cert(cert, to_be_signed)
    elif not customer_certfile:
        print("A certificate ( customer or fungible) or a label is needed "+
              "to identify the key used to sign a firmware image")
        print("Image will not be signed!")

    customer_to_be_signed = add_cert_and_signature_to_image(b'', cert, signature)
    customer_to_be_signed += to_be_signed

    if customer_certfile:
        customer_cert = read(customer_certfile)
        customer_signature = server_sign_with_cert(customer_cert,
                                                   customer_to_be_signed)
    else:
        customer_cert = b''
        customer_signature = b''

    image = add_cert_and_signature_to_image(b'', customer_cert,
                                            customer_signature)
    image += customer_to_be_signed

    # pad the image to the requested length
    n = len(image) % pad
    if n > 0:
        m = pad - n
        padbytes = b"\0" * m
        image += padbytes

    write(outfile, image)


def cert_gen(outfile, cert_key, cert_key_file, sign_key, serial_number,
             serial_number_mask, debugger_flags):

    # This is fine for the moment. Eventually, the signing server should
    # have a database of certificates and be passed all these arguments
    # and return the proper certificate. There is a SQLite implementation
    # of this in the SBPFirmware repository that is probably overkill for
    # the signing server but this would be similar

    print("WARNING: Using firmware signing service to provide a certificate.\n"
          "Currently the server does not generate certificates on the fly "
          "but only provides a pre-generated certificate associated with a given "
          "key name <{}>. This may not be desired so if a different certificate "
          "is required, a certificate must be generated using local hsm mode instead.".
          format(cert_key))

    if SigningEnv().auth_token:
        production_get_cert(outfile, cert_key, cert_key_file, sign_key, serial_number,
                            serial_number_mask, debugger_flags)
        return

    response = requests.get(CERTIFICATE_SERVICE_URL + cert_key + "_certificate.bin",
                            timeout=DEFAULT_HTTP_TIMEOUT)
    if response.status_code == requests.codes.ok:
        write(outfile, response.content)
    else:
        raise(Exception("Failed to obtain certificate for key {}, err {}".
                        format(cert_key, response.status_code)))


def export_pub_key_hash(outfile, label):
    ''' export pub key hash: used for customer keys in OTP '''
    modulus = get_modulus(label)
    new_hash = hashlib.sha256(modulus).digest()

    # export the hash of the modulus of the public key
    old_hash = b''
    try:
        old_hash = read(outfile)
    except:
        pass

    if old_hash != new_hash:
        write(outfile, new_hash)
    else:
        print("No changes in hash")
