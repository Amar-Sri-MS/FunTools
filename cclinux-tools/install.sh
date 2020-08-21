#!/bin/bash -e

if [ -z "$SDK_INSTALL_DIR" ] ; then
    echo "Error: SDK_INSTALL_DIR not set."
    exit 1
fi

#
# Tools used building deployments
#

target_dir=$SDK_INSTALL_DIR/bin/scripts

mkdir -p $target_dir

install -t $target_dir add_vmlinux_and_sign.sh
install -t $target_dir strip_tree.sh
install -t $target_dir deploy_factory.sh
install -t $target_dir deploy_ro_root.sh
