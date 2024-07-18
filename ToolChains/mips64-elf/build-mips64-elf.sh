#!/bin/bash -ex
#
# Build MIPS64r6 big-endian toolchain
#
# resulting build/toolchain should be relocatable.
#

config_only=n
clean_src_dir=n
clean_bld_dir=n
while [[ $# -gt 0 ]]
do
	case $1 in
	config-only)
		config_only=y
		;;
	clean_src_dir)
		clean_src_dir=y
		;;
	clean_bld_dir)
		clean_bld_dir=y
		;;
	*)
		echo "Unknown option"
		;;
	esac
	shift
done

# as of Mar 21st 2023 latest versions available on respective sites
binutils_version=binutils-2.40
gcc_version=gcc-12.2.0
gdb_version=gdb-11.2
# David Daney's comment in PR-2061
## We need to be careful with binutils version and test that tools like addr2line work in finite time on large FunOS release images.
# Not sure if anyone is writing the test for add2line. But documenting there just in case.


toolchain=mips64-unknown-elf-${binutils_version}_${gcc_version}_${gdb_version}-$(uname -s)_$(uname -m)

binutils_archive=${binutils_version}.tar.xz
binutils_url="http://ftpmirror.gnu.org/binutils/${binutils_archive}"

gcc_archive=${gcc_version}.tar.xz
gcc_url="http://ftpmirror.gnu.org/gcc/${gcc_version}/${gcc_archive}"

gdb_archive=${gdb_version}.tar.xz
gdb_url="http://ftpmirror.gnu.org/gdb/${gdb_archive}"

# These patches probably need to be forward ported if you upgrade the gcc version.
# patches if any
case ${gcc_version} in
gcc-11.3.0)
	gcc_patches=(970-macos_arm64-building-fix.patch)
	;;
*)
	gcc_patches=()
	;;
esac

# These patches probably need to be forward ported if you upgrade the gdb version. We cannot lose the ability to debug FunOS images.
case ${gdb_version} in
gdb-11.2)
	gdb_patches=(fungible-enable-tls.patch fungible-enable-core.patch)
	;;
*)
	gdb_patches=()
	;;
esac

# config options
case $(uname) in
	'Linux')
		host_binutils_config=--with-static-standard-libraries
		host_gcc_config=--with-static-standard-libraries
		host_gdb_config=
		;;
	'Darwin')
		# Assume it is MacOS > 12.1 where default location is /opt/homebrew
		# sed --version will fail and kill the script if not gnu-sed
		# 
		# brew install gnu-sed gcc g++ binutils 
		export PATH="/opt/homebrew/opt/gnu-sed/libexec/gnubin:$PATH"
		#export GCC_GENERATE_DEBUGGING_SYMBOLS=no

		sed --version
		host_binutils_config=--with-static-standard-libraries
		host_gcc_config=--with-static-standard-libraries
		#host_gcc_config=--enable-offload-target=mips64-unknown-elf
		host_gdb_config=
		;;
	*)
		echo "Unknown platform"
		exit 1
		;;
esac

mkdir -p build
cd build

dest_dir=$PWD/${toolchain}


common_config='--enable-lto --enable-64-bit-bfd --enable-targets=all'

if [ $(uname) = "Darwin" ] ; then
common_config="${common_config} --without-isl"
fi

###### binutils ######

build_binutils () {
	if [ ! -f $binutils_archive ] ; then
		wget $binutils_url
	fi

	binutils_dir=mips64-${binutils_version}

	[ "$clean_bld_dir" = "y" ] && rm -rf $binutils_dir
	[ "$clean_src_dir" = "y" ] && rm -rf $binutils_version $binutils_dir

	[ ! -d $binutils_version ] && tar Jxf $binutils_archive

	mkdir -p $binutils_dir
	pushd $binutils_dir
	../${binutils_version}/configure --target=mips64-unknown-elf --prefix=$dest_dir $host_binutils_config \
	$common_config
	if [ "$config_only" = "n" ] ; then
		make -j4
		make -j4 install
	fi
	popd
}

###### gcc ######

build_gcc () {
	if [ ! -f $gcc_archive ] ; then
	wget $gcc_url
	fi

	gcc_dir=mips64-${gcc_version}

	[ "$clean_bld_dir" = "y" ] && rm -rf $gcc_dir
	[ "$clean_src_dir" = "y" ] && rm -rf $gcc_version $gcc_dir

	if [ ! -d $gcc_version ]
	then
		tar Jxf $gcc_archive
		pushd ${gcc_version}

		contrib/download_prerequisites

		for gcc_patch in ${gcc_patches[@]} ; do
			patch -p1 < ../../$gcc_patch
		done
		popd
	fi

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
		--with-arch=i6500 --with-abi=64 \
		CFLAGS='-v -O2'

	if [ "$config_only" = "n" ] ; then
		make -j4
		make -j4 install
		# Install libgmp to be able to build gdb
		make -C gmp install
	fi
	popd
}

###### gdb ######

build_gdb () {
	if [ ! -f $gdb_archive ] ; then
		wget $gdb_url
	fi

	gdb_dir=mips64-${gdb_version}

	[ "$clean_bld_dir" = "y" ] && rm -rf $gdb_dir
	[ "$clean_src_dir" = "y" ] && rm -rf $gdb_version $gdb_dir

	if [ ! -d $gdb_version ]
	then
		tar Jxf $gdb_archive
		pushd ${gdb_version}

		for gdb_patch in ${gdb_patches[@]} ; do
			patch -p1 < ../../$gdb_patch
		done
		popd
	fi

	orig_path=$PATH
	export PATH=$PATH:$dest_dir/bin
	mkdir -p $gdb_dir
	pushd $gdb_dir
	../${gdb_version}/configure --disable-sim --target=mips64-unknown-elf --prefix=$dest_dir $host_gdb_config \
		$common_config --with-python=python3

	if [ "$config_only" = "n" ] ; then
		make -j4
		make -j4 install
	fi
	popd
}

# useful to comment out what is already built if repeatedly attempting to build failed later stages.
# comment out any of following as needed during experimental builds of new versions
build_binutils
build_gcc
build_gdb

###### tarball ######

pushd $dest_dir
if [ "$config_only" = "n" ] ; then
	tar cJf ../${toolchain}.tar.xz *
fi
popd
