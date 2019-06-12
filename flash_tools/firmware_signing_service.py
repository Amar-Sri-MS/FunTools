import os
import requests
import struct
import sys

import enrollment_service as es
import generate_firmware_image as gfi

SIGNING_SERVICE_URL = "https://f1reg.fungible.com:4443/cgi-bin/signing_server.cgi"

def GetModulus(name):
    params = {
        'cmd' : 'modulus',
        'format' : 'binary',
        'key' : name
    }

    response = requests.get(SIGNING_SERVICE_URL, params=params)
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
             serial_number_mask, debugger_flags, tamper_flags):
        return gfi.cert_gen(outfile, cert_key, cert_key_file, sign_key, serial_number,
            serial_number_mask, debugger_flags, tamper_flags)

    @staticmethod
    def image_gen(outfile, infile, ftype, version, description, sign_key,
          certfile, customer_certfile):
        return gfi.image_gen(outfile, infile, ftype, version, description, sign_key,
            certfile, customer_certfile)

    @staticmethod
    def export_pub_key_hash(outfile, label):
        gfi.export_pub_key_hash(outfile, label)

class NetSigningService(FirmwareSigningService):
    @staticmethod
    def cert_gen(outfile, cert_key, cert_key_file, sign_key, serial_number,
             serial_number_mask, debugger_flags, tamper_flags):
        return gfi.cert_gen(outfile, cert_key, cert_key_file, sign_key, serial_number,
            serial_number_mask, debugger_flags, tamper_flags)

        # CODE BELOW NEVER EXECUTED, BUT LEFT FOR REFERENCE
        # when using the service to generate/sign the certificate, and the
        # certificate file is not available, need to generate the public key
        # modulus first
        if cert_key:
            modulus = GetModulus(cert_key)
        else:
            modulus = None

        tbs = gfi.cert_gen(outfile=None,
                cert_key=None,
                cert_key_file=cert_key_file,
                sign_key=None,
                serial_number=serial_number,
                serial_number_mask=serial_number_mask,
                debugger_flags=debugger_flags,
                tamper_flags=tamper_flags,
                modulus=modulus)

        #TBS to be signed, but server doesn't implement this currently
        gfi.write(outfile, tbs)
        raise(Exception())

    @staticmethod
    def image_gen(outfile, infile, ftype, version, description, sign_key,
          certfile, customer_certfile):

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
                   'type' : ftype,
                   'version': version,
                   'description': description }

        response = requests.post(SIGNING_SERVICE_URL,
                                files=multipart_form_data,
                                params=params)

        gfi.write(outfile, response.content)

    @staticmethod
    def export_pub_key_hash(outfile, label):
        gfi.export_pub_key_hash(outfile, None, modulus=GetModulus(label))
