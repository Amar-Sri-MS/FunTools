#!/bin/bash
#
# This script creates a SDK tarball using FunOSPackageDemo and FunSDK source
# code suitable to give to customers.
#
# Optionally it create a MIPS toolchain tarball
#

# Output tarball
tarball_name=""

# README file
readme_file="README"

# Default is to use the master branch, no build ID, and to only build posix
branch=""
build_id=""
include_mips=""
toolchain_dir=""

# Top level directory
root_dir=`pwd`

show_usage()
{
    echo "usage: `basename "$0"` [options]"
    echo "options:"
    echo "  -h:                 Display this information."
    echo "  -b <branch>         Specify the FunSDK branch to use"
    echo "  -m                  Include MIPS and MIPS toolchain"
    echo "  -v <build_id>       Specify the FunSDK and FunOS build ID/version to use"
    echo "  -r <version>        Specify the release version to assign to the SDK"
    echo "                      Defaults to the FunSDK build_id"
}

# This is the text tha goes into the README file
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

sudo pip3 install python-pkcs11


MIPS toolchain installation
===========================

sudo mkdir -p /opt/cross
cd /opt/cross
sudo tar zxvf linux-mips64-gcc-9.3.tar.gz


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
./build/funospkg-s1-posix app=hello_world_pkg_wuh


Running sample channel push hello world package
===============================================

cd FunOSPackageDemo
./build/funospkg-s1-posix app=hello_world_ch


Running sample timer handler package
====================================

cd FunOSPackageDemo
./build/funospkg-s1-posix app=timer_test


Running sample NVMe memory volume package
=========================================

cd FunOSPackageDemo
./build/funospkg-s1-posix app=pkg_memvol_module_init,epnvme_test voltype=VOL_TYPE_SDK_BLK_MEMORY numios=100 nvfile=nvfile
EOM
}

# FunSDK download and setup
funsdk_setup()
{
    cd $root_dir

    # There can't be a FunSDK directory already present
    if [ -d FunSDK ]; then
	echo ""
	echo "Error: FunSDK already present. Remove and try again"
	echo ""
	exit 1
    fi

    # Clone FunSDK repository
    if [ "$branch" == "" ]; then
	git clone ssh://git@github.com/fungible-inc/FunSDK-small FunSDK
    else
	git clone ssh://git@github.com/fungible-inc/FunSDK-small -b \
	    $branch FunSDK
    fi

    cd FunSDK

    # Checkout the build_id if passed as argument
    if [ "$build_id" != "" ]; then
	git checkout tags/bld_$build_id
    fi

    # Download SDK packages
    if [ "$build_id" == "" ]; then
	./scripts/bob --sdkup --including sdk
	if [ "$include_mips" != "" ]; then
	    ./scripts/bob --sdkup --including deps-funos.mips64
	fi
    else
	./scripts/bob --sdkup -v $build_id --including sdk
	if [ "$include_mips" != "" ]; then
	    ./scripts/bob --sdkup -v $build_id --including deps-funos.mips64
	fi
    fi

    # Remove unneeded files
    find . -name .git |xargs rm -rf
    find . -name .gitignore |xargs rm -rf
    rm -rf FunSDK/chip/f1d1
    rm -rf FunSDK/chip/s2
    rm -rf palladium_test
    rm -rf bin/funos-f1d1*
    rm -rf bin/funos-f1*
    rm -rf bin/funos-s1-posix
    mv bin/funos-s1-posix.stripped bin/funos-s1-posix
    rm -rf bin/funos-posix*
    rm -rf bin/funos-s1-qemu*
    rm -rf FunQemu-Linux
    rm -rf gpl
    rm -rf integration_test
    rm -rf silicon_tests
    rm -rf static

    # Extract the build id from the downloaded FunSDK packages
    file="build_info.txt"
    build_id=$(cat "$file")
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

    # Clone FunOS and checkout using the tag bld_<build_id>
    tag=bld_$build_id
    git clone ssh://git@github.com/fungible-inc/FunOS
    cd FunOS
    git checkout tags/$tag
}

# Build FunOS and export the libraries and header files
funos_export_lib_headers()
{
    cd $root_dir/FunOS
    if ! make -j8 MACHINE=s1-posix install-libfunosrt install-funosrt-makefiles install-headers; then
	echo ""
	echo "FunOS s1-posix fails to build"
	echo ""
	exit 1
    fi

    # Check MIPS builds if requested
    if [ "$include_mips" != "" ]; then
	if ! make -j8 MACHINE=s1 install-libfunosrt install-funosrt-makefiles install-headers; then
	    echo ""
	    echo "FunOS s1 fails to build"
	    echo ""
	    exit 1
	fi
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

    # Build the MIPS packages if requested
    if [ "$include_mips" != "" ]; then
	if ! make -j8 MACHINE=s1; then
	    echo ""
	    echo "FunOSPackageDemo s1 fails to build"
	    echo ""
	    exit 1
	fi
    fi
}

# MIPS toolchain setup
mips_toolchain_setup()
{
    cd $root_dir
    mkdir $toolchain_dir
    cd $toolchain_dir
    wget http://dochub.fungible.local/doc/sw/tools/mips/linux-mips64-gcc-9.3.tar.gz
}

# Verify the posix packages run to completion
run_posix()
{
    cd $root_dir/FunOSPackageDemo
    if ! ./build/funospkg-s1-posix app=hello_world_pkg_wuh; then
	echo ""
	echo "s1-posix hello_world package fails to run to completion"
	echo ""
	exit 1
    fi

    if ! ./build/funospkg-s1-posix app=hello_world_ch; then
	echo ""
	echo "s1-posix hello_world_ch package fails to run to completion"
	echo ""
	exit 1
    fi

    if ! ./build/funospkg-s1-posix app=timer_test; then
	echo ""
	echo "s1-posix timer package fails to run to completion"
	echo ""
	exit 1
    fi

    if ! ./build/funospkg-s1-posix app=pkg_memvol_module_init,epnvme_test voltype=VOL_TYPE_SDK_BLK_MEMORY numios=100 nvfile=nvfile; then
	echo ""
	echo "s1-posix memvol package fails to run to completion"
	echo ""
	exit 1
    fi
}

# Parse the options
while getopts "hb:mv:r:" option; do
    case "$option" in
	h)
	    show_usage
	    exit 1
	    ;;
	b)
	    branch=$OPTARG
	    ;;
	m)
	    include_mips="yes"
	    toolchain_dir="toolchain"
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

# Setup the FunSDK source code
funsdk_setup

# Setup the FunOSPackageDemo source code
funos_package_demo_setup

# Setup the FunOS source code
funos_setup

# Verify the software builds and export libraries and header files to FunSDK
funos_export_lib_headers

# Download the MIPS toolchain if requested
if [ "$include_mips" != "" ]; then
    mips_toolchain_setup
fi

# Create README file
readme_setup

# Set the SDK tarball version to the build ID, if not passed as argument
if [ "$tarball_name" == "" ]; then
    tarball_name="Fungible-SDK-v$build_id.tgz"
fi

# Create tarball
cd root_dir
tar zcvf $tarball_name FunSDK FunOSPackageDemo $toolchain_dir $readme_file

# Build the FunOSPackageDemo packages
funos_package_demo_build

# Verify software runs
run_posix

echo ""
echo "$tarball_name is ready"
echo ""
