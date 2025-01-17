#!/usr/bin/env python3

'''
Copyright (c) 2017-2020 Fungible, inc.
Copyright (c) 2023 Microsoft Corporation.
All Rights Reserved.
'''

import os
import sys
import struct
import binascii
import hashlib
import time
import configparser

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

## resolve which signing server the user is talking about
SIGNING_SERVERS = {
        "fungible": ("https://f1reg.fungible.com:4443", None),
        "corpnet": ("https://dpuhub.corp.microsoft.com:4443", "dpuhub.pem"),

        ## ADO is on a private network for build VMs, but uses the same
        ## domain name as the corpnet server for simplicity
        "ado": ("https://dpuhub.corp.microsoft.com:4443", "dpuhub.pem"),
}

DEFAULT_SIGNING_SERVER = "fungible"
SIGNING_SERVER = os.environ.get('DPU_SIGNING_SERVER', DEFAULT_SIGNING_SERVER)

# do a direct lookup
url = SIGNING_SERVERS.get(SIGNING_SERVER, SIGNING_SERVERS[DEFAULT_SIGNING_SERVER])[0]
SIGNING_SERVER_URL = url

# look for possible override ~/.config/signing.ini
try:
    config_path = os.path.join(os.path.expanduser('~'),
                               '.config',
                               'signing.ini')
    with open(config_path) as f:
        content = "[no_section]\n" + f.read()

    config = configparser.ConfigParser()
    config.read_string(content)
    SIGNING_SERVER_URL = config['no_section']['server_url']
    print(">>> NOTE: overriding signing server url to %s" %
          SIGNING_SERVER_URL)
except:
    pass


# check if we need to load a self-signed cert
cert_verif = True
for (url, v) in SIGNING_SERVERS.values():
    if (url != SIGNING_SERVER_URL):
        continue
    if (v is not None):
        cert_verif = os.path.join(os.path.dirname(__file__), v)
    break


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

# environment variable that points to a mutual authentication
# certificate and key: if it is set and points to a file, it triggers the use
# of the production keys and certificates
PROD_SIGN_CERT_ENV_VAR = "PROD_SIGN_CERT_FILE"

##############################################################################
# Environment variable: client cert
# This file must consist of the concatenation of the cert and the key
#
def production_client_cert_file():
    return os.environ.get(PROD_SIGN_CERT_ENV_VAR)


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
    except Exception as exc:
        raise Exception("Cannot open file '%s' for read" % filename) from exc
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
    except Exception as exc:
        raise Exception("Cannot open file '%s' for write" % filename) from exc
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
    return requests.get(*args, verify=cert_verif, **kwargs)

@connection_retry_handler
def try_post(*args, **kwargs):
    return requests.post(*args, verify=cert_verif, **kwargs)



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
    cert_file = production_client_cert_file()
    if cert_file:
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

    params = {}

    # if production, use typical URL with production=1
    cert_file = production_client_cert_file()
    if cert_file:
        params['production'] = '1'

    multipart_form_data = {'digest' : pack_binary_form_data("sha512", digest)}

    if modulus:
        multipart_form_data['modulus'] = pack_binary_form_data("modulus",
                                                               modulus)
    if sign_key:
        params['key'] = sign_key


    response = try_post(SIGNING_SERVICE_URL,
                        files=multipart_form_data,
                        cert=cert_file,
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

    # optional locations -- restrict to 2 for the moment -- easy to add more
    num_locs = len(locations)
    if num_locs > 2:
        print("****** Warning: more than 2 pointers in authenticated headers")

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
    content = retrieve_cert(production_client_cert_file(),
                            chip_type, cert_key, security_group)
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
