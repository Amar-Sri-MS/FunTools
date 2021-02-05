#! /usr/bin/env python3
#
# cavp.py
# CAVP file parser
# Copyright (c) 2020. Fungible, Inc. All rights reserved.
#

''' Rationale: CAVP test files follow the same overall syntax
This module reads a CAVP test file, extract the tests from it based on
the syntax, calls the proper method to execute the tests and writes
the results to the CAVP response file
The response file is a copy of the request file with the result
appended to each individual test
'''

import os
import sys
import argparse
import requests
import json


from cryptography import exceptions
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec, utils
from cryptography.hazmat.backends import default_backend


CURVE_MAPPING = { 'P-192' : ec.SECP192R1,
                  'P-224' : ec.SECP224R1,
                  'P-256' : ec.SECP256R1,
                  'P-384' : ec.SECP384R1,
                  'P-521' : ec.SECP521R1 }

HASH_ALGO_MAPPING = { 'SHA1' : hashes.SHA1,
                      'SHA2-224' : hashes.SHA224,
                      'SHA2-256' : hashes.SHA256,
                      'SHA2-384' : hashes.SHA384,
                      'SHA2-512' : hashes.SHA512 }



def rreplace(s, old, new, maxreplace):
    ''' replace at most maxreplace occurences of old with new in s '''
    return new.join(s.rsplit(old, maxreplace))


def int_to_hex(x):
    ''' integer to hex big endian representation '''
    x_bytes = x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')
    return x_bytes.hex().upper()

def hex_to_int(s):
    ''' hex big endian to int representation '''
    return int(s, 16)


def collect_request_tests(req):

    ret_val = {}

    groups = req["testGroups"]
    for req_group in groups:
        tests = req_group["tests"]
        for test in tests:
            ret_val[test["tcId"]] = test
    return ret_val



def DSA_sigGen(resp, req):

    print("DSA Signature Generation")
    req_tests = collect_request_tests(req)

    groups = resp["testGroups"]

    for group in groups:

        print("Group %d" % group["tgId"])

        grp_hash_algo = HASH_ALGO_MAPPING.get(group["hashAlg"])
        p = hex_to_int(group["p"])
        q = hex_to_int(group["q"])
        g = hex_to_int(group["g"])
        y = hex_to_int(group["y"])
        grp_public_key = dsa.DSAPublicNumbers(y,
                                              dsa.DSAParameterNumbers(p, q, g)
                                              ).public_key()

        for test in group["tests"]:

            req_test = req_tests[test["tcId"]]
            data = bytes.fromhex(req_test["message"])
            signature = utils.encode_dss_signature(hex_to_int(test["r"]),
                                                   hex_to_int(test["s"]))
            try:
                grp_public_key.verify(signature, data, grp_hash_algo())
                print("%d: Pass" % test["tcId"])
            except exceptions.InvalidSignature:
                print("%d: Error: Invalid signature" % test["tcId"])


def RSA_sigGen(resp, req):
    pass


def ECDSA_sigGen(resp, req):
    print("ECDSA Signature Generation")
    req_tests = collect_request_tests(req)

    groups = resp["testGroups"]

    for group in groups:

        print("Group %d" % group["tgId"])

        grp_hash_algo = HASH_ALGO_MAPPING.get(group["hashAlg"])
        grp_curve = CURVE_MAPPING.get(group["curve"])

        qx = hex_to_int(group["qx"])
        qy = hex_to_int(group["qy"])

        grp_public_key = ec.EllipticCurvePublicNumbers(qx,qy,grp_curve()).public_key()
        prehashed = group["componentTest"]

        for test in group["tests"]:

            req_test = req_tests[test["tcId"]]
            data = bytes.fromhex(req_test["message"])
            signature = utils.encode_dss_signature(hex_to_int(test["r"]),
                                                   hex_to_int(test["s"]))

            try:
                if prehashed:
                    grp_public_key.verify(signature,
                                          data,
                                          ec.ECDSA(utils.Prehashed(grp_hash_algo())))
                else:
                    grp_public_key.verify(signature,
                                          data,
                                          ec.ECDSA(grp_hash_algo()))

                print("%d: Pass" % test["tcId"])
            except exceptions.InvalidSignature as exc:
                print("%d: Error: Invalid signature: %s" % (test["tcId"], exc))





#########################################
# CAVP Test Verifier
#

def verify(rsp_file, req_file):

    # load the whole file
    with open(rsp_file, 'r') as rspf:
        rsp = json.load(rspf)

    # load the whole file
    with open(req_file, 'r') as reqf:
        req = json.load(reqf)

    results = rsp[1]
    algo = results["algorithm"] + "_" + results["mode"]

    verifier = globals().get(algo)
    if verifier:
        verifier(results, req[1])
    else:
        print("No verifier for test %s" % algo)




class WebDavClient:

    DOWNLOAD_CHUNK_SIZE_BYTES = 1 * 1024 * 1024

    def __init__(self, baseurl, username=None, password=None):

        self.baseurl = baseurl
        self.cwd = '/'
        self.session = requests.session()
        self.session.stream = True

        if username and password:
            self.session.auth = requests.auth.HTTPDigestAuth(username, password)

    def _send(self, method, path, expected_code, **kwargs):
        url = self._get_url(path)
        response = self.session.request(method, url, allow_redirects=False, **kwargs)
        if isinstance(expected_code, int):
            if response.status_code != expected_code:
                raise RuntimeError("%s: %s : unexpected code %d" %
                                   (method, path, response.status_code))
        else:
            if response.status_code not in expected_code:
                raise RuntimeError("%s: %s : unexpected code %d" %
                                   (method, path, response.status_code))
        return response

    def _get_url(self, path):
        path = str(path).strip()
        if path.startswith('/'):
            return self.baseurl + path
        return "".join((self.baseurl, self.cwd, path))

    def cd(self, path):
        path = path.strip()
        if not path:
            return
        stripped_path = '/'.join(part for part in path.split('/') if part) + '/'
        if stripped_path == '/':
            self.cwd = stripped_path
        elif path.startswith('/'):
            self.cwd = '/' + stripped_path
        else:
            self.cwd += stripped_path

    def mkdir(self, path, safe=False):
        expected_codes = 201 if not safe else (201, 301, 405)
        self._send('MKCOL', path, expected_codes)

    def mkdirs(self, path):
        dirs = [d for d in path.split('/') if d]
        if not dirs:
            return
        if path.startswith('/'):
            dirs[0] = '/' + dirs[0]
        old_cwd = self.cwd
        try:
            for dir in dirs:
                try:
                    self.mkdir(dir, safe=True)
                except Exception as e:
                    if e.actual_code == 409:
                        raise
                finally:
                    self.cd(dir)
        finally:
            self.cd(old_cwd)

    def rmdir(self, path, safe=False):
        path = str(path).rstrip('/') + '/'
        expected_codes = 204 if not safe else (204, 404)
        self._send('DELETE', path, expected_codes)

    def delete(self, path):
        self._send('DELETE', path, 204)

    def upload(self, local_path_or_fileobj, remote_path):
        if isinstance(local_path_or_fileobj, str):
            with open(local_path_or_fileobj, 'rb') as f:
                self._upload(f, remote_path)
        else:
            self._upload(local_path_or_fileobj, remote_path)

    def _upload(self, fileobj, remote_path):
        self._send('PUT', remote_path, (200, 201, 204), data=fileobj)

    def download(self, remote_path, local_path_or_fileobj,depth=0):
        print(remote_path)
        response = self._send('GET', remote_path, 200, stream=True)

        if isinstance(local_path_or_fileobj, str):
            with open(local_path_or_fileobj, 'wb') as f:
                self._download(f, response)
        else:
            self._download(local_path_or_fileobj, response)

    def _download(self, fileobj, response):
        for chunk in response.iter_content(self.DOWNLOAD_CHUNK_SIZE_BYTES):
            fileobj.write(chunk)

    def exists(self, remote_path):
        response = self._send('HEAD', remote_path, (200, 301, 404))
        return True if response.status_code != 404 else False



def parse_args():

    parser = argparse.ArgumentParser(description="Verify CAVP Test")

    parser.add_argument('inputs', metavar='FILE', nargs='+',
                        help='Response files')
    parser.add_argument('-u', '--user',
                        help='user name (remote)')
    parser.add_argument('-p', '--password',
                        help='password (remote)')
    parser.add_argument('-r', '--remote', required=True,
                        help='HTTP URL where the files can be found')
    return parser.parse_args()


def execute_all_tests(args):
    # download the file, run the test, upload the file
    webclient = WebDavClient(args.remote, args.user, args.password)
    for arg in args.inputs:

        rsp_local = os.path.basename(arg)

        print("%s -> %s" % (arg, rsp_local))

        webclient.download(arg, rsp_local)

        req_fname = rreplace(arg, '.rsp', '.req', 1)
        req_local = os.path.basename(req_fname)

        print("%s -> %s" % (req_fname, req_local))
        webclient.download(req_fname, req_local)

        verify(rsp_local, req_local)


def main():
    args = parse_args()
    execute_all_tests(args)


if __name__ == '__main__':
    main()
