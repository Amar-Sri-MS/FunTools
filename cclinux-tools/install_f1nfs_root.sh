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

install -t $target_dir deploy_f1nfs_root.sh

runtime_target_dir=$SDK_INSTALL_DIR/bin/mips64/Linux
mkdir -p $runtime_target_dir

install -t $runtime_target_dir -m 0644 interfaces-nfs
install -t $runtime_target_dir -m 0644 vlan-bmc
