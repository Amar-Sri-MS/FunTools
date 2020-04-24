#!/bin/bash
set -ex

if [[ "$(uname)" == "Linux" ]]; then
    INSTALL_DIR=/opt/cross/mips64
    OLD_TOOL_PREFIX=/opt/cross/bin/mipsel-unknown-linux-gnu-
    SUDO=sudo
else
    INSTALL_DIR=/Users/Shared/cross/mips64
    OLD_TOOL_PREFIX=/Users/Shared/cross-el/bin/mips64el-
    SUDO=
fi

####################################################
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

error() {
	echo "ERROR: $@"
	exit 1
}

# Download library sources for static linking
./contrib/download_prerequisites


SRC_DIR=${SCRIPT_DIR}

if [[ ! -f ./configure ]]; then
   error "Cannot find configure script"
fi

OBJ_DIR=${SRC_DIR}-objdir

#rm -rf /Users/Shared/cross/mips64
rm -rf ${HOME}/src/gcc-8.2.0-objdir

##if [[ -d ${INSTALL_DIR} ]]; then
##    error "Could not delete INSTALL_DIR=${INSTALL_DIR}"
##fi

if [[ -d ${OBJ_DIR} ]]; then
    error "Could not delete OBJ_DIR=${OBJ_DIR}"
fi

# This is not an arbitrary name, it affects configure behavior
TARGET=mips64-unknown-elf

mkdir -p ${OBJ_DIR}
cd ${OBJ_DIR}

export CC=gcc-8
export CXX=g++-8

export AR_FOR_TARGET=${OLD_TOOL_PREFIX}ar
export AS_FOR_TARGET=${OLD_TOOL_PREFIX}as
export LD_FOR_TARGET=${OLD_TOOL_PREFIX}ld
export NM_FOR_TARGET=${OLD_TOOL_PREFIX}nm
export RANLIB_FOR_TARGET=${OLD_TOOL_PREFIX}ranlib

${SRC_DIR}/configure			\
    --target=${TARGET}			\
    --enable-languages=c,c++		\
    --prefix=${INSTALL_DIR}		\
    --with-gcc-major-version-only	\
    --disable-shared			\
    --disable-libitm			\
    --disable-libsanitizer		\
    --disable-libquadmath		\
    --disable-libquadmath-support	\
    --disable-multiarch			\
    --disable-werror			\
    --disable-libssp			\
    --disable-libstdcxx			\
    --enable-plugin			\
    --with-arch-64=mips64r6		\
    --with-abi=64			\
    --disable-multilib			\
    --enable-targets=64			\
    --enable-checking=release		\
    --without-headers			\


make -j 8

${SUDO} make install

ls -al ${INSTALL_DIR}/bin

echo "All done"
