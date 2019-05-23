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

from contextlib import closing
import cgi

import traceback

# db connection
import psycopg2

# to validate the point received
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec

from common import *


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


def db_retrieve_cert(conn, values_dict):

    with conn.cursor() as cur:
        cur.execute(RETRIEVE_STMT,
                    (values_dict['serial_nr'],
                     values_dict['serial_info']))
        if cur.rowcount > 0:
            return cur.fetchone()[0]
    return None


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

###########################################################################
#
# Output common
#
###########################################################################

def send_certificate_response(cert):
    ''' send back a certificate response '''
    cert_b64 = binascii.b2a_base64(cert).decode('ascii')
    send_response_body(cert_b64)


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
# Return some information: fpk4 modulus, certificate
#
########################################################################
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

    with closing(psycopg2.connect("dbname=enrollment_db")) as db_conn:
        cert = db_retrieve_cert(db_conn, values_dict)

    if cert is None:
        print("Status: 404 Not Found\n")
    else:
        send_certificate_response(cert)


def process_query():

    form = cgi.FieldStorage()
    cmd = safe_form_get(form, "cmd", "modulus")
    if cmd == "modulus":
        send_modulus(form, "fpk4")
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
