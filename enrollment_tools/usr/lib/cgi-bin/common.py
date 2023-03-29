
##############################################################################
#  common.py
#
#
#  Copyright (c) 2018-2019. Fungible, inc. All Rights Reserved.
#
##############################################################################

import os
import sys
import struct
import binascii
import datetime
import textwrap


# HSM connection
import pkcs11
import pkcs11.util.rsa

MAX_SIGNATURE_SIZE = 512


#################################################################################
#
# BadParamError
#
#################################################################################

class BadParamError:
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)


#################################################################################
#
# Logging Apache style
#
#################################################################################
def log(msg):
    dt_stamp = datetime.datetime.now().strftime("%c")
    print("[%s] [enrollment] %s" % (dt_stamp, msg), file=sys.stderr)


###########################################################################
#
# HTTP common routines
#
###########################################################################

def safe_form_get(form, key, default):
    ''' deprecated : use form.getvalue(key, default) instead '''
    return form.getvalue(key, default)

def send_response_body(body, filename=None):
    print("Status: 200 OK")
    if filename:
        print("Content-Disposition: attachment; filename = %s" %
              filename)
    print("Content-length: %d\n" % len(body))
    print("%s\n" % body)


def send_binary_buffer(bin_buffer, form, filename=None):

    format = form.getvalue("format", "hex")
    if format == "hex":
        bin_str = binascii.b2a_hex(bin_buffer).decode('ascii')
    elif format == "base64":
        bin_str = textwrap.fill(
            binascii.b2a_base64(bin_buffer).decode('ascii'),
            width=57)
    elif format == "c_struct":
        bin_c_struct = "%d,\n{\n" % len(bin_buffer)

        for pos in range(0, len(bin_buffer)):
            bin_c_struct += "0x%02x, " % bin_buffer[pos]
            if pos % 8 == 7:
                bin_c_struct += "\n"
        if len(bin_buffer) %8 != 0:
            bin_c_struct += "\n"
        bin_c_struct += "}"
        bin_str = bin_c_struct
    else:
        raise ValueError("Unknown format: %s" % format)

    send_response_body(bin_str, filename)



##################################################################################################
#
# HSM commands
#
##################################################################################################

# libraries in order of preference -- second argument: prompt for password
LIBSOFTHSM2_PATHS = [
    ("/usr/safenet/lunaclient/lib/libCryptoki2_64.so", True), # Safenet ubuntu 14
    ("/usr/lib/softhsm/libsofthsm2.so", False), # Ubuntu-17, 18
    ("/usr/lib/x86_64-linux-gnu/softhsm/libsofthsm2.so", False), # Ubuntu-16
    ("/usr/local/lib/softhsm/libsofthsm2.so", False), # macOS brew
    ("/project/tools/softhsm-2.3.0/lib/softhsm/libsofthsm2.so", False), # shared vnc machines for verification team
]


def get_pkcs11_lib():
    ''' connect to a PKCS#11 library. Returns instance '''
    lib = None

    for entry in LIBSOFTHSM2_PATHS:
        if os.path.exists(entry[0]):
            try:
                lib = pkcs11.lib(entry[0])
            except:
                pass

    if lib is None:
        raise RuntimeError("Could not find PKCS#11 library")

    return lib


def get_ro_session():
    lib = get_pkcs11_lib()

    with open('/etc/hsm_password') as f:
        lines = f.readlines()

    token_label = lines[0].strip()
    password = lines[1].strip()

    # look into the slots with token
    # the old lib.get_token does not work well with Safenet PKCS#11
    for slot in lib.get_slots(True):
        token = slot.get_token()
        if token.label == token_label:
            return token.open(user_pin=password, rw=False)

    raise RuntimeError("Could not find the token '%s'" % token_label)

def get_modulus(pub):
    return pub[pkcs11.Attribute.MODULUS]

def append_signature_to_binary(binary, signature):
    binary += struct.pack('<I', len(signature))
    binary += signature
    # pad to MAX_SIGNATURE_SIZE with 0
    binary += b'\x00' * (MAX_SIGNATURE_SIZE - len(signature))
    return binary

def get_public_rsa_with_label(ro_session, label):
    ''' Returns public key '''
    return ro_session.get_key(object_class=pkcs11.constants.ObjectClass.PUBLIC_KEY,
                              label=label)

def get_private_rsa_with_label(ro_session, label):
    return ro_session.get_key(object_class=pkcs11.constants.ObjectClass.PRIVATE_KEY,
                              label=label)

def get_private_rsa_with_modulus(ro_session, modulus):
    ''' retrieve the private key with the modulus specified '''
    private = None
    try:
        privates = ro_session.get_objects(
            {pkcs11.Attribute.CLASS:pkcs11.ObjectClass.PRIVATE_KEY,
             pkcs11.Attribute.KEY_TYPE:pkcs11.KeyType.RSA,
             pkcs11.Attribute.MODULUS:modulus})
        private = next(privates)
    except Exception as err:
        print(err)

    return private

def sign_with_key(session, key_label, data):
    private = get_private_rsa_with_label(session, key_label)
    return private.sign(data, mechanism=pkcs11.Mechanism.SHA512_RSA_PKCS)


def sign_binary(session, key_label, binary):
    ''' sign a binary and appends the signature to it '''
    signature = sign_with_key(session, key_label, binary)
    return append_signature_to_binary(binary, signature)


########################################################################
#
# Common commands
#
########################################################################

def send_modulus(form_values, key_label):

    # get modulus from HSM
    with get_ro_session() as session:
        modulus = get_modulus(get_public_rsa_with_label(session, key_label))
        send_binary_buffer(modulus, form_values)
