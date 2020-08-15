#!/bin/bash -e

zcat bin/cc-linux-yocto/mips64hv/fun-s1-factory-image-mips64r6.cpio.gz | (cd $DEPLOY_ROOT ; cpio -i -d)
mkdir -p $DEPLOY_ROOT/etc $DEPLOY_ROOT/etc/rc5.d
cp bin/mips64/Linux/dhclient-enter-hooks $DEPLOY_ROOT/etc
cp bin/mips64/Linux/S99do-provision $DEPLOY_ROOT/etc/rc5.d

mkdir -p $DEPLOY_ROOT/home/root
cp bin/mips64/Linux/do_emmc_partition.sh $DEPLOY_ROOT/home/root
cp bin/mips64/Linux/factory-mmc.sh $DEPLOY_ROOT/home/root

bin/scripts/xdata.py -r --data-offset=4096 --data-alignment=512 $DEPLOY_ROOT/home/root/fv.xdata.blob add bin/cc-linux-yocto/mips64hv/vmlinux.bin

mkdir -p $DEPLOY_ROOT/etc/modprobe.d
echo 'options vfio enable_unsafe_noiommu_mode=yes' > $DEPLOY_ROOT/etc/modprobe.d/vfio.conf

if [ -f build_info.txt ] ; then
    fw_version=$(cat build_info.txt)
else
    fw_version=1
fi

bin/flash_tools/make_funos_emmc.py -v $fw_version -d $DEPLOY_ROOT/home/root bin/funos-s1.stripped

bin/flash_tools/sign_for_development.py --fourcc ccfg feature_sets/ccfg-s1-demo-10g_mpg.bjson -o $DEPLOY_ROOT/home/root/ccfg-s1-demo-10g_mpg.bjson.signed
ln -s ccfg-s1-demo-10g_mpg.bjson.signed $DEPLOY_ROOT/home/root/ccfg.bjson.signed

rm -f $DEPLOY_ROOT/home/root/emmc.ext4 $DEPLOY_ROOT/home/root/mmc0_image.bin $DEPLOY_ROOT/home/root/mmc1_image.bin
rm -f $DEPLOY_ROOT/home/root/boot.img $DEPLOY_ROOT/home/root/boot.pad.img $DEPLOY_ROOT/home/root/bootloader.scr
