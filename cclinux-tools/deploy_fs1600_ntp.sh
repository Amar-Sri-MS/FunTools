#!/bin/bash -e

cp bin/mips64/Linux/ntp-fs1600.conf $DEPLOY_ROOT/etc/ntp.conf
chmod 0444 $DEPLOY_ROOT/etc/ntp.conf


cp bin/mips64/Linux/vlan-bmc $DEPLOY_ROOT/etc/init.d
chmod 0755 $DEPLOY_ROOT/etc/init.d/vlan-bmc
ln -s ../init.d/vlan-bmc $DEPLOY_ROOT/etc/rc5.d/S00vlan-bmc

#
# Force NTP to synchronize before continuing the boot.
#
sed -i -E '/settick\(\)\{/a\\        $DAEMON -u ntp:ntp -p $PIDFILE -g -q' $DEPLOY_ROOT/etc/init.d/ntpd
