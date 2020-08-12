
import os
import sys
import struct
import binascii
import hashlib
import requests


RSA_KEY_SIZE_IN_BITS = 2048
SIGNING_INFO_SIZE = 2048
MAX_SIGNATURE_SIZE = 512
HEADER_RESERVED_SIZE = SIGNING_INFO_SIZE - (4 + MAX_SIGNATURE_SIZE)
SIGNED_ATTRIBUTES_SIZE = 32
SIGNED_DESCRIPTION_SIZE = 32
SERIAL_INFO_NUMBER_SIZE = 24
CERT_PUB_KEY_POS = 64
MAX_KEYS_IN_KEYBAG = 96

MAGIC_NUMBER_CERTIFICATE = 0xB1005EA5
MAGIC_NUMBER_ENROLL_CERT = 0xB1005C1E

SIGNING_SERVICE_URL = "https://f1reg.fungible.com:4443/cgi-bin/signing_server.cgi"
CERTIFICATE_SERVICE_URL = "https://f1reg.fungible.com:4443/"
DEFAULT_HTTP_TIMEOUT = 100


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
# Signing server

def get_modulus(name):
    params = {
        'cmd' : 'modulus',
        'format' : 'binary',
        'key' : name
    }

    response = requests.get(SIGNING_SERVICE_URL, params=params, timeout=DEFAULT_HTTP_TIMEOUT)
    return response.content

def pack_binary_form_data(title, bin_data):
    return (title, bin_data, 'application/octet-stream',
            {"Content-Length" : str(len(bin_data)) })


def hash_sign(digest, sign_key=None, modulus=None):
    ''' send a POST sign request new API with only digest sent '''
    multipart_form_data = { 'digest' : pack_binary_form_data("sha512", digest) }
    if modulus:
        multipart_form_data['modulus'] = pack_binary_form_data("modulus", modulus)
    params = {}
    if sign_key:
        params['key'] = sign_key

    response = requests.post(SIGNING_SERVICE_URL,
                             files=multipart_form_data,
                             params=params,
                             timeout=DEFAULT_HTTP_TIMEOUT)
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
              certfile, customer_certfile, key_index, pad=1):
    ''' generate signed firmware image '''
    if ((pad == 0) or (pad is None)):
        pad = 1 # make the lazy thing work
    binary = read(infile)
    to_be_signed = struct.pack('<2I', len(binary), version)
    to_be_signed += struct.pack('4s', ftype.encode())
    to_be_signed += b'\x00' * SIGNED_ATTRIBUTES_SIZE
    if description:
        # Max allowed size is (block size - 1) to allow for terminating null
        if len(description) > SIGNED_DESCRIPTION_SIZE - 1:
            raise ValueError( "Image description too long, max is {}".
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
    if (n > 0):
        m = pad - n
        padbytes = b"\0" * m
        image += padbytes

    write(outfile, image)


def cert_gen(outfile, cert_key, cert_key_file, sign_key, serial_number,
             serial_number_mask, debugger_flags):
    print("WARNING: Using firmware signing service to provide a certificate.\n"
          "Currently the server does not generate certificates on the fly "
          "but only provides a pre-generated certificate associated with a given "
          "key name <{}>. This may not be desired so if a different certificate "
          "is required, a certificate must be generated using local hsm mode instead.".format(cert_key))

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
