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
CHIP="s1"

usage() {
    echo ""
    echo "Usage :"
    echo "Prepare S1 image from latest :          ./prepare_funos_image_from_dochub.sh"
    echo "Prepare F1 image from latest :          ./prepare_funos_image_from_dochub.sh --f1"
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
	--chip )
	    CHIP=$2
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
    wget http://dochub.fungible.local/doc/jenkins/master/funsdk/${VERSION}/Linux/funos~${CHIP}-release.tgz  -q --show-progress
    wget http://dochub.fungible.local/doc/jenkins/master/funsdk/${VERSION}/build_info.txt -q
    wget http://dochub.fungible.local/doc/jenkins/master/funsdk/latest/Linux/cc-linux-yocto.mips64.tgz
}

create_funos_image() {
    cd $TMPLOC
    VER=$(cat ./build_info.txt)
    touch $VER.txt    
    tar xf funos~${CHIP}-release.tgz
    tar xf cc-linux-yocto.mips64.tgz
    
    $WORKSPACE/FunSDK/bin/scripts/xdata.py $TMPLOC/bin/funos-$CHIP-release.stripped add $TMPLOC/bin/cc-linux-yocto/mips64hv/vmlinux.bin
    $WORKSPACE/FunSDK/bin/flash_tools/sign_for_development.py --fourcc fun1 --chip $CHIP -o $TMPLOC/funos-$CHIP-release.signed $TMPLOC/bin/funos-$CHIP-release.stripped
    gzip $TMPLOC/funos-$CHIP-release.signed
    filename=funos-$CHIP.signed.${VER}.gz
    cp $TMPLOC/funos-$CHIP-release.signed.gz $FINALLOC/$filename

    echo "Built $filename from FunSDK  $VER at $(date)" >  ${FINALLOC}/funos_image_${VER}.txt
    echo ""
    echo "cat ${FINALLOC}/funos_image_${VER}.txt "
    cat ${FINALLOC}/funos_image_${VER}.txt
    echo ""
    ls -l $FINALLOC/$filename
    
}

download_images
create_funos_image


