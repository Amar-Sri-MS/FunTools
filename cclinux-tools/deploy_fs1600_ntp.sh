#!/bin/bash -e

cp bin/mips64/Linux/ntp-fs1600.conf $DEPLOY_ROOT/etc/ntp.conf
chmod 0444 $DEPLOY_ROOT/etc/ntp.conf
