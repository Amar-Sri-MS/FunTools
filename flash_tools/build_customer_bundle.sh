#!/bin/bash -e

if [ -n "${SDKDIR}" ]; then
    echo "Using SDKDIR: ${SDKDIR}"
elif [ -n "${WORKSPACE}" ]; then
    SDKDIR=${WORKSPACE}/FunSDK
    echo "SDKDIR not set, using ${SDKDIR}"
else
    echo "SDKDIR or WORKSPACE must be set"
    exit 1
fi

if [ "$#" -ne 2 ]; then
    echo "Incorrect arguments, usage:"
    echo "$0 sdk_version {f1|s1|f1d1}"
    echo "     sdk_version value should be the same as used by 'bob'"
    exit 1
fi

CHIP="$2"
USER_VERSION="$1"

pushd ${SDKDIR}

./scripts/bob --version ${USER_VERSION} --sdkup release
./scripts/bob --version ${USER_VERSION} --deploy-up

BUILD_VERSION=$(cat build_info.txt)
WORKDIR=$(mktemp -d)
CUSTOMER_BUNDLE_NAME="customer_sdk_${CHIP}_${BUILD_VERSION}"
BUNDLEDIR=${WORKDIR}/${CUSTOMER_BUNDLE_NAME}


# prepare an sdk release package
./bin/flash_tools/release.py --action sdk-prepare --destdir "${BUNDLEDIR}" \
    --chip "${CHIP}" bin/flash_tools/mmc_config_sdk.json bin/flash_tools/key_bag_config.json \
    --force-version "${BUILD_VERSION}" --force-description "customer sdk bundle"

cd ${BUNDLEDIR}

# sign images that should be signed by fungible
./release.py --destdir . --action sign --default-config-files

# remove some temporary stuff
rm -rf __pycache__
find . -name '*.pyc' -delete

cd ${WORKDIR}
tar czf "${CUSTOMER_BUNDLE_NAME}.tgz" "${CUSTOMER_BUNDLE_NAME}"

popd

cp "${WORKDIR}/${CUSTOMER_BUNDLE_NAME}.tgz" .

echo "Generated customer bundle: ${CUSTOMER_BUNDLE_NAME}.tgz"

rm -rf ${WORKDIR}
