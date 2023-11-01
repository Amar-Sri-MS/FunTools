########################################################
#
# test_enrollment_server.py
#
# Copyright (c) Fungible,inc. 2019
#
########################################################


import argparse
import subprocess
import traceback
import re
import binascii
import configparser
import warnings
import urllib3
import requests

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from test_signing_server import get_key


CGI_SCRIPT="enrollment_server.cgi"

RECV_ROOT_CERT_FILE = 'recv_root_cert.pem'
RECV_CERT_FILE = 'recv_cert.pem'

SUBJECT_SN_RE = r'serialNumber = (\w+)'
SUBJECT_CN_RE = r'CN = (\w+)'

SERIAL_NR_OFFSET = 8
SERIAL_NR_LENGTH = 24

KEY_OFFSET = SERIAL_NR_OFFSET + SERIAL_NR_LENGTH

NIST_CURVE = 'NIST curve'
ASN1_OID =   'asn1 oid'

CURVES = { 32: {ASN1_OID: 'prime256v1',
                NIST_CURVE : 'P-256' },
           48 : {ASN1_OID: 'secp384r1',
                 NIST_CURVE: 'P-384'} }


def compare_with_expected(text_result, expected_result):

    if text_result.rstrip() == expected_result.rstrip():
        print("Success")
        return 0

    print("Mismatch")
    print("Response=\n%s" % text_result)
    print("Expected=\n%s" % expected_result)
    return 1


def retrieve_modulus(server, expected_output, tls_verify):

    url_str = "https://" + server + "/cgi-bin/" + CGI_SCRIPT

    response = requests.get(url_str,
                            params={'cmd':'modulus', 'format':'hex'},
                            verify=tls_verify)

    errors = compare_with_expected(response.text, expected_output)

    # try to get another key -- should still get fpk4

    response =  requests.get(url_str,
                             params={'cmd':'modulus', 'format':'hex', 'key' : 'fpk2'},
                             verify=tls_verify)

    errors += compare_with_expected(response.text, expected_output)

    return errors



def verify_cert_response(response, tbs_64, fpk4, verbose):

    errs = 0
    cert_b64 = response.content # bytes
    cert_bin = binascii.a2b_base64(cert_b64)
    if len(cert_bin) < 516:
        errs+=1
        if verbose:
            print(cert_b64)
            print("cert length %d  < 516" % len(cert_bin))
        return errs

    f_signature = cert_bin[-516:] # last 516 bytes
    tbs_bin = cert_bin[:-516]   # all less signature

    if tbs_bin != binascii.a2b_base64(tbs_64):
        errs +=1
        if verbose:
            print(cert_b64)
            print("TBS received != TBS sent!")


    signature_len = int.from_bytes(f_signature[:4], byteorder='little')
    if signature_len > 512:
        errs+=1
        if verbose:
            print(cert_b64)
            print("signature length %d > 512" % signature_len)
        return errs

    signature = f_signature[4:4+signature_len]

    # verify signature
    try:

        fpk4.verify(signature, tbs_bin, padding.PKCS1v15(), hashes.SHA512())

    except Exception as ex:
        if verbose:
            print("Debugging Certificate verification failed: ex = %s" % ex)
        errs += 1

    return errs



def retrieve_enroll_cert(server, sn, tbs_64, fpk4, tls_verify, verbose=True):
    ''' test GET with Serial Number '''
    url_str = "https://" + server + "/cgi-bin/" + CGI_SCRIPT

    response = requests.get(url_str,
                            params={'cmd':'cert', 'sn':sn},
                            verify=tls_verify)

    return verify_cert_response(response, tbs_64, fpk4, verbose)


def enroll_cert_gen_verify(server, tbs_64, fpk4, tls_verify, verbose=True):
    ''' test PUT with whole TBS '''
    errs = 0
    url_str = "https://" + server + "/cgi-bin/" + CGI_SCRIPT

    response = requests.put(url_str,
                            data=tbs_64,
                            verify=tls_verify)

    return verify_cert_response(response, tbs_64, fpk4, verbose)



def retrieve_x509_root_cert(server, expected_modulus, tls_verify):

    url_str = "https://" + server + "/cgi-bin/" + CGI_SCRIPT

    response = requests.get(url_str,
                            params={'cmd':'x509'},
                            verify=tls_verify)

    # write the response as a certificate
    open(RECV_ROOT_CERT_FILE, 'w').write(response.text)

    # do a couple of OpenSSL checks
    # 1: modulus should be fpk4
    cmd = "openssl x509 -modulus -noout -in".split()
    cmd.append(RECV_ROOT_CERT_FILE)

    mod_str = subprocess.check_output(cmd).decode('ascii')

    if not mod_str.startswith('Modulus='):
        print("Openssl unexpected output: " + mod_str)
        return 1

    mod_str = mod_str[len('Modulus='):].lower()

    errors = compare_with_expected(mod_str, expected_modulus)

    # 2: should verify itself
    cmd = "openssl verify -CAfile".split()
    cmd.append(RECV_ROOT_CERT_FILE)
    cmd.append(RECV_ROOT_CERT_FILE)
    verified = subprocess.check_output(cmd).decode('ascii')

    if verified != RECV_ROOT_CERT_FILE + ': OK\n':
        print(verified)
        errors += 1

    return errors


def retrieve_x509_cert(server, sn, sn_hex, pub_key_bin, tls_verify):

    errors = 0

    pub_key_hex = binascii.b2a_hex(pub_key_bin).decode('ascii')

    url_str = "https://" + server + "/cgi-bin/" + CGI_SCRIPT

    response = requests.get(url_str,
                            params={'cmd':'x509', 'sn': sn },
                            verify=tls_verify)

    # write the response as a certificate
    open(RECV_CERT_FILE, 'w').write(response.text)

    # openssl checks
    # 1: subject
    cmd = "openssl x509 -subject -noout -in".split()
    cmd.append(RECV_CERT_FILE)
    subject = subprocess.check_output(cmd).decode('ascii')
    m = re.search(SUBJECT_SN_RE, subject)
    if not m:
        errors +=1
    elif m.group(1) != sn_hex:
        print("Mismatch serial number: {0} != {1}".format(m.group(1),sn_hex))
        errors += 1

    # 2: public key
    cmd = "openssl x509 -pubkey -noout -in " + RECV_CERT_FILE
    cmd += " | openssl ec -pubin -text -noout"
    # the output of openssl ec is parsable as a config file
    key_out = "[key]\n"  # dummy section required by configparser
    key_out += subprocess.check_output(cmd, shell=True).decode('ascii')

    curve_params = CURVES[len(pub_key_bin)//2]

    key_info = configparser.ConfigParser()
    key_info.read_string(key_out)
    curve_name = key_info.get('key', NIST_CURVE)
    if curve_name != curve_params[NIST_CURVE]:
        print("NIST Curve Name: %s expected %s" %
              (curve_name, curve_params[NIST_CURVE]))
        errors += 1

    curve_oid = key_info.get('key', ASN1_OID)
    if curve_oid != curve_params[ASN1_OID]:
        print("OID for curve: %s expected %s" %
              (curve_oid, curve_params[ASN1_OID]))
        errors += 1

    # compare the key
    pub = key_info.get('key', 'pub')
    # remove all the non hexadecimal characters in this string (:, \n, )
    hex_set = set('abcdefABCDEF0123456789')
    key_hex = ''.join(c for c in pub if c in hex_set)
    # remove the format indicator (04)
    key_hex = key_hex[2:]

    if key_hex.lower() != pub_key_hex.lower():
        print("Key error")
        print(key_hex)
        print(pub_key_hex)
        errors += 1

    # 3: verification with previously retrieved root cert
    cmd = "openssl verify -CAfile".split()
    cmd.append(RECV_ROOT_CERT_FILE)
    cmd.append(RECV_CERT_FILE)
    verified = subprocess.check_output(cmd).decode('ascii')

    if verified != RECV_CERT_FILE + ': OK\n':
        print(verified)
        errors += 1

    return errors



# This test is best run by first deleting the record for SN = 0000_0001 from the database
def main_program():

    errors = 0

    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--server", dest="server",
                        default="f1reg.fungible.com",
                        help="Ip address or DNS name of server to test")

    args = parser.parse_args()

    tls_verify = args.server.endswith(".fungible.com")

    if not tls_verify:
        warnings.simplefilter('ignore',
                              category=urllib3.exceptions.InsecureRequestWarning)

    test_cases = (('./tbs_enrollment_cert.txt', 32),
                  ('./tbs_enrollment_cert_posix.txt', 32),
                  ('./tbs_enrollment_cert_384.txt', 48),
                  ('./tbs_enrollment_cert_0001.txt', 48))  #"disposable" cert: 0000_0001 S/N

    try:

        # use signing server -- should be accessible
        fpk4_hex = get_key(args.server,
                           tls_verify,
                           'fpk4', oformat="hex").decode('ascii')

        errors += retrieve_modulus(args.server, fpk4_hex, tls_verify)

        errors += retrieve_x509_root_cert(args.server, fpk4_hex, tls_verify)

        fpk4 = rsa.RSAPublicNumbers(0x010001, int(fpk4_hex, 16)).public_key()

        for test_case in test_cases:
            tbs_file = test_case[0]
            key_length = test_case[1]

            tbs_64 = open(tbs_file, 'r').read()

            tbs_bin = binascii.a2b_base64(tbs_64)

            pk_bin = tbs_bin[KEY_OFFSET: KEY_OFFSET +  2 * key_length]

            sn_bin = tbs_bin[SERIAL_NR_OFFSET:
                             SERIAL_NR_OFFSET+SERIAL_NR_LENGTH]
            sn_64 = binascii.b2a_base64(sn_bin).rstrip().decode('utf-8')
            sn_hex = binascii.b2a_hex(sn_bin).decode('utf-8')

            print("\n\n%s" % sn_hex)

            sub_errs = 0

            if retrieve_enroll_cert(args.server, sn_64, tbs_64, fpk4,
                                    tls_verify, False) == 0:
                print("Certificate already in database\n")

            else:
                # do an enroll_cert to generate the cert -- no cert will be returned
                # so ignore errors
                enroll_cert_gen_verify(args.server, tbs_64, fpk4,
                                       tls_verify,False)

            # should retrieve a cert there when enrolling again or when cert
            # was in database
            sub_errs += enroll_cert_gen_verify(args.server, tbs_64, fpk4,
                                               tls_verify)

            sub_errs += retrieve_enroll_cert(args.server, sn_64, tbs_64, fpk4,
                                             tls_verify)

            sub_errs += retrieve_enroll_cert(args.server, sn_hex, tbs_64, fpk4,
                                             tls_verify)

            sub_errs += retrieve_x509_cert(args.server, sn_64, sn_hex, pk_bin,
                                           tls_verify)

            sub_errs += retrieve_x509_cert(args.server, sn_hex, sn_hex, pk_bin,
                                           tls_verify)


            print("Test case for sn %s: %d errors" % (sn_hex, sub_errs))

            errors += sub_errs

    except Exception:
        traceback.print_exc()
        errors += 1

    print("Test completed on server %s with %d errors" % (args.server, errors))


if __name__=="__main__":
    main_program()
