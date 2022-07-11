#!/usr/bin/python3

import argparse
import requests
import pprint
import time
import os
import sys
import threading
import shutil
import shlex
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

### List of API endpoints
API_VERSION = 'http://{target}/platform/version'
API_BOOT_DEFAULTS = 'http://{target}/platform/boot_defaults'
API_FAST_RESTART = 'http://{target}/storage_agent/fast_restart'
API_UPGRADE_INIT = 'http://{target}/platform/upgrade/init'
API_UPGRADE_START = 'http://{target}/platform/upgrade/{proc}/start'
API_UPGRADE_STATUS = 'http://{target}/platform/upgrade/{proc}/status'
API_UPGRADE_COMPLETE = 'http://{target}/platform/upgrade/{proc}/complete'

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
            r = requests.post(API_VERSION.format(target=TARGET))
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
    r = requests.post(API_BOOT_DEFAULTS.format(target=TARGET))
    print(r.status_code)
    pp.pprint(r.json())


def dpu_restart():
    url = API_FAST_RESTART.format(target=TARGET)
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

def setup_http_server(targetip, filename, host=None):

    httpd = server(('',0), handler)
    httpd.timeout = 30
    httpd.set_filename(filename)

    # determine the IP address we're going to serve
    # the target on so we can construct the URL
    if (args.host is None):
        sq = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sq.connect((targetip, 1234))
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

ccfg_parser = parser.add_mutually_exclusive_group()

ccfg_parser.add_argument('--ccfg',
                    action='store', default=None,
                    help='update feature set (ccfg) as part of complete firmware upgrade')

ccfg_parser.add_argument('--ccfg-only',
                    action='store', default=None,
                    help='update feature set (ccfg) only without doing a complete firmware update')

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

# host/ip : port
TARGET = args.dpu + ":9332"
filename = args.filename

CCFG=None
if args.ccfg:
    CCFG = f"ccfg={shlex.quote(args.ccfg)}"
elif args.ccfg_only:
    CCFG = f"ccfg-only={shlex.quote(args.ccfg_only)}"

print(f"Target: {TARGET}")
print(f"Bundle: {filename}")
if CCFG:
    print(f"CCFG option: {CCFG}")

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

if (filename is None):
    if (args.restart):
        # restart without checking boot defaults
        print("Restarting device...")
        dpu_restart()
    else:
        # poll boot default info and exit
        check_boot_defaults()
        print("No update bundle, exiting")
    sys.exit(0)

# poll boot default info and continue
check_boot_defaults()

# stand up the http server if we need to
if (local_server):
    httpd = setup_http_server(args.dpu, filename, args.host)
    url = httpd.url

# name for the rest of the script
BUNDLE = url
print("Initiating update to URL %s" % BUNDLE)

# start the update process
js = {"URL": BUNDLE}
r = requests.post(API_UPGRADE_INIT.format(target=TARGET), json=js)

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

PROC = r.json()["process_id"]
pp.pprint("Upgrade process ID is %s" % PROC)

# setup ccfg
js = {}
if (CCFG is not None):
    js["args"] = [CCFG]
r = requests.post(API_UPGRADE_START.format(target=TARGET, proc=PROC), json=js)
print(r.status_code)
if (r.status_code != 200):
    print("Upgrade start failed... %s" % r.reason)
    sys.exit(1)
pp.pprint(r.json())

fail = False
while (True):
        url = API_UPGRADE_STATUS.format(target=TARGET, proc=PROC)
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
                fail = True
                break
        break

pp.pprint(r.json())

# clean up the update, regardless of success
r = requests.post(API_UPGRADE_COMPLETE.format(target=TARGET, proc=PROC))

if (fail):
    print("ERROR: DPU update operation FAILED. Exiting")
    sys.exit(1)

print(r.status_code)
pp.pprint(r.json())

if (args.restart):
    dpu_restart()
    print("Update successful, device restart issued...")
else:
    print("Update successful, but did not restart device")


