#!/bin/bash -e

if [ ! -e "$SDK_INSTALL_DIR" ] ; then
    echo "Error: SDK_INSTALL_DIR \"$SDK_INSTALL_DIR\" does not exist."
    exit 1
fi

target_dir=$SDK_INSTALL_DIR/bin/scripts

mkdir -p $target_dir

install -t $target_dir add_vmlinux_and_sign.sh
install -t $target_dir strip_tree.sh

