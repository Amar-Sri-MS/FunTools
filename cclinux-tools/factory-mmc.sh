#!/bin/sh
set -e

fs_archive=fs.tar.xz
kernel_blob=linux.blob

if [ ! -e $fs_archive ] ; then
    echo "Error: Missing $fs_archive"
    exit 1
fi
if [ ! -e $kernel_blob ] ; then
    echo "Error: Missing $kernel_blob"
    exit 1
fi

install_to() {
    base_dev=$1
    vmlinux_part=${base_dev}1
    fs_part=${base_dev}2
    echo "Partitioning eMMC ${base_dev} ..."
    ./do_emmc_partition.sh $base_dev
    echo "  ... Done partitioning eMMC ${base_dev}"

    echo "Writing linux blob to ${vmlinux_part} ..."
    dd if=${kernel_blob} of=${vmlinux_part} bs=1M
    echo "  ... Done writing linux blob to ${vmlinux_part}"

    echo "Formatting ${fs_part} as ext4 ..."
    mkfs.ext4 -F ${fs_part}
    echo "  ... Done formatting ${fs_part}"

    echo "Mounting ${fs_part} ..."
    mount ${fs_part} /mnt
    echo "Extracting fs contents to ${fs_part} ..."
    xzcat ${fs_archive} | tar -xf - -C /mnt
    echo "Unmounting ${fs_part} ..."
    umount /mnt
    echo "  ... Done unmounting ${fs_part}"
}

install_to /dev/vda

install_to /dev/vdb

funq_dev=$(lspci -d 1dad::ff00 -mmn | cut -d ' ' -f1)

echo "Using funq on: ${funq_dev}"

/usr/bin/funq-setup bind vfio $funq_dev

fwupgrade -d $funq_dev -i emmc_image.bin -f emmc
fwupgrade -d $funq_dev -i ccfg-s1-demo-10g_mpg.bjson.signed -f ccfg

fwupgrade -d $funq_dev -i emmc_image.bin -f emmc --active
fwupgrade -d $funq_dev -i ccfg-s1-demo-10g_mpg.bjson.signed -f ccfg --active

echo "Provisioning complete"

