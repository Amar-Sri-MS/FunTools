#! /usr/bin/env python3.9

##############################################################################
#  enrollment_server.py
#
#
#  Copyright (c) 2018-2020. Fungible, inc. All Rights Reserved.
#  Copyright (c) 2023. Microsoft Corporation. All Rights Reserved.
#
##############################################################################

''' module implementing chip enrollment: enrollment certificate generation,
provision and storage
'''

import sys
import binascii
import struct
import os
import string
import datetime
import hashlib
import json

import cgi

import traceback

# certificate generation
from asn1crypto import pem, core, keys, x509

# to validate the point received
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec

from psycopg2 import sql

from common import (log,
                    send_response_body,
                    send_binary_buffer)

from db_helper import (SN_DESC,
                       SN_LEN,
                       ID_FLD,
                       make_slicer_of,
                       insert_select_chip_id,
                       get_sn_values,
                       pack_bytes_with_len_prefix,
                       db_func)


# serial number validation
import sn_validation

# signature and keys
from openssl_esrp import (esrp_get_modulus,
                          esrp_get_public_key,
                          esrp_sign_hash_with_key)

#################################################################################
#
# Database routines
#
#################################################################################

PUF_KEY_COORD_LENS = [32, 48]

TBS_CERT_DESCS = [
    (
        ('magic', 4),
        ('flags', 4),
    ) + SN_DESC + (
        ('puf_key', 2 * coord_len),
        ('nonce', 48),
        ('activation_code', 888),
    ) for coord_len in PUF_KEY_COORD_LENS]

CERT_DESCS = [ tbs_cert_desc + (('rsa_signature', 516),)
               for tbs_cert_desc in TBS_CERT_DESCS]

TBS_CERT_LEN_MAP = { sum(desc[1] for desc in tbs_cert_desc) : tbs_cert_desc
                     for tbs_cert_desc in TBS_CERT_DESCS}

CERT_LEN_MAP = {sum(desc[1] for desc in cert_desc) : cert_desc
             for cert_desc in CERT_DESCS}

def get_desc_for_cert(cert):
    return CERT_LEN_MAP.get(len(cert))

def get_desc_for_tbs_cert(tbs_cert):
    return TBS_CERT_LEN_MAP.get(len(tbs_cert))

def get_cert_values(cert):
    ''' slice the cert into constituent buffers dictionary '''
    slicer = make_slicer_of(cert)
    return {desc[0]: slicer(desc[1]) for desc in get_desc_for_cert(cert) }


# fields are the same so used CERT_DESCS[0]
FIELDS = [desc[0] for desc in CERT_DESCS[0]]
FIELDS_CONCAT = " || ".join(FIELDS)


# psycopg2 parameters are always represented by %s
# retrieve from the view
RETRIEVE_STMT_ROOT = "SELECT " + FIELDS_CONCAT + " FROM enrollment_certs_v "
RETRIEVE_STMT = RETRIEVE_STMT_ROOT + "WHERE serial_info = %s AND serial_nr = %s"
RETRIEVE_STMT_BY_ID = RETRIEVE_STMT_ROOT + " WHERE " + ID_FLD + " = %s"

# insertion
#specific enroll_cert_fields: chip_id + all - SN_DESC
ENROLL_CERT_FIELDS = [ID_FLD] + [desc[0] for desc in CERT_DESCS[0]
                                  if not desc in SN_DESC]
ENROLL_CERT_FIELDS_LIST = ",".join(ENROLL_CERT_FIELDS)
ENROLL_CERT_ARGS_LIST = ",".join([f"%({fld})s" for fld in ENROLL_CERT_FIELDS])

INSERT_ENROLL_CERT_STMT  = "INSERT INTO enrollment_certs (" + \
    ENROLL_CERT_FIELDS_LIST + ") VALUES (" + ENROLL_CERT_ARGS_LIST + " ) "

def db_store_cert(conn, cert):
    ''' store the full certificate in the database '''
    values = get_cert_values(cert)
    with conn.cursor() as cur:
        values[ID_FLD] = insert_select_chip_id(cur,
                                                  values['serial_info'],
                                                  values['serial_nr'])
        cur.execute(INSERT_ENROLL_CERT_STMT, values)
    conn.commit()

def db_retrieve_cert_by_values(conn, values_dict):
    ''' retrieve the cert for the serial number '''
    with conn.cursor() as cur:
        cur.execute(RETRIEVE_STMT,
                    (values_dict['serial_info'],
                     values_dict['serial_nr']))
        row = cur.fetchone()
        if row:
            return row[0]
        return None

def db_retrieve_cert_with_sn(conn, sn):
    ''' retrieve the certificate based on serial number '''
    if len(sn) != SN_LEN:
        raise ValueError(f"SN length = {len(sn)}")
    # slice the sn into constituent buffers
    return db_retrieve_cert_by_values(conn, get_sn_values(sn))


def db_retrieve_cert_with_id(conn, cert_id):
    ''' retrieve the certificate based on id '''
    with conn.cursor() as cur:
        cur.execute(RETRIEVE_STMT_BY_ID, (cert_id,))
        row = cur.fetchone()
        if row:
            return row[0]
        return None


def db_print_summary(conn, fld_list):
    ''' generate listing of specified fields for all certificates '''
    # safely generate the dynamic list of fields
    fields=sql.SQL(',').join(
        sql.Identifier(fld_name) for fld_name in fld_list)
    # safely generate the dynamic query
    query = sql.SQL('select row_to_json(t) from (select {0} from enrollment_certs_v) t'
                    ).format(fields)

    print("[")
    with conn.cursor('summary') as cur:
        cur.execute(query)
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

def pt_to_curve(pt):
    ''' point -> x, y, EC curve '''
    coord_len = len(pt)//2
    x = int.from_bytes(pt[:coord_len], byteorder='big')
    y = int.from_bytes(pt[coord_len:], byteorder='big')
    curve = ec.SECP256R1 if coord_len == 32 else ec.SECP384R1
    return x, y, curve

def validate_tbs_cert(tbs_cert):
    ''' perform some validation on the input '''

    tbs_desc = get_desc_for_tbs_cert(tbs_cert)

    if not tbs_desc:
        raise ValueError("Invalid length for TBS enrollment certificate")

    slicer = make_slicer_of(tbs_cert)
    values = {desc[0]: slicer(desc[1]) for desc in tbs_desc}

    # check magic
    if values['magic'] != b'\x1e\x5c\x00\xb1':
        raise ValueError(f"Bad Magic: {values}")

    # check the point is on the correct curve
    x, y, curve = pt_to_curve(values['puf_key'])
    # will raise a ValueError if x and y do not represent a point on the curve
    _ = ec.EllipticCurvePublicNumbers(x, y, curve()).public_key(
        backend=default_backend())

    # validate serial info: this routines should raise a ValueError
    # if the serial number is not correct
    sn_validation.check(values['serial_info'], values['serial_nr'])

    return values


###########################################################################
#
# X509 routines
#
###########################################################################

def int_to_bytes(x):
    ''' convert x to the minimum number of big endian bytes '''
    return x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')


def x509_serial_number(hash_input):
    ''' generate a X509 serial number using the digest '''
    # serial number is going to be hash of input with the current time
    hash_op = hashlib.sha1(hash_input)
    ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
    hash_op.update(struct.pack('>d', ts))
    # return digest as integer
    return int.from_bytes(hash_op.digest(), byteorder='big')

def x509_basic_constraints(critical, ca, path_len=None):
    ''' generate X.509 basic constraints extension '''
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
    ''' generate X.509 Key Usage extension '''
    key_usage = x509.KeyUsage()
    key_usage.set(key_usages)
    ku_extension = x509.Extension()
    ku_extension['extn_id'] = 'key_usage'
    ku_extension['critical'] = critical
    ku_extension['extn_value'] = key_usage
    return ku_extension

def x509_key_identifier(pub_key_info):
    ''' generate X.509 Key Identifier '''
    key_id = core.OctetString()
    key_id.set(pub_key_info.sha1)
    ki_extension = x509.Extension()
    ki_extension['extn_id'] = 'key_identifier'
    ki_extension['critical'] = False
    ki_extension['extn_value'] = key_id
    return ki_extension

def x509_auth_key_identifier(key_id):
    ''' generate X.509 Authority Key Identifier '''
    aki_value = x509.AuthorityKeyIdentifier()
    aki_value['key_identifier'] = key_id
    aki_extension = x509.Extension()
    aki_extension['extn_id'] = 'authority_key_identifier'
    aki_extension['critical'] = False
    aki_extension['extn_value'] = aki_value
    return aki_extension

def x509_tbs_cert(values, parent_cert):
    ''' generate a ToBeSigned X.509 Certificate '''
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
    not_before = x509.GeneralizedTime()
    start_dt = datetime.datetime.now(datetime.timezone.utc)
    start_dt = start_dt.replace(microsecond = 0) # asn1 crypto bug
    not_before.set(start_dt)
    not_after = x509.GeneralizedTime()
    not_after.set(start_dt + datetime.timedelta(days=DEFAULT_DAYS_VALID))
    validity = x509.Validity()
    validity['not_before'] = not_before
    validity['not_after'] = not_after
    tbs['validity'] = validity

    # subject: CommonName, Serial Number, Organization Name
    serial_info_hex = binascii.b2a_hex(serial_info)
    serial_nr_hex = binascii.b2a_hex(serial_nr)
    full_serial_nr = (serial_info_hex + serial_nr_hex).decode('utf-8')
    subject_names = { "serial_number" : full_serial_nr,
                      "organization_name" : "Fungible" }
    tbs['subject'] = x509.Name.build(subject_names)

    # subject public key info
    Qx, Qy, curve = pt_to_curve(key)
    ecpt_bit_string = keys.ECPointBitString().from_coords(Qx,Qy)

    named_curve = keys.NamedCurve()
    named_curve.set(curve.name)
    public_key_algo = keys.PublicKeyAlgorithm()
    public_key_algo['algorithm'] = 'ec'
    public_key_algo['parameters'] = named_curve

    public_key_info = keys.PublicKeyInfo()
    public_key_info['algorithm'] = public_key_algo
    public_key_info['public_key'] = ecpt_bit_string

    tbs['subject_public_key_info'] = public_key_info

    # extensions
    extensions = x509.Extensions()
    # for DICE/RIoT, make it a CA cert
    extensions.append(x509_basic_constraints(critical=True, ca=True))
    extensions.append(x509_key_usage(True,
                                     set(['digital_signature',
                                          'key_agreement',
                                          'key_cert_sign',
                                          'crl_sign'])))
    extensions.append(x509_key_identifier(public_key_info))

    parent_key_identifier = parent_cert.key_identifier_value
    if parent_key_identifier:
        extensions.append(x509_auth_key_identifier(parent_key_identifier))

    tbs['extensions'] = extensions

    return tbs


def x509_tbs_root_cert():
    ''' generate a ToBeSigned X.509 Certificate '''
    DEFAULT_DAYS_VALID = 365

    tbs = x509.TbsCertificate()
    tbs['version'] = 2
    tbs['serial_number'] = 0

    # build signature
    signature = x509.SignedDigestAlgorithm()
    signature['algorithm'] = 'sha512_rsa'
    tbs['signature'] = signature

    subject_names = { "common_name" :
                      "PUF EC Key Verification Root Cert (Convenience)",
                      "organization_name" : "Fungible",
                      "country_name" : "US"
                     }

    distinguished_name =x509.Name.build(subject_names)
    # issuer = subject
    tbs['issuer'] = tbs['subject'] = distinguished_name

    # validity
    not_before = x509.GeneralizedTime()
    start_dt = datetime.datetime.now(datetime.timezone.utc)
    start_dt = start_dt.replace(microsecond = 0) # asn1 crypto bug
    not_before.set(start_dt)
    not_after = x509.GeneralizedTime()
    not_after.set(start_dt + datetime.timedelta(days=DEFAULT_DAYS_VALID))
    validity = x509.Validity()
    validity['not_before'] = not_before
    validity['not_after'] = not_after
    tbs['validity'] = validity

    fpk4_pub_key_pem = esrp_get_public_key(0, 'fpk4')
    _,_,fpk4_pub_key_der = pem.unarmor(fpk4_pub_key_pem)
    public_key_info = keys.PublicKeyInfo().load(fpk4_pub_key_der)

    tbs['subject_public_key_info'] = public_key_info

    # extensions
    extensions = x509.Extensions()
    # for DICE/RIoT, make it a CA cert
    extensions.append(x509_basic_constraints(critical=True, ca=True))
    extensions.append(x509_key_usage(True,
                                     set(['digital_signature',
                                          'key_agreement',
                                          'key_cert_sign',
                                          'crl_sign'])))
    extensions.append(x509_key_identifier(public_key_info))

    tbs['extensions'] = extensions

    return tbs


def x509_cert(values, parent_cert):
    ''' generate a X.509 Certificate '''
    cert = x509.Certificate()

    if parent_cert:
        tbs = x509_tbs_cert(values, parent_cert)
    else:
        tbs = x509_tbs_root_cert()

    cert['tbs_certificate'] = tbs
    cert['signature_algorithm'] = tbs['signature']

    digest = hashlib.sha512(tbs.dump()).digest()
    raw_signature = esrp_sign_hash_with_key(0, 'fpk4', 'sha512', digest)

    # package the raw signature
    bit_str = core.OctetBitString()
    bit_str.set(raw_signature)
    cert['signature_value'] = bit_str

    return cert


def x509_from_fungible_cert(cert):
    ''' generate a X509 certificate for the device based
    on the enrollment certificate '''

    parent_cert = x509_cert(None, None)
    values =  get_cert_values(cert)

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


def send_x509_certificate_response(cert):
    ''' send back a X509 certificate '''
    cert = x509_from_fungible_cert(cert)
    sn = cert.subject.native['serial_number']
    # return the PEM encoded value
    x509_pem = pem.armor('CERTIFICATE', cert.dump())
    send_response_body(x509_pem.decode('ascii'),
                       'FUNGIBLE_' + sn + '.pem')


def send_x509_root_certificate_response():
    ''' send back the X509 certificate '''
    cert = x509_cert(None, None)
    x509_pem = pem.armor('CERTIFICATE', cert.dump())
    send_response_body(x509_pem.decode('ascii'),
                       'fpk4root.pem')


##########################################################################
#
# Enrollment
#
##########################################################################

def tbs_sign(tbs_cert):
    ''' Compute RAW signature for data '''
    digest = hashlib.sha512(tbs_cert).digest()
    signature = esrp_sign_hash_with_key(0, 'fpk4', 'sha512', digest)
    return tbs_cert + pack_bytes_with_len_prefix(signature, 516)

def select_insert_enroll_cert(db_conn, tbs_cert):
    ''' retrieve or generate and insert enrollment certificate with db '''
    values = validate_tbs_cert(tbs_cert)
    cert = db_retrieve_cert_by_values(db_conn, values)
    if cert is None:
        # sign the tbs_cert
        cert = tbs_sign(tbs_cert)
        # store it
        db_store_cert(db_conn, cert)
    return cert

def do_enroll():
    ''' process POST request
    return enrollment certificate -- generate one in db if not  there '''
    # read the TBS from request
    request = sys.stdin.read()
    tbs_cert = binascii.a2b_base64(request)
    cert = db_func(select_insert_enroll_cert, tbs_cert)
    send_certificate_response(cert)


########################################################################
#
# certificate
#
########################################################################

def get_sn_from_form(form):
    ''' retrieve serial number from request -- can be in several format '''
    sn = form.getvalue("sn", None)
    if not sn:
        return sn
    if len(sn) == 48 and all(c in string.hexdigits for c in sn):
        return binascii.a2b_hex(sn)
    return binascii.a2b_base64(sn)


def send_certificate(form, x509_format=False):
    ''' return a certificate from the request '''
    cert = None

    chip_id = form.getvalue("id", None)
    if chip_id:
        cert = db_func(db_retrieve_cert_with_id, chip_id)
    else:
        sn = get_sn_from_form(form)
        if sn:
            cert = db_func(db_retrieve_cert_with_sn, sn)
        else:
            # if there is no serial number, return the X509 root cert
            if x509_format:
                send_x509_root_certificate_response()
                return

            raise ValueError("Missing parameter")

    if cert is None:
        print("Status: 404 Not Found\n")
        return

    if x509_format:
        send_x509_certificate_response(cert)
    else:
        send_certificate_response(cert)


def send_summary(form):
    ''' send a listing of the enrollment certificates '''
    print("Status: 200 OK")
    print("Content-Type: application/json\n")
    fld_list = form.getvalue("fld",
                             ('serial_info',
                              'serial_nr',
                              'puf_key',
                              'timestamp'))
    if not isinstance(fld_list, list):
        fld_list = (fld_list,)

    db_func(db_print_summary, fld_list)
    print("\n")


def process_query():
    ''' process HTTP GET '''
    form = cgi.FieldStorage()
    cmd = form.getvalue("cmd", "modulus")
    if cmd == "modulus":
        modulus = esrp_get_modulus(0,"fpk4")
        send_binary_buffer(modulus, form)
    elif cmd == "cert":
        send_certificate(form)
    elif cmd == "x509":
        send_certificate(form, x509_format=True)
    elif cmd == "summary":
        send_summary(form)
    else:
        raise ValueError("Invalid command")

def main_program():
    ''' start of script '''
    # our content is always text/plain
    print("Content-type: text/plain")
    try:
        # get the request -- base64 encoded TBS
        method = os.environ["REQUEST_METHOD"]
        if method not in ("PUT", "GET"):
            raise ValueError(f"Invalid request method {method}")

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
        log(f"Exception: {err}: {traceback.print_exc()}")
        # Response
        print("Status: 400 Bad Request\n")

        # all other errors are reported as 500 Internal Server Error
    except Exception as err: # pylint: disable=broad-exception-caught
        # Log
        log(f"Exception: {err}\n{traceback.format_exc()}")
        # Response
        print("Status: 500 Internal Server Error\n")


main_program()
