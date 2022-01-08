#!/bin/bash
#
# This script creates a SDK tarball using FunOSPackageDemo and FunSDK source
# code suitable to give to customers.

# fail if anything fails
set -e

# Output tarball
tarball_name=""

# README file
readme_file="README"

# Default is to use the master branch, no build ID, and to only build posix
branch_funsdk=""
branch_funos=""
build_id=""
build_funos="no"

# Top level directory
root_dir=`pwd`

show_usage()
{
    echo "usage: `basename "$0"` [options]"
    echo "options:"
    echo "  -h:                 Display this information."
    echo "  -b <branch>         Specify the FunSDK branch to use"
    echo "  -f <branch>         Specify the FunOS branch to use"
    echo "  -v <build_id>       Specify the FunSDK and FunOS build ID/version to use"
    echo "  -r <sdk-version>    Specify the release version to assign to the SDK"
    echo "                      Defaults to the FunSDK build_id"
}

# This is the text that goes into the FunSDK README file
readme_setup()
{
    cd $root_dir

    /bin/cat <<EOM >$readme_file
Build environment setup
=======================

The following packages must be installed on the Ubuntu 20.04 host to build
and run FunOS posix.

sudo apt-get install make
sudo apt-get install gcc-9
sudo apt-get install python
sudo apt-get install python3-pip
sudo apt-get install python-jinja2
sudo apt-get install python3-jinja2
sudo apt-get install clang
sudo apt-get install llvm
sudo apt-get install python-yaml
sudo apt-get install python3-asn1crypto
sudo apt-get install python3-pyelftools
sudo apt-get install makeself

MIPS toolchain installation
===========================

Download toolchain tarball (linux-mips64-gcc-8.2.tar.gz)
sudo mkdir -p /opt/cross
cd /opt/cross
sudo tar zxvf linux-mips64-gcc-8.2.tar.gz


Building the S1 posix target binary (funospkg-s1-posix)
=======================================================

tar zxvf Fungible-SDK-v0.1.tgz
cd FunOSPackageDemo
make -j8 MACHINE=s1-posix

The binary funospkg-s1-posix is placed in the build directory.


Building the S1 target binary (funospkg-s1)
===========================================

tar zxvf Fungible-SDK-v0.1.tgz
cd FunOSPackageDemo
make -j8 MACHINE=s1

The binary funospkg-s1 is placed in the build directory.


Running sample WU handler hello world package
=============================================

cd FunOSPackageDemo
./build/funospkg-s1-posix app=hello_world_pkg


Running sample channel push hello world package
===============================================

cd FunOSPackageDemo
./build/funospkg-s1-posix app=hello_world_channel


Running sample timer handler package
====================================

cd FunOSPackageDemo
./build/funospkg-s1-posix app=timer_test


Running sample workerpool package
====================================

cd FunOSPackageDemo
./build/funospkg-s1-posix app=workerpool_test_init


Running sample NVMe memory volume package
=========================================

cd FunOSPackageDemo
./build/funospkg-s1-posix app=pkg_memvol_module_init,epnvme_test voltype=VOL_TYPE_SDK_BLK_MEMORY numios=100 nvfile=nvfile


Running sample NVMe replication volume package
==============================================

cd FunOSPackageDemo
./build/funospkg-s1-posix app=pkg_repvol_template_module_init,mdt_test,volsetup_cp,voltest,vol_teardown --serial voltype=VOL_TYPE_BLK_REPLICA_TEMPLATE  numios=40 UUID=repvol-000000000 transport=TCP --csr-replay localip=29.1.1.2 remoteip=29.1.1.2 rdstype=funtcp nplex=2 remote_plex_count=0


Running sample CRC package
==========================

cd FunOSPackageDemo
./build/funospkg-s1-posix app=crc64_all_pkg
./build/funospkg-s1-posix app=crc_check_32_pkg
./build/funospkg-s1-posix app=crc_check_32c_pkg
./build/funospkg-s1-posix app=crc_tcp_csum_pkg
./build/funospkg-s1-posix app=crc_t10_test_pkg
./build/funospkg-s1-posix app=crc16_random_pkg
./build/funospkg-s1-posix app=crc32c_random_pkg
./build/funospkg-s1-posix app=crc32_fixed_pkg
./build/funospkg-s1-posix app=crc32_fixed_default_seed_pkg
./build/funospkg-s1-posix app=crc32c_fixed_pkg
./build/funospkg-s1-posix app=crc16_fixed_pkg
./build/funospkg-s1-posix app=crc16_fixed_default_seed_pkg
./build/funospkg-s1-posix app=crc32c_iscsi_payload_pkg


Running sample ZIP package
==========================

cd FunOSPackageDemo
./build/funospkg-s1-posix app=ziptest_pkg


Signing server
==============

Development bundles are signed during the build phase. This requires a
signing server to be accessible by the build system.

1. Installing a signing server
   . sudo ./signing_server.run

2. Configuring the build system to use the signing server
   . cd FunSDK
   . config_sdk_signing_server.sh http://<IP address of signing server>
   . Examples:
       . config_sdk_signing_server.sh http://192.168.122.22
       . config_sdk_signing_server.sh http://localhost


Building development bundles
============================

Development bundles are required to install custom FunOS binaries in the
hardware.

make -j8 MACHINE=s1 dev_bundle

Alternatevely, release images can also be installed

make -j8 MACHINE=s1-release dev_bundle


Installing development bundles
==============================

Before installing a development bundle, the matching release bundle must be
installed. This guarantees all the APIs across the complete system match. Note
that development bundles only include FunOS whereas release bundles include all
the system's binaries.
Installation of the release bundle is done only once for each new version of
the SDK.

1. scp release bundle to ccLinux's /tmp directory and install it
   . scp dev_signed_setup_bundle_s1-rootfs-ro.squashfs-v15578.sh root@10.1.1.20:/tmp
   . ssh root@10.1.1.20
   . cd /tmp
   . ./dev_signed_setup_bundle_s1-rootfs-ro.squashfs-v15578.sh
   . reboot
2. scp development bundle to ccLinux's /tmp directory and install it
   . scp setup_bundle_development_image.sh root@10.1.1.20:/tmp
   . ssh root@10.1.1.20
   . cd /tmp
   . ./setup_bundle_development_image.sh
   . reboot
EOM
}

# Gather the files needed to create a developemnt bundle
create_dev_bundle_environment()
{
    cd $root_dir/FunSDK

    # Development bundle directory
    mkdir -p bundle/development

    # Populate the bundle development directory
    ./bin/flash_tools/release.py --action sdk-prepare --destdir bundle/development --chip s1 bin/flash_tools/mmc_config_dev_funos.json bin/flash_tools/key_bag_config.json --force-version $build_id --force-description "SDK development bundle" --dev-image
    cd bundle/development
    ./release.py --chip s1  --destdir . --action sign --default-config-files

    # Remove unneeded files
    rm -rf __pycache__
    find . -name '*.pyc' -delete
    rm funos.signed.bin
    rm funos*.stripped
    rm *rootfs*
}

# FunSDK download and setup
funsdk_setup()
{
    cd $root_dir

    # There can't be a FunSDK directory already present
    if [ -d FunSDK ]; then
	echo ""
	echo "Error: FunSDK already present. Remove it and try again"
	echo ""
	exit 1
    fi

    # Clone FunSDK repository
    if [ "$branch_funsdk" == "" ]; then
	git clone ssh://git@github.com/fungible-inc/FunSDK-small FunSDK
    else
	git clone ssh://git@github.com/fungible-inc/FunSDK-small -b \
	    $branch_funsdk FunSDK
    fi

    cd FunSDK

    # Checkout the build_id if passed as an argument
    if [ "$build_id" != "" ]; then
	git checkout tags/bld_$build_id
    build_str="-v $build_id"
    fi

    # Download SDK packages
	./scripts/bob --sdkup $build_str --including sdk
	./scripts/bob --sdkup $build_str --including deps-funos.mips64
	./scripts/bob --sdkup $build_str release
	./scripts/bob --sdkup $build_str nu.csrreplay
	./scripts/bob --sdkup $build_str funos.fundoc
	./scripts/bob $build_str --deploy-up

    # Extract the build id from the downloaded FunSDK packages
    file="build_info.txt"
    build_id=$(cat "$file")

    # Download the packages needed to create bundles
    create_dev_bundle_environment

    # Remove unneeded files
    cd $root_dir/FunSDK
    find . -name .git |xargs rm -rf
    find . -name .gitignore |xargs rm -rf
    rm -rf FunSDK/chip/f1d1
    rm -rf FunSDK/chip/s2
    rm -rf FunSDK/config/pipeline/*f1d1*
    rm -rf palladium_test
    rm -rf FunQemu-Linux
    rm -rf gpl
    rm -rf integration_test
    rm -rf silicon_tests
    rm -rf static
    rm -rf bin/flash_tools/__pycache__
    rm -rf bin/funos*
    rm -rf bin/cc-linux-yocto
    rm -rf FunSDK/u-boot
    rm -rf FunSDK/sbpfw
    rm -rf FunSDK/nvdimm_fw
    rm -rf deployments
    rm -rf fdc_cbs
}

# FunOSPackageDemo download and setup
funos_package_demo_setup()
{
    cd $root_dir

    # There can't be a FunOS directory already present
    if [ -d FunOSPackageDemo ]; then
	echo ""
	echo "Error: FunOSPackageDemo already present. Remove and try again"
	echo ""
	exit 1
    fi

    # Clone FunOSPackageDemo and checkout the tag bld_<build_id>
    tag=bld_$build_id
    git clone git@github.com:fungible-inc/FunOSPackageDemo.git
    cd FunOSPackageDemo
    git checkout tags/$tag

    # Remove unneeded files
    find . -name .git |xargs rm -rf
    find . -name .gitignore |xargs rm -rf
}

# FunOS download and setup
funos_setup()
{
    cd $root_dir

    # There can't be a FunOS directory already present
    if [ -d FunOS ]; then
	echo ""
	echo "Error: FunOS already present. Remove and try again"
	echo ""
	exit 1
    fi

    # Clone FunOS repository
    if [ "$branch_funos" == "" ]; then
        # Clone FunOS and checkout using the tag bld_<build_id>
        tag=bld_$build_id
        git clone ssh://git@github.com/fungible-inc/FunOS
        cd FunOS
        git checkout tags/$tag
    else
        git clone ssh://git@github.com/fungible-inc/FunOS -b $branch_funos --depth 1
    fi
}

# Build FunOS and install the libraries and header files
funos_install_lib_headers()
{
    cd $root_dir/FunOS

    # Install makefiles and header files
    if ! make -j8 install-funosrt-makefiles install-headers; then
	echo ""
	echo "FunOS headers fails to build"
	echo ""
	exit 1
    fi

    # Build and install posix funos library & config
    if ! make -j8 MACHINE=s1-posix install-libfunosrt install-defaultcfg; then
	echo ""
	echo "FunOS s1-posix fails to build"
	echo ""
	exit 1
    fi

    # Build and install s1 funos library & config
    if ! make -j8 MACHINE=s1 install-libfunosrt install-defaultcfg; then
	echo ""
	echo "FunOS s1 fails to build"
	echo ""
	exit 1
    fi
}

# Build the FunOSPackageDemo packages
funos_package_demo_build()
{
    cd $root_dir/FunOSPackageDemo
    if ! make -j8 MACHINE=s1-posix; then
	echo ""
	echo "FunOSPackageDemo s1-posix fails to build"
	echo ""
	exit 1
    fi

    if ! make -j8 MACHINE=s1 dev_bundle; then
	echo ""
	echo "FunOSPackageDemo s1 fails to build"
	echo ""
	exit 1
    fi

    # copy the bundle to a versioned file in the root
    cd $root_dir
    cp $root_dir/FunOSPackageDemo/build/s1/setup_bundle_development_image.sh package-demo-bundle-s1-v${build_id}.sh
}

# fungible-host-drivers download and setup
fungible_host_drivers_setup()
{
    cd $root_dir

    # There can't be a FunOS directory already present
    if [ -d fungible-host-drivers ]; then
	echo ""
	echo "Error: fungible-host-drivers already present. Remove and try again"
	echo ""
	exit 1
    fi

    # Clone FunOS and checkout using the tag bld_<build_id>
    tag=bld_$build_id
    git clone git@github.com:fungible-inc/fungible-host-drivers.git
    cd fungible-host-drivers
    git checkout tags/$tag
}

# Build the FunOSPackageDemo packages
package_host_drivers()
{
    cd $root_dir/fungible-host-drivers/linux/kernel

    # package it into the distro directory
    PKG_NAME=fungible_drv_v${build_id}.tgz
    make PKG_PATH=$root_dir/$PKG_NAME PKG_NAME=$PKG_NAMAE package_tgz

    # build the whole thing
    make   
}

# Verify the posix packages run to completion
run_posix()
{
    cd $root_dir/FunOSPackageDemo
    if ! ./build/funospkg-s1-posix app=hello_world_pkg; then
	echo ""
	echo "s1-posix hello_world package fails to run to completion"
	echo ""
	exit 1
    fi

    if ! ./build/funospkg-s1-posix app=hello_world_channel; then
	echo ""
	echo "s1-posix hello_world_channel package fails to run to completion"
	echo ""
	exit 1
    fi

    if ! ./build/funospkg-s1-posix app=timer_test; then
	echo ""
	echo "s1-posix timer package fails to run to completion"
	echo ""
	exit 1
    fi

    if ! ./build/funospkg-s1-posix app=workerpool_test_init; then
	echo ""
	echo "s1-posix workerpool package fails to run to completion"
	echo ""
	exit 1
    fi

    if ! ./build/funospkg-s1-posix app=pkg_memvol_module_init,epnvme_test voltype=VOL_TYPE_SDK_BLK_MEMORY numios=100 nvfile=nvfile; then
	echo ""
	echo "s1-posix memvol package fails to run to completion"
	echo ""
	exit 1
    fi

    if ! ./build/funospkg-s1-posix app=pkg_repvol_template_module_init,mdt_test,volsetup_cp,voltest,vol_teardown --serial voltype=VOL_TYPE_BLK_REPLICA_TEMPLATE  numios=40 UUID=repvol-000000000 transport=TCP --csr-replay localip=29.1.1.2 remoteip=29.1.1.2 rdstype=funtcp nplex=2 remote_plex_count=0; then
	echo ""
	echo "s1-posix repvol package fails to run to completion"
	echo ""
	exit 1
    fi

    if  ! ./build/funospkg-s1-posix app=crc64_all_pkg ||
	! ./build/funospkg-s1-posix app=crc_check_32_pkg ||
	! ./build/funospkg-s1-posix app=crc_check_32c_pkg ||
	! ./build/funospkg-s1-posix app=crc_tcp_csum_pkg ||
	! ./build/funospkg-s1-posix app=crc_t10_test_pkg ||
	! ./build/funospkg-s1-posix app=crc16_random_pkg ||
	! ./build/funospkg-s1-posix app=crc32c_random_pkg ||
	! ./build/funospkg-s1-posix app=crc32_fixed_pkg ||
	! ./build/funospkg-s1-posix app=crc32_fixed_default_seed_pkg ||
	! ./build/funospkg-s1-posix app=crc32c_fixed_pkg ||
	! ./build/funospkg-s1-posix app=crc16_fixed_pkg ||
	! ./build/funospkg-s1-posix app=crc16_fixed_default_seed_pkg ||
	! ./build/funospkg-s1-posix app=crc32c_iscsi_payload_pkg; then
	echo ""
	echo "s1-posix CRC package fails to run to completion"
	echo ""
	exit 1
    fi

    if ! ./build/funospkg-s1-posix app=ziptest_pkg; then
	echo ""
	echo "s1-posix ZIP package fails to run to completion"
	echo ""
	exit 1
    fi
}

# Clean the FunOSPackageDemo
funos_package_demo_clean()
{
    cd $root_dir/FunOSPackageDemo
    make clean
    rm -f .map
    rm -f nvfile
}

# default to latest master
build_id="latest"

# Parse the options
while getopts "hb:f:v:r:" option; do
    case "$option" in
	h)
	    show_usage
	    exit 1
	    ;;
	b)
	    branch_funsdk=$OPTARG
        build_funos="yes"
	    ;;
	f)
	    branch_funos=$OPTARG
        build_funos="yes"
	    ;;
	v)
	    build_id=$OPTARG
	    ;;
	r)
	    tarball_name="Fungible-SDK-v$OPTARG.tgz"
	    ;;
	*)
	    show_usage
	    exit 1
	    ;;
    esac
done
shift $((OPTIND-1))

# check for "latest" build
if [ "$build_id" = "latest" ]; then
    echo "Retrieving latest build version"
    build_id=`wget -q -O - http://dochub.fungible.local/doc/jenkins/master/funsdk/latest/build_info.txt`
    echo "Latest build version is $build_id"
fi

# Setup the FunSDK source code
funsdk_setup

# Setup the FunOSPackageDemo source code
funos_package_demo_setup

# Setup the FunOS source code
if [ "$build_funos" == "yes" ]; then
    echo "Building FunOS"
    funos_setup

    # Verify the software builds and install libraries and header files to FunSDK
    funos_install_lib_headers
else
    echo "Using FunOS from SDK"
fi

# Setup the fungible-host-driver source code
fungible_host_drivers_setup

# Create README file
readme_setup

# Set the SDK tarball version to the build ID, if not passed as argument
if [ "$tarball_name" == "" ]; then
    tarball_name="Fungible-SDK-v$build_id.tgz"
fi

# Remove FunOSPackageDemo build objects
funos_package_demo_clean

# Create tarball
cd $root_dir
tar zcvf $tarball_name FunSDK FunOSPackageDemo $readme_file

# Build the bundle name without the build ID
bundle_name="dev_signed_s1_setup_bundle.sh"
cust_bundle="dev_signed_setup_bundle_s1-rootfs-ro.squashfs-v$build_id.sh"

# Download accompanying S1 bundle
wget http://dochub.fungible.local/doc/jenkins/master/funsdk/$build_id/$bundle_name
mv $bundle_name $cust_bundle

# Build the FunOSPackageDemo packages
funos_package_demo_build

# Verify software runs
run_posix

# Package and build test the host drivers
package_host_drivers

# Assemble a final directory
out_dir=Fungible-SDK-v$build_id
cd $root_dir
mkdir $out_dir
mv *.sh *.tgz $out_dir
cd $out_dir
md5sum * >manifest.txt

echo ""
echo "Accompanying S1 release bundle ($cust_bundle) is ready"
echo ""
echo "$tarball_name is ready"
echo ""
