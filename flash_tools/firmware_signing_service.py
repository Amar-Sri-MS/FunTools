import os
import requests
import struct
import sys

import enrollment_service as es
import generate_firmware_image as gfi

SIGNING_SERVICE_URL = "https://f1reg.fungible.local:4443/cgi-bin/signing_server.cgi"
CERT = os.path.join(sys.path[0],'f1registration.ca.pem')

def GetModulus(name):
    params = {
        'cmd' : 'modulus',
        'format' : 'binary',
        'key' : name
    }

    response = requests.get(SIGNING_SERVICE_URL, params=params, verify=CERT)

    return response.content

