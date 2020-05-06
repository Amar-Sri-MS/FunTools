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

if [[ ! -n "$DEV_LINE" ]] ; then
    DEV_LINE=master
    if [[ -f $WORKSPACE/dev_line.txt ]] ; then
	source $WORKSPACE/dev_line.txt
    fi
fi

DOCHUB='http://dochub.fungible.local/doc/jenkins'

function fetch_dochub
{
    local fetch_dev_line=$1
    local dev_line_path=$2
    local target_file=$3
    local src_url=$DOCHUB/$fetch_dev_line/$dev_line_path

    echo "Fetching $src_url to $target_file..."

    if curl -s -f $DOCHUB/$fetch_dev_line/$dev_line_path -o $target_file ; then
	: # All good.
    else
	if [[ ($? -eq 22) && ($fetch_dev_line != "master") ]] ; then
	    echo "Not found, trying master..."
	    fetch_dev_line=master
	    src_url=$DOCHUB/$fetch_dev_line/$dev_line_path
	    echo "Fetching $src_url to $target_file..."
	    curl -s -f $DOCHUB/$fetch_dev_line/$dev_line_path -o $target_file
	else
	    exit 1
	fi
    fi
}

if [[ ! -n "$DKR_IMG_TAG" ]] ; then
    if [[ -f $WORKSPACE/build_info.txt ]] ; then
	read DKR_IMG_TAG < $WORKSPACE/build_info.txt
    else
	DKR_IMG_TAG='test_build'
    fi
fi

DOCKER_BUILD_DIR=$PWD/docker-build
mkdir -p $DOCKER_BUILD_DIR

# Get the proper Dockerfile. If a Dockerfile already exists in the
# docker-build directory, just use it.

DOC_IMG="docker.fungible.com/come_yocto:$DKR_IMG_TAG"
DOC_TAR="docker.fungible.com-come_yocto-$DKR_IMG_TAG.tar.xz"
DOCKERFILE="Dockerfile.come-yocto"

if [[ ! -f $DOCKER_BUILD_DIR/$DOCKERFILE ]] ; then
    echo "Copying $DOCKERFILE from $THIS_DIR..."
    cp $THIS_DIR/$DOCKERFILE $DOCKER_BUILD_DIR/$DOCKERFILE
fi

CC_LINUX_YOCTO_DIR=$WORKSPACE/cc-linux-yocto

# Fetch the base root filesystem image.

FUN_ARCH=x86_64
YOCTO_BASE_FILE=fun-image-x86-64dkr-qemux86-64.tar.xz

if [[ ! -f $DOCKER_BUILD_DIR/$YOCTO_BASE_FILE ]] ; then
    if [[ -f $CC_LINUX_YOCTO_DIR/$YOCTO_BASE_FILE ]] ; then
	echo "Copying $YOCTO_BASE_FILE from $CC_LINUX_YOCTO_DIR..."
	cp $CC_LINUX_YOCTO_DIR/$YOCTO_BASE_FILE $DOCKER_BUILD_DIR/$YOCTO_BASE_FILE
    else
	echo "Fetching $YOCTO_BASE_FILE from dochub..."
	fetch_dochub $DEV_LINE cc-linux-yocto/latest/$FUN_ARCH/$YOCTO_BASE_FILE $DOCKER_BUILD_DIR/$YOCTO_BASE_FILE
    fi
fi

# LIBFUNQ_FILE is an example of how to add tar files to docker context
# and Dockerfile so that they are installed into docker image when
# image is built. Please follow similar steps for other component
# install tar balls.


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
