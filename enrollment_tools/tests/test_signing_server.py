########################################################
#
# test_signing_server.py
#
# Copyright (c) Fungible,inc. 2019
#
########################################################

import argparse
import requests
import binascii


def create_binary_form_data( infile):

    with open(infile, 'rb') as input:
        bin_data = input.read()
        return (infile, bin_data, 'application/octet-stream',
                {"Content-Length" : str(len(bin_data)) })

def image_gen(server, infile,
              ftype, version, description,
              sign_key, certfile, customer_certfile):

    url_str = "https://" + server + ":4443/cgi-bin/signing_server.cgi"

    multipart_form_data = { 'img' : create_binary_form_data(infile) }

    if certfile:
        multipart_form_data['cert'] = create_binary_form_data(certfile)

    if customer_certfile:
        multipart_form_data['customer_cert'] = create_binary_form_data(customer_certfile)

    params = { 'key' : sign_key, 'type': ftype, 'version' : version, 'description': description }

    response = requests.post(url_str,
                             files=multipart_form_data,
                             params=params)

    return response.content


def get_key(server, key_label):

    url_str = "https://" + server + ":4443/cgi-bin/signing_server.cgi"

    params = { 'cmd' : 'modulus', 'key' : key_label }

    response = requests.get(url_str,params=params)

    return response.content



####### tests

def test_get_binary_fpk4(server):
    fpk4 = get_key(server, 'fpk4')

    fpk4_text = open('./fpk4_hex.txt', 'r').read().rstrip()

    fpk4_exp = binascii.unhexlify(fpk4_text)

    if fpk4 == fpk4_exp:
        return 0

    return 1


def test_image_gen_with_key(server):

    signed_image = image_gen(server, './firmware_m5150.bin',
                             'frmw', 1, 'eSecure Firmware',
                             'fpk3', None, None)

    signed_image_exp = open('./signed_firmware_m5150.bin', 'rb').read()

    if signed_image == signed_image_exp:
        return 0

    return 1


def test_image_gen_with_cert(server):

    signed_image = image_gen(server, './puf_rom_m5150.bin',
                             'pufr', 1, 'eSecure PUF-ROM',
                             None, '../development_start_certificate.bin', None)

    signed_image_exp = open('./signed_puf_rom_m5150.bin', 'rb').read()

    if signed_image == signed_image_exp:
        return 0

    return 1

def main_program():
    errors = 0

    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--server", dest="server",
                        default="f1reg.fungible.com",
                        help="Ip address or DNS name of server to test")

    options = parser.parse_args()

    try:
        errors += test_get_binary_fpk4(options.server)
        errors += test_image_gen_with_key(options.server)
        errors += test_image_gen_with_cert(options.server)

    except Exception as ex:
        print("Exception occurred %s" % str(ex))
        errors += 1

    print("Test completed on server %s with %d errors" % (options.server, errors))


if __name__=="__main__":
    main_program()