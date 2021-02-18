#!/bin/bash -e
MYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cp bin/mips64/Linux/interfaces-nfs $DEPLOY_ROOT/etc/network/interfaces
chmod 0444 $DEPLOY_ROOT/etc/network/interfaces

cp bin/mips64/Linux/vlan-bmc $DEPLOY_ROOT/etc/init.d
chmod 0755 $DEPLOY_ROOT/etc/init.d/vlan-bmc
ln -s ../init.d/vlan-bmc $DEPLOY_ROOT/etc/rc5.d/S00vlan-bmc

