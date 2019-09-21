#!/bin/bash -ex

echo "SKUP Release"
mkdir -p ${WORKSPACE}/SDK_RELEASE
${WORKSPACE}/FunSDK/scripts/bob --sdkup -s ${WORKSPACE}/SDK_RELEASE -C ${WORKSPACE}/FunSDK-cache --version=$1 release funos.posix-extra


# if the current branch in FunTools is not master, then build flash_tools on top of the SDK
# this is useful for development of flash_tools
flash_tools_br=`cat ${WORKSPACE}/FunTools/.git/HEAD`
if [[ ${flash_tools_br} !=  *refs/heads/master ]]; then
    ## for testing our changes in the FunTools/flash_tools area
    echo "WARNING: using the currently checked out branch of FunTools"
    ${WORKSPACE}/FunSDK/scripts/bob --build -s ${WORKSPACE}/SDK_RELEASE --version=$1 flash_tools
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
	    bin/flash_tools/mmc_config_fungible.json
echo
echo "Done -- For signing a release, copy the start certificate (start_certificate.bin) to the directory "${WORKSPACE}"/TO_BE_SIGNED"
echo
echo "Done -- Finally copy the directory "${WORKSPACE}"/TO_BE_SIGNED to the HSM computer to sign and inject the real keys"
