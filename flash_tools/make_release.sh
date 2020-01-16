#!/bin/bash -e

show_help ()
{
    echo "make_release.sh: Prepare files for creating a release or a start certificate"
    echo ""
    echo "Usage:"
    echo "./make_release.sh [-b] <bundle or build number>"
    echo ""
    echo "-h help: show this message"
    echo "-b bundle: number is a bundle number"

}

build_number_of_bundle_number ()
{
    # retrieve the build properties file
    wget -O - "http://dochub.fungible.local/doc/jenkins/master/fs1600/"$1"/bld_props.json" | \
	python3 -c "import sys,json; print(json.load(sys.stdin)['components']['funsdk_flash_images'])"
}


if [[ `uname` != "Linux" ]] ; then
    echo "Sorry. This script can only be run on Linux"
    exit 1
fi

BUNDLE_FLAG=0
while getopts "b" opt; do
    case "$opt" in
	h) show_help
	   exit 0
	   ;;
	b) BUNDLE_FLAG=1
	   ;;
    esac
done

shift $(($OPTIND - 1))

# argument required
if [  $# != 1 ] ; then
    show_help
    echo "Missing argument: build number or bundle number"
    exit 1
fi

if [ $BUNDLE_FLAG -eq 1 ]; then
    BUILD_NUMBER=$(build_number_of_bundle_number $1)
else
    BUILD_NUMBER=$1
fi

echo "SDKUP Release for build number "$BUILD_NUMBER
mkdir -p ${WORKSPACE}/SDK_RELEASE
${WORKSPACE}/FunSDK/scripts/bob --sdkup -s ${WORKSPACE}/SDK_RELEASE -C ${WORKSPACE}/FunSDK-cache \
	    --version=$BUILD_NUMBER release funos.posix-extra


# if the current branch in FunTools is not master, then build flash_tools on top of the SDK
# this is useful for development of flash_tools
flash_tools_br=`cat ${WORKSPACE}/FunTools/.git/HEAD`
if [[ ${flash_tools_br} !=  *refs/heads/master ]]; then
    ## for testing our changes in the FunTools/flash_tools area
    echo "WARNING: using the currently checked out branch of FunTools"
    ${WORKSPACE}/FunSDK/scripts/bob --build -s ${WORKSPACE}/SDK_RELEASE --version=$BUILD_NUMBER flash_tools
fi

echo "Injecting keys..."
mkdir -p ${WORKSPACE}/TO_BE_SIGNED
cd ${WORKSPACE}/SDK_RELEASE
sdknum=`cat build_info.txt`
buildts=`date -u +%Y%m%dT%H%M%SZ`
${WORKSPACE}/FunTools/flash_tools/release.py --action prepare --force-version ${sdknum} \
	    --force-description ${sdknum}'_'${buildts} \
	    --sdkdir `pwd` --destdir ${WORKSPACE}/TO_BE_SIGNED \
	    bin/flash_tools/qspi_config_fungible.json \
	    bin/flash_tools/key_bag_config.json \
	    bin/flash_tools/mmc_config_fungible.json
echo
echo "Done -- For signing a release, copy the start certificate (start_certificate.bin) to the directory "${WORKSPACE}"/TO_BE_SIGNED"
echo
echo "Done -- Finally copy the directory "${WORKSPACE}"/TO_BE_SIGNED to the HSM computer to sign and inject the real keys"
