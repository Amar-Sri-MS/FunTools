#!/usr/bin/python -u

## use ifconfig to monitor link status of an ethernet device.  F1 dev
## boards were seeing issues where the link from the MPG port to the
## linux i40e device was not coming up or was flapping. This allows the
## host driving the boot to check whether U-boot has checked in or if the link
## came up hosed. In the case it's hosed, we take down the boot and try again
## for a good link, lest we get long timeouts in tftpboot.

import time
import optparse
import subprocess
import os
import sys

def log(s = ""):
    sys.stderr.write("%s\r\n" % s)
    sys.stderr.flush()

parser = optparse.OptionParser(usage="usage: %prog <iface> [file2touch] [pid2kill]")

pid = None
fname = None
if (len(sys.argv) == 1):
    parser.error("expected interface name")
    sys.exit(1)
elif (len(sys.argv) == 2):
    pass
elif (len(sys.argv) == 3):
    fname = sys.argv[2]
elif (len(sys.argv) == 4):
    fname = sys.argv[2]
    pid = sys.argv[3]
else:
    parser.error("too many arguments")
    sys.exit(1)

iface = sys.argv[1]
log("Monitoring link status (%s, %s, %s):" % (iface, fname, pid))

time.sleep(2)

ycount = 0
ncount = 0
last5 = []
for i in range(30):
    output = subprocess.check_output("ethtool %s 2>/dev/null | grep 'Link detected'" % iface, shell=True)
    if "yes" in output:
        ycount += 1
        last5.append("yes")
    else:
        ncount += 1
        last5.append("no")
    last5 = last5[-5:]
    sys.stderr.write(".")
    time.sleep(0.1)

log("")
log("yes: %d, no: %d, last5: %s" % (ycount, ncount, last5))

if (((ncount/30.0) < 0.3) or ("no" not in last5)):
    log("Link looks OK??")
    sys.exit(0)

log("Link looks bad. Shutting down everything")
if (pid is not None):
    log("Killing pid %s" % pid)
    os.system("kill -HUP %s" % pid)
else:
    log("No pid and no file specified. Failing in silence")
        
if (fname is not None):
    log("Touching restart file")
    open(fname, "w").write("restart")
