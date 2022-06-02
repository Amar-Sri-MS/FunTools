#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilities for interacting with s3 servers
"""

## This file is based on Apache licensed sample code from Amazon &
## modified to support librification. See below.

# Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# This file is licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License. A copy of the
# License is located at
#
# http://aws.amazon.com/apache2.0/
#
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

# AWS Version 4 signing example

# See: http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
# This version makes a POST request and passes request parameters
# in the body (payload) of the request. Auth information is passed in
# an Authorization header.
import sys, os, base64, datetime, hashlib, hmac 
import requests # pip install requests
import netrc
import mimetypes
import argparse
import json

# Key derivation functions. See:
# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def getSignatureKey(key, date_stamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

###
##  utility functions
#

VERBOSE = False

# upload to http://host/bucket/payload_name. "payload" can be a file or a
# file-like object. must pre-compute payload_digest
def put_request(host, bucket,
                payload_name, payload, payload_digest, payload_length,
                content_type = None,
                access_key = None, secret_key = None,
                region=None, tags=None, query_string=''):
    

    # ************* REQUEST VALUES *************
    method = 'PUT'
    service = 's3'
    endpoint = 'http://%s' % host

    # catch all
    if (content_type is None):
        content_type = 'application/octet-stream'

    if (region is None):
        region = 'us-santa-clara'

    # Read AWS access key from env. variables or configuration file. Best
    # practice is NOT to embed credentials in code.
    if ((access_key is None) or (secret_key is None)):
        nrc = netrc.netrc()
        (access_key, _, secret_key) = nrc.authenticators(host)
        if access_key is None or secret_key is None:
            raise RuntimeError('No credentials available.')


    # Create a date for headers and the credential string
    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope


    # ************* TASK 1: CREATE A CANONICAL REQUEST *************
    # http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

    # Step 1 is to define the verb (GET, POST, etc.)--already done.

    # Step 2: Create canonical URI--the part of the URI from domain to query 
    # string (use '/' if no path)
    canonical_uri = os.path.join("/", bucket, payload_name)

    ## Step 3: Create the canonical query string. In this example, request
    # parameters are passed in the body of the request and the query string
    # is blank.
    canonical_querystring = query_string


    # Step 4: Create the canonical headers. Header names must be trimmed
    # and lowercase, and sorted in code point order from low to high.
    # Note that there is a trailing \n.
    canonical_headers = ('host:' + host + '\n' +
                        'x-amz-content-sha256:' + payload_digest + '\n' +
                        'x-amz-date:' + amz_date + '\n' +
                        'x-amz-decoded-content-length:' +
                         str(payload_length) + '\n')
    if tags:
        canonical_headers += 'x-amz-tagging:' + tags + '\n'

    # Step 5: Create the list of signed headers. This lists the headers
    # in the canonical_headers list, delimited with ";" and in alpha order.
    # Note: The request can include any headers; canonical_headers and
    # signed_headers include those that you want to be included in the
    # hash of the request. "Host" and "x-amz-date" are always required.
    # signed_headers = 'content-type;host;x-amz-date'
    signed_headers = 'host;x-amz-content-sha256;x-amz-date;x-amz-decoded-content-length'
    if tags:
        signed_headers += ';x-amz-tagging'


    # Step 7: Combine elements to create canonical request
    canonical_request = (method + '\n' + canonical_uri + '\n' +
                         canonical_querystring + '\n' + canonical_headers +
                         '\n' + signed_headers + '\n' + payload_digest)

    # ************* TASK 2: CREATE THE STRING TO SIGN*************
    # Match the algorithm to the hashing algorithm you use, either SHA-1 or
    # SHA-256 (recommended)
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = (date_stamp + '/' + region + '/' +
                        service + '/' + 'aws4_request')
    request_u8 = canonical_request.encode('utf-8')
    request_digest = hashlib.sha256(request_u8).hexdigest()
    string_to_sign = (algorithm + '\n' +  amz_date + '\n' +
                      credential_scope + '\n' +
                      request_digest)


    # ************* TASK 3: CALCULATE THE SIGNATURE *************
    # Create the signing key using the function defined above.
    signing_key = getSignatureKey(secret_key, date_stamp, region, service)

    # Sign the string_to_sign using the signing_key
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'),
                         hashlib.sha256).hexdigest()


    # ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
    # Put the signature information in a header named Authorization.
    authorization_header = (algorithm + ' ' + 'Credential=' + access_key +
                            '/' + credential_scope + ',' +
                            'SignedHeaders=' + signed_headers + ',' +
                            'Signature=' + signature)

    # the headers must be included in the canonical_headers and
    # signed_headers values, as noted earlier. Order here is not
    # significant.
    # Python note: The 'host' header is added
    # automatically by the Python 'requests' library.
    headers = {'x-amz-content-sha256': payload_digest,
               'X-Amz-Date':amz_date,
               'x-amz-decoded-content-length':str(payload_length),
               'Content-type':content_type,
               'Authorization':authorization_header}

    if tags:
        headers['x-amz-tagging'] = tags

    # ************* SEND THE REQUEST *************
    url = endpoint + canonical_uri
    if canonical_querystring:
        url += '?' + canonical_querystring

    if (VERBOSE):
        print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
        print('Request URL = ' + url)

    r = requests.put(url,
                     data=payload,
                     headers=headers)

    if (VERBOSE):
        print('\nRESPONSE++++++++++++++++++++++++++++++++++++')

        print(r.request.body)
        print(r.request.headers)

        print('Response code: %d\n' % r.status_code)
        print(r.text)

    # barf, should that be applicable on this response
    r.raise_for_status()

# given a file, upload it, with optional remote name
BLOCKSIZE = 128*1024
def upload_file(filename, host, bucket,
                content_type=None,
                remote_name=None, key=None, secret=None, region=None,
                tags=None):

    ### derive a name if missing
    if (remote_name is None):
        remote_name = os.path.basename(filename)
        
    ### guess the mimetype, if it wasn't specified
    if (content_type is None):
        mimetypes.init()
        (content_type, enc) = mimetypes.guess_type(filename)
        print("Guessng content-type %s" % content_type)
    
    ### open the file
    fl = open(filename, "rb")

    ### hash it & compute the size as we go
    hasher = hashlib.sha256()
    nbytes = 0
    buf = fl.read(BLOCKSIZE)
    while len(buf) > 0:
        hasher.update(buf)
        nbytes += len(buf)
        buf = fl.read(BLOCKSIZE)
    digest = hasher.hexdigest()
        
    ### seek back to the start for the upload
    fl.seek(0)

    ### do the upload
    put_request(host, bucket, remote_name, fl, digest, nbytes, content_type,
                key, secret, region, tags=tags)
        
# given a python dict/list/whatever type, upload it as a nicely formatted
# json
def upload_json(obj, host, bucket, remote_name,
                key=None, secret=None, region=None, tags=None):

    # convert the object to a formatted json string
    payload = json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))
    payload = payload.encode("utf-8")

    # hash & size it
    payload_length = len(payload)
    payload_digest = hashlib.sha256(payload).hexdigest()

    content_type = 'application/json'
    put_request(host, bucket, remote_name, payload,
                payload_digest, payload_length, content_type,
                key, secret, region, tags=tags)


###
##  stand-along script for uploading, if you please
#

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("host", help="S3 compatible host to upload to")
    parser.add_argument("bucket", help="Bucket to upload to")
    parser.add_argument("filename", help="File to upload")
    
    parser.add_argument("-c", "--content-type", action="store", default=None)
    parser.add_argument("-n", "--remote-name", action="store", default=None)
    parser.add_argument("-k", "--key", action="store", default=None)
    parser.add_argument("-s", "--secret", action="store", default=None)
    parser.add_argument("-r", "--region", action="store", default=None)
    parser.add_argument("-t", "--tags", default=None,
                        help="Tags encoded as URL query parameters e.g."
                             " tag=value")

    parser.add_argument("-v", "--verbose", action="store_true", default=False)

    args: argparse.Namespace = parser.parse_args()

    if (args.verbose):
        global VERBOSE
        VERBOSE = True
    
    upload_file(args.filename, args.host, args.bucket, args.content_type,
                args.remote_name, args.key, args.secret, args.region, args.tags)
    print("OK")

if (__name__ == "__main__"):
    main()
