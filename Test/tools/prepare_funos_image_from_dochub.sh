#!/bin/bash
#set -x

if [ -z ${WORKSPACE+x} ]; then
    echo "WORKSPACE is unset"
    exit 1
fi

TMPLOC="/tmp/download"
mkdir -p $TMPLOC
FINALLOC=$WORKSPACE

VERSION="latest"

usage() {
    echo ""
    echo "Usage :"
    echo "Prepare from latest :          ./prepare_funos_image_from_dochub.sh"
    echo "Prepare from a given version : ./prepare_funos_image_from_dochub.sh --ver 13225"
    echo ""
}
while test $# -gt 0
do
    case "$1" in
	--ver )
            IMAGEVER=$2
	    shift
            ;;
        *)
            usage
	    exit 1
            ;;
    esac
    shift
done


download_images() {
    cd $TMPLOC
    rm -rf *
    wget http://dochub.fungible.local/doc/jenkins/master/funsdk/${VERSION}/Linux/funos.mips64-extra.tgz  -q --show-progress
    wget http://dochub.fungible.local/doc/jenkins/master/funsdk/${VERSION}/build_info.txt -q
}

create_funos_image() {
    cd $TMPLOC
    VER=$(cat ./build_info.txt)
    touch $VER.txt    
    tar xf funos.mips64-extra.tgz

    $WORKSPACE/FunSDK/bin/scripts/xdata.py $TMPLOC/bin/funos-s1-release.stripped add $WORKSPACE/FunSDK/bin/cc-linux-yocto/mips64hv/vmlinux.bin
    $WORKSPACE/FunSDK/bin/flash_tools/sign_for_development.py --fourcc fun1 --chip s1 -o $TMPLOC/funos-s1-release.signed $TMPLOC/bin/funos-s1-release.stripped
    gzip $TMPLOC/funos-s1-release.signed
    filename=funos-s1.signed.gz.${VER}
    cp $TMPLOC/funos-s1-release.signed.gz $FINALLOC/$filename

    echo "Built $filename from FunSDK  $VER at $(date)" >  ${FINALLOC}/funos_image_${VER}.txt
    echo ""
    echo "cat ${FINALLOC}/funos_image_${VER}.txt "
    cat ${FINALLOC}/funos_image_${VER}.txt
    echo ""
    ls -l $FINALLOC/$filename
    
}

download_images
create_funos_image


