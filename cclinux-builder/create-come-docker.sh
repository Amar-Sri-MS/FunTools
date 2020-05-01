#!/bin/bash

set -e
#set -x

THIS_DIR=$(dirname $(realpath $0))

if [[ (! -n "$WORKSPACE") || ! -d $WORKSPACE ]] ; then
    echo 'Error: WORKSPACE not set'
    exit 1
fi


if [[ ! -n "$SDKDIR" ]] ; then
    SDKDIR=$WORKSPACE/FunSDK
fi

if [[ ! -d $SDKDIR ]] ; then
    echo 'Error: SDKDIR does not exist'
    exit 1
fi

if [[ -n "BUILD_NUMBER" ]] ; then
    BUILD_NUMBER="test_build"
fi

FUN_ARCH=x86_64
FUN_BRANCH=master
YOCTO_BASE_FILE=fun-image-x86-64dkr-qemux86-64.tar.xz

if [[ ! -f $YOCTO_BASE_FILE ]] ; then
    echo "Fetching $YOCTO_BASE_FILE from dochub..."
    FILE_URL="http://dochub.fungible.local/doc/jenkins/$FUN_BRANCH/cc-linux-yocto/latest/$FUN_ARCH/$YOCTO_BASE_FILE"
    curl -s --output $YOCTO_BASE_FILE $FILE_URL
fi

DOC_IMG="docker.fungible.com/come_yocto:$BUILD_NUMBER"
DOC_TAR="docker.fungible.com-come_yocto-$BUILD_NUMBER.tar.xz"
DOCKERFILE="Dockerfile.come-yocto"

if [[ ! -f $DOCKERFILE ]] ; then
    echo "Copying $DOCKERFILE from $THIS_DIR..."
    cp $THIS_DIR/$DOCKERFILE $DOCKERFILE
fi

LIBFUNQ_FILE=libfunq.tgz
if [[ ! -f $LIBFUNQ_FILE ]] ; then
    LIBFUNQ_LOC=$SDKDIR/FunSDK/host-drivers/$FUN_ARCH/user/x86_yocto_palladium
    echo "Copying $LIBFUNQ_FILE from $LIBFUNQ_LOC..."
    cp $LIBFUNQ_LOC/$LIBFUNQ_FILE $LIBFUNQ_FILE
fi

echo "Building docker image..."
docker build -t $DOC_IMG -f $DOCKERFILE .

echo "Saving docker image..."
docker save $DOC_IMG | xz -c > $DOC_TAR
