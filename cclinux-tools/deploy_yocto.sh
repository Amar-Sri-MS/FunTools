#!/bin/bash -e

tar Jxf bin/cc-linux-yocto/mips64hv/fun-image-mips64r6hv-mips64r6.tar.xz -C $DEPLOY_ROOT

#
# By default, don't start NTP.  System specific deployments may add a custom ntp.conf
#

rm -f $DEPLOY_ROOT/etc/ntp.conf
