#! /usr/bin/env python3
#
# trng.py
# Get TRNG data
# Copyright (c) 2021. Fungible, Inc. All rights reserved.
#

import os
import sys
import argparse
import requests
import json

import dpc_client

def rreplace(s, old, new, maxreplace):
    ''' replace at most maxreplace occurences of old with new in s '''
    return new.join(s.rsplit(old, maxreplace))


def int_to_hex(x):
    ''' integer to hex big endian representation '''
    x_bytes = x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')
    return x_bytes.hex().upper()


class DPCTRNGRunner:

    def __init__(self):
        try:
            with open('./env.json', 'r') as f:
                env_dict = json.load(f)
            if len(env_dict['dpc_hosts']) < 1:
                raise RuntimeError('No DPC hosts!')
            # use the name and TCP port of the DPC proxy for 1st chip
            dpc_host = env_dict['dpc_hosts'][0]
            host = dpc_host['host']
            port = 4223 # dpc_host['tcp_port']
            print('Using dpc host at %s:%s' % (host, port))
            self.dpc_client = dpc_client.DpcClient(server_address=(host, port))

        except FileNotFoundError:
            self.dpc_client = dpc_client.DpcClient()
            # no file try default

    def run(self, app, request):
        # package the request as JSON and send to FunOS
        execute_args = [app, request]
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




class TRNGDataSet:

    def __init__(self, file_path, tester, suffix):
        self.req_file = os.path.abspath(file_path)
        self.rsp_file = response_file_name(self.req_file)
        self.tester = tester
        self.suffix = suffix


    def result_path(self):
        return self.rsp_file

    def run(self):

        # load the whole file
        with open(self.req_file, 'r') as reqf:
            request = json.load(reqf)

        # hierarchy is [ {} {file_params, testGroups:[] } ] i.e. an  array
        # BUT can also be {file_params, testGroups:[] } i.e. a dictionary
        # each testGroup is { group_param, tests:[] }
        # each test is a dictionary with a field "tcId"

        if 'keys' in dir(request):
            # a dictionary
            response = None
            test_dict = request
        else:
            # an array
            response = [request[0]] # response is an array to
            test_dict = request[1]


        # the file keys but without testGroups items
        file_params = {k:v for (k,v) in test_dict.items() if k != "testGroups"}
        test_groups = []

        algorithm_mode = file_params["algorithm"]
        if file_params.get("mode"):
            algorithm_mode += "." + file_params.get("mode")

        for test_group in test_dict["testGroups"]:
            # add the test group keys but without tests items
            test_group_params = {k:v for (k,v) in test_group.items() if k != "tests" }
            tests = []

            # add more info if necessary:
            # req -> sent to tester, rsp -> written to response file
            test_group_params_req, test_group_params_rsp = self.augment_test_group(file_params,
                                                                                   test_group_params)

            # if one of the group returned is None, omit that group
            if test_group_params_rsp is None or test_group_params_req is None:
                continue

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

        # if response (is an array)
        if response:
            response.append(file_params)
        else:
            response = file_params

        with open(self.rsp_file, "w",) as respf:
            json.dump(response, respf, indent=4)



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
        description="Execute TRGN Data Gathering")

    parser.add_argument('-u', '--user', required=True,
                        help='user name (remote)')
    parser.add_argument('-p', '--password', required=True,
                        help='password (remote)')
    parser.add_argument('-r', '--remote', required=True,
                        help='HTTP URL where the files will be saved')
    parser.add_argument('-d', '--disabled-rings', default="0",
                        help='Disabled Rings Mask')
    parser.add_argument('-s', '--sample-size', default="131072",
                        help='Size of sample')
    parser.add_argument('-c', '--clock-divider', default="0",
                        help='Clock Divider')
    parser.add_argument('-a', '--app',
                        help='FunOS app to execute')

    return parser.parse_args()


def execute_all_tests(args):
    if args.app:
        app_name = args.app
        dpc_args = {'app': app_name}
        remote_file_name = "trng_data_" + app_name
    else:
        app_name = 'sbp_trng_data'
        ARGS_NAMES = ["disabled_rings", "clock_divider", "sample_size"]
        dict_args = vars(args)
        dpc_args = { n : int(dict_args.get(n,0),0) for n in ARGS_NAMES }
        remote_file_name = "trng_data_" + "_".join(["%s_x%x" % (k[0], v) for k,v in dpc_args.items()])

        # deal with fun_json limitation
        val64 = dpc_args["disabled_rings"]
        dpc_args["disabled_rings_hi"] = (val64 >> 32)
        dpc_args["disabled_rings_lo"] = (val64 & 0xFFFF_FFFF)

    print(dpc_args)
    print(remote_file_name)


    LOCAL_FILE = 'dataset.json'
    # run the test, save to local file, upload the file
    webclient = WebDavClient(args.remote, args.user, args.password)
    runner = DPCTRNGRunner()

    result = runner.run(app_name, dpc_args)
    result.update(dpc_args)

    with open(LOCAL_FILE, "w") as respf:
        json.dump(result, respf, indent=4)

    webclient.upload(LOCAL_FILE,remote_file_name)


def main():
    args = parse_args()
    execute_all_tests(args)


if __name__ == '__main__':
    main()
