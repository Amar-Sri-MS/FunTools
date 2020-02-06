import os
import requests
import struct
import sys
import hashlib

import enrollment_service as es
import generate_firmware_image as gfi

SIGNING_SERVICE_URL = "https://f1reg.fungible.com:4443/cgi-bin/signing_server.cgi"
CERTIFICATE_SERVICE_URL = "https://f1reg.fungible.com:4443/"
DEFAULT_HTTP_TIMEOUT = 100

def GetModulus(name):
    params = {
        'cmd' : 'modulus',
        'format' : 'binary',
        'key' : name
    }

    response = requests.get(SIGNING_SERVICE_URL, params=params, timeout=DEFAULT_HTTP_TIMEOUT)
    return response.content


class FirmwareSigningService(object):
    MOD_HSM = 1 << 0
    MOD_NET = 1 << 1

    def __init__(self):
        pass

    @staticmethod
    def create(mode):
        if mode & FirmwareSigningService.MOD_NET:
            return NetSigningService()
        elif mode & FirmwareSigningService.MOD_HSM:
            return HsmSigningService()

        raise TypeError("Mode {} not available".format(mode))

class HsmSigningService(FirmwareSigningService):
    @staticmethod
    def cert_gen(outfile, cert_key, cert_key_file, sign_key, serial_number,
             serial_number_mask, debugger_flags):
        return gfi.cert_gen(outfile, cert_key, cert_key_file, sign_key, serial_number,
            serial_number_mask, debugger_flags)

    @staticmethod
    def image_gen(outfile, infile, ftype, version, description, sign_key,
                  certfile, customer_certfile, key_index):
        return gfi.image_gen(outfile, infile, ftype, version, description, sign_key,
                             certfile, customer_certfile, key_index)

    @staticmethod
    def export_pub_key_hash(outfile, label):
        gfi.export_pub_key_hash(outfile, label)

    @staticmethod
    def raw_sign(file):
        return gfi.raw_sign(None, file, "fpk4")

class NetSigningService(FirmwareSigningService):
    @staticmethod
    def cert_gen(outfile, cert_key, cert_key_file, sign_key, serial_number,
             serial_number_mask, debugger_flags):
        print("WARNING: Using firmware signing service to provide a certificate.\n"
              "Currently the server does not generate certificates on the fly "
              "but only provides a pre-generated certificate associated with a given "
              "key name <{}>. This may not be desired so if a different certificate "
              "is required, a certificate must be generated using local hsm mode instead.".format(sign_key))

        response = requests.get(CERTIFICATE_SERVICE_URL + sign_key + "_certificate.bin", timeout=DEFAULT_HTTP_TIMEOUT)
        if response.status_code == requests.codes.ok:
            gfi.write(outfile, response.content)
        else:
            raise(Exception("Failed to obtain certificate for key {}, err {}".format(
                                    sign_key, response.status_code)))

    @staticmethod
    def image_gen(outfile, infile, ftype, version, description, sign_key,
                  certfile, customer_certfile, key_index):

        def pack_binary_form_data(title, bin_data):
            return (title, bin_data, 'application/octet-stream',
                    {"Content-Length" : str(len(bin_data)) })


        def create_binary_form_data( infile):
            with open(infile, 'rb') as input:
                bin_data = input.read()
                return pack_binary_form_data(infile, bin_data)

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
            return hash_sign(digest, sign_key=label),gfi.pkcs11.KeyType.RSA


        def server_sign_with_cert(cert, data):
            ''' when signing with certificate, the certificate is part of the digest
            to keep things simple, this is done here and not on the server '''
            m = hashlib.sha512()
            m.update(cert)
            m.update(data)
            digest = m.digest()
            modulus = gfi.get_cert_modulus(cert)
            return hash_sign(digest, modulus=modulus)

        return gfi.image_gen(outfile, infile, ftype, version, description, sign_key,
                             certfile, customer_certfile, key_index,
                             sign_with_key_func=server_sign_with_key,
                             sign_with_cert_func=server_sign_with_cert)


    @staticmethod
    def export_pub_key_hash(outfile, label):
        gfi.export_pub_key_hash(outfile, None, modulus=GetModulus(label))

    @staticmethod
    def raw_sign(file):
        with open(file, 'rb') as f:
            return es.Sign(f.read())
