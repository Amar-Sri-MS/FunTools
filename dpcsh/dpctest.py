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

# load up a dpcsh
# print "### Running dpcsh as text proxy"
# pid = subprocess.Popen(["./dpcsh", "--text_proxy"])

# print "### pid is %s" % pid

# connect to it
client = dpc_client.DpcClient()

print "### Running a command 1"
message = "Hello dpc"
result = client.execute_command('echo', message)
if (result.strip() != message):
    raise RuntimeError("echo failed")
print "Echo OK"

print "### Running a command 2"
result = client.execute_command('math "+"  2 3 4 5', 6)
if (int(result) != 20):
    raise RuntimeError("math failed")
print "Math OK"


for i in (10, 100, 1000, 10000, 100000):
    message = "a" * i
    result = client.execute_command('echo', message)
    if (result.strip() != message):
        raise RuntimeError("large message failed at size = %d" % result)
    print "Large message OK for size = %d" % i
