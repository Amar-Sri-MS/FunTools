#!/bin/bash -e
MYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cp bin/mips64/Linux/fstab-ro $DEPLOY_ROOT/etc/fstab
chmod 0444 $DEPLOY_ROOT/etc/fstab

cp bin/mips64/Linux/interfaces-ro $DEPLOY_ROOT/etc/network/interfaces
chmod 0444 $DEPLOY_ROOT/etc/network/interfaces

cp bin/mips64/Linux/eth0-dhcp.iface $DEPLOY_ROOT/etc/network/eth0-dhcp.iface
chmod 0444 $DEPLOY_ROOT/etc/network/eth0-dhcp.iface

ln -s /tmp/resolv.conf $DEPLOY_ROOT/etc/resolv.conf

mkdir -p $DEPLOY_ROOT/etc/ssh/
rm -f $DEPLOY_ROOT/etc/ssh/sshd_config*
cp bin/mips64/Linux/sshd_config-ro $DEPLOY_ROOT/etc/ssh/sshd_config
chmod 0400 $DEPLOY_ROOT/etc/ssh/sshd_config

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

#
# NTP things
#
ln -s /tmp/ntp.conf $DEPLOY_ROOT/etc/ntp.conf

#
# cron & logrotate
#

mkdir -p $DEPLOY_ROOT/etc/cron/crontabs
# cron.daily is automatically created but it's not used anywhere
# so delete it from rootfs to avoid confusion
rm -rf $DEPLOY_ROOT/etc/cron.daily
ln -s ../init.d/busybox-cron $DEPLOY_ROOT/etc/rc5.d/S30cron
cp bin/mips64/Linux/crontab.root $DEPLOY_ROOT/etc/cron/crontabs/root
chmod 0444 $DEPLOY_ROOT/etc/cron/crontabs/root

cp bin/mips64/Linux/uboot_mpg_update.sh $DEPLOY_ROOT/usr/bin/uboot_mpg_update
chmod 0555 $DEPLOY_ROOT/usr/bin/uboot_mpg_update

# rootfs boot-time verification
cp bin/mips64/Linux/ro-verify-emmc/verify_ro_root.sh $DEPLOY_ROOT/etc/init.d/verify_ro_root
chmod 0555 $DEPLOY_ROOT/etc/init.d/verify_ro_root
ln -s ../init.d/verify_ro_root $DEPLOY_ROOT/etc/rc5.d/S25verify_ro_root

mkdir -p $DEPLOY_ROOT/etc/boot-success-hooks.d
cp bin/mips64/Linux/ro-verify-emmc/verify_ro_root_hook.sh $DEPLOY_ROOT/etc/boot-success-hooks.d
chmod 0555 $DEPLOY_ROOT/etc/boot-success-hooks.d/verify_ro_root_hook.sh

cp bin/mips64/Linux/ro-verify-emmc/verify_root_version_hook.sh $DEPLOY_ROOT/etc/boot-success-hooks.d
chmod 0555 $DEPLOY_ROOT/etc/boot-success-hooks.d/verify_root_version_hook.sh
