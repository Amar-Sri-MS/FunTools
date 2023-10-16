#!/bin/bash -xe
#
# Build MIPS64r6 big-endian toolchain
#
# resulting build/toolchain should be relocatable.
#

if [ $# -ge 1 ] && [ "$1" == "config-only" ] ; then
    config_only=y
else
    config_only=n
fi

binutils_version=binutils-2.40
gcc_version=gcc-12.2.0
gdb_version=gdb-11.2

toolchain=mips64-unknown-elf-${binutils_version}_${gcc_version}_${gdb_version}-$(uname -s)_$(uname -m)
dest_dir=$PWD/${toolchain}

binutils_archive=${binutils_version}.tar.xz
binutils_url="http://ftpmirror.gnu.org/binutils/${binutils_archive}"

gcc_archive=${gcc_version}.tar.xz
gcc_url="http://ftpmirror.gnu.org/gcc/${gcc_version}/${gcc_archive}"

case ${gcc_version} in
gcc-11.3.0)
    gcc_patches=(970-macos_arm64-building-fix.patch)
    ;;
*)
    gcc_patches=()
    ;;
esac

gdb_archive=${gdb_version}.tar.xz
gdb_url="http://ftpmirror.gnu.org/gdb/${gdb_archive}"

gdb_patches=(fungible-enable-tls.patch fungible-enable-core.patch)

common_config='--enable-lto --enable-64-bit-bfd --enable-targets=all'

case $(uname) in
'Linux')
    host_binutils_config=--with-static-standard-libraries
    host_gcc_config=--with-static-standard-libraries
    host_gdb_config=
	;;
'Darwin')
	# experiment with gnu gcc and not clang
	# export DSYMUTIL=":"
    # export PATH="/opt/homebrew/opt/binutils/bin:$PATH"
	# export GCC_GENERATE_DEBUGGING_SYMBOLS=no
	# export LD_LIBRARY_PATH=$PWD/$gcc_dir/mpfr/src/.libs
	# export C_INCLUDE_PATH=$PWD/${gcc_version}/mpfr/src
    # host_binutils_config=--with-static-standard-libraries

	# need to brew install gnu-sed texinfo
    # sed --version will fail and kill the script if not gnu-sed
    export PATH="/opt/homebrew/opt/gnu-sed/libexec/gnubin:$PATH"
    sed --version
    host_binutils_config=
    host_gcc_config=
    host_gcc_config=
    #host_gcc_config=--with-static-standard-libraries
    #host_gcc_config=--enable-offload-target=mips64-unknown-elf
    host_gdb_config=

    # common_config="${common_config} --with-sysroot=$(xcrun -show-sdk-path)"
    common_config="${common_config} --without-isl"
	;;
*)
	echo "Unknown platform"
	exit 1
	;;
esac

mkdir -p build
cd build

if [ ! -e $binutils_archive ] ; then
    wget $binutils_url
fi

if [ ! -e $gcc_archive ] ; then
    wget $gcc_url
fi

if [ ! -e $gdb_archive ] ; then
    wget $gdb_url
fi

###### binutils ######

if [[ ! $SKIP_BINUTILS ]] # useful to skip during interactive experimentation, set to true
then
	[ ! -d ${binutils_version} ] && tar Jxf $binutils_archive

	binutils_dir=mips64-${binutils_version}
	mkdir -p $binutils_dir
	pushd $binutils_dir
	../${binutils_version}/configure --target=mips64-unknown-elf --prefix=$dest_dir $host_binutils_config \
	$common_config
	if [ "$config_only" = "n" ] ; then
	make -j4
	make -j4 install
	fi
	popd
fi

###### gcc ######

if [[ ! $SKIP_GCC ]] # useful to skip during interactive experimentation, set to true
then
	[ ! -d ${gcc_version} ] && tar Jxf $gcc_archive

	pushd ${gcc_version}
	for gcc_patch in ${gcc_patches[@]} ; do
		patch -p1 < ../../$gcc_patch
	done
	contrib/download_prerequisites
	popd

	gcc_dir=mips64-${gcc_version}
	pwd
	echo $PATH
	gcc --version

	mkdir -p $gcc_dir
	pushd $gcc_dir

	../${gcc_version}/configure --target=mips64-unknown-elf --prefix=$dest_dir $host_gcc_config \
		$common_config			\
		--enable-checking=release		\
		--enable-languages=c,c++		\
		--without-headers			\
		--disable-shared			\
		--disable-libssp			\
		--disable-libsanitizer		\
		--disable-libquadmath		\
		--disable-libquadmath-support	\
		--disable-multilib			\
		--disable-libstdcxx			\
		--enable-plugin			\
		--enable-targets=64			\
		--with-arch=i6500 --with-abi=64 CFLAGS='-v -O2'
	if [ "$config_only" = "n" ] ; then
		make -j4
		make -j4 install
		# Install libgmp to be able to build gdb
		make -C gmp install
	fi
	popd
fi

###### gdb ######

tar Jxf $gdb_archive

pushd ${gdb_version}
for gdb_patch in ${gdb_patches[@]} ; do
    patch -p1 < ../../$gdb_patch
done
popd

gdb_dir=mips64-${gdb_version}

orig_path=$PATH
export PATH=$PATH:$dest_dir/bin
mkdir -p $gdb_dir
pushd $gdb_dir
../${gdb_version}/configure --disable-sim --target=mips64-unknown-elf --prefix=$dest_dir $host_gdb_config \
   $common_config \
   --with-python=python3
if [ "$config_only" = "n" ] ; then
    make -j4
    make -j4 install
fi
popd

###### tarball ######

pushd $dest_dir
if [ "$config_only" = "n" ] ; then
    tar cJf ../${toolchain}.tar.xz *
fi
popd
