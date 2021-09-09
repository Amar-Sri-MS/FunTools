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

CGI_SCRIPT="enrollment_server.cgi"

RECV_ROOT_CERT_FILE = 'recv_root_cert.pem'
RECV_CERT_FILE = 'recv_cert.pem'

SUBJECT_SN_RE = r'serialNumber = (\w+)'
SUBJECT_CN_RE = r'CN = (\w+)'

KEY_OFFSET = 32
KEY_LENGTH = 64

def compare_with_expected(text_result, expected_output):

    expected_out = open(expected_output, 'r').read()

    if text_result.rstrip() == expected_out.rstrip():
        print("Success")
        return 0
    else:
        print("Mismatch")
        print("Response=\n%s" % text_result)
        print("Expected=\n%s" % expected_out)
        return 1

def enroll_cert_gen(server, infile, expected_output, tls_verify):

    url_str = "https://" + server + "/cgi-bin/" + CGI_SCRIPT

    response = requests.put(url_str,
                            data=open(infile, 'rb').read(),
                            verify=tls_verify)

    return compare_with_expected(response.text, expected_output)


def retrieve_enroll_cert(server, sn, expected_output, tls_verify):

    url_str = "https://" + server + "/cgi-bin/" + CGI_SCRIPT

    response = requests.get(url_str,
                            params={'cmd':'cert', 'sn':sn},
                            verify=tls_verify)

    return compare_with_expected(response.text, expected_output)

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


def retrieve_x509_cert(server, sn, enroll_cert, tls_verify):

    errors = 0

    sn_bin = binascii.a2b_base64(sn)
    sn_hex = binascii.b2a_hex(sn_bin).decode('ascii')

    cert_64 = open(enroll_cert, 'r').read()
    cert_bin = binascii.a2b_base64(cert_64)
    pub_key_bin = cert_bin[KEY_OFFSET:KEY_OFFSET+KEY_LENGTH]
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

    key_info = configparser.ConfigParser()
    key_info.read_string(key_out)
    if key_info.get('key', 'nist curve') != 'P-256':
        errors += 1
    if key_info.get('key', 'asn1 oid') != 'prime256v1':
        errors += 1

    # compare the key
    pub = key_info.get('key', 'pub')
    # remove all the non hexadecimal characters in this string (:, \n, )
    hex_set = set('abcdefABCDEF0123456789')
    key_hex = ''.join(c for c in pub if c in hex_set)
    # remove the format indicator (04)
    key_hex = key_hex[2:]

    if key_hex.lower() != pub_key_hex.lower():
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

    try:
        errors += enroll_cert_gen(options.server,
                                  './tbs_enrollment_cert.txt',
                                  './enrollment_cert.txt',
                                  tls_verify)
        errors += retrieve_enroll_cert(options.server,
                                       'AAAAAAAAAAAAAAAAAAAAAAAAAAAAABI0',
                                       './enrollment_cert.txt',
                                       tls_verify)

        errors += retrieve_modulus(options.server,
                                   './fpk4_hex.txt',
                                   tls_verify)

        errors += retrieve_x509_root_cert(options.server,
                                          './fpk4_hex.txt',
                                          tls_verify)

        errors += retrieve_x509_cert(options.server,
                                     'AAAAAAAAAAAAAAAAAAAAAAAAAAAAABI0',
                                     './enrollment_cert.txt',
                                     tls_verify)


    except Exception as ex:
        traceback.print_exc()
        errors += 1

    print("Test completed on server %s with %d errors" % (options.server, errors))


if __name__=="__main__":
    main_program()
