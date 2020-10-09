#!/bin/bash -e

cp bin/mips64/Linux/fstab-ro $DEPLOY_ROOT/etc/fstab
chmod 0444 $DEPLOY_ROOT/etc/fstab

mkdir -p $DEPLOY_ROOT/etc/modprobe.d/
cp bin/mips64/Linux/vfio.conf $DEPLOY_ROOT/etc/modprobe.d/vfio.conf
chmod 0444 $DEPLOY_ROOT/etc/modprobe.d/vfio.conf

ln -s /tmp/resolv.conf $DEPLOY_ROOT/etc/resolv.conf

mv -f $DEPLOY_ROOT/etc/ssh/sshd_config_readonly $DEPLOY_ROOT/etc/ssh/sshd_config

sed -i -e 's^/etc/resolv.conf^/tmp/resolv.conf^' $DEPLOY_ROOT/sbin/dhclient-script

