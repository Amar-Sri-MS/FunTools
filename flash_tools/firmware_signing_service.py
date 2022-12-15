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
import time

import requests

# image file format description
# https://docs.google.com/document/d/1wb34TuVJmPlikeVjvE0tdCQxP8ZgzLc0RSMbyd1prwM

MAGIC_STRING_FUNGIBLE_SIGN = b'Fungible'
MAGIC_STRING_CUSTOMER_SIGN = b'FunCustS'
EXTRA_INFO_SIZE = len(MAGIC_STRING_CUSTOMER_SIGN)

SIGNING_INFO_SIZE = 2048
MAX_SIGNATURE_SIZE = 512
SIGNATURE_STRUCT_SIZE = 4 + MAX_SIGNATURE_SIZE # length prefix

HEADER_RESERVED_SIZE = SIGNING_INFO_SIZE - (
    EXTRA_INFO_SIZE + SIGNATURE_STRUCT_SIZE)
SIGNED_ATTRIBUTES_CHIP_ID_SIZE = 4
SIGNED_ATTRIBUTES_PAD_SIZE = 28 # zero pad + key_addrs
SIGNED_DESCRIPTION_SIZE = 32
SERIAL_INFO_NUMBER_SIZE = 24
CERT_PUB_KEY_POS = 64
MAX_KEYS_IN_KEYBAG = 96
SEC_GRP_POS = 14
SEC_GRP_SIZE = 2

CERT_LEN = 1096

MAGIC_NUMBER_CERTIFICATE = 0xB1005EA5
MAGIC_NUMBER_ENROLL_CERT = 0xB1005C1E

SIGNING_SERVER_URL = "https://f1reg.fungible.com:4443"
SIGNING_SERVICE_URL = SIGNING_SERVER_URL + "/cgi-bin/signing_server.cgi"
# Certificate files hierarchy:
#.
# ├── development
# │   ├── f1
# │   │   ├── cpk1_certificate.bin
# │   │   └── fpk2_certificate.bin
# │   ├── f1d1 -> f1
# │   ├── s1 -> f1
# │   └── s2
# └── production
#     ├── f1
#     │   ├── fpk2_certificate_0000.bin
#     │   └── fpk2_certificate_0001.bin
#     ├── f1d1 -> f1
#     ├── s1 -> f1
#     └── s2

DEVELOPMENT_CERTIFICATE_ROOT_URL = SIGNING_SERVER_URL + "/development/"
PRODUCTION_CERTIFICATE_ROOT_URL = SIGNING_SERVER_URL + "/production/"

DEFAULT_HTTP_TIMEOUT = 180
MAX_CONNECTION_RETRY = 20
RETRY_CONNECTION_SLEEP_SECS = 10

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

#####################################################################
# Connection TimeOut Exception wrapper
# the *single* signing server is unfrequently restarted to install
# security updates so try to connect or reconnect for a while

def connection_retry_handler(func):
    def inner_function(*args, **kwargs):
        retries = 0
        while True:
            try:
                ret = func(*args, **kwargs)
                break
            except (ConnectionError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout) as exc:
                time.sleep(RETRY_CONNECTION_SLEEP_SECS)
                retries += 1
                if retries >= MAX_CONNECTION_RETRY:
                   raise RuntimeError("Unable to connect to server!") from exc
        return ret

    return inner_function


@connection_retry_handler
def try_get(*args, **kwargs):
    return requests.get(*args, **kwargs)

@connection_retry_handler
def try_post(*args, **kwargs):
    return requests.post(*args, **kwargs)



#########################################################################
# server certificate retrieval2
def retrieve_cert(production, chip_type, cert_key, security_group):

    if production:
        request = "".join([PRODUCTION_CERTIFICATE_ROOT_URL,
                           chip_type, "/",
                           cert_key, "_certificate_",  security_group, ".bin"])
    else:
        request = "".join([DEVELOPMENT_CERTIFICATE_ROOT_URL,
                           chip_type, "/",
                           cert_key, "_certificate.bin"])

    response = try_get(request, timeout=DEFAULT_HTTP_TIMEOUT)

    if response.status_code == requests.codes.ok:
        return response.content

    raise(Exception("Failed to obtain certificate at {} for "
                    "chip {}, security group {}, key {}: err: {}".
                    format(request, chip_type, security_group, cert_key,
                           response.status_code)))


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

    response = try_get(SIGNING_SERVICE_URL, params=params,
                            timeout=DEFAULT_HTTP_TIMEOUT)
    if response.status_code != requests.codes.ok:
        raise RuntimeError("Server responded with [{}]:\n{}\n".format(
            response.status_code, response.content).replace("\\n", "\n"))

    return response.content

def pack_binary_form_data(title, bin_data):
    return (title, bin_data, 'application/octet-stream',
            {"Content-Length" : str(len(bin_data))})


def hash_sign(digest, sign_key=None, modulus=None):
    ''' send a POST sign request with digest '''

    auth_token = SigningEnv().auth_token

    multipart_form_data = {'digest' : pack_binary_form_data("sha512", digest)}

    if modulus:
        multipart_form_data['modulus'] = pack_binary_form_data("modulus",
                                                               modulus)

    if auth_token:
        multipart_form_data['auth_token'] = pack_binary_form_data("auth",
                                                                  auth_token)


    params = {}
    if sign_key:
        params['key'] = sign_key


    response = try_post(SIGNING_SERVICE_URL,
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


def add_cert_and_signature_to_image(image, cert, signature, magic):
    image += cert
    image += b'\x00' * (HEADER_RESERVED_SIZE - len(cert))
    assert len(magic) == 8
    image += struct.pack('8s', magic)
    return append_signature_to_binary(image, signature)

def image_gen(outfile, infile, ftype, version, description, sign_key,
              certfile, customer_certfile, key_index, locations=[],
              chip_type=None, pad=1, **kwargs):
    ''' generate signed firmware image '''

    chip_type_map = {
        # chip name : [ family, device, revision, zero(reserved-alignment) ]
        # see https://docs.google.com/document/d/1qojY63VZvkhmbDenbl6J2j51yeA_9FfhU8s_aTUhvJs
        'f1'   : [1, 1, 0, 0],
        's1'   : [2, 1, 0, 0],
        'f1d1' : [1, 1, 1, 0],
        's2'   : [2, 2, 0, 0],
        'f2'   : [1, 2, 0, 0] # check that this is correct ...
    }

    if ((pad == 0) or (pad is None)):
        pad = 1 # make the lazy thing work
    binary = read(infile)
    to_be_signed = struct.pack('<2I', len(binary), version)
    to_be_signed += struct.pack('4s', ftype.encode())
    if chip_type:
        to_be_signed += struct.pack('4B', *chip_type_map[chip_type])
    else:
        to_be_signed += b'\x00' * (SIGNED_ATTRIBUTES_CHIP_ID_SIZE)

    # optional locations -- restrict to 1 for the moment -- easy to add more
    num_locs = len(locations)
    if num_locs > 1:
        print("****** Warning: more than 1 pointers in authenticated headers")

    for loc in locations:
        to_be_signed += struct.pack("<I", loc)

    # zero pad
    zero_pad_len = SIGNED_ATTRIBUTES_PAD_SIZE - 4 * num_locs
    if zero_pad_len < 0:
        raise(Exception("Too many locations {} ({}) specified for header of {}".
                        format(num_locs, locations, ftype)))
    to_be_signed += b'\x00' * zero_pad_len

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

    customer_to_be_signed = add_cert_and_signature_to_image(b'', cert,
                                                            signature,
                                                            MAGIC_STRING_FUNGIBLE_SIGN)
    customer_to_be_signed += to_be_signed

    if customer_certfile:
        customer_cert = read(customer_certfile)
        customer_signature = server_sign_with_cert(customer_cert,
                                                   customer_to_be_signed)
    else:
        customer_cert = b''
        customer_signature = b''

    image = add_cert_and_signature_to_image(b'', customer_cert,
                                            customer_signature,
                                            MAGIC_STRING_CUSTOMER_SIGN)
    image += customer_to_be_signed

    # pad the image to the requested length
    n = len(image) % pad
    if n > 0:
        m = pad - n
        padbytes = b"\0" * m
        image += padbytes

    write(outfile, image)


def get_cert(outfile, chip_type, cert_key, security_group):
    ''' retrieve the desired start certificate and store it in outfile '''
    if chip_type not in ['f1', 's1', 'f1d1', 's2', 'f2']:
        raise Exception("Start certificate: Unknown chip type %s" % chip_type)

    if SigningEnv().auth_token:
        content = retrieve_cert(True, chip_type, cert_key, security_group)
    elif security_group == 0:
        content = retrieve_cert(False, chip_type, cert_key, security_group)
    else:
        raise Exception("No current production authentication token and "
                        "a non-zero security group was specified")

    write(outfile, content)


def export_pub_key_hash(outfile, chip_type, label):
    ''' export pub key hash: used for customer keys in OTP '''
    if chip_type not in ['f1', 's1', 'f1d1', 's2', 'f2']:
        raise Exception("Export pub key hash: Unknown chip type %s" % chip_type)

    modulus = get_modulus(label)

    if chip_type in ['f1', 's1', 'f1d1', 's2']:
        new_hash = hashlib.sha256(modulus).digest()
    else:
        new_hash = hashlib.sha512(modulus).digest()

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


def sign_debugging_certificate(label, cert_file_name):
    # read the TBS part of the file (can be TBS or Full Cert)
    tbs_cert = open(cert_file_name, 'rb').read(CERT_LEN -
                                               (SIGNATURE_STRUCT_SIZE))
    cert = append_signature_to_binary(tbs_cert,
                                      server_sign_with_key(label, tbs_cert))
    # write back to input file
    open(cert_file_name, 'wb').write(cert)
