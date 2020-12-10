#!/bin/bash -e

cp bin/mips64/Linux/fstab-ro $DEPLOY_ROOT/etc/fstab
chmod 0444 $DEPLOY_ROOT/etc/fstab

cp bin/mips64/Linux/interfaces-ro $DEPLOY_ROOT/etc/network/interfaces
chmod 0444 $DEPLOY_ROOT/etc/network/interfaces

cp bin/mips64/Linux/eth0-dhcp.iface $DEPLOY_ROOT/etc/network/eth0-dhcp.iface
chmod 0444 $DEPLOY_ROOT/etc/network/eth0-dhcp.iface

mkdir -p $DEPLOY_ROOT/etc/modprobe.d/
cp bin/mips64/Linux/vfio.conf $DEPLOY_ROOT/etc/modprobe.d/vfio.conf
chmod 0444 $DEPLOY_ROOT/etc/modprobe.d/vfio.conf

ln -s /tmp/resolv.conf $DEPLOY_ROOT/etc/resolv.conf

mv -f $DEPLOY_ROOT/etc/ssh/sshd_config_readonly $DEPLOY_ROOT/etc/ssh/sshd_config

sed -i -e 's^/etc/resolv.conf^/tmp/resolv.conf^' $DEPLOY_ROOT/sbin/dhclient-script

#
# establish /persist
#
mkdir -p $DEPLOY_ROOT/persist
mkdir -p $DEPLOY_ROOT/b-persist

cp bin/mips64/Linux/persist $DEPLOY_ROOT/etc/init.d
chmod 0555 $DEPLOY_ROOT/etc/init.d/persist
ln -s ../init.d/persist $DEPLOY_ROOT/etc/rc5.d/S00persist

cp bin/mips64/Linux/umountpersist $DEPLOY_ROOT/etc/init.d
chmod 0555 $DEPLOY_ROOT/etc/init.d/umountpersist
ln -s ../init.d/umountpersist $DEPLOY_ROOT/etc/rc0.d/S39umountpersist

cp bin/mips64/Linux/b-persist $DEPLOY_ROOT/usr/bin
chmod 0555 $DEPLOY_ROOT/usr/bin/b-persist
#
# relay timezone and localtime through /tmp
#

ln -f -s /tmp/timezone $DEPLOY_ROOT/etc/timezone
ln -f -s /tmp/localtime $DEPLOY_ROOT/etc/localtime
