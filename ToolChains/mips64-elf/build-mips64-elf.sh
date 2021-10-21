#!/bin/bash
#
# Build MIPS64r6 big-endian toolchain
#
# resulting build/toolchain should be relocatable.
#
set -e

binutils_version=binutils-2.37
gcc_version=gcc-11.2.0
gdb_version=gdb-9.2

binutils_archive=${binutils_version}.tar.xz
binutils_url="http://ftpmirror.gnu.org/binutils/${binutils_archive}"

gcc_archive=${gcc_version}.tar.xz
gcc_url="http://ftpmirror.gnu.org/gcc/${gcc_version}/${gcc_archive}"

gdb_archive=${gdb_version}.tar.xz
gdb_url="http://ftpmirror.gnu.org/gdb/${gdb_archive}"

gdb_patches=0001-Fix-Python3.9-related-runtime-problems.patch

if [ $(uname) = 'Linux' ] ; then
    build_ldflags="LDFLAGS='-static-libstdc++ -static-libgcc'"
else
    # Assume it is MacOS
    export PATH=/usr/local/opt/gnu-sed/libexec/gnubin:$PATH
    # sed --version will fail and kill the script if not gnu-sed
    sed --version
    build_ldflags=
fi

mkdir -p build
cd build

dest_dir=$PWD/toolchain

if [ ! -e $binutils_archive ] ; then
    wget $binutils_url
fi

if [ ! -e $gcc_archive ] ; then
    wget $gcc_url
fi

if [ ! -e $gdb_archive ] ; then
    wget $gdb_url
fi

tar Jxf $binutils_archive

binutils_dir=mips64-${binutils_version}

mkdir -p $binutils_dir
pushd $binutils_dir
$build_ldflags ../${binutils_version}/configure --target=mips64-unknown-elf --prefix=$dest_dir
make -j4
make -j4 install
popd

tar Jxf $gcc_archive

pushd ${gcc_version}
contrib/download_prerequisites
popd

gcc_dir=mips64-${gcc_version}

mkdir -p $gcc_dir
pushd $gcc_dir
$build_ldflags ../${gcc_version}/configure --target=mips64-unknown-elf --prefix=$dest_dir --enable-languages=c,c++ --without-headers \
    --disable-shared			\
    --disable-libssp			\
    --disable-libsanitizer		\
    --disable-libquadmath		\
    --disable-libquadmath-support	\
    --disable-multilib			\
    --disable-libstdcxx			\
    --enable-plugin			\
    --enable-targets=64			\
    --with-arch=mips64r6 --with-abi=64
make -j4
make -j4 install
popd

tar Jxf $gdb_archive

pushd ${gdb_version}
for gdb_patch in $gdb_patches ; do
    patch -p1 < ../../$gdb_patch
done
popd

gdb_dir=mips64-${gdb_version}

orig_path=$PATH
export PATH=$PATH:$dest_dir/bin
mkdir -p $gdb_dir
pushd $gdb_dir
../${gdb_version}/configure --disable-sim --target=mips64-unknown-elf --prefix=$dest_dir
make -j4
make -j4 install
popd

pushd $dest_dir
tar cJf ../toolchain.tar.xz *
popd
