#!/bin/bash
#
# Example script for creating file system images to be used in ACU emulation runs.
#
# The resulting image can be used to populate an NVMe memvol namespace
# which is accessible to ACU software on the NVMe controller function
# present in the ACU PCI hierarchy
#
set -e

if [ $# -lt 1 ] ; then
    echo "Usage: $0 image_name"
    exit 1
fi

image_name=$1

fs_size_mb=16

#
# Use 4096 for NVMe volumes as epnvme has problems with 512
#
sector_size=4096

#
# Create all zero file of desired image size.
#
dd if=/dev/zero of=$image_name bs=1M count=$fs_size_mb

#
# Create the filesystem
#
mkfs.vfat -S $sector_size $image_name

#
# Connect to loopback device
#
image_dev=$(losetup --show -f -b $sector_size $image_name)

mount_point=$(mktemp -d)

#
# Mount it so we can add files
#
mount $image_dev $mount_point

#
# Create STARTUP.NSH
#
cat > $mount_point/STARTUP.NSH <<EOF
pci -i
EOF

#
# Cleanup by unmounting
#
umount $mount_point

rm -d $mount_point

#
# Disconnect loopback
#
losetup -d $image_dev
