#!/bin/bash

set -e

if [ -z "$1" ]; then
    echo "usage: $0 <FunTools src> <artifacts out>"
    exit 1
fi

if [ -z "$2" ]; then
    echo "usage: $0 <FunTools src> <artifacts out>"
    exit 1
fi

SRCDIR=$1
OUTDIR=$2

mkdir -p ${OUTDIR}

# Run the Docker container
sudo docker run --rm --name bmcbuild0 \
    -v ${SRCDIR}:/home/bmcbuild/src \
    -v ${OUTDIR}:/home/bmcbuild/artifacts \
    bmcbuild \
    /home/bmcbuild/src/ado-build/bmcbuild/build-i2c-dbg.sh

