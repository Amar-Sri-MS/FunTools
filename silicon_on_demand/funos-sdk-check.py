#!/usr/bin/env python2.7

# automatically download and run a funos-f1 binary from a specified
# FunSDK build

import os
import sys
import stat
import optparse
import tempfile


URL = "http://dochub.fungible.local/doc/jenkins/funsdk/%s/Linux/funos.mips64-extra.tgz"
PATH = "/home/cgray/sdk-check"

###
##   entrypoint
#
def main():
    
    parser = optparse.OptionParser(usage="usage: %prog [build-number]")

    global opts
    (opts, args) = parser.parse_args()

    if (len(args) != 1):
        parser.error("missing build number")
        sys.exit(1)

    bldno = args[0]
        
    # make us somewhere to play
    path = tempfile.mkdtemp(dir=PATH, prefix="bld_%s_" % bldno )

    # make it readable
    os.chmod(path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    # cd to it
    os.chdir(path)

    # pull down the file
    url = URL % bldno
    os.system("wget %s" % url)

    # extract it
    os.system("tar zxvf funos.mips64-extra.tgz")

    if (not os.path.exists("bin/funos-f1")):
        raise RuntimeError("no funos, womp womp")

    os.system("/project/tools/mips/cross/bin/mipsel-unknown-linux-gnu-strip bin/funos-f1")
    os.system("gzip bin/funos-f1")
    
    os.system("/home/cgray/bin/silicon_on_demand.py -x '-P \"/home/cgray/sdk-check/sdk-check-post.py %s\"' -e chip-chums@fungible.com submit %s/bin/funos-f1.gz" % (bldno, path))

    print "job scheduled"
    
###
##   entrypoint
#

if (__name__ == "__main__"):
    main()
