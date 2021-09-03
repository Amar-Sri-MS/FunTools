#! /usr/bin/env python3

##############################################################################
#  enrollment_server.py
#
#
#  Copyright (c) 2018-2020. Fungible, inc. All Rights Reserved.
#
##############################################################################

import sys
import binascii
import struct
import os
import datetime
import hashlib
import json

from contextlib import closing
import cgi

import traceback

# db connection
import psycopg2


# certificate generation
from asn1crypto import pem, core, keys, x509

# to validate the point received
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec

from common import *

# serial number validation
import sn_validation


PUF_KEY_COORD_LEN = 32
ROOT_CERTIFICATE_PATH_NAME = 'enrollment_root_cert.der'

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
    ('puf_key', 2 * PUF_KEY_COORD_LEN),
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
    # slice the cert into constituent buffers
    slicer = make_slicer_of(cert)
    values = {desc[0]: slicer(desc[1]) for desc in CERT_DESC}

    with conn.cursor() as cur:
        cur.execute(INSERT_STMT, values)

    conn.commit()


def db_retrieve_cert(conn, values_dict):

    with conn.cursor() as cur:
        cur.execute(RETRIEVE_STMT,
                    (values_dict['serial_nr'],
                     values_dict['serial_info']))
        if cur.rowcount > 0:
            return cur.fetchone()[0]
    return None

def db_print_summary(conn):
    print("[")
    with conn.cursor('summary') as cur:
        cur.execute('''select row_to_json(t) from (
        select serial_info, serial_nr, puf_key, timestamp from enrollment ) t ''')
        first = True
        for row in cur:
            if first:
                first = False
            else:
                print(",")
            print(json.dumps(row[0]), end="")
    print("\n]")


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
    x = int.from_bytes(ec_pt[:PUF_KEY_COORD_LEN], byteorder='big')
    y = int.from_bytes(ec_pt[PUF_KEY_COORD_LEN:], byteorder='big')

    # this will raise a ValueError if x and y do not represent a point on the curve
    pub_key = ec.EllipticCurvePublicNumbers(x,
                                            y,
                                            ec.SECP256R1()).public_key(backend=default_backend())

    # validate serial info: this routines should raise a ValueError
    # if the serial number is not correct
    sn_validation.check(values_dict['serial_info'], values_dict['serial_nr'])


###########################################################################
#
# X509 routines
#
###########################################################################

def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')


def x509_serial_number(hash_input):
    # serial number is going to be hash of input with the current time
    hash = hashlib.sha1(hash_input)
    ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
    hash.update(struct.pack('>d', ts))
    # return digest as integer
    return int.from_bytes(hash.digest(),byteorder='big')

def x509_basic_constraints(critical, ca, path_len=None):

    basic_constraints = x509.BasicConstraints()
    basic_constraints['ca'] = ca
    if path_len:
        basic_constraints['path_len_contraint'] = path_len
    bc_extension = x509.Extension()
    bc_extension['extn_id'] = 'basic_constraints'
    bc_extension['critical'] = critical
    bc_extension['extn_value'] = basic_constraints
    return bc_extension

def x509_key_usage(critical, key_usages):
    key_usage = x509.KeyUsage()
    key_usage.set(key_usages)
    ku_extension = x509.Extension()
    ku_extension['extn_id'] = 'key_usage'
    ku_extension['critical'] = critical
    ku_extension['extn_value'] = key_usage
    return ku_extension

def x509_key_identifier(pub_key_info):
    key_id = core.OctetString()
    key_id.set(pub_key_info.sha1)
    ki_extension = x509.Extension()
    ki_extension['extn_id'] = 'key_identifier'
    ki_extension['critical'] = False
    ki_extension['extn_value'] = key_id
    return ki_extension

def x509_auth_key_identifier(key_id):
    aki_value = x509.AuthorityKeyIdentifier()
    aki_value['key_identifier'] = key_id
    aki_extension = x509.Extension()
    aki_extension['extn_id'] = 'authority_key_identifier'
    aki_extension['critical'] = False
    aki_extension['extn_value'] = aki_value
    return aki_extension

def x509_tbs_cert(values, parent_cert):

    DEFAULT_DAYS_VALID = 365

    ## the only information needed is the Serial Number and the Public Key
    serial_info = values['serial_info']
    serial_nr = values['serial_nr']
    key = values['puf_key']

    tbs = x509.TbsCertificate()
    tbs['version'] = 2
    tbs['serial_number'] = x509_serial_number(serial_info.tobytes() +
                                              serial_nr.tobytes() +
                                              key.tobytes())

    # build signature
    signature = x509.SignedDigestAlgorithm()
    signature['algorithm'] = 'sha512_rsa'
    tbs['signature'] = signature

    # issuer: subject of parent
    tbs['issuer'] = parent_cert.subject

    # validity
    not_before = x509.UTCTime()
    start_dt = datetime.datetime.now(datetime.timezone.utc)
    not_before.set(start_dt)
    not_after = x509.UTCTime()
    not_after.set(start_dt + datetime.timedelta(days=DEFAULT_DAYS_VALID))
    validity = x509.Validity()
    validity['not_before'] = not_before
    validity['not_after'] = not_after
    tbs['validity'] = validity

    # subject: CommonName, Serial Number, Organization Name
    serial_info_hex = binascii.b2a_hex(serial_info)
    serial_nr_hex = binascii.b2a_hex(serial_nr)
    full_serial_nr = (serial_info_hex + serial_nr_hex).decode('utf-8')
    subject_names = { "common_name" : "FUNGIBLE_" + full_serial_nr,
                      "serial_number" : full_serial_nr,
                      "organization_name" : "Fungible,Inc." }
    tbs['subject'] = x509.Name.build(subject_names)

    # subject public key info
    Qx = int.from_bytes(key[:PUF_KEY_COORD_LEN], byteorder='big')
    Qy = int.from_bytes(key[PUF_KEY_COORD_LEN:], byteorder='big')

    ecpt_bit_string = keys.ECPointBitString().from_coords(Qx,Qy)

    named_curve = keys.NamedCurve()
    named_curve.set('secp256r1')
    public_key_algo = keys.PublicKeyAlgorithm()
    public_key_algo['algorithm'] = 'ec'
    public_key_algo['parameters'] = named_curve

    public_key_info = keys.PublicKeyInfo()
    public_key_info['algorithm'] = public_key_algo
    public_key_info['public_key'] = ecpt_bit_string

    tbs['subject_public_key_info'] = public_key_info

    # extensions
    extensions = x509.Extensions()
    extensions.append(x509_basic_constraints(True, False))
    extensions.append(x509_key_usage(True,
                                     set(['digital_signature',
                                          'key_agreement'])))
    extensions.append(x509_key_identifier(public_key_info))

    parent_key_identifier = parent_cert.key_identifier_value
    if parent_key_identifier:
        extensions.append(x509_auth_key_identifier(parent_key_identifier))

    tbs['extensions'] = extensions

    return tbs

def x509_cert(values, parent_cert):

    cert = x509.Certificate()

    tbs = x509_tbs_cert(values, parent_cert)
    cert['tbs_certificate'] = tbs
    cert['signature_algorithm'] = tbs['signature']

    # sign with key in parent cert -- TODO
    parent_pub_key = parent_cert.public_key
    # do not use wrap/unwrap because asn1crypto has deprecated them
    # in some versions
    if parent_pub_key.algorithm != 'rsa':
        raise ValueError("Signing Certificate: unsupported algorithm")

    # pub key is a ParsableOctetBitString and parsed will retunr an rsa pub key
    rsa_pub_key = parent_pub_key['public_key'].parsed
    modulus = int_to_bytes(int(rsa_pub_key['modulus']))

    with get_ro_session() as session:
        private = get_private_rsa_with_modulus(session, modulus)
        raw_signature = sign_with_key(session, 'fpk4', tbs.dump())

    # package the raw signature
    bit_str = core.OctetBitString()
    bit_str.set(raw_signature)
    cert['signature_value'] = bit_str

    return cert


def x509_from_fungible_cert(cert, parent_cert_file):
    ''' generate a X509 certificate for the device based
    on the enrollment certificate '''

    # load the parent signing certificate
    parent_cert_bytes = open(parent_cert_file, 'rb').read()
    if pem.detect(parent_cert_bytes):
        _,_,parent_cert_bytes = pem.unarmor(parent_cert_bytes)

    parent_cert = x509.Certificate.load(parent_cert_bytes)

    slicer = make_slicer_of(cert)
    values = {desc[0]: slicer(desc[1]) for desc in CERT_DESC}

    return x509_cert(values, parent_cert)


###########################################################################
#
# Output
#
###########################################################################

def send_certificate_response(cert):
    ''' send back a certificate response '''
    cert_b64 = binascii.b2a_base64(cert).decode('ascii')
    send_response_body(cert_b64)


def send_x509_certificate_response(cert, parent_cert_file):
    ''' send back a X509 certificate '''
    cert = x509_from_fungible_cert(cert, parent_cert_file)
    # return the PEM encoded value
    x509_pem = pem.armor('CERTIFICATE', cert.dump())
    send_response_body(x509_pem.decode('ascii'))


def send_x509_root_certificate_response(parent_cert_file):
    ''' send back the X509 certificate '''
    x509_pem = open(parent_cert_file, 'rb').read()
    if not pem.detect(x509_pem):
        x509_pem = pem.armor('CERTIFICATE', x509_pem)
    send_response_body(x509_pem.decode('ascii'))


##########################################################################
#
# Enrollment
#
##########################################################################

def hsm_sign( tbs_cert):
    with get_ro_session() as session:
        return sign_binary(session, 'fpk4', tbs_cert)

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

    with closing(psycopg2.connect("dbname=enrollment_db")) as db_conn:
        cert = db_retrieve_cert(db_conn, values_dict)
        if cert is None:
            # sign the tbs_cert
            cert = hsm_sign(tbs_cert)
            # store it
            db_store_cert(db_conn, cert)

    send_certificate_response(cert)


########################################################################
#
# certificate
#
########################################################################
def send_certificate(form_values, x509_format=False):

    sn_64 = safe_form_get(form_values, "sn", None)
    if not sn_64:
        # if there is no serial number, return the X509 root cert
        if x509_format:
            send_x509_root_certificate_response(ROOT_CERTIFICATE_PATH_NAME)
            return


        raise ValueError("Missing parameter")

    sn = binascii.a2b_base64(sn_64)
    if len(sn) != SN_LEN:
        raise ValueError("SN length = %d" % len(sn))

    # slice the sn into constituent buffers
    slicer = make_slicer_of(sn)
    values_dict = {desc[0]: slicer(desc[1]) for desc in SN_DESC }

    with closing(psycopg2.connect("dbname=enrollment_db")) as db_conn:
        cert = db_retrieve_cert(db_conn, values_dict)

    if cert is None:
        print("Status: 404 Not Found\n")
        return

    if x509_format:
        send_x509_certificate_response(cert, ROOT_CERTIFICATE_PATH_NAME)
    else:
        send_certificate_response(cert)

def send_summary(form_values):

    print("Status: 200 OK")
    print("Content-Type: application/json\n")
    with closing(psycopg2.connect("dbname=enrollment_db")) as db_conn:
        db_print_summary(db_conn)
    print("\n")


def process_query():

    form = cgi.FieldStorage()
    cmd = safe_form_get(form, "cmd", "modulus")
    if cmd == "modulus":
        send_modulus(form, "fpk4")
    elif cmd == "cert":
        send_certificate(form)
    elif cmd == "x509":
        send_certificate(form, x509_format=True)
    elif cmd == "summary":
        send_summary(form)
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
