#!/bin/bash -e
#
# To use, choose a read-only file system image, pass its path to this
# script.
#
# fvos.signed contains vmlinux.bin from the SDK
# fvht.bin is the signed hash tree for the read-only file system image.
# fgpt.signed is the signed partition table.
#
# These four components (file system image, fvos.signed, fvht.bin,
# fgpt.signed) are written to the MMC and compose the guest OS
# environment.
#
if [ $# -lt 1 ] ; then
    echo "Usage: gen_cclinux_dev_images.sh rootfs-file [vmlinux.bin]"
    exit 1
fi

rootfs_file=$1

if [ $# -lt 2 ] ; then
    vmlinux_file=$WORKSPACE/FunSDK/bin/cc-linux-yocto/mips64hv/vmlinux.bin
else
    vmlinux_file=$2
fi

if [ -z "$WORKSPACE" ] ; then
    echo "Error: WORKSPACE not set."
    exit 1
fi

if [ ! -d "$WORKSPACE/FunSDK/bin/scripts" ] ; then
   echo "Error: $WORKSPACE/FunSDK/bin/scripts does not exist"
   exit 1
fi

scripts_dir=$WORKSPACE/FunSDK/bin/scripts
flash_tools=$WORKSPACE/FunSDK/bin/flash_tools

# Generate fgpt.signed

$scripts_dir/gen_fgpt.py fgpt.tosign
$flash_tools/sign_for_development.py --fourcc fgpt fgpt.tosign -o fgpt.signed --sign_key hkey1 --version 1 --key_index 0
rm fgpt.tosign

# Generate fvos.signed
rm -f fvos.tosign
echo "vmlinux.bin ${vmlinux_file}" > fvos.filelist
$scripts_dir/xdata.py -r --data-offset=4096 --data-alignment=512 -P 4 fvos.tosign add-file-lists fvos.filelist
$flash_tools/sign_for_development.py --fourcc fvos fvos.tosign -o fvos.signed --sign_key hkey1 --version 1 --key_index 0
rm fvos.tosign fvos.filelist

# Generate fvht.bin

$flash_tools/gen_hash_tree.py -O fvht.bin hash -N rootfs.hashtree --to-sign fvht.tosign -I $rootfs_file
$flash_tools/sign_for_development.py --fourcc fvht fvht.tosign -o fvht.signed --sign_key hkey1 --version 1 --key_index 0
$flash_tools/gen_hash_tree.py -O fvht.bin insert --signed fvht.signed
rm fvht.signed  fvht.tosign

