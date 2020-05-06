#!/bin/bash

set -e
#set -x

THIS_DIR=$(dirname $(realpath $0))

if [[ ! -n "$WORKSPACE" ]] ; then
    if [[ -d ../FunSDK ]] ; then
	WORKSPACE=$(realpath ..)
	echo "Using WORKSPACE=$WORKSPACE"
    else
	echo 'Error: WORKSPACE not set'
	exit 1
    fi
elif [[ ! -d $WORKSPACE ]] ; then
    echo "Error: WORKSPACE $WORKSPACE does not exist"
    exit 1
fi


if [[ ! -n "$SDKDIR" ]] ; then
    SDKDIR=$WORKSPACE/FunSDK
fi

if [[ ! -d $SDKDIR ]] ; then
    echo 'Error: SDKDIR does not exist'
    exit 1
fi

if [[ ! -n "$BUILD_NUMBER" ]] ; then
    if [[ -f $WORKSPACE/build_info.txt ]] ; then
	read BUILD_NUMBER < $WORKSPACE/build_info.txt
    else
	BUILD_NUMBER='test_build'
    fi
fi

DOCKER_BUILD_DIR=$PWD/docker-build
mkdir -p $DOCKER_BUILD_DIR

CC_LINUX_YOCTO_DIR=$WORKSPACE/cc-linux-yocto

FUN_ARCH=x86_64
FUN_BRANCH=master
YOCTO_BASE_FILE=fun-image-x86-64dkr-qemux86-64.tar.xz

if [[ ! -f $DOCKER_BUILD_DIR/$YOCTO_BASE_FILE ]] ; then
    if [[ -f $CC_LINUX_YOCTO_DIR/$YOCTO_BASE_FILE ]] ; then
	echo "Copying $YOCTO_BASE_FILE from $CC_LINUX_YOCTO_DIR..."
	cp $CC_LINUX_YOCTO_DIR/$YOCTO_BASE_FILE $DOCKER_BUILD_DIR/$YOCTO_BASE_FILE
    else
	echo "Fetching $YOCTO_BASE_FILE from dochub..."
	FILE_URL="http://dochub.fungible.local/doc/jenkins/$FUN_BRANCH/cc-linux-yocto/latest/$FUN_ARCH/$YOCTO_BASE_FILE"
	curl -s --output $DOCKER_BUILD_DIR/$YOCTO_BASE_FILE $FILE_URL
    fi
fi

DOC_IMG="docker.fungible.com/come_yocto:$BUILD_NUMBER"
DOC_TAR="docker.fungible.com-come_yocto-$BUILD_NUMBER.tar.xz"
DOCKERFILE="Dockerfile.come-yocto"

if [[ ! -f $DOCKER_BUILD_DIR/$DOCKERFILE ]] ; then
    echo "Copying $DOCKERFILE from $THIS_DIR..."
    cp $THIS_DIR/$DOCKERFILE $DOCKER_BUILD_DIR/$DOCKERFILE
fi

LIBFUNQ_FILE=libfunq.tgz
if [[ ! -f $DOCKER_BUILD_DIR/$LIBFUNQ_FILE ]] ; then
    LIBFUNQ_LOC=$SDKDIR/FunSDK/host-drivers/$FUN_ARCH/user/x86_yocto_palladium
    echo "Copying $LIBFUNQ_FILE from $LIBFUNQ_LOC..."
    cp $LIBFUNQ_LOC/$LIBFUNQ_FILE $DOCKER_BUILD_DIR/$LIBFUNQ_FILE
fi

echo "Building docker image..."
docker build -t $DOC_IMG -f $DOCKER_BUILD_DIR/$DOCKERFILE $DOCKER_BUILD_DIR

echo "Saving docker image to $DOC_TAR ..."
docker save $DOC_IMG | xz -c > $DOC_TAR
