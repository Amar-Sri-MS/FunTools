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

# need to generate some RSA keys for RSA sig gen tests
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

import dpc_client

def rreplace(s, old, new, maxreplace):
    ''' replace at most maxreplace occurences of old with new in s '''
    return new.join(s.rsplit(old, maxreplace))


def int_to_hex(x):
    ''' integer to hex big endian representation '''
    x_bytes = x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')
    return x_bytes.hex()

######
# Tester classes
#


class AbsCAVPTestRunner:
    ''' abstract tester class '''
    def test(self, request):
        raise RuntimeError("abstract class called")


class TestTester(AbsCAVPTestRunner):
    ''' dummy tester class '''
    def test(self, request):
        #print(request)
        return {'md' : 'daa1e4c446d9c7f34bb8547b1339b901f536a7e4' }


class DPCCAVP(AbsCAVPTestRunner):
    ''' tester using DPC function '''

    def __init__(self):
        try:
            with open('./env.json', 'r') as f:
                env_dict = json.load(f)
            if len(env_dict['dpc_hosts']) < 1:
                raise RuntimeError('No DPC hosts!')
            # use the name and TCP port of the DPC proxy for 1st chip
            dpc_host = env_dict['dpc_hosts'][0]
            host = dpc_host['host']
            port = dpc_host['tcp_port']
            print('Using dpc host at %s:%s' % (host, port))
            self.dpc_client = dpc_client.DpcClient(server_address=(host, port))

        except FileNotFoundError:
            self.dpc_client = dpc_client.DpcClient()
            # no file try default

    def test(self, request):
        # package the request as JSON and send to FunOS
        execute_args = ['cavp', request]
        results = self.dpc_client.execute('execute', execute_args)
        print("Result = %s" % str(results))
        # result is a dictionary with either a key 'error' or a key 'result'
        if 'error' in results:
            raise RuntimeError("error returned by test %s: %s" %
                               (request, results['error']))
        elif 'result' in results:
            return results['result']

        raise RuntimeError("Results returned not understood: %s" %
                           results)




#########################################
# CAVP File Parser
#
class CAVPTest:

    def __init__(self, file_path, tester, suffix):
        self.req_file = os.path.abspath(file_path)
        self.rsp_file = rreplace(self.req_file, '.req', '.rsp', 1)
        self.tester = tester
        self.suffix = suffix


    def result_path(self):
        return self.rsp_file

    def run(self):
        meta_params = {} # global params for the file

        # load the whole file
        with open(self.req_file, 'r') as reqf:
            request = json.load(reqf)

        # hierarchy is [ {} {file_params, testGroups:[] } ]
        # each testGroup is { group_param, tests:[] }
        # each test is a dictionary with a field "tcId"

        # create response: first element of request
        response = [ request[0] ]

        # the file keys but without testGroups items
        file_params = {k:v for (k,v) in request[1].items() if k != "testGroups"}
        test_groups = []

        algorithm_mode = file_params["algorithm"]
        if file_params.get("mode"):
            algorithm_mode += "." + file_params.get("mode")

        for test_group in request[1]["testGroups"]:
            # add the test group keys but without tests items
            test_group_params = {k:v for (k,v) in test_group.items() if k != "tests" }
            tests = []

            # add more info if necessary:
            # req -> sent to tester, rsp -> written to response file
            test_group_params_req, test_group_params_rsp = self.augment_test_group(file_params,
                                                                                   test_group_params)

            # create a synthetic key "full_type" for ease of dispatching in FunOS
            full_type = algorithm_mode + "." + test_group_params["testType"]
            if self.suffix:
                full_type += "." + self.suffix

            for test in test_group["tests"]:
                # generate a test request
                test["full_type"] = full_type # dispatch on this
                test_request = { "file_params" : file_params,
                                 "test_group" : test_group_params_req,
                                 "test" : test }
                full_response = { "tcId" : test["tcId"] }
                test_response = self.tester.test(test_request)
                full_response.update(test_response)
                tests.append(full_response)


            test_group_params_rsp["tests"] = tests
            test_groups.append(test_group_params_rsp)

        file_params["testGroups"] = test_groups
        response.append(file_params)

        with open(self.rsp_file, "w",) as respf:
            json.dump(response, respf, indent=4)


    def augment_test_group(self, file_props, test_group):
        ''' generate a test group dictionary for input to the test,
        and a test group dictionary for the response.'''

        if file_props["algorithm"] == "RSA" and file_props["mode"] == "sigGen":
            return self.augment_rsa_sig_gen_test_group(test_group)

        # default: return same
        return test_group, test_group


    def augment_rsa_sig_gen_test_group(self, test_group):
        # need to generate a private key
        private_key = rsa.generate_private_key(public_exponent=65537,
                                               key_size=test_group["modulo"],
                                               backend=default_backend())
        # private components -> input
        # public components -> output
        test_group_resp = test_group.copy()

        private_numbers = private_key.private_numbers()
        public_numbers = private_numbers.public_numbers

        for priv_attr in ("p", "q", "dmp1", "dmq1", "iqmp"):
            test_group[priv_attr] = int_to_hex(getattr(private_numbers, priv_attr))
        test_group["n"] = int_to_hex(public_numbers.n)

        for pub_attr in ("n", "e"):
            test_group_resp[pub_attr] = int_to_hex(getattr(public_numbers, pub_attr))

        return test_group, test_group_resp


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

    def ls(self, remote_path='.'):
        headers = {'Depth': '1'}
        response = self._send('PROPFIND', remote_path, (207, 301), headers=headers)

        # Redirect
        if response.status_code == 301:
            url = urlparse(response.headers['location'])
            return self.ls(url.path)

        tree = xml.fromstring(response.content)
        return [elem2file(elem) for elem in tree.findall('{DAV:}response')]

    def exists(self, remote_path):
        response = self._send('HEAD', remote_path, (200, 301, 404))
        return True if response.status_code != 404 else False



def parse_args():

    parser = argparse.ArgumentParser(
        description="Execute CAVP Test")

    parser.add_argument('inputs', metavar='FILE', nargs='+',
                        help='Test file')
    parser.add_argument('-u', '--user',
                        help='user name (remote)')
    parser.add_argument('-p', '--password',
                        help='password (remote)')
    parser.add_argument('-r', '--remote',
                        help='HTTP URL where the files can be found')
    parser.add_argument('-s', '--suffix-test-type',
                        help='Suffix added to the testType field in the test spec')
    parser.add_argument('-t', '--tester', default='TestTester',
                        help='tester class')
    return parser.parse_args()


def execute_all_tests(args):

    LOCAL_FILE_NAME = 'curr_test.req.json'

    tester = globals()[args.tester]()
    if args.remote:
        # download the file, run the test, upload the file
        webclient = WebDavClient(args.remote, args.user, args.password)
        for arg in args.inputs:
            webclient.download(arg, LOCAL_FILE_NAME)
            curr_cavp = CAVPTest(LOCAL_FILE_NAME, tester, args.suffix_test_type)
            curr_cavp.run()
            webclient.upload(curr_cavp.result_path(),
                             rreplace(arg, '.req', '.rsp', 1))


    else:
        # local case
        for arg in args.inputs:
            curr_cavp = CAVPTest(arg, tester, args.suffix_test_type)
            curr_cavp.run()

def main():
    args = parse_args()
    execute_all_tests(args)


if __name__ == '__main__':
    main()