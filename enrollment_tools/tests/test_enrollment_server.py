########################################################
#
# test_enrollment_server.py
#
# Copyright (c) Fungible,inc. 2019
#
########################################################


import argparse
import requests

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

    url_str = "https://" + server + "/cgi-bin/enrollment_server.cgi"

    response = requests.put(url_str,
                            data=open(infile, 'rb').read(),
                            verify=tls_verify)

    return compare_with_expected(response.text, expected_output)


def retrieve_enroll_cert(server, sn, expected_output, tls_verify):

    url_str = "https://" + server + "/cgi-bin/enrollment_server.cgi"

    response = requests.get(url_str,
                            params={'cmd':'cert', 'sn':sn},
                            verify=tls_verify)

    return compare_with_expected(response.text, expected_output)

def retrieve_modulus(server, expected_output, tls_verify):

    url_str = "https://" + server + "/cgi-bin/enrollment_server.cgi"

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

    except Exception as ex:
        print("Exception occurred %s" % str(ex))
        errors += 1

    print("Test completed on server %s with %d errors" % (options.server, errors))


if __name__=="__main__":
    main_program()
