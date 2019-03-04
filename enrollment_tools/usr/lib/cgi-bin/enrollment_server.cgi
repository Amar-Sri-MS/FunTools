#! /usr/bin/env python3

##############################################################################
#  enrollment_server.py
#
#
#  Copyright (c) 2018-2019. Fungible, inc. All Rights Reserved.
#
##############################################################################

import sys
import binascii
import struct
import os
import datetime
import textwrap
from contextlib import closing
import cgi

import traceback

# HSM connection
import pkcs11
import pkcs11.util.rsa

# db connection
import psycopg2

# to validate the point received
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec


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


#################################################################################
#
# Database routines
#
#################################################################################

SN_DESC = (
    ('serial_info', 8),
    ('serial_nr', 16))

TBS_CERT_DESC = (
    ('magic', 4),
    ('flags', 4),
) + SN_DESC + (
    ('puf_key', 64),
    ('nonce', 48),
    ('activation_code', 888),
)

CERT_DESC = TBS_CERT_DESC + (('rsa_signature', 516),)

SN_LEN = sum([desc[1] for desc in SN_DESC])
TBS_CERT_LEN = sum([desc[1] for desc in TBS_CERT_DESC])
CERT_LEN = sum([desc[1] for desc in CERT_DESC])


def make_slicer_of(b):
    ''' return an object that will slice a string into multiple buffers '''
    offset = [0]

    def make_buff(size):
        ''' create a buffer at the current offset of the specified size '''
        ret = b[offset[0]:offset[0]+size]
        offset[0] += size
        return ret

    return make_buff


FIELDS = [desc[0] for desc in CERT_DESC]
FIELDS_LIST = ",".join(FIELDS)
FIELDS_CONCAT = " || ".join(FIELDS)
ARGS_LIST = ",".join(["%({0})s".format(fld) for fld in FIELDS])

INSERT_STMT = "INSERT INTO enrollment (" + \
    FIELDS_LIST + ") VALUES (" + ARGS_LIST + ")"
RETRIEVE_STMT = "SELECT " + FIELDS_CONCAT + """ FROM enrollment WHERE serial_nr = %s
                                               AND serial_info = %s """

def db_store_cert(conn, cert):
    ''' store the full certificate in the database '''
    # slice the tbs cert into constituent buffers
    slicer = make_slicer_of(cert)
    values = {desc[0]: slicer(desc[1]) for desc in CERT_DESC}

    with conn.cursor() as cur:
        cur.execute(INSERT_STMT, values)

    conn.commit()


def db_retrieve_cert_for_serial_nr( conn, serial_nr, serial_info):

    with conn.cursor() as cur:
        cur.execute(RETRIEVE_STMT, (serial_nr, serial_info))
        if cur.rowcount > 0:
            return cur.fetchone()[0]
    return None


def fetch_cert( values_dict):

    # connect to the database
    with closing(psycopg2.connect("dbname=enrollment_db")) as db_conn:
        # see if there is such a serial number already
        cert = db_retrieve_cert_for_serial_nr(db_conn,
                                              values_dict['serial_nr'],
                                              values_dict['serial_info'])
        if cert:
            log("Certificate retrieved for  %s - %s" % (
                binascii.b2a_hex(values_dict['serial_nr']),
                binascii.b2a_hex(values_dict['serial_info'])))
        else:
            log("Generating certificate for %s - %s" % (
                binascii.b2a_hex(values_dict['serial_nr']),
                binascii.b2a_hex(values_dict['serial_info'])))

            # sign the tbs_cert
            cert = hsm_sign(tbs_cert)
            # store it
            db_store_cert(db_conn, cert)

    # encode the certificate
    cert_b64 = binascii.b2a_base64(cert).decode('ascii')

    print("Status: 200 OK")
    print("Content-length: %d\n" % len(cert_b64))
    print("%s\n" % cert_b64)



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

def sign_with_key(session, key_label, data):
    private = get_private_rsa_with_label(session, key_label)
    return private.sign(data, mechanism=pkcs11.Mechanism.SHA512_RSA_PKCS)

def sign_binary(session, binary):
    ''' sign a binary and appends the signature to it '''
    signature = sign_with_key(session, 'fpk4', binary)
    return append_signature_to_binary(binary, signature)

def hsm_sign( tbs_cert):
    with get_ro_session() as session:
            return sign_binary(session, tbs_cert)


###########################################################################
#
# Input validation
#
###########################################################################

def validate_tbs_cert(values_dict):
    ''' perform some validation on the input '''

    # check magic
    if values_dict['magic'] != b'\x1e\x5c\x00\xb1':
        raise ValueError("Bad Magic: %s" % values_dict)

    # check the point is on the P256 curve
    ec_pt = values_dict['puf_key']
    x = int.from_bytes(ec_pt[:32], byteorder='big')
    y = int.from_bytes(ec_pt[32:], byteorder='big')

    # this will raise a ValueError if x and y do not represent a point on the curve
    pub_key = ec.EllipticCurvePublicNumbers(x,y, ec.SECP256R1()).public_key(backend=default_backend())

    # TODO: validate serial info -> install a format filter

##########################################################################
#
# Enrollment
#
##########################################################################
def do_enroll():

    # read the TBS from request
    request = sys.stdin.read()
    tbs_cert = binascii.a2b_base64( request)

    if len(tbs_cert) != TBS_CERT_LEN:
        raise ValueError("TBS length = %d" % len(tbs_cert))

    # slice the tbs cert into constituent buffers
    slicer = make_slicer_of(tbs_cert)
    values_dict = {desc[0]: slicer(desc[1]) for desc in TBS_CERT_DESC}

    validate_tbs_cert(values_dict)

    fetch_cert(values_dict)


########################################################################
#
# Return some information: fpk4 modulus, certificate
#
########################################################################

def safe_form_get(form, key, default):
    if key in form:
        return form[key].value
    else:
        return default

def send_certificate(form_values):

    sn_64 = safe_form_get(form_values, "sn", None)
    if not sn_64:
        raise ValueError("Missing parameter")

    sn = binascii.a2b_base64(sn_64)
    if len(sn) != SN_LEN:
        raise ValueError("SN length = %d" % len(sn))

    # slice the sn into constituent buffers
    slicer = make_slicer_of(sn)
    values_dict = {desc[0]: slicer(desc[1]) for desc in SN_DESC }

    fetch_cert(values_dict)


def send_modulus(form_values):

    # get fpk4 modulus from HSM
    with get_ro_session() as session:
        modulus = get_modulus(get_public_rsa_with_label(session, 'fpk4'))

    format = safe_form_get(form_values, "format", "hex")
    if format == "hex":
        modulus_str = binascii.b2a_hex(modulus).decode('ascii')
    elif format == "base64":
        modulus_str = textwrap.fill(
            binascii.b2a_base64(modulus).decode('ascii'),
            width=57)
    elif format == "c_struct":
        c_modulus = "%d,\n{\n" % len(modulus)

        for pos in range(0, len(modulus)):
            c_modulus += "0x%02x, " % modulus[pos]
            if pos % 8 == 7:
                c_modulus += "\n"
        if len(modulus) %8 != 0:
            c_modulus += "\n"
        c_modulus += "}"
        modulus_str = c_modulus

    print("Status: 200 OK")
    print("Content-length: %d\n" % len(modulus_str))
    print("%s\n" % modulus_str)


def process_query():

    form = cgi.FieldStorage()
    cmd = safe_form_get(form, "cmd", "modulus")
    if cmd == "modulus":
        send_modulus(form)
    elif cmd == "cert":
        send_certificate(form)
    else:
        raise ValueError("Invalid command")



def main_program():

    # our content is always text/plain
    print("Content-type: text/plain")
    try:
        # get the request -- base64 encoded TBS
        method = os.environ["REQUEST_METHOD"]
        if method != "PUT" and method != "GET":
            raise ValueError("Invalid request method %s" % method)

        if method == "GET":
            # GET: query
            process_query()
        else:
            # PUT: enrollment
            do_enroll()

    # key errors (missing form entries) as well as
    # value errors are translated as 400 Bad Request
    except (ValueError, KeyError) as err:
        # Log
        log("Exception: %s" % err)
        # Response
        print("Status: 400 Bad Request\n")

        # all other errors are reported as 500 Internal Server Error
    except Exception as err:
        # Log
        log("Exception: %s" % err)
        traceback.print_exc()
        # Response
        print("Status: 500 Internal Server Error\n")


main_program()
