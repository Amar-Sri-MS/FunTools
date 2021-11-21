#!/usr/bin/python3

import argparse
import requests
import pprint
import time
import os
import sys
import threading
import shutil
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

###
##  quick helpers
#

def wait_for_version():
    failed = True
    while (failed):
        # Check current running version
        #curl -s  http://$TARGET:9332/platform/version | jq -r ".FunSDK,.debug"
        #r = requests.post('http://{}:9332/platform/version'.format(TARGET), json={"key": "value"})
        try:
            r = requests.post('http://{}:9332/platform/version'.format(TARGET))
            print("# Return stats %s" % r.status_code)
            pp.pprint(r.json())
            break
        except KeyboardInterrupt:
            sys.exit(1)
        except:
            print("Failed to get version, still waiting...")

        time.sleep(1)

def check_boot_defaults():
    # Check boot defaults
    r = requests.post('http://{}:9332/platform/boot_defaults'.format(TARGET))
    print(r.status_code)
    pp.pprint(r.json())


def dpu_restart():
    url = 'http://{}:9332/storage_agent/fast_restart'.format(TARGET)
    try:
        requests.post(url, timeout=0.01)
    except requests.exceptions.ReadTimeout: 
        pass

###
##  http server
#

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if (self.path != "/" + self.server.getname):
            self.send_error(404)
            self.server.request_state = "Bad request name"
            return

        try:
            self.send_response(200)
            self.send_header('Content-type','application/octet-stream')
            self.end_headers()

            # copy the file down
            shutil.copyfileobj(self.server.fl, self.wfile)

            self.server.request_state = "OK"
        except:
            self.server.request_state = "Failed request"

        self.server.fl.close()

class server(HTTPServer):
    def handle_timeout(self):
        print("timeout!")
        self.request_state = "Request Timeout"

    def set_filename(self, fname):
        self.fullname = fname
        self.getname = os.path.basename(self.fullname)
        self.fl = open(self.fullname, "rb")
        self.request_state = "No connection"

def server_loop(httpd):
    print("Waiting to serve file to dpu...")
    httpd.handle_request()
    print("Shutting down server...")

def setup_http_server(target, filename, host=None):

    httpd = server(('',0), handler)
    httpd.timeout = 30
    httpd.set_filename(filename)

    # determine the IP address we're going to serve
    # the target on so we can construct the URL
    if (args.host is None):
        sq = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sq.connect((target, 1234))
        ip = sq.getsockname()[0]
        sq.close()
    else:
        ip = args.host

    # get the port our server is bound to
    port = httpd.socket.getsockname()[1]
    httpd.url = "http://%s:%s/%s" % (ip, port, httpd.getname)
    
    # kick off a thread to handle the request since the http post is blocking
    thread = threading.Thread(target=server_loop, args=(httpd,), daemon=True)
    thread.start()

    return httpd

###
##  entrypoint
#

DESC = (
"""
Update a DPU via REST interface.

Examples:

Query if a DPU is responding and its current FunOS version

    update-dpu.py --dpu <cclinux-address>

Reboot a DPU

    update-dpu.py --dpu <cclinux-address> --restart

Run a bundle update on a DPU to a bundle in local file and restart

    update-dpu.py --dpu <cclinux-address> --restart <filename>

Run a bundle update on a DPU to a bundle on a webserver without restart

    update-dpu.py --dpu <cclinux-address> http://<server>[:port]/path/file
"""
)

parser = argparse.ArgumentParser(description=DESC,
                                 formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--dpu',
                    action='store', default=None,
                    help='target dpu cclinux address')

parser.add_argument('--host',
                    action='store', default=None,
                    help='override automatic server address')

parser.add_argument('--restart',
                    action='store_true', default=False,
                    help='restart the device')

parser.add_argument('filename', nargs='?',
                    action='store', default=None,
                    help='Filename for local bundle (.sh) file, or URL (http://)')

args = parser.parse_args()

if (args.dpu is None):
    print("Required --dpu option missing")
    sys.exit(1)

TARGET = args.dpu
filename = args.filename

print("Target: %s" % TARGET)
print("Bundle: %s" % filename)

pp = pprint.PrettyPrinter(depth=4)

# pre-flight some checks & work out if we need a server
if (filename is not None):
    if (filename.startswith("http://") or filename.startswith("https://")):
        # direct URL specified, just use it
        url = filename
        local_server = False
    elif (os.path.exists(filename)):
        # local file, make sure we stand up a server
        url = None
        local_server = True
    else:
        print("File not found: %s" % filename)
        sys.exit(1)
    
# start communicating with the dpu
print("Querying dpu version and boot defaults...")
wait_for_version()
check_boot_defaults()

if (filename is None):    
    if (args.restart):
        print("Restarting device...")
        dpu_restart()
    else:
        print("No update bundle, exiting")
    sys.exit(0)

# stand up the http server if we need to
if (local_server):
    httpd = setup_http_server(TARGET, filename, args.host)
    url = httpd.url

# name for the rest of the script
BUNDLE = url
print("Initiating update to URL %s" % BUNDLE)

# start the update process
r = requests.post('http://{}:9332/platform/upgrade/init'.format(TARGET), json={"URL": BUNDLE})

print("# Return stats %s" % r.status_code)
if (r.status_code != 200):
        print("failed to init upgrade!")
        pp.pprint(r.reason)
        sys.exit(1)

# check in with the server if we're using it
if (local_server):
    if (httpd.request_state == "OK"):
        print("File served OK from local server")
    else:
        raise RuntimeError("Bad http server state: %s" % httpd.request_state)

pp.pprint(r.json())
PROC = r.json()["process_id"]
pp.pprint("PROC is %s" % PROC)

r = requests.post('http://{}:9332/platform/upgrade/{}/start'.format(TARGET, PROC))
print(r.status_code)
pp.pprint(r.json())

while (True):
        url = 'http://{}:9332/platform/upgrade/{}/status'.format(TARGET, PROC)
        #print("url is %s" % url)
        r = requests.get(url)
        if (r.status_code != 200):
                print("Status request failed: %s" % r.status_code)
        # pp.pprint(r.json())
        status = r.json()["status"]
        if (status == "started"):
                print("Waiting for upgrade to complete...")
                time.sleep(1)
                continue
        if (status == "failed"):
                print("FAILED")
                break
        break

pp.pprint(r.json())

r = requests.post('http://{}:9332/platform/upgrade/{}/complete'.format(TARGET, PROC))
print(r.status_code)
pp.pprint(r.json())

if (args.restart):    
    dpu_restart()
    print("Done, device restart issued...")
else:
    print("Done, but did not restart device")


