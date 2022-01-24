#!/usr/bin/env python3


#
# TODO bucketloads of error handling
#

import argparse
import glob
import os
import time


import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tracedir', type=str, help='Path to directory with traces')
    parser.add_argument('server', type=str, help='IP address of processing server')
    args = parser.parse_args()

    server_url = 'http://%s:8008' % args.server

    create_url = '%s/traces' % server_url
    resp = requests.post(create_url)
    js = resp.json()
    print(js)
    uuid = js['id']

    # Grab all the trace files and upload them
    upload_url = '%s/traces/%s' % (server_url, uuid)
    glob_path = os.path.join(args.tracedir, 'trace_cluster_*')
    traces = glob.glob(glob_path)

    for trace in traces:
        print(trace)
        resp = requests.post(upload_url, files={'file': (os.path.basename(trace), open(trace, 'rb'))})
        print(resp.json())

    # Start the processing
    process_url = '%s/traces/%s/process' % (server_url, uuid)
    resp = requests.post(process_url)
    print(resp.json())

    results = []
    # Poll until the processing is done
    while True:
        time.sleep(10)
        resp = requests.get(process_url)
        js = resp.json()
        print(js)

        if js['ret']:
            summary = js['summary']
            results = summary['files']
            print(results)
            break

    # Grab the result files
    for result in results:
        result_url = '%s/traces/%s/results/%s' % (server_url, uuid, result)
        resp = requests.get(result_url, stream=True)

        with open(result, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=16384):
                f.write(chunk)

    # Kick off missmap
    pass


if __name__ == '__main__':
    main()