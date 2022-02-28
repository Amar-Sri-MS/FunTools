#!/bin/bash -e
#
# Copy Yocto build products to SDK so they can be used to build
# deployment images
#
#

fun_image="fun-image-mips64r6hv-mips64r6.tar.xz"

for i in "$@" ; do
    if [ "$i" = "--developer" ]; then
        fun_image="fun-image-mips64r6hv-developer-mips64r6.tar.xz"
        break
    fi
done


if [ -z "$SDK_INSTALL_DIR" ] ; then
    echo "Error: SDK_INSTALL_DIR not set."
    exit 1
fi

src_dir=$WORKSPACE/cc-linux-yocto/mips64hv

if [ ! -d $src_dir ] ; then
    echo "Error: $src_dir doesn't exist."
    exit 1
fi

target_dir=$SDK_INSTALL_DIR/bin/cc-linux-yocto/mips64hv

mkdir -p $target_dir

cp $src_dir/vmlinux.bin $target_dir
tar xJf $src_dir/fun-image-kernel-dev-mips64r6.tar.xz -C $target_dir --strip-components=5 --wildcards '*System.map*'

cp $src_dir/$fun_image $target_dir
cp $src_dir/fun-s1-factory-image-mips64r6.cpio.gz $target_dir

cp $src_dir/../build_info.txt $target_dir

scripts_dir=$SDK_INSTALL_DIR/bin/scripts
mkdir -p $scripts_dir

patches_dir=$scripts_dir/patches
mkdir -p $patches_dir

install -t $scripts_dir deploy_yocto.sh
install -m 0644 -t $patches_dir patches/rc.patch
install -m 0644 -t $patches_dir patches/dhclient-script.patch
install -m 0644 -t $patches_dir patches/nfsroot.patch
install -m 0644 -t $patches_dir patches/ntpd.patch
install -t $scripts_dir gzip-stdin
install -t $scripts_dir miscinit

runtime_target_dir=$SDK_INSTALL_DIR/bin/mips64/Linux
mkdir -p $runtime_target_dir
install -t $runtime_target_dir -m 0644 vfio.conf
install -t $runtime_target_dir -m 0644 boot_success
