import os
import requests
import struct
import sys

import enrollment_service as es
import generate_firmware_image as gfi

SIGNING_SERVICE_URL = "https://f1reg.fungible.com:4443/cgi-bin/signing_server.cgi"
CERTIFICATE_SERVICE_URL = "https://f1reg.fungible.com:4443/"
DEFAULT_HTTP_TIMEOUT = 10

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

        def create_binary_form_data( infile):
            with open(infile, 'rb') as input:
                bin_data = input.read()
                return (infile, bin_data, 'application/octet-stream',
                    {"Content-Length" : str(len(bin_data)) })

        multipart_form_data = { 'img' : create_binary_form_data(infile) }

        if certfile:
            multipart_form_data['cert'] = create_binary_form_data(certfile)

        if customer_certfile:
            multipart_form_data['customer_cert'] = create_binary_form_data(customer_certfile)

        params = { 'key' : sign_key,
                   'key_index' : key_index,
                   'type' : ftype,
                   'version': version,
                   'description': description }

        response = requests.post(SIGNING_SERVICE_URL,
                                files=multipart_form_data,
                                params=params,
                                timeout=DEFAULT_HTTP_TIMEOUT)

        if response.status_code == requests.codes.ok:
            gfi.write(outfile, response.content)
        else:
            raise(Exception("Failed to sign image {}, err {}: {}".format(
                                    infile, response.status_code, response.content)))

    @staticmethod
    def export_pub_key_hash(outfile, label):
        gfi.export_pub_key_hash(outfile, None, modulus=GetModulus(label))

    @staticmethod
    def raw_sign(file):
        with open(file, 'rb') as f:
            return es.Sign(f.read())
