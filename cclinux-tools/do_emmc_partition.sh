#!/bin/sh
#
# Funvisor access to eMMC is offset by 2GiB (which is reserved for
# other things).
#
# Create two partitions:
#
#  1) Offset 8192 sectors holds XDATA
#     formated filesystem for vmlinux.bin et al.
#
#  2) Offset 65536 sectors for FunVisor Root.
#
# Total size is 14GiB (16Gib - 2 GiB reserved region)
#
set -e

if [ $# -ge 1 ] ; then
    DEV=$1
else
    DEV=/dev/vda
fi

parted -s $DEV -- mklabel gpt mkpart bxdata ext2 8192s 65535s mkpart root ext2 65536s -1MB


