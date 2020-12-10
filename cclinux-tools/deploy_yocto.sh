#!/bin/bash -e

tar Jxf bin/cc-linux-yocto/mips64hv/fun-image-mips64r6hv-mips64r6.tar.xz -C $DEPLOY_ROOT

#
# By default, don't start NTP.  System specific deployments may add a custom ntp.conf
#

rm -f $DEPLOY_ROOT/etc/ntp.conf

#
# By default, don't create bondX devices when bonding is loaded
#

echo 'options bonding max_bonds=0' > $DEPLOY_ROOT/etc/modprobe.d/bonding.conf

#
# Allow DHCP to change hostname away from mips64r6
#

sed -i -E "/current_hostname\" = 'localhost' ] \|\|\$/a\\           [ \"\$current_hostname\" = 'mips64r6' ] \|\|" $DEPLOY_ROOT/sbin/dhclient-script
