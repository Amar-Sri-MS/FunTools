#!/bin/bash -e

if [ -z "$SDK_INSTALL_DIR" ] ; then
    echo "Error: SDK_INSTALL_DIR not set."
    exit 1
fi

#
# Tools copied to the deloyment.
#
target_dir=$SDK_INSTALL_DIR/bin/scripts

mkdir -p $target_dir

install -t $target_dir deploy_ro_root.sh

runtime_target_dir=$SDK_INSTALL_DIR/bin/mips64/Linux

mkdir -p $runtime_target_dir

#
# Read only rootfs tools.
#
install -t $runtime_target_dir -m 0644 fstab-ro
install -t $runtime_target_dir -m 0644 interfaces-ro
install -t $runtime_target_dir -m 0644 eth0_0-dhcp.iface
install -t $runtime_target_dir -m 0644 vfio.conf
install -t $runtime_target_dir -m 0644 persist
install -t $runtime_target_dir -m 0644 umountpersist
install -t $runtime_target_dir -m 0644 b-persist
