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
import xml.etree.ElementTree as et
import urllib.parse

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

def put_request(host, bucket,
                payload_name, payload, payload_digest, payload_length,
                content_type = None,
                access_key = None, secret_key = None,
                region=None, tags_header=None, query_string=''):
    """
    Make a put request to http://host/bucket/payload_name.

    "payload" can be a file or a file-like object.
    "payload_digest" must be pre-computed.

    "tags_header" will append the value to the x-amz-tagging request header.
    "query_string" amends the PUT request with a query string.
    """
    

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
    access_key, secret_key = get_auth_keys(host, access_key, secret_key)

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

    # Step 3: Create the canonical query string.
    canonical_querystring = query_string


    # Step 4: Create the canonical headers. Header names must be trimmed
    # and lowercase, and sorted in code point order from low to high.
    # Note that there is a trailing \n.
    canonical_headers = ('host:' + host + '\n' +
                        'x-amz-content-sha256:' + payload_digest + '\n' +
                        'x-amz-date:' + amz_date + '\n' +
                        'x-amz-decoded-content-length:' +
                         str(payload_length) + '\n')
    if tags_header:
        canonical_headers += 'x-amz-tagging:' + tags_header + '\n'

    # Step 5: Create the list of signed headers. This lists the headers
    # in the canonical_headers list, delimited with ";" and in alpha order.
    # Note: The request can include any headers; canonical_headers and
    # signed_headers include those that you want to be included in the
    # hash of the request. "Host" and "x-amz-date" are always required.
    # signed_headers = 'content-type;host;x-amz-date'
    signed_headers = 'host;x-amz-content-sha256;x-amz-date;x-amz-decoded-content-length'
    if tags_header:
        signed_headers += ';x-amz-tagging'


    # Step 7: Combine elements to create canonical request
    canonical_request = (method + '\n' + canonical_uri + '\n' +
                         canonical_querystring + '\n' + canonical_headers +
                         '\n' + signed_headers + '\n' + payload_digest)

    auth_header = generate_authorization_header(canonical_request, signed_headers, amz_date, date_stamp,
                                                region, service, access_key, secret_key)

    # the headers must be included in the canonical_headers and
    # signed_headers values, as noted earlier. Order here is not
    # significant.
    # Python note: The 'host' header is added
    # automatically by the Python 'requests' library.
    headers = {'x-amz-content-sha256': payload_digest,
               'X-Amz-Date':amz_date,
               'x-amz-decoded-content-length':str(payload_length),
               'Content-type':content_type,
               'Authorization':auth_header}

    if tags_header:
        headers['x-amz-tagging'] = tags_header

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


def generate_authorization_header(canonical_request, signed_headers,
                                  amz_date, date_stamp, region, service,
                                  access_key, secret_key):
    # ************* TASK 2: CREATE THE STRING TO SIGN*************
    # Match the algorithm to the hashing algorithm you use, either SHA-1 or
    # SHA-256 (recommended)
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = (date_stamp + '/' + region + '/' +
                        service + '/' + 'aws4_request')

    request_u8 = canonical_request.encode('utf-8')
    request_digest = hashlib.sha256(request_u8).hexdigest()
    string_to_sign = (algorithm + '\n' + amz_date + '\n' +
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

    return authorization_header


def get_auth_keys(host, access_key, secret_key):
    """
    Read AWS access key from env. variables or configuration file. Best
    practice is NOT to embed credentials in code.
    """
    if ((access_key is None) or (secret_key is None)):
        nrc = netrc.netrc()
        (access_key, _, secret_key) = nrc.authenticators(host)
        if access_key is None or secret_key is None:
            raise RuntimeError('No credentials available.')
    return access_key, secret_key


def get_request(host, bucket, object_key, access_key=None, secret_key=None,
                region=None, query_string=''):
    # ************* REQUEST VALUES *************
    method = 'GET'
    service = 's3'
    endpoint = 'http://%s' % host

    if (region is None):
        region = 'us-santa-clara'

    payload_digest = hashlib.sha256(b'').hexdigest()

    access_key, secret_key = get_auth_keys(host, access_key, secret_key)

    # Create a date for headers and the credential string
    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope

    canonical_uri = os.path.join("/", bucket, object_key)

    canonical_querystring = query_string

    # Create the canonical headers. Header names must be trimmed
    # and lowercase, and sorted in code point order from low to high.
    # Note that there is a trailing \n.
    canonical_headers = ('host:' + host + '\n' +
                         'x-amz-date:' + amz_date + '\n')

    # Create the list of signed headers. This lists the headers
    # in the canonical_headers list, delimited with ";" and in alpha order.
    signed_headers = 'host;x-amz-date'

    canonical_request = (method + '\n' + canonical_uri + '\n' +
                         canonical_querystring + '\n' + canonical_headers +
                         '\n' + signed_headers + '\n' + payload_digest)

    auth_header = generate_authorization_header(canonical_request, signed_headers, amz_date, date_stamp,
                                                region, service, access_key, secret_key)

    # Python note: The 'host' header is added
    # automatically by the Python 'requests' library.
    headers = {
        'X-Amz-Date': amz_date,
        'Authorization': auth_header}

    url = endpoint + canonical_uri
    if canonical_querystring:
        url += '?' + canonical_querystring
    if (VERBOSE):
        print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
        print('Request URL = ' + url)

    r = requests.get(url, headers=headers)

    if (VERBOSE):
        print('\nRESPONSE++++++++++++++++++++++++++++++++++++')

        print(r.request.body)
        print(r.request.headers)

        print('Response code: %d\n' % r.status_code)
        print(r.text)

    # barf, should that be applicable on this response
    r.raise_for_status()
    return r


# given a file handle fl, upload it with optional remote name
def upload_file_handle(filename, host, bucket, fl,
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
        print("Guessing content-type %s" % content_type)

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
                key, secret, region, tags_header=tags)


# given a file, upload it, with optional remote name
BLOCKSIZE = 128*1024
def upload_file(filename, host, bucket,
                content_type=None,
                remote_name=None, key=None, secret=None, region=None,
                tags=None):

    ### open the file
    fl = open(filename, "rb")
    upload_file_handle(filename, host, bucket, fl,
                       content_type, remote_name, key, secret, region, tags)


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
                key, secret, region, tags_header=tags)


def set_tags(object_key, host, bucket,
             key=None, secret=None, region=None, tags={}):
    """
    Sets the tags on an object.

    tags is a dict of tag names to values, as strings please.
    """
    xml_str = _dict_to_xml_tags(tags)
    digest = hashlib.sha256(xml_str).hexdigest()

    put_request(host, bucket, object_key, xml_str, digest, len(xml_str),
                None, key, secret, region, None, 'tagging=')


def _dict_to_xml_tags(tags):
    root = et.Element('Tagging')
    tagset = et.Element('TagSet')
    root.append(tagset)

    for t in tags:
        tag = et.Element('Tag')
        key = et.Element('Key')
        key.text = t
        val = et.Element('Value')
        val.text = str(tags[t])

        tag.append(key)
        tag.append(val)

        tagset.append(tag)

    return et.tostring(root)

def get_tags(object_key, host, bucket, key=None, secret=None, region=None):
    """ Returns the tags on an object as a dict """
    r = get_request(host, bucket, object_key, key, secret, region, 'tagging=')
    return _xml_tags_to_dict(r.text)


def _xml_tags_to_dict(xml_str):
    if not xml_str:
        return {}

    result = {}
    try:
        root = et.fromstring(xml_str)
        tagset = root.find('TagSet')
        tags = tagset.findall('Tag')

        for tag in tags:
            k = tag.find('Key')
            v = tag.find('Value')
            result[k.text] = v.text
    except et.ParseError:
        print('Error parsing response %s' % xml_str)
        return {}

    return result


def list_bucket(host, bucket, key, secret, continuation_token, max_keys=1000):
    params = []
    if continuation_token:
        params.append(('continuation-token', continuation_token))
    params.append(('list-type', 2))
    params.append(('max-keys', max_keys))

    query = urllib.parse.urlencode(params)
    r = get_request(host, bucket, '', key, secret, None, query)

    objects = []
    token = None
    try:
        root = et.fromstring(r.text)
        token_elem = root.find(s3ify_xml_tag('NextContinuationToken'))
        if token_elem is not None:
            token = token_elem.text

        contents = root.findall(s3ify_xml_tag('Contents'))
        for content in contents:
            key_elem = content.find(s3ify_xml_tag('Key'))
            objects.append(key_elem.text)

    except et.ParseError:
        print('Error parsing response' % r.text)
        return []

    return token, objects

def s3ify_xml_tag(element_tag):
    return '{http://s3.amazonaws.com/doc/2006-03-01/}' + element_tag


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
