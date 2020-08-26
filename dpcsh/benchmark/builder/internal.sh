#!/bin/bash

export GOARCH=mips64
prefix=/usr/bin/mipsisa64r6-linux-gnuabi64-

if [ -n "$USE_EL" ]; then
    prefix=/usr/bin/mipsisa64r6el-linux-gnuabi64-
fi

set -e -x
tmpdir=$(tempfile)
rm -rf ${tmpdir}
toolsbin=${tmpdir}/mips64/bin
mkdir -p ${toolsbin}
cd ${toolsbin}
ln -sf ${prefix}ar-10 ar
ln -sf ${prefix}as as
ln -sf ${prefix}gcc-10 gcc
ln -sf ${prefix}g++-10 g++
ln -sf ${prefix}ld ld
ln -sf ${prefix}ld.gold ld.gold
ln -sf ${prefix}ld.bfd ld.bfd
ln -sf ${prefix}gccgo-10 gccgo
ln -sf ${prefix}strip strip

export PATH=${toolsbin}:${PATH}
cd -

export GOPRIVATE=github.com/fungible-inc
export CGO_ENABLED="1"

go env
go build -v -gccgoflags "-static" \
    -compiler gccgo .
