########################################################
#
# test_enrollment_server.py
#
# Copyright (c) Fungible,inc. 2019
#
########################################################


import argparse
import requests
import subprocess
import traceback
import re
import binascii
import configparser
import json
import warnings
import urllib3

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


def quiet(*args, **kw_args):
    pass

def compare_with_expected(text_result, expected_result, print_fn=print):

    if text_result.rstrip() == expected_result.rstrip():
        print_fn("Success")
        return 0
    else:
        print_fn("Mismatch")
        print_fn("Response=\n%s" % text_result)
        print_fn("Expected=\n%s" % expected_result)
        return 1


def enroll_cert_gen(server, infile, expected_output, tls_verify, verbose=True):

    url_str = "https://" + server + "/cgi-bin/" + CGI_SCRIPT

    response = requests.put(url_str,
                            data=open(infile, 'rb').read(),
                            verify=tls_verify)

    return compare_with_expected(response.text, expected_output,
                                 print if verbose else quiet)

def retrieve_enroll_cert(server, sn, expected_output, tls_verify, verbose=True):

    url_str = "https://" + server + "/cgi-bin/" + CGI_SCRIPT

    response = requests.get(url_str,
                            params={'cmd':'cert', 'sn':sn},
                            verify=tls_verify)

    return compare_with_expected(response.text, expected_output,
                                 print if verbose else quiet)


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


def retrieve_x509_cert(server, sn, sn_hex, key_length,
                       cert_64, tls_verify):

    errors = 0

    cert_bin = binascii.a2b_base64(cert_64)
    pub_key_bin = cert_bin[KEY_OFFSET:KEY_OFFSET+ (2 * key_length)]
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

    curve_params = CURVES[key_length]
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



# This test is best run by first deleting the record for SN = 1234 from the database
def main_program():

    errors = 0

    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--server", dest="server",
                        default="f1reg.fungible.com",
                        help="Ip address or DNS name of server to test")

    options = parser.parse_args()

    tls_verify = True if options.server == "f1reg.fungible.com" else False

    if not tls_verify:
        warnings.simplefilter('ignore',
                              category=urllib3.exceptions.InsecureRequestWarning)

    test_cases = (('./tbs_enrollment_cert.txt',
                   './enrollment_cert.txt', 32),
                  ('./tbs_enrollment_cert_384.txt',
                   './enrollment_cert_384.txt', 48))

    fpk4_hex = open('./fpk4_hex.txt', 'r').read()

    try:
        errors += retrieve_modulus(options.server, fpk4_hex, tls_verify)

        errors += retrieve_x509_root_cert(options.server, fpk4_hex, tls_verify)

        for test_case in test_cases:
            tbs_file = test_case[0]
            cert_file = test_case[1]
            key_length = test_case[2]

            tbs = open(tbs_file, 'r').read()
            tbs_bin = binascii.a2b_base64(tbs)

            sn_bin = tbs_bin[SERIAL_NR_OFFSET:
                             SERIAL_NR_OFFSET+SERIAL_NR_LENGTH]
            sn_64 = binascii.b2a_base64(sn_bin).rstrip().decode('utf-8')
            sn_hex = binascii.b2a_hex(sn_bin).decode('utf-8')

            print("\n\n%s" % sn_hex)

            case_errors = 0
            enroll_cert = open(cert_file, 'r').read() if cert_file else None

            if retrieve_enroll_cert(options.server,
                                    sn_64,
                                    enroll_cert,
                                    tls_verify,
                                    False) == 0:
                print("Certificate already in database\n")

            else:
                # do an enroll_cert to generate the cert -- no cert will be returned
                # so ignore errors
                enroll_cert_gen(options.server,
                                tbs_file,
                                enroll_cert,
                                tls_verify,
                                False)

            # should retrieve a cert there when enrolling again or when cert
            # was in database
            case_errors += enroll_cert_gen(options.server,
                                           tbs_file,
                                           enroll_cert,
                                           tls_verify)

            case_errors += retrieve_enroll_cert(options.server,
                                                sn_64,
                                                enroll_cert,
                                                tls_verify)

            case_errors += retrieve_enroll_cert(options.server,
                                                sn_hex,
                                                enroll_cert,
                                                tls_verify)

            case_errors += retrieve_x509_cert(options.server,
                                              sn_64, sn_hex, key_length,
                                              enroll_cert,
                                              tls_verify)

            case_errors += retrieve_x509_cert(options.server,
                                              sn_hex, sn_hex, key_length,
                                              enroll_cert,
                                              tls_verify)
            print("Test case for sn %s: %d errors" % (sn_hex, case_errors))

            errors += case_errors

    except Exception as ex:
        traceback.print_exc()
        errors += 1

    print("Test completed on server %s with %d errors" % (options.server, errors))


if __name__=="__main__":
    main_program()
