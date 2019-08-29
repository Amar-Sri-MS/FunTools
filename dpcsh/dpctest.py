#!/usr/bin/python
##
##  dpc_test.py
##
##  Created by Charles Gray on 2018-03-19
##  Copyright (C) 2018 Fungible. All rights reserved.
##

import os
import sys
import subprocess
import dpc_client
import time

def test_commands(client):

    print "### Running a command 1"
    message = "Hello dpc"
    result = client.execute('echo', message)
    print("result: %s" % result)
    if (result.strip() != message):
        raise RuntimeError("echo failed")
    print "Echo OK"

    result = client.execute("math", ['+', 2, 3, 4])
    print result

    print "### Running a command 2"
    result = client.execute('math', [ "+", 2, 3, 4, 5, 6])
    if (int(result) != 20):
        raise RuntimeError("math failed")
    print "Math OK"

    print "### Running large sized commands"
    for i in (10, 100, 1000, 10000, 100000):
        message = "a" * i
        result = client.execute('echo', message)
        if (result.strip() != message):
            raise RuntimeError("large message failed at size = %d" % result)
        print "Large message OK for size = %d" % i

    print "### Testing async"

    # send three different times
    client.async_send("delay", [3, "echo", "third"])
    client.async_send("delay", [2, "echo", "second"])
    client.async_send("delay", [1, "echo", "first"])

    # collect results and expect in order
    r1 = client.async_recv_any()
    r2 = client.async_recv_any()
    r3 = client.async_recv_any()

    print "r1 = %s, r2 = %s, r3 = %s" % (r1, r2, r3)

    if ((r1 != "first") or (r2 != "second") or (r3 != "third")):
        raise RuntimeError("async messages in wrong order")
    
    print "All tests OK!"

def run_dpc_test(args, legacy_ok, delay):
    # load up a dpcsh tcp socket
    print "### Running dpcsh as text proxy"
    pid = subprocess.Popen(["./dpcsh", "--oneshot"] + args)

    print "### pid is %s" % pid
    time.sleep(1)

    # connect to it
    client = dpc_client.DpcClient(False, legacy_ok)

    time.sleep(delay)
    
    test_commands(client)
    
###
## main
#

STYLES = {"tcp": (True, ["--tcp_proxy"], False, 0),
          "unix": (True, ["--unix_proxy"], True, 0),
          "qemu": (False, ["--tcp_proxy", "--base64_sock"], False, 10)}

def run_style(manual, style):

    (auto, args, legacy_ok, delay) = STYLES[style]

    if (manual or auto):
        print "Running tests for '%s'" % style
        run_dpc_test(args, legacy_ok, delay)
    else:
        print "Skipping '%s'" % style

def usage():
    print "usage: %s [tcp, unix, qemu]" % sys.argv[0]
    sys.exit(1)
        
def main():

    if (len(sys.argv) > 2):
        usage()

    style = None
    if (len(sys.argv) == 2):
        style = sys.argv[1]

    if (style is not None):
        run_style(True, style)
    else:
        for style in STYLES:
            run_style(False, style)



###
##  entrypoint
#
if (__name__ == "__main__"):
    main()
