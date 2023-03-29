#! /usr/bin/env python3

##############################################################################
#  hsmdaemon.cgi
#
# simple cgi-script that extract a message from the request and
# sends it
#
# only used by the HSM crypto officer client: funkey.py
#
# Copyright (c) 2018-2020. Fungible, inc. All Rights Reserved.
#
##############################################################################

import os
import sys
import cgi

import traceback

from common import log
from hsmd_common import hsmd_rpc_call

RESTRICTED_PORT = 4443

########################################################################
#
# Send json
#
########################################################################

def send_json(json):
    print("Content-type: application/json")
    print("Status: 200 OK")
    print("Content-length: %d\n" % len(json))
    print(json)


def handle_post():
    ''' just package the content into a RPC message '''
    len = int(os.environ['CONTENT_LENGTH'])
    request = sys.stdin.read(len)

    form = cgi.FieldStorage()
    hsm_id = int(form.getvalue("hsm_id", 1))

    response = hsmd_rpc_call(request, hsm_id)
    send_json(response)


def main_program():

    try:
        # enforce a command coming from an intranet only accessible port
        port = int(os.environ['SERVER_PORT'])

        if port != RESTRICTED_PORT:
            raise ValueError("Attempt to access signing server from port %d" % port)

        method = os.environ["REQUEST_METHOD"]
        if method not in ("POST"):
            raise ValueError("Invalid request method %s" % method)

        handle_post()

    # key errors (missing form entries) as well as
    # value errors are translated as 400 Bad Request
    except (ValueError, KeyError) as err:
        # Log
        log("Exception: %s" % err)
        # Response
        print("Status: 400 Bad Request")
        err_msg = str(err)
        print("Content-Length: %d\n" % len(err_msg))
        print(err_msg)

    except ConnectionError as err:
         # Log
        log("Exception: %s" % err)
        traceback.print_exc()
        # Response
        print("Status: 503 Service Unavailable")
        err_msg = str(err) + "\n" + traceback.format_exc()
        print("Content-Length: %d\n" % len(err_msg))
        print(err_msg)

    except FileNotFoundError as err:
        err_str = "%s: file: %s" % (err, err.filename)
        log("Exception: %s" % err_str)
        traceback.print_exc()
        # Response
        print("Status: 503 Service Unavailable")
        err_msg = err_str + "\n" + traceback.format_exc()
        print("Content-Length: %d\n" % len(err_msg))
        print(err_msg)


        # all other errors are reported as 500 Internal Server Error
    except Exception as err:
        # Log
        log("Exception: %s" % err)
        traceback.print_exc()
        # Response
        print("Status: 500 Internal Server Error")
        err_msg = str(err) + "\n" + traceback.format_exc()
        print("Content-Length: %d\n" % len(err_msg))
        print(err_msg)


main_program()
