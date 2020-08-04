#!/bin/bash -e

zcat bin/cc-linux-yocto/mips64hv/fun-s1-factory-image-mips64r6.cpio.gz | (cd $DEPLOY_ROOT ; cpio -i -d)
mkdir -p $DEPLOY_ROOT/etc $DEPLOY_ROOT/etc/rc5.d
cp bin/mips64/Linux/dhclient-enter-hooks $DEPLOY_ROOT/etc
cp bin/mips64/Linux/S99do-provision $DEPLOY_ROOT/etc/rc5.d

mkdir -p $DEPLOY_ROOT/home/root
cp bin/mips64/Linux/do_emmc_partition.sh $DEPLOY_ROOT/home/root
cp bin/mips64/Linux/factory-mmc.sh $DEPLOY_ROOT/home/root

bin/scripts/xdata.py -r --data-offset=4096 --data-alignment=512 $DEPLOY_ROOT/home/root/linux.blob add bin/cc-linux-yocto/mips64hv/vmlinux.bin
