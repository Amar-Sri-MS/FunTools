import argparse
import base64
import os
import ssl
import sys
import urllib.request, urllib.error, urllib.parse

ENROLL_SERVICE_URL = "https://f1reg.fungible.com/cgi-bin/enrollment_server.cgi"

def _get_ssl_ctx():
    ctx = ssl.create_default_context()
    return ctx

def GetModulus():
    params = urllib.parse.urlencode({
        'cmd' : 'modulus',
        'format' : 'base64'
    })
    url = ENROLL_SERVICE_URL + "?{}".format(params)
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, context=_get_ssl_ctx())
    return base64.b64decode(resp.read())

def Sign(data):
    url = ENROLL_SERVICE_URL
    d = base64.b64encode(data)
    req = urllib.request.Request(url, d, method='PUT')
    resp = urllib.request.urlopen(req, context=_get_ssl_ctx())
    return base64.b64decode(resp.read())
