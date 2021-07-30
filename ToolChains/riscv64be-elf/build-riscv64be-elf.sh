#!/bin/bash
#
# Build RiscV big-endian toolchain
#
# resulting build/toolchain should be relocatable.
#
set -e

binutils_version=binutils-2.37
gcc_version=gcc-11.2.0

binutils_archive=${binutils_version}.tar.xz
binutils_url="http://ftpmirror.gnu.org/binutils/${binutils_archive}"

gcc_archive=${gcc_version}.tar.xz
gcc_url="http://ftpmirror.gnu.org/gcc/${gcc_version}/${gcc_archive}"

cd build

dest_dir=$PWD/toolchain

if [ ! -e $binutils_archive ] ; then
    wget $binutils_url
fi

if [ ! -e $gcc_archive ] ; then
    wget $gcc_url
fi

tar Jxf $binutils_archive

binutils_dir=riscv-${binutils_version}

mkdir -p $binutils_dir
pushd $binutils_dir
../${binutils_version}/configure --target=riscv64be-elf --prefix=$dest_dir
make -j4
make -j4 install
popd

tar Jxf $gcc_archive

gcc_dir=riscv-${gcc_version}

mkdir -p $gcc_dir
pushd $gcc_dir
../${gcc_version}/configure --target=riscv64be-elf --prefix=$dest_dir --enable-languages=c --without-headers --disable-libssp
make -j4
make -j4 install
popd

