#!/usr/bin/env python3

#
# Implements a cache miss processing pipeline.
#
# cm_pipeline.py -h for usage directives.
#
# TODO bucketloads of error handling
#

import argparse
import glob
import os
import sys
import time


import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tracedir', type=str, help='Path to directory with traces')
    parser.add_argument('server', type=str, help='IP address of processing server')
    args = parser.parse_args()

    server_url = 'http://%s:8008' % args.server

    uuid = create_trace(server_url)
    if not uuid:
        sys.exit(1)

    ret = upload_trace_files(server_url, uuid, args.tracedir)
    if not ret:
        sys.exit(1)

    start_processing(server_url, uuid)

    ret, results = poll_for_completion(server_url, uuid)
    if not ret:
        sys.exit(1)

    # Grab the result files
    for result in results:
        print('Downloading result file %s' % result)
        result_url = '%s/traces/%s/results/%s' % (server_url, uuid, result)
        resp = requests.get(result_url, stream=True)

        with open(result, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=16384):
                f.write(chunk)

    # Kick off missmap locally
    pass


def create_trace(server_url):
    """ Returns the uuid of the trace, or None for failure. """
    create_url = '%s/traces' % server_url
    resp = requests.post(create_url)
    if resp.status_code != 200:
        return None

    js = resp.json()
    if not js['ret']:
        print('Problem creating trace %s' % js)
        return None
    print('Created trace with id %s' % js['id'])
    return js['id']


def upload_trace_files(server_url, uuid, tracedir):
    """
    Uploads all trace files.

    Returns True on success, False on failure.
    """
    upload_url = '%s/traces/%s' % (server_url, uuid)
    glob_path = os.path.join(tracedir, 'trace_cluster_*')
    traces = glob.glob(glob_path)

    if not traces:
        print('No trace files (trace_cluster_*) in %s' % tracedir)
        return False

    for trace in traces:
        print('Uploading trace file %s' % trace)
        resp = requests.post(upload_url,
                             files={'file': (os.path.basename(trace),
                                             open(trace, 'rb'))})
        if resp.status_code != 200:
            print('Unexpected status code %d while uploading %s' % (resp.status_code, trace))
            return False

        js = resp.json()
        if not js['ret']:
            print('Problem uploading %s: %s' % (trace, js['msg']))
            return False

    return True


def start_processing(server_url, uuid):
    """ Starts the processing """
    print('Kicking off processing')
    process_url = '%s/traces/%s/process' % (server_url, uuid)
    resp = requests.post(process_url)
    js = resp.json()
    return js['ret']


def poll_for_completion(server_url, uuid, timeout_secs=3600):
    """ Polls until completion or timeout """
    results = []
    start_time = time.time()
    process_url = '%s/traces/%s/process' % (server_url, uuid)

    while True:
        time.sleep(60)
        resp = requests.get(process_url)
        if resp.status_code != 200:
            print('Result poll returned status %d' % resp.status_code)
            return False, results

        js = resp.json()
        if js['complete']:
            if not js['ret']:
                print('Processing failed: %s' % js['msg'])
            results = js['files']
            return js['ret'], results

        elapsed = time.time() - start_time
        if elapsed > timeout_secs:
            print('Timed out during result polling')
            return False, []

        print('Waited %d seconds (%d max)' % (elapsed, timeout_secs))


if __name__ == '__main__':
    main()
