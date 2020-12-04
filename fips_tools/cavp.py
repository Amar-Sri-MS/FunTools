#! /usr/bin/env python3
#
# cavp.py
# CAVP file parser
# Copyright (c) 2020. Fungible, Inc. All rights reserved.
#

''' Rationale: CAVP test files follow the same overall syntax,
which is really a variation of the ConfigFile format.
https://docs.python.org/3/library/configparser.html

This module follows some simple syntax rule to extract the
tests from different types of CAVP tests.

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

import dpc_client

######
# Tester classes
#


class AbsCAVPTestRunner:
    ''' abstract tester class '''
    def test(self, test_no, request):
        raise RuntimeError("abstract class called")


class TestTester(AbsCAVPTestRunner):
    ''' dummy tester class '''
    def test(self, test_no, request):
        return ['Result = FAIL']


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

    def test(self, test_no, request):
        # package the request as JSON and send to FunOS
        execute_args = ['cavp', request]
        results = self.dpc_client.execute('execute', execute_args)
        print("Result = %s" % str(results))
        # result is a dictionary with either a key 'error' or a key 'result'
        if 'error' in results:
            raise RuntimeError("error returned by test #%d: %s" %
                               (test_no, results['error']))
        elif 'result' in results:
            return results['result']

        raise RuntimeError("Results returned not understood: %s" %
                           results)




#########################################
# CAVP File Parser
#
class CAVPTest:

    HEADERS = '[headers]'

    def __init__(self, name, file_path, tester):
        self.name = name
        self.req_file = os.path.abspath(file_path)
        self.rsp_file = os.path.splitext(self.req_file)[0] + '.rsp'
        self.tester = tester


    def result_path(self):
        return self.rsp_file

    def run(self):
        meta_params = {self.HEADERS: '',
                       'req_file': self.name} # global params for the file
        with open(self.req_file, 'r') as reqf:
            with open(self.rsp_file, 'w') as rspf:
                test_no = 1
                while True:
                    request = self._read_request(reqf, rspf, meta_params)
                    if request is None:
                        return # EOF
                    response = self.tester.test(test_no, request)
                    self._write_response(rspf, response)
                    test_no = test_no + 1


    def _read_request(self, in_fp, out_fp, params):
        ''' read a test from the rsp file; also write the test to the out file '''
        test_input = {}
        in_test = False

        l = in_fp.readline()

        while l:

            l = l.strip()

            if len(l)==0:
                if in_test:
                    # no more test value and do not write line
                    # since the response needs to be appended
                    break
            elif l[0] == '#':
                # comment -> headers
                params[self.HEADERS] += l[1:]
            elif l[0] == '[':
                # meta parameters
                end_pos = l.rfind(']')
                if end_pos >= 0:
                    spec = l[1:end_pos]
                else:
                    spec = l[1:]
                self._parse_kv(params, spec)
            else:
                self._parse_kv(test_input, l)
                in_test = True # still collect test values

            # always input to response file
            print(l, file=out_fp)
            l = in_fp.readline()


        # test is read: something to do?
        if bool(test_input) == 0:
            return None # done

        # return the test parameters
        test_input['params'] = params
        return test_input

    def _write_response(self, out_fp, reply):
        # write the reply which can be None, a single line or
        # an array of lines in the correct order
        if reply is None:
            pass
        elif isinstance(reply, str):
            print(reply, file=out_fp)
        else :
            for t in reply:
                print(t, file=out_fp)

        # print the empty line test separator
        print(file=out_fp)


    def _parse_kv(self, d, kv):
        vals = kv.split(' = ')
        if len(vals) == 2:
            d[vals[0]] = vals[1]
        else:
            d[len(d)] = vals



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
    parser.add_argument('-t', '--tester', default='TestTester',
                        help='tester class')
    return parser.parse_args()


def execute_all_tests(args):

    LOCAL_FILE_NAME = 'curr_test.req'

    tester = globals()[args.tester]()
    if args.remote:
        # download the file, run the test, upload the file
        webclient = WebDavClient(args.remote, args.user, args.password)
        for arg in args.inputs:
            webclient.download(arg, LOCAL_FILE_NAME)
            curr_cavp = CAVPTest(os.path.basename(arg), LOCAL_FILE_NAME, tester)
            curr_cavp.run()
            webclient.upload(curr_cavp.result_path(),
                             os.path.splitext(arg)[0] + '.rsp')

    else:
        # local case
        for arg in args.inputs:
            curr_cavp = CAVPTest(os.path.basename(arg), arg, tester)
            curr_cavp.run()

def main():
    args = parse_args()
    execute_all_tests(args)


if __name__ == '__main__':
    main()
