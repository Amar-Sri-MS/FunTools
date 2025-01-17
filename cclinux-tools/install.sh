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

install -t $target_dir strip_tree.sh

install -t $target_dir gen_fgpt.py
install -t $target_dir gen_cclinux_dev_images.sh
