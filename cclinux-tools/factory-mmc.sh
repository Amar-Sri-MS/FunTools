#!/bin/sh
set -e

# Force eMMC partition start blocks
if [ "$1" = "both" ] ; then
    dpcsh -n modcfg set fw_upgrade/active_sector 0
    dpcsh -n modcfg set fw_upgrade/inactive_sector 2097152
fi

fs_archive=root-image.tar.xz
kernel_blob=fv.xdata.blob

if [ ! -e $fs_archive ] ; then
    echo "Error: Missing $fs_archive"
    exit 1
fi
if [ ! -e $kernel_blob ] ; then
    echo "Error: Missing $kernel_blob"
    exit 1
fi

if grep -q provision-10g /proc/cmdline
then
    ccfg_image=ccfg-s1-demo-10g_mpg.signed.bin
else
    ccfg_image=ccfg-s1-demo-1g.signed.bin
fi

funq_dev=$(lspci -d 1dad::ff00 -mmn | cut -d ' ' -f1)

echo "Using funq on: ${funq_dev}"
/usr/bin/funq-setup bind vfio $funq_dev

usage() {
    echo "Usage: factory-mmc.sh {active, inactive, both}"
    exit 1
}

install_to() {
    case $1 in
	inactive)
	    base_dev=/dev/vdb
	    fwupgrade_flag=
	    ;;
	active)
	    base_dev=/dev/vda
	    fwupgrade_flag='--active'
	    ;;
	*)
	    echo "Bad install destination $1"
	    exit 1
	    ;;
    esac

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

    echo "fwupgrade emmc"
    fwupgrade -d $funq_dev -i emmc_image.bin -f emmc $fwupgrade_flag
    if [ -e $ccfg_image ] ; then
	echo "fwupgrade ccfg to $ccfg_image"
	fwupgrade -d $funq_dev -i $ccfg_image -f ccfg $fwupgrade_flag
    fi
    if [ -e host_firmware_packed.bin ] ; then
	echo "fwupgrade host"
	fwupgrade -d $funq_dev -i host_firmware_packed.bin -f host $fwupgrade_flag
    fi
    if [ -e esecure_firmware_all.bin ] ; then
	echo "fwupgrade sbpf"
	fwupgrade -d $funq_dev -i esecure_firmware_all.bin -f sbpf $fwupgrade_flag
    fi
    if [ -e key_bag.bin ] ; then
	echo "fwupgrade kbag"
	fwupgrade -d $funq_dev -i key_bag.bin -f kbag $fwupgrade_flag
    fi
    if [ -e hu_sbm_serdes.bin ] ; then
	echo "fwupgrade husc"
	fwupgrade -d $funq_dev -i hu_sbm_serdes.bin -f husc $fwupgrade_flag
    fi
    echo "fwupgrade done"
}

if [ $# -lt 1 ] ; then
    usage
fi

case $1 in
    active)
	install_to active
	;;
    inactive)
	install_to inactive
	;;
    both)
	install_to inactive
	install_to active
	;;
    *)
	usage
	;;
esac

echo "Provisioning complete"
